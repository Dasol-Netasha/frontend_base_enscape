# -*- coding: utf-8 -*-
"""
렌즈 브랜드별 크롤링 대상 설정

각 항목 구조:
{
    "brand": 브랜드명 (출력 데이터의 brand 컬럼에 들어감),
    "lens_type": 우리가 분류한 렌즈 종류
                 (fixed_focal / telecentric / linescan_telecentric / macro / zoom / view360 / unknown)
                 -> 이 listing_urls 에서 발견되는 제품은 일단 이 타입으로 태깅됨
                 -> 실제 표준화 단계에서 원본 카테고리명(raw_category)과 비교해서 재조정 가능
    "raw_category": 사이트에 표시된 원래 카테고리명 (참고용, raw_category 컬럼으로 저장)
    "listing_urls": 제품 목록/카테고리 페이지 URL들. 여기서 상품 상세 링크를 추출함.
    "product_link_pattern": 목록 페이지에서 "상품 상세 페이지"로 추정되는 링크를 거르는 정규식.
                            *** 디버깅 결과를 보고 채워야 하는 항목이 많음 (None = 전체 링크 사용) ***
    "base_url": sitemap.xml 점검용 도메인 루트
    "status": "ready" (바로 크롤 시도 가능) / "needs_debug" (디버깅 먼저 필요)
    "notes": 참고사항
}

먼저 각 타겟에 대해:
    python debug_target.py <key>
를 실행해서 report.txt 를 확인하고, product_link_pattern / 파서 보정이 필요한지 판단합니다.
"""

LENS_TARGETS = {
    # ------------------------------------------------------------------
    # Basler (렌즈) — docs.baslerweb.com/sitemap.xml 기반
    #
    # 브랜드 구분:
    #   Basler 자체 제조: C125/C23/C10/C11/C12/F-S35 (고정초점), C11T/C12T/C23T (텔레센트릭)
    #   파트너 브랜드 (Computar, Fujinon, Kowa, Moritex 등): partner-* 페이지에서 별도 크롤
    #
    # listing 전략: sitemap.xml에서 모델명 패턴으로 URL 필터링
    #   - sitemap URL 형식: https://docs.baslerweb.com/<model-slug>
    #   - 개별 페이지 스펙: table 또는 dl 구조 (로컬 debug_target으로 확인 필요)
    # ------------------------------------------------------------------
    "basler_lens_fixed_focal": {
        "brand": "Basler",
        "lens_type": "fixed_focal",
        "raw_category": "Fixed Focal Lenses (Basler)",
        "listing_urls": [
            "https://docs.baslerweb.com/sitemap.xml",
        ],
        # C125-, C23-, C10-, C11-, C12- (C-Mount), F-S35- (F-Mount)
        # telecentric(C11T/C12T/C23T) 제외: t가 없는 것만
        "product_link_pattern": r"docs\.baslerweb\.com/(c(?:125|23|10|11|12)-[0-9a-z-]+|f-s35-[0-9a-z-]+)$",
        "base_url": "https://docs.baslerweb.com/",
        "parser": "tables",
        "model_from_url": True,
        "status": "ready",
        "notes": (
            "sitemap.xml에서 Basler 자체 고정초점 렌즈 URL 추출. "
            "C125/C23/C10/C11/C12 (C-Mount), F-S35 (F-Mount). "
            "텔레센트릭(C11T/C12T/C23T)은 basler_lens_telecentric에서 처리. "
            "개별 페이지 스펙: table 구조 (Order Number, Magnification, WD 등 16개 필드)."
        ),
    },
    "basler_lens_telecentric": {
        "brand": "Basler",
        "lens_type": "telecentric",
        "raw_category": "Telecentric Lenses (Basler)",
        "listing_urls": [
            "https://docs.baslerweb.com/sitemap.xml",
        ],
        # C11T-, C12T-, C23T- 시리즈만
        "product_link_pattern": r"docs\.baslerweb\.com/c(?:11|12|23)t-[0-9a-z-]+$",
        "base_url": "https://docs.baslerweb.com/",
        "parser": "tables",
        "model_from_url": True,
        "status": "ready",
        "notes": (
            "sitemap.xml에서 Basler 자체 텔레센트릭 렌즈 URL 추출. "
            "C11T (1.1inch sensor), C12T (1.2inch), C23T (2/3inch). "
            "VI = variable iris, C = coaxial light coupling. "
            "개별 페이지 스펙: table 구조 (Order Number, Magnification, WD 등 16개 필드)."
        ),
    },
    "basler_lens_partner_telecentric": {
        "brand": "(partner)",
        "lens_type": "telecentric",
        "raw_category": "Telecentric Lenses (Partner: Moritex 등)",
        "listing_urls": [
            "https://docs.baslerweb.com/partner-telecentric-lenses",
        ],
        "product_link_pattern": r"docs\.baslerweb\.com/[a-z]+[0-9]+-[a-z0-9-]+$",
        "base_url": "https://docs.baslerweb.com/",
        "parser": "dl_specs",
        "status": "needs_debug",
        "notes": (
            "Basler가 판매하는 파트너 브랜드 텔레센트릭 렌즈 (Moritex MML 시리즈 등). "
            "brand 컬럼은 표준화 단계에서 개별 모델명으로 수정 필요. "
            "listing 페이지 구조 확인 필요."
        ),
    },

    # ------------------------------------------------------------------
    # T-Optics (티옵틱스, 한국)
    # robots.txt 차단 → 로컬에서 debug_target.py로 구조 확인 필요
    # 제품 카테고리 (검색 기반):
    #   Telecentric: Sensor Dia.9mm / 11mm / HRP11mm / Long WD 18mm / 25M50M / Line Scan 12K,16K
    #   Non-Telecentric: MCL 8~18mm / Line Scan 2K,4K
    # ------------------------------------------------------------------
    "toptics_telecentric": {
        "brand": "T-Optics",
        "lens_type": "telecentric",
        "raw_category": "Telecentric Lenses",
        "listing_urls": [
            "http://www.toptics.co.kr/design/subpage/sub2-1.asp?category=C1548933630",
        ],
        "product_link_pattern": r"sub2-1\.asp\?mode=view&id=\d+",
        "base_url": "http://www.toptics.co.kr/",
        "parser": "toptics",
        "encoding": "euc-kr",
        "status": "ready",
        "notes": (
            "카테고리: sub2-1.asp?category=C1548933630 (Telecentric). "
            "제품 링크: sub2-1.asp?mode=view&id=<n>. "
            "EUC-KR 인코딩. detail-view div 안에 detail-table 클래스 테이블로 스펙 존재. "
            "헤더가 <th> 대신 <td>로 구성된 특수 구조 → toptics 파서 사용."
        ),
    },
    "toptics_fa_lens": {
        "brand": "T-Optics",
        "lens_type": "fixed_focal",
        "raw_category": "Non-Telecentric Lenses (MCL)",
        "listing_urls": [
            "http://www.toptics.co.kr/design/subpage/sub2-1.asp?category=C1548933732",
        ],
        "product_link_pattern": r"sub2-1\.asp\?mode=view&id=\d+",
        "base_url": "http://www.toptics.co.kr/",
        "parser": "toptics",
        "encoding": "euc-kr",
        "status": "ready",
        "notes": (
            "카테고리: sub2-1.asp?category=C1548933732 (Non-Telecentric). "
            "제품 링크: sub2-1.asp?mode=view&id=<n>. "
            "EUC-KR 인코딩. toptics 파서 사용."
        ),
    },

    # ------------------------------------------------------------------
    # Vico (Vico Imaging)
    # ------------------------------------------------------------------
    # *** 핵심 발견: Vico 카테고리 페이지가 모든 제품 스펙을 하나의 넓은 HTML 테이블로
    #     한꺼번에 보여줌. 개별 제품 페이지 크롤 불필요.
    #     -> product_link_pattern=None (listing_url 자체를 파싱)
    #     -> parser="vico_category" (전용 파서, parsers.py에 추가됨)
    #
    #     카테고리 목록 (메뉴에서 확인):
    #       - matrix-bi-telecentric-lenses   : area scan 텔레센트릭 (DTCM/DTCMA 등)
    #       - ultra-resolution-bi-telecentric-lenses : 라인스캔/고해상도 텔레센트릭 (DTCA/DTCL 등)
    #       - c-mount-high-resolution-telecentric-lenses : C-Mount 텔레센트릭 (DTCM125 등)
    #       - c-mount-fixed-focal-length-lenses : C-Mount 고정초점 FA 렌즈 (MFA 등)
    #
    #     테이블 헤더 구조:
    #       "Details | wdt_ID | Image | Model NO. | ... | Model_NO. | FOV_ | Mag.β_ | ..."
    #       "_" 포함 컬럼이 상세 스펙 (MTF30_, DoF_, Distortion_, Telecentricity_, ...)
    "vico_telecentric": {
        "brand": "Vico",
        "lens_type": "telecentric",
        "raw_category": "Matrix Bi-Telecentric Lenses (DTCM/area scan)",
        "listing_urls": [
            "https://vicoimaging.com/product-category/matrix-bi-telecentric-lenses/",
        ],
        "product_link_pattern": None,
        "base_url": "https://vicoimaging.com/",
        "parser": "vico_ajax",
        "status": "ready",
        "notes": "wpDataTables AJAX (serverSide=true). nonce 추출 후 전체 DTCM 시리즈 수집.",
    },
    "vico_linescan_telecentric": {
        "brand": "Vico",
        "lens_type": "linescan_telecentric",
        "raw_category": "Ultra Resolution Bi-Telecentric Lenses (DTCA/라인스캔)",
        "listing_urls": [
            "https://vicoimaging.com/product-category/ultra-resolution-bi-telecentric-lenses/",
        ],
        "product_link_pattern": None,
        "base_url": "https://vicoimaging.com/",
        "parser": "vico_ajax",
        "status": "ready",
        "notes": "wpDataTables AJAX. 전체 DTCA 시리즈 수집.",
    },
    "vico_cmount_telecentric": {
        "brand": "Vico",
        "lens_type": "telecentric",
        "raw_category": "C-Mount High Resolution Telecentric Lenses",
        "listing_urls": [
            "https://vicoimaging.com/product-category/c-mount-high-resolution-telecentric-lenses/",
        ],
        "product_link_pattern": None,
        "base_url": "https://vicoimaging.com/",
        "parser": "vico_ajax",
        "status": "ready",
        "notes": "wpDataTables AJAX. 패턴 B (풀네임 컬럼, WWH 시리즈).",
    },
    "vico_fa_lens": {
        "brand": "Vico",
        "lens_type": "fixed_focal",
        "raw_category": "C-Mount Fixed Focal Length Lenses (FA)",
        "listing_urls": [
            "https://vicoimaging.com/product-category/c-mount-fixed-focal-length-lenses/",
        ],
        "product_link_pattern": None,
        "base_url": "https://vicoimaging.com/",
        "parser": "vico_ajax",
        "status": "ready",
        "notes": "wpDataTables AJAX. MFA 시리즈 전체 수집.",
    },

    # ------------------------------------------------------------------
    # Opto Engineering
    # ------------------------------------------------------------------
    "optoe_telecentric": {
        "brand": "Opto Engineering",
        "lens_type": "telecentric",
        "raw_category": "Telecentric lenses (TC / TC CORE / TCLWD / TCHM ...)",
        "listing_urls": [
            "https://www.opto-e.com/en/products/telecentric-lenses",
            "https://www.opto-e.com/en/products/tc-series",
        ],
        "product_link_pattern": r"/en/products/",
        "base_url": "https://www.opto-e.com/",
        "status": "needs_debug",
        "notes": (
            "*** 주의: 모델별 스펙 비교표가 JS/AJAX로 로딩됨 ('Unable to process your request' 메시지 확인됨). "
            "정적 크롤링으로는 테이블이 비어있을 가능성 높음. "
            "debug_target.py 실행 시 find_api_like_urls / find_json_blobs 결과를 꼭 확인. "
            "필요시 Selenium/Playwright 전환 또는 PDF 카탈로그(Download catalog) 활용 검토."
        ),
    },
    "optoe_fixed_focal": {
        "brand": "Opto Engineering",
        "lens_type": "fixed_focal",  # macro 포함
        "raw_category": "Macro & Fixed focal length lenses",
        "listing_urls": [
            "https://www.opto-e.com/en/products/macro-fixed-focal-length-lenses",
        ],
        "product_link_pattern": r"/en/products/",
        "base_url": "https://www.opto-e.com/",
        "status": "needs_debug",
        "notes": "telecentric과 동일하게 JS 로딩 스펙표 의심.",
    },
    "optoe_view360": {
        "brand": "Opto Engineering",
        "lens_type": "view360",
        "raw_category": "360° view lenses",
        "listing_urls": [
            "https://www.opto-e.com/en/products/360-view-lenses",
        ],
        "product_link_pattern": r"/en/products/",
        "base_url": "https://www.opto-e.com/",
        "status": "needs_debug",
        "notes": "일반 검사용 렌즈와 스펙 구조가 많이 다를 수 있음. 우선순위는 낮게.",
    },

    # ------------------------------------------------------------------
    # Schneider-Kreuznach
    # ------------------------------------------------------------------
    # *** 핵심 발견: https://schneiderkreuznach.com/en/sitemap (footer의 "Sitemap"
    #     링크) 이 정적 HTML로 전체 사이트 트리를 보여줌. 카테고리/패밀리 페이지의
    #     "Loading lens data..." 비교표(JS)와는 무관하게, 이 사이트맵 한 페이지에서
    #     모든 개별 렌즈 제품 URL을 product_link_pattern으로 추출 가능.
    #
    #     개별 제품 URL 형태: /industrial-optics/lenses/<category-slug>/<family>/<variant>
    #     (카테고리 슬러그 다음에 family/variant 2단계 -> 패밀리 허브 페이지
    #      [/<category-slug>/<family>, 1단계]는 패턴에서 자동 제외됨)
    #
    #     개별 제품 페이지 구조 (확인 완료, mock HTML 테스트 통과):
    #       - "Technical specifications: <Model>" 2열 표 (실제 스펙, ~24개 필드)
    #       - 바로 뒤에 "Lens specifications glossary" 2열 표 (전 페이지 공통,
    #         용어 설명. "Aperture range F/#", "ß'P" 등 일부 키가 위 표와 겹침
    #         -> parsers.py의 first-wins 수정으로 실제 스펙값 보존됨)
    #       - "MTF charts" 절의 작은 N열 표 (파장/가중치) -> parsers.py의
    #         MIN_COMPARISON_FIELDS 필터로 가짜 모델 레코드 생성 방지됨
    #
    #     사이트맵에서 집계한 카테고리별 제품 수 (총 178개):
    #       c-mount-lenses(84) + fast-lenses(2) + telecentric-lenses(5)
    #       + swir-lenses(4) + large-format-lenses(51) + liquid-lenses(4)
    #       + line-scan-lenses(28)
    #     (v-mount-lenses는 하위 variant 없이 허브 1개뿐이라 제외)
    "schneider_cmount": {
        "brand": "Schneider-Kreuznach",
        "lens_type": "fixed_focal",
        "raw_category": "C-Mount Lenses (CITRINE/TURQUOISE/AQUAMARINE/OPAL/JADE/TOURMALINE/TOPAZ)",
        "listing_urls": [
            "https://schneiderkreuznach.com/en/sitemap",
        ],
        "product_link_pattern": r"/industrial-optics/lenses/c-mount-lenses/[\w.-]+/[\w.-]+$",
        "base_url": "https://schneiderkreuznach.com/",
        "parser": "tables",
        "status": "needs_debug",
        "notes": (
            "사이트맵 기준 84개 제품. 7개 Schneider 타겟의 파일럿 - 먼저 이 타겟으로 "
            "'python crawl_lens.py --target schneider_cmount --max-products 3' 테스트 후 "
            "결과 CSV를 공유해주세요. 정상 동작하면 동일 메커니즘(사이트맵+패턴)을 쓰는 "
            "나머지 6개 타겟도 status를 ready로 올릴 수 있음."
        ),
    },
    "schneider_fast": {
        "brand": "Schneider-Kreuznach",
        "lens_type": "fixed_focal",
        "raw_category": "Fast Lenses (ONYX, F0.95)",
        "listing_urls": [
            "https://schneiderkreuznach.com/en/sitemap",
        ],
        "product_link_pattern": r"/industrial-optics/lenses/fast-lenses/[\w.-]+/[\w.-]+$",
        "base_url": "https://schneiderkreuznach.com/",
        "parser": "tables",
        "status": "needs_debug",
        "notes": "사이트맵 기준 2개 제품 (ONYX 0.95/25 C, C-FI). schneider_cmount 검증 후 ready로.",
    },
    "schneider_telecentric": {
        "brand": "Schneider-Kreuznach",
        "lens_type": "telecentric",
        "raw_category": "Telecentric Lenses (SYLVINE)",
        "listing_urls": [
            "https://schneiderkreuznach.com/en/sitemap",
        ],
        "product_link_pattern": r"/industrial-optics/lenses/telecentric-lenses/[\w.-]+/[\w.-]+$",
        "base_url": "https://schneiderkreuznach.com/",
        "parser": "tables",
        "status": "needs_debug",
        "notes": "사이트맵 기준 5개 제품 (SYLVINE 0.03/0.2x ~ 0.14/1.0x). schneider_cmount 검증 후 ready로.",
    },
    "schneider_swir": {
        "brand": "Schneider-Kreuznach",
        "lens_type": "fixed_focal",
        "raw_category": "SWIR Lenses (CHAROITE/CUPRITE/CRYOLITE)",
        "listing_urls": [
            "https://schneiderkreuznach.com/en/sitemap",
        ],
        "product_link_pattern": r"/industrial-optics/lenses/swir-lenses/[\w.-]+/[\w.-]+$",
        "base_url": "https://schneiderkreuznach.com/",
        "parser": "tables",
        "status": "needs_debug",
        "notes": "사이트맵 기준 4개 제품. schneider_cmount 검증 후 ready로.",
    },
    "schneider_large_format": {
        "brand": "Schneider-Kreuznach",
        "lens_type": "fixed_focal",
        "raw_category": "Large Format Lenses (PYRITE/AMBER/THULITE/EMERALD/TITANITE)",
        "listing_urls": [
            "https://schneiderkreuznach.com/en/sitemap",
        ],
        "product_link_pattern": r"/industrial-optics/lenses/large-format-lenses/[\w.-]+/[\w.-]+$",
        "base_url": "https://schneiderkreuznach.com/",
        "parser": "tables",
        "status": "needs_debug",
        "notes": (
            "사이트맵 기준 49개 제품 (가장 큰 카테고리). TITANITE 5.0x/0.27 처럼 "
            "확대배율(magnification) 표기 모델이 섞여있어 lens_type=fixed_focal이 "
            "정확하지 않을 수 있음 - 표준화 단계에서 raw_category/모델명 보고 재분류 필요. "
            "schneider_cmount 검증 후 ready로."
        ),
    },
    "schneider_liquid": {
        "brand": "Schneider-Kreuznach",
        "lens_type": "fixed_focal",
        "raw_category": "Liquid Lenses (PYRITE LF, Optotune EL-16-40-TC-5D 기반 액체렌즈)",
        "listing_urls": [
            "https://schneiderkreuznach.com/en/sitemap",
        ],
        "product_link_pattern": r"/industrial-optics/lenses/liquid-lenses/[\w.-]+/[\w.-]+$",
        "base_url": "https://schneiderkreuznach.com/",
        "parser": "tables",
        "status": "needs_debug",
        "notes": (
            "사이트맵 기준 4개 제품. 가변초점(liquid lens)이라 lens_type 분류축에 "
            "딱 맞는 카테고리가 없어 일단 fixed_focal로 태깅 (raw_category로 구분 가능). "
            "schneider_cmount 검증 후 ready로."
        ),
    },
    "schneider_linescan": {
        "brand": "Schneider-Kreuznach",
        "lens_type": "linescan_telecentric",
        "raw_category": "Line Scan Lenses (ZIRCONIA/SAPPHIRE/DIAMOND)",
        "listing_urls": [
            "https://schneiderkreuznach.com/en/sitemap",
        ],
        "product_link_pattern": r"/industrial-optics/lenses/line-scan-lenses/[\w.-]+/[\w.-]+$",
        "base_url": "https://schneiderkreuznach.com/",
        "parser": "tables",
        "status": "needs_debug",
        "notes": "사이트맵 기준 28개 제품 (가장 많은 variant). schneider_cmount 검증 후 ready로.",
    },

    # ------------------------------------------------------------------
    # Vieworks (렌즈 - VEO 시리즈, 로그인 불필요 사이트)
    # ------------------------------------------------------------------
    "vieworks_lens_veo": {
        "brand": "Vieworks",
        "lens_type": "fixed_focal",
        "raw_category": "VEO Series (JM/JK/CS/YK/HJ/MH)",
        "listing_urls": [
            "https://vision.vieworks.com/en/lens/veo_jm",
            "https://vision.vieworks.com/en/lens/veo_jk",
            "https://vision.vieworks.com/en/lens/veo_cs",
            "https://vision.vieworks.com/en/lens/veo_yk",
            "https://vision.vieworks.com/en/lens/veo_hj",
            "https://vision.vieworks.com/en/lens/veo_mh",
        ],
        "product_link_pattern": r"/en/lens/",
        "base_url": "https://vision.vieworks.com/",
        "status": "needs_debug",
        "notes": (
            "vision.vieworks.com 은 메인 페이지 기준 로그인 불필요해 보임. "
            "VEO 시리즈가 각각 어떤 광학 타입인지(고정초점/텔레센트릭)는 시리즈별로 다를 수 있어 "
            "lens_type=fixed_focal 은 가정값이며 debug 결과로 시리즈별 재분류 필요."
        ),
    },
}


# Vieworks 카메라도 같은 사이트에서 로그인 없이 수집 가능한지 확인용 (참고)
VIEWORKS_CAMERA_TARGET = {
    "brand": "Vieworks",
    "listing_urls": [
        "https://vision.vieworks.com/en/camera/area_scan",
        "https://vision.vieworks.com/en/camera/tdi_line_scan",
        "https://vision.vieworks.com/en/camera/line_scan",
    ],
    "product_link_pattern": r"/en/camera/",
    "base_url": "https://vision.vieworks.com/",
    "status": "needs_debug",
    "notes": "이전에 로그인 때문에 못 모았던 Vieworks 카메라 - 이 도메인에서는 로그인 없이 접근 가능한지 확인.",
}
