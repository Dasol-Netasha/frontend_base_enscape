# -*- coding: utf-8 -*-
"""
공통 파서 유틸리티

크롤링한 HTML에서 다음을 추출하는 범용 함수 모음:
1. extract_tables_as_records(html)
2. extract_dl_specs(html)
3. extract_vico_category_table(html)
4. extract_specs(html, parser_name)  -- PARSER_REGISTRY 기반 디스패치
5. extract_links(html, base_url, pattern)
6. find_json_blobs(html) / find_api_like_urls(html)
"""

import re
import json
from urllib.parse import urljoin
from bs4 import BeautifulSoup


def _clean_text(s: str) -> str:
    return re.sub(r"\s+", " ", s or "").strip()


# 비교표(N열)에서 모델별 레코드로 인정하기 위한 최소 스펙 필드 수("model" 키 제외).
# 이보다 적으면 차트/그래프용 작은 표(예: MTF 파장-가중치 표)일 가능성이 높아 스킵.
MIN_COMPARISON_FIELDS = 3


def extract_tables_as_records(html: str, source_url: str = "") -> list[dict]:
    """
    HTML 내 모든 table을 찾아 레코드(dict) 리스트로 변환.

    - 2열 테이블 (key, value) -> 한 레코드로 합쳐짐 (여러 2열 테이블이 있으면 병합)
    - N열 테이블 (1열=스펙명, 헤더행=모델명들) -> 모델별 레코드 N개

    반환되는 각 dict는 원본 컬럼명을 key로 그대로 사용 (표준화는 나중 단계).
    공통 메타 필드: _source_url, _table_index
    """
    soup = BeautifulSoup(html, "lxml")
    tables = soup.find_all("table")

    # 표 앞의 heading(h2/h3/h4) 텍스트가 아래 키워드를 포함하면 해당 표를 스킵.
    SKIP_HEADING_KEYWORDS = (
        "glossary",
        "mtf chart",
        "testing criteria",
        "environmental",
        "accessories",
    )

    def _should_skip_table(table) -> bool:
        for sibling in table.find_all_previous(["h2", "h3", "h4"]):
            heading_text = _clean_text(sibling.get_text(strip=True)).lower()
            if any(kw in heading_text for kw in SKIP_HEADING_KEYWORDS):
                return True
            if "technical specification" in heading_text or "specification" in heading_text:
                break
            break
        return False

    records: list[dict] = []
    kv_merged: dict = {}

    for t_idx, table in enumerate(tables):
        if _should_skip_table(table):
            continue

        rows = table.find_all("tr")
        if not rows:
            continue

        grid = []
        for tr in rows:
            cells = tr.find_all(["th", "td"])
            grid.append([_clean_text(c.get_text(" ", strip=True)) for c in cells])

        grid = [r for r in grid if any(r)]
        if not grid:
            continue

        max_cols = max(len(r) for r in grid)

        if max_cols <= 2:
            # key-value: first-wins (glossary 덮어쓰기 방지)
            for r in grid:
                if len(r) >= 2 and r[0]:
                    if r[0] not in kv_merged:
                        kv_merged[r[0]] = r[1]
                elif len(r) == 1 and r[0]:
                    continue
        else:
            # 비교표: header[0]이 비어있어야 진짜 비교표
            header = grid[0]
            if header[0]:  # 비어있지 않으면 스킵
                continue
            spec_names = []
            model_cols = list(range(1, max_cols))

            data_rows = grid[1:]
            for r in data_rows:
                if not r:
                    continue
                spec_name = r[0]
                if not spec_name:
                    continue
                for col_idx in model_cols:
                    model_name = header[col_idx] if col_idx < len(header) else f"col_{col_idx}"
                    val = r[col_idx] if col_idx < len(r) else ""
                    spec_names.append((model_name, spec_name, val))

            by_model: dict[str, dict] = {}
            for model_name, spec_name, val in spec_names:
                if not model_name:
                    continue
                by_model.setdefault(model_name, {"model": model_name})
                by_model[model_name][spec_name] = val

            for model_name, rec in by_model.items():
                spec_field_count = len(rec) - 1
                if spec_field_count < MIN_COMPARISON_FIELDS:
                    continue
                rec["_source_url"] = source_url
                rec["_table_index"] = t_idx
                records.append(rec)

    if kv_merged:
        kv_merged["_source_url"] = source_url
        kv_merged["_table_index"] = "merged_kv"

        if "model" not in kv_merged:
            title = soup.find("title")
            if title:
                title_text = _clean_text(title.get_text(strip=True))
                for sep in (" | ", " - "):
                    if sep in title_text:
                        kv_merged["model"] = title_text.split(sep)[0].strip()
                        break
                else:
                    if title_text:
                        kv_merged["model"] = title_text

        records.insert(0, kv_merged)

    return records


def extract_dl_specs(html: str, source_url: str = "") -> list[dict]:
    """
    <dl><dt>...</dt><dd>...</dd></dl> 형태 스펙 추출. Euresys 류.
    """
    soup = BeautifulSoup(html, "lxml")
    spec: dict = {}

    for dt in soup.find_all("dt"):
        dd = dt.find_next_sibling("dd")
        if dd is None:
            parent = dt.parent
            dd = parent.find("dd") if parent else None
        if dd is None:
            continue

        key = _clean_text(dt.get_text(" ", strip=True))
        if not key:
            continue

        ps = dd.find_all("p")
        if ps:
            parts = []
            for p in ps:
                text = _clean_text(p.get_text(" ", strip=True))
                if not text:
                    continue
                classes = p.get("class") or []
                if "level2" in classes:
                    text = "  - " + text
                parts.append(text)
            value = " | ".join(parts)
        else:
            value = _clean_text(dd.get_text(" ", strip=True))

        spec[key] = value

    if not spec:
        return []

    spec["_source_url"] = source_url
    spec["_table_index"] = "dl_specs"

    title = soup.find("title")
    if title:
        title_text = title.get_text(strip=True)
        spec["model"] = title_text.split(" - ")[0].strip()

    return [spec]


def extract_vico_category_table(html: str, source_url: str = "") -> list[dict]:
    """
    Vico Imaging 카테고리 페이지 전용 파서.

    Vico 사이트의 카테고리 페이지들은 모든 제품 스펙을 하나의 넓은 HTML 테이블로
    한꺼번에 보여준다. 두 가지 헤더 패턴이 존재:

    [패턴 A] Matrix/Ultra/FA 카테고리: 헤더 첫 셀 = "Details"
      - 상세 스펙 컬럼: "Model_NO.", "FOV_ (Φmm)", "MTF30_" 등 "_"를 포함한 이름
      - model = "Model_NO." 컬럼 값

    [패턴 B] C-Mount High Resolution 카테고리: 헤더 첫 셀 = "wdt_ID" (숫자행 header)
      - 상세 스펙 컬럼: "Lens Model NO.", "Magnification β(x)", "Working Distance(mm)"
        등 완전히 다른 이름 (언더스코어 없음)
      - "Lens Model NO." 또는 "Model NO." 컬럼을 model로 사용
      - 표시용("Model NO.", "Mag.β(x)" 등)과 상세용("Lens Model NO.", "Magnification...")
        컬럼이 중복으로 존재 → 상세용만 추출
    """
    soup = BeautifulSoup(html, "lxml")

    META_SKIP = {"wdt_id", "image", "compare", "product", "specification pdf",
                 "3d igs", "3d step", "details", "series"}

    for table in soup.find_all("table"):
        rows = table.find_all("tr")
        if len(rows) < 2:
            continue

        header_cells = rows[0].find_all(["th", "td"])
        if not header_cells:
            continue
        headers = [_clean_text(c.get_text(" ", strip=True)) for c in header_cells]

        if headers[0] not in ("Details", "wdt_ID", ""):
            continue

        spec_cols = []
        model_col_idx = None

        # --- 패턴 A: "_" 포함 헤더 컬럼 ---
        has_underscore_cols = any("_" in h for h in headers if h.lower() not in META_SKIP)

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

        # --- 패턴 B: C-Mount HR 페이지 ("Lens Model NO.", "Magnification β(x)" 등) ---
        else:
            # "Lens" 또는 "Magnification" 또는 "Working Distance" 등 상세 스펙 컬럼 탐색
            # 표시용 컬럼과 이름이 다른 "두 번째 세트" 컬럼들
            # 기준: 헤더 절반 이후에 등장하거나, "Lens " 접두어가 있거나,
            #        "Magnification", "Working Distance", "Numerical Aperture",
            #        "Resolution", "Depth of Field", "Distortion", "Telecentricity",
            #        "Length", "With Coaxial" 같은 풀네임 컬럼
            DETAIL_KEYWORDS = {
                "magnification", "working distance", "maximum sensor", "aperture",
                "numerical aperture", "resolution", "depth of field", "distortion",
                "telecentricity", "length", "coaxial", "lens mount",
            }
            for idx, h in enumerate(headers):
                h_lower = h.lower()
                if h_lower in META_SKIP:
                    continue
                # "Lens Model NO." → model
                if h_lower.startswith("lens") and "model" in h_lower and "no" in h_lower:
                    model_col_idx = idx
                    spec_cols.append((idx, "model"))
                    continue
                # 풀네임 상세 스펙 컬럼
                if any(kw in h_lower for kw in DETAIL_KEYWORDS):
                    # 컬럼 이름 정리: 괄호 안 단위 보존
                    col_name = h.strip()
                    spec_cols.append((idx, col_name))

        if not spec_cols or model_col_idx is None:
            continue

        # 데이터 행 → 레코드 변환
        records = []
        for row_idx, tr in enumerate(rows[1:], 1):
            cells = tr.find_all(["th", "td"])
            if not cells:
                continue
            cell_texts = [_clean_text(c.get_text(" ", strip=True)) for c in cells]

            model_val = cell_texts[model_col_idx] if model_col_idx < len(cell_texts) else ""
            if not model_val or model_val.isdigit():
                continue

            rec = {"model": model_val, "_source_url": source_url, "_table_index": f"vico_row_{row_idx}"}
            for col_idx, col_name in spec_cols:
                if col_name == "model":
                    continue
                val = cell_texts[col_idx] if col_idx < len(cell_texts) else ""
                rec[col_name] = val

            records.append(rec)

        if records:
            return records

    return []


def extract_toptics_tables(html: str, source_url: str = "") -> list[dict]:
    """
    T-Optics 제품 페이지 전용 파서.

    구조:
      <div class="detail-view">
        <p class="detail-group">OTC-Sensor Dia 9mm W.D. 65mm</p>
        <table class="detail-table">
          <thead><tr><td>Model</td><td>Coaxial</td>...</tr></thead>
          <tbody><tr><td>OTC0.5X-65/C-9</td>...</tr></tbody>
        </table>
      </div>

    특이사항:
      - 헤더가 <th> 대신 <td>로 구성됨
      - 한 페이지에 여러 WD 그룹 테이블 → 전부 수집
      - detail-group <p> 텍스트를 _group 필드로 보존
    """
    soup = BeautifulSoup(html, "lxml")
    detail_view = soup.find("div", class_="detail-view")
    if not detail_view:
        return []

    records = []
    current_group = ""
    row_idx = 0

    for elem in detail_view.children:
        if not hasattr(elem, "name"):
            continue

        if elem.name == "p" and "detail-group" in elem.get("class", []):
            current_group = _clean_text(elem.get_text(" ", strip=True))
            continue

        if elem.name == "table":
            rows = elem.find_all("tr")
            if not rows:
                continue

            header_cells = rows[0].find_all(["td", "th"])
            headers = [_clean_text(c.get_text(" ", strip=True)) for c in header_cells]
            if not headers:
                continue

            model_idx = 0
            for i, h in enumerate(headers):
                if "model" in h.lower():
                    model_idx = i
                    break

            for tr in rows[1:]:
                cells = tr.find_all("td")
                if not cells:
                    continue
                cell_texts = [_clean_text(c.get_text(" ", strip=True)) for c in cells]

                model_val = cell_texts[model_idx] if model_idx < len(cell_texts) else ""
                if not model_val:
                    continue

                row_idx += 1
                rec = {
                    "model": model_val,
                    "_source_url": source_url,
                    "_table_index": f"toptics_row_{row_idx}",
                    "_group": current_group,
                }
                for col_idx, col_name in enumerate(headers):
                    if col_idx == model_idx:
                        continue
                    val = cell_texts[col_idx] if col_idx < len(cell_texts) else ""
                    rec[col_name] = val

                records.append(rec)

    return records


# parser_name(str) -> 함수. targets_*.py 의 "parser" 필드에서 이 이름을 참조한다.
PARSER_REGISTRY = {
    "tables": extract_tables_as_records,
    "dl_specs": extract_dl_specs,
    "vico_category": extract_vico_category_table,
    "toptics": extract_toptics_tables,
}


def extract_specs(html: str, source_url: str = "", parser_name: str = "tables") -> list[dict]:
    """
    parser_name 으로 지정된 파서를 우선 시도하고, 결과가 비어있으면
    PARSER_REGISTRY 의 다른 파서들도 순서대로 시도 (자동 fallback).
    """
    primary = PARSER_REGISTRY.get(parser_name, extract_tables_as_records)
    records = primary(html, source_url=source_url)
    if records:
        return records

    for name, fn in PARSER_REGISTRY.items():
        if fn is primary:
            continue
        records = fn(html, source_url=source_url)
        if records:
            return records

    return []


def extract_links(html: str, base_url: str, pattern: str | None = None) -> list[str]:
    """
    HTML의 <a href> 또는 sitemap XML의 <loc> 태그에서 URL 추출.
    base_url이 sitemap.xml로 끝나는 경우 <loc> 파싱 모드로 동작.
    pattern (정규식 문자열)이 주어지면 매칭되는 URL만 반환.
    중복 제거, 순서 유지.
    """
    urls = []
    seen = set()
    regex = re.compile(pattern) if pattern else None

    # sitemap XML 모드: <loc> 태그 추출
    if "sitemap" in base_url and ("<loc>" in html or "<urlset" in html or "<sitemapindex" in html):
        for m in re.finditer(r"<loc>(.*?)</loc>", html):
            abs_url = m.group(1).strip()
            if regex and not regex.search(abs_url):
                continue
            if abs_url not in seen:
                seen.add(abs_url)
                urls.append(abs_url)
        return urls

    # 일반 HTML 모드: <a href> 추출
    soup = BeautifulSoup(html, "lxml")
    for a in soup.find_all("a", href=True):
        href = a["href"].strip()
        if not href or href.startswith("#") or href.startswith("javascript:"):
            continue
        abs_url = urljoin(base_url, href)
        if regex and not regex.search(abs_url):
            continue
        if abs_url not in seen:
            seen.add(abs_url)
            urls.append(abs_url)

    return urls


def find_json_blobs(html: str) -> list[dict]:
    """
    <script type="application/json"> 또는 __NEXT_DATA__ / __NUXT__ 같은
    전역 변수에 들어있는 JSON 데이터를 찾아 dict 리스트로 반환.
    """
    soup = BeautifulSoup(html, "lxml")
    blobs = []

    for script in soup.find_all("script", attrs={"type": "application/json"}):
        try:
            blobs.append(json.loads(script.string or ""))
        except (ValueError, TypeError):
            continue

    for script in soup.find_all("script"):
        text = script.string or ""
        m = re.search(r"__NEXT_DATA__\s*=\s*({.*?})\s*;?\s*$", text, re.S)
        if not m:
            m = re.search(r"__NUXT__\s*=\s*({.*?})\s*;?\s*$", text, re.S)
        if m:
            try:
                blobs.append(json.loads(m.group(1)))
            except (ValueError, TypeError):
                continue

    return blobs


def find_api_like_urls(html: str) -> list[str]:
    """
    HTML/JS 안에서 fetch/axios/api/json 관련 URL 후보 추출 (디버깅용).
    """
    candidates = set()
    for m in re.finditer(r"""['"](/[a-zA-Z0-9_\-/.]*(?:api|json|specs?|products?)[a-zA-Z0-9_\-/.]*)['"]""", html):
        candidates.add(m.group(1))
    return sorted(candidates)
