# 렌즈 / 보드(프레임그래버) 스펙 크롤러

카메라 작업(column_rules_v*.py)과 같은 흐름으로, "일단 원본 그대로 모은 뒤 표준화"를 위한
1차 수집용 크롤러입니다.

## 0. 설치

```bash
pip install -r requirements.txt
```

## 1. 진행 순서 (중요)

각 브랜드/카테고리는 `targets_lens.py`, `targets_board.py` 에 `target_key` 단위로 정의되어 있고,
대부분 `status: "needs_debug"` 상태입니다. **바로 크롤링 돌리지 말고 먼저 구조를 확인**하세요.

### Step 1) 구조 디버깅

```bash
python debug_target.py --list                 # 전체 target_key 목록
python debug_target.py schneider_cmount        # 특정 타겟 구조 분석
python debug_target.py --url https://...       # 임의 URL 1개 점검
```

실행하면 `debug_output/<target_key>/` 에 다음이 생성됩니다:
- `page_00_xxx.html` : 원본 HTML 캐시
- `report.txt` : 구조 분석 리포트
  - `<table>` 추출 결과 (몇 개, 어떤 필드)
  - 링크 후보 (상품 상세 페이지로 추정되는 URL들)
  - JS 렌더링 의심 신호 (script 안의 JSON, API 같은 경로)
  - sitemap.xml 존재 여부 및 일부 URL 목록

**`report.txt` 내용을 그대로 Claude에게 붙여넣어 주세요.** 그 내용을 보고:
- `product_link_pattern` (상품 상세 페이지 링크 정규식) 을 정확하게 채우고
- 필요하면 `common/parsers.py` 의 테이블 추출 로직을 그 사이트에 맞게 보정하고
- JS 렌더링 사이트(예: Opto Engineering)는 별도 방식(API 직접 호출 / Selenium 등)을 논의합니다.

### Step 2) 실제 크롤링

구조가 확인된 타겟부터 실행:

```bash
# 테스트: 상품 5개만
python crawl_lens.py --target schneider_cmount --max-products 5

# 본 실행
python crawl_lens.py --target schneider_cmount schneider_fast
python crawl_lens.py            # targets_lens.py 전체

python crawl_board.py --target euresys_frame_grabbers
python crawl_board.py           # targets_board.py 전체
```

## 2. 출력물

- `raw_html/<target_key>/` : 크롤링한 원본 HTML 캐시 (재실행/디버깅용)
- `output/lens_<target_key>.jsonl`, `.csv` : 타겟별 결과
- `output/lens_all.jsonl`, `output/lens_all.csv` : 전체 합본
- `output/board_*.jsonl/csv` : 보드(프레임그래버) 결과

각 레코드(행)에는 다음 메타 컬럼이 공통으로 붙습니다:

| 컬럼 | 설명 |
|---|---|
| `brand` | 브랜드명 (Basler, Vico, Schneider-Kreuznach 등) |
| `lens_type` / `board_type` | 우리가 분류한 종류 (telecentric / fixed_focal / linescan_telecentric / camera_link / coaxpress 등) |
| `raw_category` | 사이트에 표시된 원래 카테고리명 (참고용) |
| `target_key` | targets_lens.py / targets_board.py 의 키 |
| `model` | 비교표에서 추출된 경우 모델명 (key-value형 페이지는 없을 수 있음) |
| `_source_url` | 크롤링한 페이지 URL |
| `_table_index` | 페이지 내 몇 번째 테이블에서 나왔는지 (`merged_kv` = key-value형 테이블 병합) |

나머지 컬럼은 **사이트에 표시된 스펙 항목명을 그대로** 사용합니다 (예: "Focal Length", "Magnification",
"Working Distance (mm)" 등). 표준화(컬럼명 통일, 단위 변환 등)는 이 raw 데이터를 모은 뒤
카메라 작업 때처럼 `column_rules_v*.py` 형태로 별도 진행합니다.

## 3. 파일 구조

```
spec_crawler/
├── common/
│   ├── http_client.py   # requests 세션 (재시도, 헤더, 딜레이)
│   ├── parsers.py        # 테이블/링크/JSON 추출 (범용)
│   ├── debug_tools.py    # 구조 분석 로직
│   └── io_utils.py        # HTML 캐시, JSONL/CSV 저장
├── targets_lens.py        # 렌즈 브랜드별 설정 (lens_type, listing_urls, 패턴)
├── targets_board.py       # 보드 브랜드별 설정 (board_type, listing_urls, 패턴)
├── debug_target.py         # 구조 분석 CLI
├── crawl_lens.py            # 렌즈 크롤러
├── crawl_board.py           # 보드 크롤러
├── raw_html/                # (실행 후 생성) HTML 캐시
└── output/                  # (실행 후 생성) 결과 JSONL/CSV
```

## 4. 현재 알려진 이슈 / 주의사항

- **Opto Engineering**: 모델별 스펙 비교표가 JS/AJAX로 로딩됨 ("Unable to process your request" 확인).
  `debug_target.py optoe_telecentric` 결과의 `api-like 경로 후보` 부분을 꼭 확인해서 공유해주세요.
- **Vico, T-Optics**: 카테고리 URL이 추정값입니다. 메인 페이지 메뉴 구조를 보고 실제 슬러그를 확인해야 합니다.
- **Vieworks**: `vision.vieworks.com` 은 로그인 없이 접근 가능해 보이지만, 실제 카메라/렌즈 상세 페이지의
  스펙 표 구조는 확인 전입니다 (`vieworks_camera`, `vieworks_lens_veo` 타겟으로 디버깅 가능).
- **Basler**: `baslerweb.com` (마케팅 페이지) vs `docs.baslerweb.com` (제품 문서) 중 어느 쪽에
  실제 스펙 표가 있는지 디버깅 후 결정.
