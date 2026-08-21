# -*- coding: utf-8 -*-
"""
보드(프레임그래버) 브랜드별 크롤링 대상 설정

구조는 targets_lens.py 와 동일하나, lens_type 대신 board_type 사용.
board_type 후보: camera_link / coaxpress / analog / unknown
(보드는 "인터페이스 표준" 기준이 카메라의 area/line, 렌즈의 telecentric/fixed_focal 에 대응하는
 가장 큰 분류축이라고 보면 됨 - Camera Link 보드와 CoaXPress 보드는 스펙 항목 구성이 다름)

board_type == "auto" 인 타겟은 crawl_board.py 가 "board_type_fn"을 이용해
각 상품 URL마다 개별적으로 board_type 을 분류한다.
"""


def classify_euresys_board(url: str) -> str:
    """URL 경로의 제품 라인명으로 board_type 분류 (Euresys 전용)"""
    path = url.lower()
    if "/coaxlink" in path:
        return "coaxpress"          # CoaXPress 인터페이스
    if "/grablink" in path:
        return "camera_link"        # Camera Link 인터페이스
    if "/domino" in path:
        return "analog"             # 비표준 아날로그 영상 입력
    if "/picolo" in path:
        return "analog_video"       # PAL/NTSC 비디오 캡처
    return "unknown"


def classify_basler_board(url: str) -> str:
    """URL slug 기준 board_type 분류 (Basler 전용).

    microEnable 5 marathon ACL / VCL / VCLx 만 Camera Link 인터페이스이고,
    나머지(imaFlex/imaWorx, marathon ACX-*/VCX-QP)는 CoaXPress(-over-Fiber 포함) 계열.
    """
    slug = url.rstrip("/").split("/")[-1].lower()
    if slug.endswith("-acl") or slug.endswith("-vcl") or slug.endswith("-vclx"):
        return "camera_link"
    return "coaxpress"


BOARD_TARGETS = {
    # ------------------------------------------------------------------
    # Basler 프레임그래버
    # ------------------------------------------------------------------
    "basler_fg_hub": {
        "brand": "Basler",
        "board_type": "auto",
        "board_type_fn": classify_basler_board,
        "raw_category": "Frame Grabbers (imaFlex/imaWorx/microEnable 5 marathon)",
        # docs.baslerweb.com/frame-grabbers/microenable-5-marathon 의 "Models" 목록 +
        # docs.baslerweb.com/frame-grabbers/index.html 의 imaFlex/imaWorx 목록 기준 11개 직접 나열.
        # frame-grabbers 허브 페이지(#products)는 JS/AJAX 로딩이라 상품 카드가 비어있으므로,
        # sitemap/링크패턴 대신 /shop/<slug>/ 상품 페이지 URL을 직접 listing_urls로 사용
        # (product_link_pattern=None -> crawl_board.py가 listing_url 자체를 product URL로 처리).
        "listing_urls": [
            # imaFlex / imaWorx (CXP-12 / CoaXPress-over-Fiber)
            "https://www.baslerweb.com/en-us/shop/imaflex-2-dual-100/",
            "https://www.baslerweb.com/en-us/shop/imaflex-cxp-12-quad/",
            "https://www.baslerweb.com/en-us/shop/imaflex-cxp-12-penta/",
            "https://www.baslerweb.com/en-us/shop/imaworx-cxp-12-quad/",
            # microEnable 5 marathon - CoaXPress (A Series / V Series)
            "https://www.baslerweb.com/en-us/shop/microenable-5-marathon-acx-sp/",
            "https://www.baslerweb.com/en-us/shop/microenable-5-marathon-acx-dp/",
            "https://www.baslerweb.com/en-us/shop/microenable-5-marathon-acx-qp/",
            "https://www.baslerweb.com/en-us/shop/microenable-5-marathon-vcx-qp/",
            # microEnable 5 marathon - Camera Link (A Series / V Series)
            "https://www.baslerweb.com/en-us/shop/microenable-5-marathon-acl/",
            "https://www.baslerweb.com/en-us/shop/microenable-5-marathon-vcl/",
            "https://www.baslerweb.com/en-us/shop/microenable-5-marathon-vclx/",
        ],
        "product_link_pattern": None,  # listing_url 자체가 product 상세 페이지
        "base_url": "https://www.baslerweb.com/en-us/shop/",
        "parser": "tables",
        "status": "ready",
        "notes": (
            "11개 슬러그 전부 200 OK, parser='tables'로 40~47개 필드씩 정상 추출 확인됨 (debug_target.py 실행 "
            "결과). 'model'은 <title>의 ' | ' 앞부분에서 자동 추출 (예: 'microEnable 5 marathon ACX-DP'). "
            "추정했던 microenable-5-marathon-acx-sp(Order Number 2200000356, 47필드) / "
            "-acx-dp(Order Number 2200000355) 슬러그 둘 다 실존 확인됨. "
            "다만 acx-dp는 5필드(Order Number/Type/Last Time Buy: 12/31/2022/Last Time Service: 03/31/2025/model)만 "
            "추출되는데, 이는 파서 문제가 아니라 해당 모델이 EOL(단종)이라 Basler가 상세 스펙 표를 페이지에서 "
            "제거하고 단종 안내만 남겨둔 것 - 정상 데이터임 (표준화 단계에서 빈 칸으로 처리하면 됨). "
            "classify_basler_board()로 board_type 자동 분류 "
            "(슬러그가 -acl/-vcl/-vclx로 끝나면 camera_link, 나머지는 coaxpress/CoF 포함 - imaFlex/imaWorx 4종 + "
            "marathon ACX-{SP,DP,QP}/VCX-QP는 coaxpress, marathon ACL/VCL/VCLx 3종은 camera_link)."
        ),
    },

    # ------------------------------------------------------------------
    # Euresys 프레임그래버 (전체 - sitemap 기반)
    # ------------------------------------------------------------------
    "euresys_frame_grabbers": {
        "brand": "Euresys",
        "board_type": "auto",
        "board_type_fn": classify_euresys_board,
        "raw_category": "Frame Grabbers (Coaxlink/Grablink/Domino/Picolo - all)",
        "listing_urls": [],  # sitemap으로 대체
        "product_link_pattern": None,
        "base_url": "https://www.euresys.com/",
        "use_sitemap": True,
        "sitemap_keyword": "frame-grabber",
        "sitemap_lang_prefix": "/en/",
        "parser": "dl_specs",
        "status": "ready",
        "notes": (
            "wp-sitemap-posts-frame-grabber-1.xml 에서 31개 상품 URL을 직접 가져옴 "
            "(coaxlink-* -> coaxpress, grablink-* -> camera_link, domino-*/picolo-* -> analog 계열, "
            "classify_euresys_board()로 자동 분류). "
            "Grablink Value 페이지 구조(dl.specifications__section__content > "
            "div.specification__single > dt/dd) 기준으로 dl_specs 파서 적용. "
            "Coaxlink/Domino/Picolo 페이지가 같은 구조인지는 실제 크롤링 결과로 확인 필요 "
            "(extract_specs가 dl_specs -> tables 순서로 자동 fallback하므로 구조가 달라도 일부는 잡힐 수 있음)."
        ),
    },
}
