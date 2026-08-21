# -*- coding: utf-8 -*-
"""
보드(프레임그래버) 크롤러 (범용)

구조는 crawl_lens.py 와 동일하며, targets_board.py (BOARD_TARGETS) 를 사용하고
lens_type 대신 board_type 을 메타데이터로 붙인다.

사용법:
    python crawl_board.py
    python crawl_board.py --target euresys_frame_grabbers
    python crawl_board.py --target basler_fg_hub --max-products 5
"""

import argparse
import sys

from common.http_client import get_session, fetch
from common.parsers import extract_specs, extract_links
from common.debug_tools import get_sitemap_product_urls
from common.io_utils import save_raw_html, save_jsonl, save_records_csv
from targets_board import BOARD_TARGETS

RAW_HTML_DIR = "raw_html"
OUTPUT_DIR = "output"

PRIORITY_COLS = ["brand", "board_type", "raw_category", "target_key", "model", "_source_url", "_table_index"]


def crawl_target(session, key: str, target: dict, max_products: int | None = None, save_html: bool = True):
    records = []
    product_urls = []
    seen = set()

    # 1) sitemap 기반 상품 URL 발견 (use_sitemap=True인 경우)
    if target.get("use_sitemap"):
        sm_urls = get_sitemap_product_urls(
            session,
            target.get("base_url", ""),
            target.get("sitemap_keyword", ""),
            lang_prefix=target.get("sitemap_lang_prefix", "/en/"),
        )
        for u in sm_urls:
            if u not in seen:
                seen.add(u)
                product_urls.append(u)
        print(f"  -> sitemap에서 발견된 상품 URL {len(product_urls)}개")

    # 2) listing_urls + product_link_pattern 기반 (기존 방식, 병행 가능)
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

    print(f"  -> 상품 후보 URL 총 {len(product_urls)}개")

    board_type_fn = target.get("board_type_fn")  # board_type == "auto" 일 때 사용

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
        if save_html:
            save_raw_html(RAW_HTML_DIR, key, url, html, prefix="product")

        recs = extract_specs(html, source_url=url, parser_name=target.get("parser", "tables"))
        if not recs:
            recs = [{
                "_source_url": url,
                "_table_index": "none",
                "_note": "table 추출 0건 (JS 렌더링 또는 구조 다름 - debug_target.py로 확인)",
            }]

        # board_type 결정: "auto"면 URL 기반 분류 함수 사용, 아니면 타겟에 지정된 값 그대로
        if target.get("board_type") == "auto" and board_type_fn:
            board_type = board_type_fn(url)
        else:
            board_type = target.get("board_type", "unknown")

        for rec in recs:
            rec["brand"] = target["brand"]
            rec["board_type"] = board_type
            rec["raw_category"] = target.get("raw_category", "")
            rec["target_key"] = key
            records.append(rec)

        if i % 10 == 0 or i == len(product_urls):
            print(f"  ... {i}/{len(product_urls)} 처리")

    return records


def main():
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument("--target", nargs="*", default=None, help="targets_board.py 의 키들 (생략 시 전체)")
    parser.add_argument("--max-products", type=int, default=None, help="타겟당 최대 상품 수 (테스트용)")
    parser.add_argument("--no-html-cache", action="store_true", help="raw_html 캐시 저장 끄기")
    args = parser.parse_args()

    keys = args.target if args.target else list(BOARD_TARGETS.keys())

    invalid = [k for k in keys if k not in BOARD_TARGETS]
    if invalid:
        print(f"[ERROR] 알 수 없는 target_key: {invalid}")
        print("사용 가능한 키:", list(BOARD_TARGETS.keys()))
        sys.exit(1)

    session = get_session()
    all_records = []

    for key in keys:
        target = BOARD_TARGETS[key]
        print(f"\n=== [{key}] {target['brand']} / {target.get('raw_category')} (status={target.get('status')}) ===")
        recs = crawl_target(
            session, key, target,
            max_products=args.max_products,
            save_html=not args.no_html_cache,
        )
        print(f"  -> 레코드 {len(recs)}개 수집")
        all_records.extend(recs)

        save_jsonl(recs, f"{OUTPUT_DIR}/board_{key}.jsonl")
        save_records_csv(recs, f"{OUTPUT_DIR}/board_{key}.csv", priority_cols=PRIORITY_COLS)

    print(f"\n=== 전체 레코드 {len(all_records)}개 ===")
    save_jsonl(all_records, f"{OUTPUT_DIR}/board_all.jsonl")
    save_records_csv(all_records, f"{OUTPUT_DIR}/board_all.csv", priority_cols=PRIORITY_COLS)
    print(f"저장 완료: {OUTPUT_DIR}/board_all.jsonl, {OUTPUT_DIR}/board_all.csv")


if __name__ == "__main__":
    main()
