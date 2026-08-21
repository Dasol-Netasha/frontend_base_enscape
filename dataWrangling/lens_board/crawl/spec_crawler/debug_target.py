# -*- coding: utf-8 -*-
"""
사이트 구조 분석 CLI

사용법:
    python debug_target.py <target_key>
    python debug_target.py --url https://example.com/some/page
    python debug_target.py --list                  # 사용 가능한 target_key 목록 출력

target_key 는 targets_lens.py (LENS_TARGETS) 또는 targets_board.py (BOARD_TARGETS) 의 키.

결과:
    debug_output/<target_key>/page_00_xxx.html  (원본 HTML)
    debug_output/<target_key>/report.txt        (구조 분석 리포트)

report.txt 의 내용을 Claude에게 그대로 붙여넣어 주시면,
그 결과를 보고 product_link_pattern / 파서를 보정해서 크롤러를 완성합니다.
"""

import sys

from common.debug_tools import run
from targets_lens import LENS_TARGETS, VIEWORKS_CAMERA_TARGET
from targets_board import BOARD_TARGETS


def all_targets() -> dict:
    merged = {}
    merged.update(LENS_TARGETS)
    merged.update(BOARD_TARGETS)
    merged["vieworks_camera"] = VIEWORKS_CAMERA_TARGET
    return merged


def main():
    targets = all_targets()

    if len(sys.argv) < 2:
        print(__doc__)
        sys.exit(0)

    if sys.argv[1] == "--list":
        print("=== 사용 가능한 target_key ===")
        for k, v in targets.items():
            print(f"  {k:28s} brand={v.get('brand'):20s} status={v.get('status', '-')}")
        sys.exit(0)

    if sys.argv[1] == "--url":
        if len(sys.argv) < 3:
            print("URL을 입력하세요: python debug_target.py --url https://...")
            sys.exit(1)
        run(target_key=None, url=sys.argv[2])
        sys.exit(0)

    key = sys.argv[1]
    target = targets.get(key)
    if not target:
        print(f"[ERROR] target_key '{key}' 를 찾을 수 없습니다.\n")
        print("사용 가능한 키 목록 (python debug_target.py --list):")
        for k in targets.keys():
            print(f"  - {k}")
        sys.exit(1)

    print(f"=== target: {key}  (brand={target.get('brand')}, status={target.get('status')}) ===")
    if target.get("notes"):
        print(f"notes: {target['notes']}\n")

    run(
        target_key=key,
        url=None,
        listing_urls=target.get("listing_urls", []),
        link_pattern=target.get("product_link_pattern"),
        base_url=target.get("base_url"),
        sitemap_keyword=target.get("sitemap_keyword"),
        use_sitemap=target.get("use_sitemap", False),
        sitemap_lang_prefix=target.get("sitemap_lang_prefix", "/en/"),
    )


if __name__ == "__main__":
    main()
