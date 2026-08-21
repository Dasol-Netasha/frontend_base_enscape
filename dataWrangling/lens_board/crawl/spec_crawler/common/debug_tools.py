# -*- coding: utf-8 -*-
"""
디버깅 / 사이트 구조 분석 도구

크롤러를 만들기 전에, 각 사이트의 실제 구조(테이블 유무, 링크 패턴, JS 렌더링 여부 등)를
먼저 파악하기 위한 스크립트.

사용법:
    python debug_target.py <target_key>          # targets_lens.py / targets_board.py 에 정의된 키
    python debug_target.py --url <임의의 URL>     # 임의 URL 1개만 점검

출력:
    debug_output/<target_key 또는 도메인>/ 폴더에
      - listing_<n>.html  (원본 HTML 저장)
      - report.txt        (구조 분석 리포트)

report.txt 에는 다음이 포함됨:
  - 페이지 제목
  - <table> 개수와 각 테이블의 행/열 크기, 추출 시도 결과 미리보기
  - extract_links()로 찾은 링크 후보 (상품 상세 페이지로 추정되는 것들)
  - find_json_blobs() / find_api_like_urls() 결과 (JS 렌더링 의심 시그널)
  - sitemap.xml 존재 여부 및 일부 URL 목록

이 report.txt 내용을 Claude에게 붙여넣어 주면, 그에 맞춰 크롤러 파서를 보정합니다.
"""

import os
from urllib.parse import urlparse

from common.http_client import get_session, fetch
from common.parsers import (
    extract_tables_as_records,
    extract_dl_specs,
    extract_links,
    find_json_blobs,
    find_api_like_urls,
)


def _domain_of(url: str) -> str:
    return urlparse(url).netloc.replace(":", "_")


def _safe_filename(s: str) -> str:
    return "".join(c if c.isalnum() or c in "-_." else "_" for c in s)[:80]


def inspect_url(session, url: str, outdir: str, index: int = 0, link_pattern: str | None = None):
    os.makedirs(outdir, exist_ok=True)
    report_lines = []
    report_lines.append(f"=== URL: {url} ===")

    try:
        resp = fetch(session, url)
    except Exception as e:
        report_lines.append(f"[ERROR] 요청 실패: {e}")
        return "\n".join(report_lines)

    report_lines.append(f"status_code: {resp.status_code}")
    html = resp.text

    # 원본 HTML 저장
    fname = f"page_{index:02d}_{_safe_filename(urlparse(url).path or 'root')}.html"
    fpath = os.path.join(outdir, fname)
    with open(fpath, "w", encoding="utf-8") as f:
        f.write(html)
    report_lines.append(f"saved html -> {fpath} ({len(html)} bytes)")

    # 테이블 분석
    records = extract_tables_as_records(html, source_url=url)
    report_lines.append(f"\n[<table> 추출] 레코드 수: {len(records)}")
    for i, rec in enumerate(records[:3]):
        keys = [k for k in rec.keys() if not k.startswith("_")]
        report_lines.append(f"  - record[{i}] 필드 {len(keys)}개, 미리보기: {keys[:10]}")
        sample = {k: rec[k] for k in keys[:5]}
        report_lines.append(f"    sample values: {sample}")

    if not records:
        report_lines.append("  -> <table> 추출 0건.")

    # dl/dt/dd 기반 분석 (Euresys 류 구조)
    dl_records = extract_dl_specs(html, source_url=url)
    report_lines.append(f"\n[<dl> 정의목록 추출] 레코드 수: {len(dl_records)}")
    for i, rec in enumerate(dl_records[:1]):
        keys = [k for k in rec.keys() if not k.startswith("_")]
        report_lines.append(f"  - record[{i}] 필드 {len(keys)}개: {keys}")

    if not records and not dl_records:
        report_lines.append("\n  -> table/dl 둘 다 0건. JS 렌더링 또는 또 다른 구조일 가능성 있음.")

    # 링크 분석
    links = extract_links(html, url, pattern=link_pattern)
    report_lines.append(f"\n[링크] {'패턴 매칭 ' if link_pattern else ''}링크 수: {len(links)}")
    for l in links[:15]:
        report_lines.append(f"  - {l}")
    if len(links) > 15:
        report_lines.append(f"  ... 외 {len(links) - 15}개")

    # JS / JSON 데이터 분석 (JS 렌더링 의심 신호)
    blobs = find_json_blobs(html)
    api_like = find_api_like_urls(html)
    report_lines.append(f"\n[JS/JSON 신호] script JSON blob: {len(blobs)}개, API-like 경로 후보: {len(api_like)}개")
    for a in api_like[:10]:
        report_lines.append(f"  - {a}")

    return "\n".join(report_lines)


def get_sitemap_product_urls(session, base_url: str, sitemap_keyword: str,
                              lang_prefix: str | None = "/en/") -> list[str]:
    """
    base_url 도메인의 /sitemap.xml(인덱스)에서 sitemap_keyword를 포함하는 하위 sitemap을 찾고,
    그 안의 <loc> 목록(=상품 URL)을 반환한다.
    lang_prefix 가 주어지면, 하위 sitemap URL 자체에 그 prefix가 포함된 것만 사용
    (예: wp-sitemap-posts-frame-grabber-1.xml 가 언어별로 /en/, /de/, /ko/ 등 따로 존재하는 경우).

    실패 시 빈 리스트 반환.
    """
    import re
    parsed = urlparse(base_url)
    root = f"{parsed.scheme}://{parsed.netloc}"
    index_url = root + "/sitemap.xml"

    try:
        resp = fetch(session, index_url, min_delay=0.3, max_delay=0.8)
        if resp.status_code != 200:
            return []
        sub_sitemaps = re.findall(r"<loc>(.*?)</loc>", resp.text)
    except Exception:
        return []

    matched = [
        s for s in sub_sitemaps
        if sitemap_keyword.lower() in s.lower() and (lang_prefix is None or lang_prefix in s)
    ]

    product_urls = []
    for sm_url in matched:
        try:
            resp = fetch(session, sm_url, min_delay=0.3, max_delay=0.8)
            if resp.status_code != 200:
                continue
            locs = re.findall(r"<loc>(.*?)</loc>", resp.text)
            for l in locs:
                if lang_prefix is None or lang_prefix in l:
                    product_urls.append(l)
        except Exception:
            continue

    return product_urls


def check_sitemap(session, base_url: str, sitemap_keyword: str | None = None) -> str:
    """
    robots.txt 및 sitemap.xml 확인.
    sitemap_keyword 가 주어지면, sitemap.xml(인덱스)에서 발견된 하위 sitemap URL 중
    keyword를 포함하는 것을 추가로 fetch해서 그 안의 <loc> 목록(=실제 상품 URL)까지 출력.
    (WordPress의 wp-sitemap-posts-<custom-post-type>-N.xml 구조 대응)
    """
    import re
    lines = []
    parsed = urlparse(base_url)
    root = f"{parsed.scheme}://{parsed.netloc}"

    sub_sitemaps: list[str] = []

    for path in ["/robots.txt", "/sitemap.xml", "/sitemap_index.xml"]:
        url = root + path
        try:
            resp = fetch(session, url, min_delay=0.3, max_delay=0.8)
            if resp.status_code == 200 and len(resp.text) > 0:
                lines.append(f"[OK] {url} (status={resp.status_code}, len={len(resp.text)})")
                if "sitemap" in path:
                    locs = re.findall(r"<loc>(.*?)</loc>", resp.text)
                    lines.append(f"     <loc> 개수: {len(locs)}")
                    for l in locs[:10]:
                        lines.append(f"     - {l}")
                    if len(locs) > 10:
                        lines.append(f"     ... 외 {len(locs) - 10}개")
                    sub_sitemaps.extend(locs)
            else:
                lines.append(f"[--] {url} (status={resp.status_code})")
        except Exception as e:
            lines.append(f"[ERROR] {url}: {e}")

    if sitemap_keyword and sub_sitemaps:
        matched = [s for s in sub_sitemaps if sitemap_keyword.lower() in s.lower()]
        lines.append(f"\n--- sitemap_keyword='{sitemap_keyword}' 매칭 하위 sitemap: {len(matched)}개 ---")
        for sm_url in matched:
            try:
                resp = fetch(session, sm_url, min_delay=0.3, max_delay=0.8)
                if resp.status_code != 200:
                    lines.append(f"  [--] {sm_url} (status={resp.status_code})")
                    continue
                locs = re.findall(r"<loc>(.*?)</loc>", resp.text)
                lines.append(f"  [OK] {sm_url} -> <loc> {len(locs)}개")
                for l in locs:
                    lines.append(f"     - {l}")
            except Exception as e:
                lines.append(f"  [ERROR] {sm_url}: {e}")

    return "\n".join(lines)


def run(target_key: str | None, url: str | None, listing_urls: list[str] | None = None,
        link_pattern: str | None = None, base_url: str | None = None,
        sitemap_keyword: str | None = None, use_sitemap: bool = False,
        sitemap_lang_prefix: str | None = "/en/", sample_size: int = 2):
    session = get_session()

    if url:
        urls = [url]
        outdir = os.path.join("debug_output", _domain_of(url))
    else:
        urls = list(listing_urls or [])
        outdir = os.path.join("debug_output", target_key or "unknown")

    os.makedirs(outdir, exist_ok=True)

    report_chunks = []

    sitemap_urls: list[str] = []
    if use_sitemap and base_url and sitemap_keyword:
        sitemap_urls = get_sitemap_product_urls(session, base_url, sitemap_keyword, lang_prefix=sitemap_lang_prefix)
        chunk = [f"=== sitemap 기반 상품 URL: {len(sitemap_urls)}개 (sitemap_keyword='{sitemap_keyword}') ==="]
        for u in sitemap_urls:
            chunk.append(f"  - {u}")
        report_chunks.append("\n".join(chunk))

        if not urls:
            urls = sitemap_urls[:sample_size]
            if urls:
                report_chunks.append(
                    f"\n(listing_urls가 비어있어 sitemap 결과 중 처음 {len(urls)}개를 샘플로 상세 점검합니다)"
                )

    for i, u in enumerate(urls):
        report_chunks.append(inspect_url(session, u, outdir, index=i, link_pattern=link_pattern))

    if urls or sitemap_urls:
        sm_base = base_url or (urls[0] if urls else sitemap_urls[0])
        report_chunks.append("\n=== sitemap / robots 확인 ===")
        report_chunks.append(check_sitemap(session, sm_base, sitemap_keyword=sitemap_keyword))

    report_text = "\n\n".join(report_chunks)
    report_path = os.path.join(outdir, "report.txt")
    with open(report_path, "w", encoding="utf-8") as f:
        f.write(report_text)

    print(report_text)
    print(f"\n\n[리포트 저장 완료] {report_path}")
    print("위 내용을 Claude에게 붙여넣어 주세요.")


# 이 파일은 라이브러리 모듈입니다. CLI 진입점은 프로젝트 루트의 debug_target.py 를 사용하세요.
# 예: python debug_target.py schneider_lens
#     python debug_target.py --url https://example.com/page
