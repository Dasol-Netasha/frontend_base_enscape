# -*- coding: utf-8 -*-
"""
렌즈 크롤러 (범용)

targets_lens.py 에 정의된 타겟들을 순회하며:
  1. listing_urls 에서 product_link_pattern 에 맞는 상품 상세 URL을 추출
     (pattern이 None이면 listing_url 자체를 상세 페이지로도 취급)
  2. 각 상품 상세 페이지에서 테이블을 추출 (extract_tables_as_records)
  3. brand / lens_type / raw_category / target_key 등 메타데이터를 붙여서 누적
  4. raw_html/ 에 원본 HTML 캐시, output/ 에 JSONL + CSV 저장

사용법:
    python crawl_lens.py                       # 전체 타겟
    python crawl_lens.py --target schneider_cmount schneider_fast
    python crawl_lens.py --target vico_telecentric --max-products 5   # 테스트용 일부만

주의:
  - status가 "needs_debug"인 타겟은 product_link_pattern이 부정확하거나
    스펙 테이블이 JS로 로딩될 수 있어, 결과가 비어있거나 이상할 수 있음.
    먼저 debug_target.py 로 구조를 확인하세요.
  - 결과는 "원본 그대로(raw)" 수집됩니다. 컬럼명 표준화는 이후 별도 단계(column_rules_v*.py 방식)에서 진행.
"""

import argparse
import sys
import re
import json
import time

from bs4 import BeautifulSoup
from common.http_client import get_session, fetch
from common.parsers import extract_specs, extract_links
from common.io_utils import save_raw_html, save_jsonl, save_records_csv
from targets_lens import LENS_TARGETS

RAW_HTML_DIR = "raw_html"
OUTPUT_DIR = "output"

PRIORITY_COLS = ["brand", "lens_type", "raw_category", "target_key", "model", "_source_url", "_table_index"]


def crawl_vico_ajax(session, key: str, target: dict, save_html: bool = True) -> list[dict]:
    """
    Vico 카테고리 페이지의 wpDataTables AJAX 엔드포인트를 통해 전체 데이터를 수집.

    전략:
      1. listing_url 페이지 HTML을 fetch해 nonce(wdtNonceFrontendServerSide_<id>)와
         table_id(data-wpdatatable_id)를 추출
      2. /wp-admin/admin-ajax.php?action=get_wdtable 로 POST, start=0 부터 PAGE_SIZE씩
         페이지네이션하며 전체 수집
      3. 응답 JSON의 data 배열 각 row를 헤더(columns)에 매핑해 dict로 변환
    """
    records = []
    AJAX_URL = "https://vicoimaging.com/wp-admin/admin-ajax.php"
    PAGE_SIZE = 100

    META_SKIP = {"wdt_id", "image", "compare", "product", "specification pdf",
                 "3d igs", "3d step", "details", "series"}
    DETAIL_KEYWORDS = {
        "magnification", "working distance", "maximum sensor", "aperture",
        "numerical aperture", "resolution", "depth of field", "distortion",
        "telecentricity", "length", "coaxial", "lens mount",
    }

    def cell_text(c):
        if not c:
            return ""
        s = BeautifulSoup(str(c), "lxml").get_text(" ", strip=True)
        return re.sub(r"\s+", " ", s).strip()

    for listing_url in target.get("listing_urls", []):
        try:
            resp = fetch(session, listing_url)
        except Exception as e:
            print(f"  [WARN] listing fetch 실패: {listing_url} ({e})")
            continue

        if resp.status_code != 200:
            print(f"  [WARN] listing status={resp.status_code}: {listing_url}")
            continue

        html = resp.text
        if save_html:
            save_raw_html(RAW_HTML_DIR, key, listing_url, html, prefix="listing")

        # --- nonce + table_id 추출 ---
        nonce_m = re.search(
            r'id="wdtNonceFrontendServerSide_(\d+)"[^>]*value="([a-f0-9]+)"', html
        )
        if not nonce_m:
            # 속성 순서가 반대인 경우
            nonce_m = re.search(
                r'name="wdtNonceFrontendServerSide_(\d+)"[^>]*value="([a-f0-9]+)"', html
            )
        if not nonce_m:
            print(f"  [WARN] nonce 추출 실패: {listing_url}")
            continue

        table_id = nonce_m.group(1)
        nonce = nonce_m.group(2)

        # --- 컬럼 헤더 추출 ---
        soup = BeautifulSoup(html, "lxml")
        table_tag = soup.find("table", {"data-wpdatatable_id": table_id})
        if not table_tag:
            print(f"  [WARN] table#{table_id} 태그 없음: {listing_url}")
            continue

        headers = [th.get_text(" ", strip=True)
                   for th in table_tag.find("thead").find_all("th")]

        # 스펙 컬럼 인덱스 결정 (패턴 A: _ suffix / 패턴 B: 풀네임)
        has_underscore_cols = any(
            "_" in h for h in headers if h.lower() not in META_SKIP
        )

        spec_cols = []   # [(col_index, col_name), ...]
        model_col_idx = None

        if has_underscore_cols:
            for idx, h in enumerate(headers):
                if h.lower() in META_SKIP:
                    continue
                if "_" in h:
                    col_name = h.rstrip("_").replace("_", " ").strip()
                    if col_name.lower() in META_SKIP:
                        continue
                    if "model" in col_name.lower() and "no" in col_name.lower():
                        model_col_idx = idx
                        col_name = "model"
                    spec_cols.append((idx, col_name))
        else:
            for idx, h in enumerate(headers):
                h_lower = h.lower()
                if h_lower in META_SKIP:
                    continue
                if h_lower.startswith("lens") and "model" in h_lower and "no" in h_lower:
                    model_col_idx = idx
                    spec_cols.append((idx, "model"))
                    continue
                if any(kw in h_lower for kw in DETAIL_KEYWORDS):
                    spec_cols.append((idx, h.strip()))

        if not spec_cols or model_col_idx is None:
            print(f"  [WARN] 스펙 컬럼 인식 실패 (headers={headers[:5]}): {listing_url}")
            continue

        # --- AJAX 페이지네이션으로 전체 데이터 수집 ---
        ajax_headers = {
            "Content-Type": "application/x-www-form-urlencoded; charset=UTF-8",
            "Referer": listing_url,
            "X-Requested-With": "XMLHttpRequest",
        }
        start = 0
        total = None
        url_records = []

        while True:
            post_data = {
                "action": "get_wdtable",
                "table_id": table_id,
                "draw": str(start // PAGE_SIZE + 1),
                "start": str(start),
                "length": str(PAGE_SIZE),
                "search[value]": "",
                "search[regex]": "false",
                "order[0][column]": "0",
                "order[0][dir]": "asc",
                f"wdtNonceFrontendServerSide_{table_id}": nonce,
            }

            try:
                ajax_resp = session.post(
                    AJAX_URL, data=post_data, headers=ajax_headers, timeout=30
                )
            except Exception as e:
                print(f"  [WARN] AJAX POST 실패 (start={start}): {e}")
                break

            if ajax_resp.status_code != 200:
                print(f"  [WARN] AJAX status={ajax_resp.status_code} (start={start})")
                break

            try:
                j = ajax_resp.json()
            except Exception as e:
                print(f"  [WARN] AJAX JSON 파싱 실패 (start={start}): {e}")
                break

            if total is None:
                total = j.get("recordsTotal", 0)
                print(f"  -> AJAX table#{table_id}: 총 {total}개 레코드")

            rows = j.get("data", [])
            if not rows:
                break

            for row_idx, row in enumerate(rows, start + 1):
                model_val = cell_text(row[model_col_idx]) if model_col_idx < len(row) else ""
                if not model_val or model_val.isdigit():
                    continue

                rec = {
                    "model": model_val,
                    "_source_url": listing_url,
                    "_table_index": f"vico_row_{row_idx}",
                }
                for col_idx, col_name in spec_cols:
                    if col_name == "model":
                        continue
                    val = cell_text(row[col_idx]) if col_idx < len(row) else ""
                    rec[col_name] = val

                url_records.append(rec)

            start += len(rows)
            if start >= total:
                break

            time.sleep(0.3)

        print(f"  -> {listing_url} → {len(url_records)}개 수집")
        records.extend(url_records)

    return records


def crawl_target(session, key: str, target: dict, max_products: int | None = None, save_html: bool = True):
    # vico_ajax 파서는 별도 함수로 처리 (AJAX 페이지네이션)
    if target.get("parser") == "vico_ajax":
        return crawl_vico_ajax(session, key, target, save_html=save_html)

    records = []
    product_urls = []
    seen = set()

    for listing_url in target.get("listing_urls", []):
        try:
            resp = fetch(session, listing_url)
        except Exception as e:
            print(f"  [WARN] listing fetch 실패: {listing_url} ({e})")
            continue

        if resp.status_code != 200:
            print(f"  [WARN] listing status={resp.status_code}: {listing_url}")
            continue

        html = resp.text
        # EUC-KR 사이트: bytes로 디코딩
        if target.get("encoding") == "euc-kr":
            html = resp.content.decode("euc-kr", errors="ignore")
        if save_html:
            save_raw_html(RAW_HTML_DIR, key, listing_url, html, prefix="listing")

        pattern = target.get("product_link_pattern")
        if pattern:
            links = extract_links(html, listing_url, pattern=pattern)
            for l in links:
                if l not in seen:
                    seen.add(l)
                    product_urls.append(l)
        else:
            if listing_url not in seen:
                seen.add(listing_url)
                product_urls.append(listing_url)

    if max_products:
        product_urls = product_urls[:max_products]

    print(f"  -> 상품 후보 URL {len(product_urls)}개")

    for i, url in enumerate(product_urls, 1):
        try:
            resp = fetch(session, url)
        except Exception as e:
            print(f"  [WARN] product fetch 실패 ({i}/{len(product_urls)}): {url} ({e})")
            continue

        if resp.status_code != 200:
            print(f"  [WARN] product status={resp.status_code} ({i}/{len(product_urls)}): {url}")
            continue

        html = resp.text
        # EUC-KR 사이트: bytes로 직접 디코딩
        if target.get("encoding") == "euc-kr":
            html = resp.content.decode("euc-kr", errors="ignore")
        if save_html:
            save_raw_html(RAW_HTML_DIR, key, url, html, prefix="product")

        recs = extract_specs(html, source_url=url, parser_name=target.get("parser", "tables"))
        if not recs:
            recs = [{
                "_source_url": url,
                "_table_index": "none",
                "_note": "table 추출 0건 (JS 렌더링 또는 구조 다름 - debug_target.py로 확인)",
            }]

        for rec in recs:
            rec["brand"] = target["brand"]
            rec["lens_type"] = target["lens_type"]
            rec["raw_category"] = target.get("raw_category", "")
            rec["target_key"] = key
            # model_from_url: URL 마지막 경로 세그먼트를 model로 사용 (예: Basler docs)
            if target.get("model_from_url") and "model" not in rec:
                slug = url.rstrip("/").split("/")[-1]
                slug = re.sub(r"\.html?$", "", slug)
                rec["model"] = slug.upper()
            records.append(rec)

        if i % 10 == 0 or i == len(product_urls):
            print(f"  ... {i}/{len(product_urls)} 처리")

    return records


def main():
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument("--target", nargs="*", default=None, help="targets_lens.py 의 키들 (생략 시 전체)")
    parser.add_argument("--max-products", type=int, default=None, help="타겟당 최대 상품 수 (테스트용)")
    parser.add_argument("--no-html-cache", action="store_true", help="raw_html 캐시 저장 끄기")
    args = parser.parse_args()

    keys = args.target if args.target else list(LENS_TARGETS.keys())

    invalid = [k for k in keys if k not in LENS_TARGETS]
    if invalid:
        print(f"[ERROR] 알 수 없는 target_key: {invalid}")
        print("사용 가능한 키:", list(LENS_TARGETS.keys()))
        sys.exit(1)

    session = get_session()
    all_records = []

    for key in keys:
        target = LENS_TARGETS[key]
        print(f"\n=== [{key}] {target['brand']} / {target.get('raw_category')} (status={target.get('status')}) ===")
        recs = crawl_target(
            session, key, target,
            max_products=args.max_products,
            save_html=not args.no_html_cache,
        )

        for rec in recs:
            rec.setdefault("brand", target["brand"])
            rec.setdefault("lens_type", target["lens_type"])
            rec.setdefault("raw_category", target.get("raw_category", ""))
            rec.setdefault("target_key", key)

        print(f"  -> 레코드 {len(recs)}개 수집")
        all_records.extend(recs)

        save_jsonl(recs, f"{OUTPUT_DIR}/lens_{key}.jsonl")
        save_records_csv(recs, f"{OUTPUT_DIR}/lens_{key}.csv", priority_cols=PRIORITY_COLS)

    print(f"\n=== 전체 레코드 {len(all_records)}개 ===")
    save_jsonl(all_records, f"{OUTPUT_DIR}/lens_all.jsonl")
    save_records_csv(all_records, f"{OUTPUT_DIR}/lens_all.csv", priority_cols=PRIORITY_COLS)
    print(f"저장 완료: {OUTPUT_DIR}/lens_all.jsonl, {OUTPUT_DIR}/lens_all.csv")


if __name__ == "__main__":
    main()
