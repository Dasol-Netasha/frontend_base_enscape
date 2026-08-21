# -*- coding: utf-8 -*-
"""
보드(Frame Grabber / Hub) 스펙 CSV 표준화 스크립트

수집된 브랜드별 보드 CSV를 공통 스키마로 변환한다.

실행:
    python column_rules_board.py
    python column_rules_board.py --input output --output output/standardized
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
    "board_type",         # coaxpress / cameralink / gige / hub / usb3
    "model",
    "raw_category",
    # 인터페이스
    "camera_interface",   # CoaXPress / Camera Link / GigE Vision / USB3 Vision
    "interface_standard", # CXP-12 / CXP-31 / Base/Medium/Full / 등
    "num_ports",          # 카메라 연결 포트 수
    "max_cameras",        # 최대 동시 연결 카메라 수
    # 성능
    "pcie_interface",     # PCIe x8 Gen3 / x16 Gen3 등
    "max_bandwidth_gbps", # 최대 카메라→PC 대역폭 (Gbps)
    "delivery_bandwidth_MBps", # 실효 전송 대역폭 (MB/s)
    "onboard_memory",     # 온보드 메모리 (GB / MB)
    # 카메라 지원
    "bit_depth",          # 8-16bit 등
    "sensor_type",        # Grayscale / Color / Both
    "linescan_support",   # Yes / No
    # 기구
    "form_factor",        # PCIe full / half / etc
    "dimensions",
    "weight_g",
    "power_w",
    # 환경
    "operating_temp",
    "os_support",
    # 프로그래밍
    "fpga",               # FPGA 모델 or Yes/No
    "sdk",                # SDK/API 이름
    # 메타
    "_source_url",
    "_raw_target",
]


# ────────────────────────────────────────────────────────────────────
# 2. 브랜드별 컬럼 매핑
# ────────────────────────────────────────────────────────────────────
COLUMN_MAP = {
    "camera_interface": [
        "Camera interface standard",        # Euresys
        "Interface",                        # Basler
        "Interface standard",              # Euresys (일부)
        "Standard",                        # Euresys (일부)
        "Camera interface",
    ],
    "interface_standard": [
        "Interface standard(s)",            # Euresys
        "Supported CXP down-connection speeds",  # Euresys (CXP 속도)
        "Maximum link speed",              # Euresys
        "Camera Link configuration",       # Euresys CL
    ],
    "num_ports": [
        "No. of Ports",                    # Basler
        "Number of cameras",               # Euresys (포트=카메라수)
        "Maximum link width",              # Euresys (CXP connections)
    ],
    "max_cameras": [
        "Maximum number of cameras",       # Euresys
        "No. of Ports",                    # Basler (포트=최대 카메라)
        "Configurations",                  # Basler (텍스트에서 추출)
    ],
    "pcie_interface": [
        "PC Bus Interface",                # Basler
        "Standard",                        # Euresys (PCI Express 4.0)
        "Link width",                      # Euresys
        "Link speed",                      # Euresys
    ],
    "max_bandwidth_gbps": [
        "Data Bandwidth",                  # Basler ("2 x 100 Gbit/s")
        "Maximum aggregated camera data transfer rate",  # Euresys
        "Maximum data rate",               # Euresys (일부)
    ],
    "delivery_bandwidth_MBps": [
        "Effective (sustained) delivery bandwidth",  # Euresys (실효값 우선)
        "PC Bus Interface Performance",    # Basler (theoretical 포함, typical 추출)
        "Peak delivery bandwidth",         # Euresys (피크값 fallback)
    ],
    "onboard_memory": [
        "On-Board Memory",                 # Basler
        "On-board memory",                 # Euresys
        "System memory",                   # Euresys (일부)
    ],
    "bit_depth": [
        "Bit Depth",                       # Basler
        "Camera pixel formats supported",  # Euresys (Mono8~Mono16에서 추출)
    ],
    "sensor_type": [
        "Sensor Type",                     # Basler
        "Camera types",                    # Euresys
    ],
    "linescan_support": [
        "Line-scan cameras supported",     # Euresys
        "Camera Support",                  # Basler (텍스트에서 추론)
        "Sensor Type",                     # Basler 일부
    ],
    "form_factor": [
        "Form factor",                     # Euresys ("PCI Express card")
        "Format",                          # Euresys ("Standard profile, half length...")
        "Mounting",                        # Euresys (일부)
        # Basler는 form_factor 컬럼이 없음 → Dimensions에서 앞부분 추출
    ],
    "dimensions": [
        "Dimensions",                      # Basler / Euresys
    ],
    "weight_g": [
        "Weight",                          # Basler / Euresys
    ],
    "power_w": [
        "Power Consumption / Power Source",  # Basler
        "Power consumption",               # Euresys
        "PCI Express slot power rating",   # Euresys
    ],
    "operating_temp": [
        "Operating Temperature",           # Basler
        "Operating ambient air temperature",  # Euresys
    ],
    "os_support": [
        "Software Drivers",                # Basler
        "Host PC Operating System",        # Euresys
    ],
    "fpga": [
        "Processor",                       # Basler (FPGA 모델)
        "FPGA Programming",                # Basler
        "CustomLogic",                     # Euresys
    ],
    "sdk": [
        "Software API",                    # Basler
        "APIs",                            # Euresys
        "Driver name",                     # Euresys
        "MV Software Compatibility",       # Basler
    ],
}


# ────────────────────────────────────────────────────────────────────
# 3. 값 정규화 함수들
# ────────────────────────────────────────────────────────────────────

def _strip(v: str) -> str:
    return v.strip() if v else ""


def norm_weight_g(v: str) -> str:
    """'394 g' → '394', 'Net weight: 210 g' → '210'"""
    v = _strip(v)
    if not v:
        return ""
    # 'Net weight: 210 g' 등에서 숫자 추출
    m = re.search(r"(\d+(?:\.\d+)?)\s*g", v, re.I)
    if m:
        val = float(m.group(1))
        # kg 단위인 경우
        if re.search(r"\bkg\b", v, re.I):
            val *= 1000
        return str(int(round(val)))
    # 숫자만 있는 경우
    m = re.match(r"([\d.]+)", v)
    return m.group(1) if m else v


def norm_power_w(v: str) -> str:
    """'Typ. 45W@12V, excluding camera...' → '45'
    '30.64 W' → '30.64', '75 W' → '75'"""
    v = _strip(v)
    if not v:
        return ""
    # "Typ. 45W" 또는 "45 W" 패턴
    m = re.search(r"(?:typ\.?\s*)?(\d+(?:\.\d+)?)\s*W", v, re.I)
    return m.group(1) if m else ""


def norm_bandwidth_gbps(v: str) -> str:
    """'2 x 100 Gbit/s' → '200', '100 Gbps' → '100'"""
    v = _strip(v)
    if not v:
        return ""
    # "N x M Gbit/s" 패턴
    m = re.match(r"(\d+)\s*[x×]\s*(\d+(?:\.\d+)?)\s*G", v, re.I)
    if m:
        return str(int(m.group(1)) * float(m.group(2)))
    # 단일값 "M Gbps"
    m = re.search(r"(\d+(?:\.\d+)?)\s*Gb", v, re.I)
    if m:
        return m.group(1)
    return ""


def norm_delivery_mbps(v: str) -> str:
    """Basler: '15,752 MB/s (theoretical), 13,040 MB/s (typical/max.)' → '13040' (typical 우선)
    Euresys: '13,500 MB/s' → '13500'"""
    v = _strip(v)
    if not v:
        return ""
    # typical/max 값 우선 추출 (Basler 형식)
    m = re.search(r"([\d,]+(?:\.\d+)?)\s*MB/s\s*\(typical", v, re.I)
    if m:
        return m.group(1).replace(",", "")
    # 단일 MB/s 값
    m = re.search(r"([\d,]+(?:\.\d+)?)\s*MB/s", v, re.I)
    if m:
        return m.group(1).replace(",", "")
    return ""


def norm_num_ports(v: str) -> str:
    """'2', '4 connections', 'One (1)...' → '1'"""
    v = _strip(v)
    if not v:
        return ""
    # 숫자 패턴
    m = re.match(r"(\d+)", v.replace(",", ""))
    return m.group(1) if m else ""


def norm_linescan(v: str, col_name: str = "") -> str:
    """Yes/No 정규화"""
    v = _strip(v).lower()
    if col_name == "Line-scan cameras supported":
        return "Y" if "yes" in v else ("N" if "no" in v else "")
    # Camera Support 등에서 추론
    if "line" in v or "linescan" in v:
        return "Y"
    return ""


def norm_sensor_type(v: str) -> str:
    """'Grayscale sensor' → 'Grayscale', 'Area-scan cameras: Grayscale and color' → 'Both'"""
    v = _strip(v).lower()
    has_gray = "grayscale" in v or "mono" in v or "gray" in v
    has_color = "color" in v or "rgb" in v or "bayer" in v
    if has_gray and has_color:
        return "Both"
    if has_gray:
        return "Grayscale"
    if has_color:
        return "Color"
    return _strip(v)[:50] if v else ""


def norm_pcie(v: str, extra: dict | None = None) -> str:
    """'PCIe x16 Gen3.0' / 'PCI Express 4.0' + '8 lanes' → 'PCIe x8 Gen4'"""
    v = _strip(v)
    if not v:
        return ""
    # Basler: "PCIe x16 Gen3.0"
    m = re.search(r"PCIe?\s*[xX]?(\d+)\s*Gen\s*(\d+)", v, re.I)
    if m:
        return f"PCIe x{m.group(1)} Gen{m.group(2)}"
    # Euresys: "PCI Express 4.0" + link width 별도
    m = re.search(r"PCI\s*Express\s*(\d+(?:\.\d+)?)", v, re.I)
    if m:
        gen = m.group(1).split(".")[0]
        lanes = ""
        if extra:
            lw = extra.get("Link width", "")
            lm = re.search(r"(\d+)\s*lane", lw, re.I)
            if lm:
                lanes = f" x{lm.group(1)}"
        return f"PCIe{lanes} Gen{gen}"
    return v[:60]


def norm_temp(v: str) -> str:
    """'0 - 50 °C' → '0–50°C', '0°C to +55°C / ...' → '0–55°C'
    '50–0°C' (뒤집힘) → '0–50°C' 로 정렬"""
    v = _strip(v)
    if not v:
        return ""
    nums = re.findall(r"[+-]?\d+(?:\.\d+)?", v)
    if len(nums) >= 2:
        a, b = float(nums[0]), float(nums[1])
        lo, hi = (a, b) if a <= b else (b, a)
        lo_s = str(int(lo)) if lo == int(lo) else str(lo)
        hi_s = str(int(hi)) if hi == int(hi) else str(hi)
        return f"{lo_s}–{hi_s}°C"
    return v[:40]


def norm_os(v: str) -> str:
    """Windows/Linux 추출"""
    v = _strip(v)
    parts = []
    if re.search(r"windows", v, re.I):
        parts.append("Windows")
    if re.search(r"linux", v, re.I):
        parts.append("Linux")
    return " / ".join(parts) if parts else v[:60]


def norm_camera_interface(v: str) -> str:
    """인터페이스 정규화"""
    v = _strip(v)
    v_up = v.upper()
    if "COAXPRESS" in v_up or "CXP" in v_up:
        return "CoaXPress"
    if "CAMERA LINK" in v_up or "CAMERALINK" in v_up:
        return "Camera Link"
    if "GIGE" in v_up or "GIG-E" in v_up or "GIGABIT" in v_up:
        return "GigE Vision"
    if "USB3" in v_up or "USB 3" in v_up:
        return "USB3 Vision"
    if "FIBER" in v_up or "FIBER" in v_up:
        return "CoaXPress-over-Fiber"
    return v[:60]


# ────────────────────────────────────────────────────────────────────
# 4. 행 변환 함수
# ────────────────────────────────────────────────────────────────────

def transform_row(row: dict, target_key: str = "") -> dict:
    out = {col: "" for col in STANDARD_COLS}

    out["brand"] = _strip(row.get("brand", ""))
    out["board_type"] = _strip(row.get("board_type", ""))
    out["model"] = _strip(row.get("model", ""))
    out["raw_category"] = _strip(row.get("raw_category", ""))
    out["_source_url"] = _strip(row.get("_source_url", ""))
    out["_raw_target"] = _strip(row.get("target_key", target_key))

    for std_col, candidates in COLUMN_MAP.items():
        for cand in candidates:
            val = row.get(cand, "")
            if not val or not _strip(val):
                continue

            if std_col == "camera_interface":
                val = norm_camera_interface(val)
            elif std_col == "weight_g":
                val = norm_weight_g(val)
            elif std_col == "power_w":
                val = norm_power_w(val)
            elif std_col == "max_bandwidth_gbps":
                val = norm_bandwidth_gbps(val)
            elif std_col == "delivery_bandwidth_MBps":
                val = norm_delivery_mbps(val)
            elif std_col in ("num_ports", "max_cameras"):
                val = norm_num_ports(val)
            elif std_col == "linescan_support":
                val = norm_linescan(val, cand)
            elif std_col == "sensor_type":
                val = norm_sensor_type(val)
            elif std_col == "pcie_interface":
                val = norm_pcie(val, row)
            elif std_col == "operating_temp":
                val = norm_temp(val)
            elif std_col == "os_support":
                val = norm_os(val)
            else:
                val = _strip(val)[:120]

            if val:
                out[std_col] = val
                break

    # camera_interface 없으면 board_type에서 추론
    if not out["camera_interface"] and out["board_type"]:
        bt = out["board_type"].lower()
        if "coaxpress" in bt or "cxp" in bt:
            out["camera_interface"] = "CoaXPress"
        elif "cameralink" in bt or "camera_link" in bt:
            out["camera_interface"] = "Camera Link"
        elif "gige" in bt:
            out["camera_interface"] = "GigE Vision"
        elif "usb3" in bt:
            out["camera_interface"] = "USB3 Vision"

    # form_factor 없으면 Dimensions 앞부분에서 추출 (Basler: "PCIe Standard height, half length card: ...")
    if not out["form_factor"] and out["dimensions"]:
        dim = out["dimensions"]
        m = re.match(r"(PCIe\s+\w[\w\s,]+?card)", dim, re.I)
        if m:
            out["form_factor"] = m.group(1).strip().rstrip(",")

    # pcie_interface 표기 통일: "PCIe 3.0 x8" → "PCIe x8 Gen3"
    pcie = out["pcie_interface"]
    if pcie:
        m = re.match(r"PCIe?\s*(\d+(?:\.\d+)?)\s*[xX](\d+)", pcie, re.I)
        if m:
            gen = m.group(1).split(".")[0]
            out["pcie_interface"] = f"PCIe x{m.group(2)} Gen{gen}"

    return out


# ────────────────────────────────────────────────────────────────────
# 5. 메인 실행
# ────────────────────────────────────────────────────────────────────

def process_files(input_dir: str, output_dir: str):
    Path(output_dir).mkdir(parents=True, exist_ok=True)

    files = sorted(glob.glob(os.path.join(input_dir, "board_*.csv")))
    files = [f for f in files if "board_all" not in f and "standardized" not in f]

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

        target_key = rows[0].get("target_key", "")
        brand = rows[0].get("brand", "unknown")

        transformed = [transform_row(r, target_key) for r in rows]
        useful = [r for r in transformed if any(
            r.get(c) for c in STANDARD_COLS
            if c not in ("brand", "board_type", "model", "raw_category", "_source_url", "_raw_target")
        )]

        print(f"  → {len(rows)}행 → {len(useful)}행")
        all_rows.extend(useful)
        brand_rows.setdefault(brand, []).extend(useful)

    out_all = os.path.join(output_dir, "board_standardized.csv")
    _write_csv(all_rows, out_all)
    print(f"\n✓ 전체: {len(all_rows)}행 → {out_all}")

    for brand, rows in sorted(brand_rows.items()):
        brand_slug = re.sub(r"[^a-zA-Z0-9]", "_", brand).lower().strip("_")
        out_brand = os.path.join(output_dir, f"board_{brand_slug}.csv")
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
