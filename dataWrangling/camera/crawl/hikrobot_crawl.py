"""
Hikrobot 공식 사이트 크롤러 (API 전용)
==============================
설치:
    pip install requests pandas

실행:
    python hikrobot_official_crawl.py

결과:
    hikrobot_official.csv (스크립트 실행 경로)
"""

import time
import requests
import pandas as pd

LIST_API = "https://www.hikrobotics.com/en/Api/Foreground/Vision/VisionProductContent?firstModuleId={first}&secondaryModuleId={second}&page={page}&size=50&screening=&showEol=false"
SPEC_API = "https://www.hikrobotics.com/en/Api/Foreground/Vision/VisionProductConfig?id={id}"
OUTPUT_PATH = "hikrobot_official.csv"

HEADERS = {
    "User-Agent": "Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/136.0.0.0 Safari/537.36",
    "Referer": "https://www.hikrobotics.com/en/machinevision/visionproduct",
    "Accept": "application/json, text/plain, */*",
}

# 수집할 카테고리 (first_module_id, secondary_module_id, camera_type)
CATEGORIES = [
    (78,  145, "Area Scan Camera"),
    (146, 155, "Line Scan Camera"),
    (99,  209, "3D Binocular Structured Light"),
    (99,  104, "3D Line Laser Camera"),
    (99,  175, "3D RGB-D Smart Camera"),
]


# ─────────────────────────────────────────────
# 1단계: 목록 API로 전체 ID 수집
# ─────────────────────────────────────────────
def get_product_ids(first_id, second_id, camera_type, retries=3) -> list:
    all_items = []
    seen = set()
    page = 1

    while True:
        url = LIST_API.format(first=first_id, second=second_id, page=page)
        print(f"    {page}페이지 수집 중...")

        for attempt in range(retries):
            try:
                resp = requests.get(url, headers=HEADERS, timeout=15)
                resp.raise_for_status()
                data = resp.json()

                if data.get("status") != "success":
                    raise ValueError(f"API 오류: {data.get('message')}")

                content = data["data"]["VisionProductContent"]
                records = content.get("records", [])
                total_pages = content.get("pages", 1)

                if not records:
                    return all_items

                new_items = []
                for r in records:
                    pid = str(r["id"])
                    if pid not in seen:
                        seen.add(pid)
                        new_items.append({
                            "id": pid,
                            "model_name": r.get("productName", ""),
                            "product_model": r.get("productModel", ""),
                            "camera_series": r.get("secondModuleName", ""),
                            "camera_type": camera_type,
                        })

                all_items.extend(new_items)
                print(f"    {page}페이지: {len(new_items)}개 신규 (누적 {len(all_items)}개 / 전체 {content.get('total')}개)")

                if page >= total_pages:
                    print(f"    마지막 페이지 완료")
                    return all_items

                page += 1
                time.sleep(0.5)
                break

            except Exception as e:
                print(f"    ⚠ 오류 (시도 {attempt+1}/{retries}): {e}")
                time.sleep(2 * (attempt + 1))

        else:
            print(f"    ✗ {page}페이지 수집 실패 → 스킵")
            page += 1

    return all_items


# ─────────────────────────────────────────────
# 2단계: 스펙 API로 상세 스펙 수집
# ─────────────────────────────────────────────
def get_spec(product_id: str, retries=10) -> dict:
    url = SPEC_API.format(id=product_id)

    for attempt in range(retries):
        try:
            resp = requests.get(url, headers=HEADERS, timeout=15)
            resp.raise_for_status()
            data = resp.json()

            if data.get("status") != "success":
                raise ValueError(f"API 오류: {data.get('message')}")

            spec = {}
            for item in data.get("data", []):
                key = item.get("name", "").strip()
                value = item.get("value", "").strip()
                if key:
                    spec[key] = value

            if spec:
                return spec

            print(f"    ⚠ 스펙 비어있음 (시도 {attempt+1}/{retries})")
            time.sleep(2)

        except Exception as e:
            print(f"    ⚠ 오류 (시도 {attempt+1}/{retries}): {e}")
            time.sleep(2 * (attempt + 1))

    print(f"    ✗ {product_id} 수집 실패")
    return {}


# ─────────────────────────────────────────────
# 메인
# ─────────────────────────────────────────────
def main():
    # 1단계
    print("=== 1단계: 제품 ID 수집 ===")
    all_items = []
    for first_id, second_id, camera_type in CATEGORIES:
        print(f"\n  카테고리: {camera_type}")
        items = get_product_ids(first_id, second_id, camera_type)
        all_items.extend(items)
        print(f"  카테고리 완료: {len(items)}개")
        time.sleep(1)

    print(f"\n총 {len(all_items)}개 제품 ID 수집\n")

    # 2단계
    print("=== 2단계: 스펙 수집 ===")
    rows = []
    for i, item in enumerate(all_items):
        print(f"  [{i+1}/{len(all_items)}] {item['model_name'][:50]} (id={item['id']})")
        spec = get_spec(item["id"])
        row = {
            "brand": "Hikrobot",
            "product_id": item["id"],
            "model_name": item["model_name"],
            "product_model": item["product_model"],
            "camera_type": item["camera_type"],
        }
        row.update(spec)
        rows.append(row)
        time.sleep(0.3)

    # CSV 저장
    df = pd.DataFrame(rows)
    df.to_csv(OUTPUT_PATH, index=False, encoding="utf-8-sig")
    print(f"\n=== 완료: {OUTPUT_PATH} ({len(rows)}개 모델) ===")


if __name__ == "__main__":
    main()