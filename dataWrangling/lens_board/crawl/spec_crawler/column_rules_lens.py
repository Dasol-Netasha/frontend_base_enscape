# -*- coding: utf-8 -*-
"""
렌즈 스펙 CSV 표준화 스크립트

수집된 브랜드별 렌즈 CSV를 공통 스키마로 변환한다.

실행:
    python column_rules_lens.py
    python column_rules_lens.py --input output --output output/standardized

출력:
    output/standardized/lens_standardized.csv  ← 전체 통합
    output/standardized/lens_<brand>.csv        ← 브랜드별
"""

import csv
import re
import os
import glob
import argparse
from pathlib import Path

# ────────────────────────────────────────────────────────────────────
# 1. 표준 컬럼 정의
# ────────────────────────────────────────────────────────────────────
STANDARD_COLS = [
    "brand",
    "lens_type",          # telecentric / fixed_focal / linescan_telecentric
    "model",
    "raw_category",
    # 핵심 광학 스펙
    "focal_length_mm",    # 고정초점 전용
    "magnification",      # 텔레센트릭 전용
    "working_distance_mm",
    "aperture",           # F/# (단일값 또는 범위)
    "max_sensor_format_mm",
    "image_circle_mm",
    "fov_mm",             # FOV (텔레센트릭, Φmm)
    "numerical_aperture",
    "resolution_um",
    "mtf30_lpmm",
    "dof_mm",
    "distortion_pct",
    "telecentricity_deg",
    # 기구/기타
    "mount",
    "weight_g",
    "coaxial",            # 동축 조명 (Yes/No/O/X → Y/N 정규화)
    "wavelength_range",
    # 메타
    "_source_url",
    "_raw_target",        # target_key 보존
]


# ────────────────────────────────────────────────────────────────────
# 2. 브랜드별 컬럼 매핑
#    { 표준컬럼: [원본컬럼명 후보 리스트] }
#    리스트 순서대로 첫 번째 non-empty 값 사용
# ────────────────────────────────────────────────────────────────────
COLUMN_MAP = {
    "focal_length_mm": [
        "Focal Length (mm)",        # Vico FA
        "Focal Length f'",          # Basler fixed (f' 기호 포함)
        "Focal length [mm]",        # Schneider
        "f'eff [mm]",               # Schneider (유효 초점거리)
    ],
    "magnification": [
        "Magnification β (x)",      # Basler telecentric
        "Magnification β(x)",       # Vico cmount
        "Mag. β  (x)",              # Vico linescan
        "Mag. β (x)",               # Vico telecentric
        "Mag",                      # T-Optics
        # Schneider/Basler fixed는 focal_length_mm이 핵심 — magnification 제외
    ],
    "working_distance_mm": [
        "Working Distance WD (mm)", # Basler telecentric
        "Working Distance(mm)",     # Vico cmount
        "WD (mm)",                  # Vico linescan/telecentric, T-Optics
        "W.D. (mm)",                # T-Optics
        "MOD (mm)",                 # Vico FA (minimum object distance)
        "Optimum Working Distance", # Basler fixed
        "Recommended working distance range [mm]",  # Schneider
        "Rec. working distance range [mm]",         # Schneider
    ],
    "aperture": [
        "Aperture Range",           # Basler telecentric
        "Aperture (F/#)",           # Vico cmount/FA
        "Aperture  (F/#)",          # Vico linescan
        "Aperture range F/#",       # Schneider
        "F/# range",                # Schneider linescan
        "Aperture Range",           # Basler telecentric
        "Effective F/#",            # T-Optics
    ],
    "max_sensor_format_mm": [
        "Maximum Sensor Format(Φmm)",    # Vico cmount (Φmm 단위 숫자)
        "Max. Sensor Format (Φmm)",      # Vico linescan (Φmm 단위 숫자)
        "Max. Sensor Format",            # Vico FA ("1/1.8"" 형식 → norm_sensor_format으로 처리)
        "Maximum sensor size [mm]",      # Schneider (숫자 mm)
        "Max. sensor size [mm]",         # Schneider
        "Sensorsize",                    # T-Optics ("9mm", "11mm" 형식)
    ],
    "image_circle_mm": [
        "Image Circle (⌀ mm)",      # Basler telecentric ("18.2 mm (1.1" format)" 형식)
        "Image Circle",             # Basler fixed ("16 mm (1" format)" 형식)
    ],
    "fov_mm": [
        "FOV (Φmm)",                # Vico linescan
        "FOV  (Φmm)",               # Vico telecentric (공백 포함)
        "FOV_ (Φmm)",               # Vico (내부 파서 출력)
    ],
    "numerical_aperture": [
        "Numerical Aperture N.A. (dep. on f/#)",   # Basler telecentric
        "Numerical Aperture",                       # Vico cmount
        "N.A",                                      # T-Optics
        "Numerical aperture [object | image]",      # Schneider
    ],
    "resolution_um": [
        "Theoretical Object-side Resolution (µm) (dep. on f/#)",  # Basler telecentric
        "Resolution(μm)",           # Vico cmount
        "Resolution (um)",          # T-Optics
        "Resolution (25 % MTF, Full Aperture)",     # Basler fixed
        "Resolution (25 % MTF, Center, Full Aperture)",
    ],
    "mtf30_lpmm": [
        "MTF30 (lp/mm) (dep. on f/#)",  # Basler telecentric
        "MTF30  (lp/mm)",               # Vico linescan
        "MTF30 (lp/mm)",                # Vico telecentric
    ],
    "dof_mm": [
        "Object-side Theoretical Depth of Field (mm) (dep. on f/#)",  # Basler telecentric
        "Depth of Field(mm)",       # Vico cmount
        "DoF  (mm)",                # Vico linescan
        "DoF (mm)",                 # Vico telecentric
        "D.O.F ()",                 # T-Optics
    ],
    "distortion_pct": [
        "Image-side Distortion (% max, typical)",  # Basler telecentric
        "Distortion (% max)",       # Vico cmount
        "Distortion  (% max)",      # Vico linescan
        "TV Distortion",            # Vico FA
        "Optical distortion (%)",   # T-Optics
        "Optical Distortion",       # Basler fixed, Schneider
        "Optical Distortion / TV Distortion",
        "Optical Distortion /TV Distortion",
    ],
    "telecentricity_deg": [
        "Object-side Telecentricity (° max, typical)",  # Basler telecentric
        "Telecentricity(°max)",     # Vico cmount
        "Telecentricity  (°max)",   # Vico linescan
        "Telecentricity (Degree)",  # T-Optics
    ],
    "mount": [
        "Camera Mount",             # Basler telecentric
        "Lens Mount",               # Vico cmount
        "Mount",                    # Vico/T-Optics
        "Mount",                    # T-Optics
        "Flange Back",              # Basler fixed (마운트 정보 포함)
        "Interface",                # Schneider
    ],
    "weight_g": [
        "Weight  (kg)",             # Vico linescan (kg → g 변환 필요)
        "Weight (kg)",              # Vico telecentric
        "Weight",                   # Basler fixed
        "Net weight [g]",           # Schneider
        "Net. weight [standard] [g]",  # Schneider
        "Net. weight [g]",
    ],
    "coaxial": [
        "Coaxial Lighting",         # Basler telecentric (Yes/No)
        "With Coaxial Port",        # Vico cmount/linescan (YES/NO)
        "Coaxial",                  # T-Optics (O/X)
    ],
    "wavelength_range": [
        "Wavelength Range",         # Basler telecentric/fixed
    ],
}


# ────────────────────────────────────────────────────────────────────
# 3. 값 정규화 함수들
# ────────────────────────────────────────────────────────────────────

def _strip(v: str) -> str:
    return v.strip() if v else ""


def norm_coaxial(v: str) -> str:
    """동축 조명 여부 → Y / N / '' 정규화"""
    v = _strip(v).upper()
    if v in ("YES", "Y", "O", "TRUE", "1"):
        return "Y"
    if v in ("NO", "N", "X", "FALSE", "0"):
        return "N"
    return ""


def norm_weight_g(v: str, col_name: str = "") -> str:
    """무게를 그램(g) 단위 숫자로 정규화
    - 'Approx. 220 g' → '220'
    - '0.28' (kg, Vico) → '280'
    - '55 g' → '55'
    """
    v = _strip(v)
    if not v:
        return ""

    # 숫자만 추출 (소수점 포함, 숫자가 없는 경우 제외)
    nums = re.findall(r"\d+\.?\d*|\.\d+", v)
    if not nums:
        return ""
    try:
        val = float(nums[0])
    except ValueError:
        return ""

    # kg → g 변환: 컬럼명에 kg이 있거나 값이 작은 경우
    if "kg" in col_name.lower() or (val < 10 and "g" not in v.lower()):
        val = val * 1000

    return str(int(round(val))) if val == int(val) else str(round(val, 1))


def norm_mount(v: str) -> str:
    """마운트 타입 정규화 → C / F / M42 / M58 / M72 / CS 등"""
    v = _strip(v)
    if not v:
        return ""
    v_upper = v.upper()
    if "C-MOUNT" in v_upper or v_upper == "C":
        return "C"
    if "F-MOUNT" in v_upper or v_upper == "F":
        return "F"
    if "M42" in v_upper:
        return "M42"
    if "M58" in v_upper:
        return "M58"
    if "M72" in v_upper:
        return "M72"
    if "CS" in v_upper:
        return "CS"
    return v  # 원본 보존


def norm_numeric(v: str) -> str:
    """숫자값 정규화: 앞뒤 텍스트 제거, 범위는 그대로 보존
    예: '110 ±2' → '110 ±2', '>190' → '>190', '0.5' → '0.5'
    """
    return _strip(v)


def norm_focal_length(v: str) -> str:
    """초점거리 정규화: '8.25 mm ± 5 %' → '8.25' """
    v = _strip(v)
    if not v:
        return ""
    m = re.match(r"([\d.]+)", v)
    return m.group(1) if m else v


def norm_sensor_format(v: str) -> str:
    """센서 포맷 정규화: mm 단위 숫자 추출
    - '7.2(1/2.5")' → '7.2'
    - '16 mm (1" format)' → '16'
    - '9mm' → '9'
    - '1/1.8"' → '9' (광학 포맷 → mm 변환)
    - '11.0' → '11.0'
    """
    v = _strip(v)
    if not v:
        return ""

    # 광학 포맷 문자열 룩업 (분수 인치 → 실제 이미지 서클 mm)
    FORMAT_TO_MM = {
        "1/2.5": "7.2", "1/2.3": "7.7", "1/2": "8.0", "1/1.8": "9.0",
        "1/1.7": "9.5", "2/3": "11.0", "1": "16.0", "1.1": "17.6",
        "1.2": "19.3", "4/3": "22.5", "35mm": "43.2",
    }
    # 분수 인치 패턴 우선 탐색
    m = re.search(r'(\d+/\d+(?:\.\d+)?)"?', v)
    if m:
        key = m.group(1)
        if key in FORMAT_TO_MM:
            return FORMAT_TO_MM[key]

    # 앞에 나오는 숫자 추출 (예: "7.2(1/2.5")" → "7.2")
    m = re.match(r"([\d.]+)", v)
    if m:
        return m.group(1)

    return v


# ────────────────────────────────────────────────────────────────────
# 4. 행 변환 함수
# ────────────────────────────────────────────────────────────────────

def transform_row(row: dict, target_key: str = "") -> dict:
    """원본 행 → 표준화된 행"""
    out = {col: "" for col in STANDARD_COLS}

    # 메타 컬럼 직접 복사
    out["brand"] = _strip(row.get("brand", ""))
    out["lens_type"] = _strip(row.get("lens_type", ""))
    out["model"] = _strip(row.get("model", ""))
    out["raw_category"] = _strip(row.get("raw_category", ""))
    out["_source_url"] = _strip(row.get("_source_url", ""))
    out["_raw_target"] = _strip(row.get("target_key", target_key))

    # 표준 스펙 컬럼 매핑
    for std_col, candidates in COLUMN_MAP.items():
        for cand in candidates:
            val = row.get(cand, "")
            if val and _strip(val):
                # 컬럼별 정규화
                if std_col == "coaxial":
                    val = norm_coaxial(val)
                elif std_col == "weight_g":
                    val = norm_weight_g(val, cand)
                elif std_col == "mount":
                    val = norm_mount(val)
                elif std_col == "focal_length_mm":
                    val = norm_focal_length(val)
                elif std_col in ("max_sensor_format_mm", "image_circle_mm"):
                    val = norm_sensor_format(val)
                elif std_col == "working_distance_mm":
                    # "34 ... ∞" → "34", "110 ±2" → "110", "0.5 m" → "0.5 m" (그대로)
                    v = _strip(val)
                    # 숫자로 시작하고 범위 표현("...", "~") 포함 → 앞 숫자만 추출
                    range_m = re.match(r"([\d.]+)\s*(?:\.{2,}|~|…)", v)
                    if range_m:
                        val = range_m.group(1)
                    else:
                        val = norm_numeric(v)
                else:
                    val = norm_numeric(val)

                if val:
                    out[std_col] = val
                    break

    # image_circle_mm이 있으면 max_sensor_format_mm 빈칸에 fallback (Basler fixed 등)
    if not out["max_sensor_format_mm"] and out["image_circle_mm"]:
        out["max_sensor_format_mm"] = out["image_circle_mm"]

    return out


# ────────────────────────────────────────────────────────────────────
# 5. 메인 실행
# ────────────────────────────────────────────────────────────────────

def process_files(input_dir: str, output_dir: str):
    Path(output_dir).mkdir(parents=True, exist_ok=True)

    # lens_all.csv 제외, 브랜드별 파일만
    files = sorted(glob.glob(os.path.join(input_dir, "lens_*.csv")))
    files = [f for f in files if "lens_all" not in f and "standardized" not in f]

    all_rows = []
    brand_rows: dict[str, list] = {}

    for fp in files:
        fname = os.path.basename(fp)
        print(f"처리 중: {fname}")

        with open(fp, encoding="utf-8-sig", errors="ignore", newline="") as f:
            reader = csv.DictReader(f)
            rows = list(reader)

        if not rows:
            print(f"  → 0행 (스킵)")
            continue

        # 첫 행에서 target_key 추출
        target_key = rows[0].get("target_key", "")
        brand = rows[0].get("brand", "unknown")

        transformed = [transform_row(r, target_key) for r in rows]
        # 스펙이 전혀 없는 행(vico_telecentric 미수집분 등) 필터
        useful = [r for r in transformed if any(
            r.get(c) for c in STANDARD_COLS
            if c not in ("brand", "lens_type", "model", "raw_category", "_source_url", "_raw_target")
        )]

        print(f"  → {len(rows)}행 → {len(useful)}행 (스펙 있는 행)")
        all_rows.extend(useful)
        brand_rows.setdefault(brand, []).extend(useful)

    # 전체 통합 저장
    out_all = os.path.join(output_dir, "lens_standardized.csv")
    _write_csv(all_rows, out_all)
    print(f"\n✓ 전체: {len(all_rows)}행 → {out_all}")

    # 브랜드별 저장
    for brand, rows in sorted(brand_rows.items()):
        brand_slug = re.sub(r"[^a-zA-Z0-9]", "_", brand).lower().strip("_")
        out_brand = os.path.join(output_dir, f"lens_{brand_slug}.csv")
        _write_csv(rows, out_brand)
        print(f"  {brand}: {len(rows)}행 → {out_brand}")


def _write_csv(rows: list[dict], path: str):
    if not rows:
        return
    with open(path, "w", encoding="utf-8-sig", newline="") as f:
        writer = csv.DictWriter(f, fieldnames=STANDARD_COLS, extrasaction="ignore")
        writer.writeheader()
        writer.writerows(rows)


if __name__ == "__main__":
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument("--input", default="output", help="수집 CSV 디렉토리")
    parser.add_argument("--output", default="output/standardized", help="출력 디렉토리")
    args = parser.parse_args()
    process_files(args.input, args.output)
