"""
JAI 카메라 스펙 크롤러
==============================
설치:
    pip install playwright beautifulsoup4 pandas
    playwright install chromium

실행:
    python jai_crawl.py

결과:
    jai.csv
"""

import asyncio
import pandas as pd
from bs4 import BeautifulSoup
from playwright.async_api import async_playwright

BASE_URL       = "https://www.jai.com"
SELECTION_URL  = "https://www.jai.com/products/camera-selection-guide/"
OUTPUT_PATH    = "jai.csv"


async def goto(page, url, wait=3):
    await page.goto(url, wait_until="domcontentloaded", timeout=30000)
    await asyncio.sleep(wait)


# ─────────────────────────────────────────────
# 1단계: camera-selection-guide 테이블에서 모델 수집
# ─────────────────────────────────────────────
async def get_all_models(page, retries=3) -> list:
    for attempt in range(retries):
        try:
            await goto(page, SELECTION_URL, wait=5)
            soup = BeautifulSoup(await page.content(), "html.parser")

            table = soup.find("table")
            if not table:
                raise ValueError("테이블 없음")

            # 헤더
            headers = [th.get_text(strip=True) for th in table.select("th")]
            # 'Tick to compare', '' 제거 → 실제 스펙 헤더만
            # 첫 2개 컬럼은 체크박스/Quick view
            spec_headers = headers[2:]  # Product Line, Model, Type, ...

            models = []
            seen = set()
            for tr in table.select("tbody tr"):
                cells = tr.find_all("td")
                if len(cells) < 4:
                    continue

                # 모델명은 4번째 셀 (index 3)
                model_name = cells[3].get_text(strip=True)
                if not model_name or model_name in seen:
                    continue
                seen.add(model_name)

                # 기본 스펙 수집
                row = {"brand": "JAI"}
                for i, header in enumerate(spec_headers):
                    idx = i + 2  # 앞 2개 컬럼 건너뜀
                    if idx < len(cells) and header:
                        row[header] = cells[idx].get_text(strip=True)

                # 상세 페이지 URL 구성
                row["detail_url"] = f"{BASE_URL}/products/{model_name.lower()}/"
                models.append(row)

            if models:
                print(f"  {len(models)}개 모델 수집")
                return models

            print(f"  ⚠ 모델 없음 (시도 {attempt+1}/{retries})")
            await asyncio.sleep(3)

        except Exception as e:
            print(f"  ⚠ 오류 (시도 {attempt+1}/{retries}): {e}")
            await asyncio.sleep(3)

    return []


# ─────────────────────────────────────────────
# 2단계: 상세 페이지에서 추가 스펙 수집
# ─────────────────────────────────────────────
async def get_detail_spec(page, url, retries=10) -> dict:
    for attempt in range(retries):
        try:
            await goto(page, url, wait=2)
            soup = BeautifulSoup(await page.content(), "html.parser")

            spec = {}
            # specifications-title + 값 구조
            for row in soup.select(".row.margin-bottom-small"):
                title = row.select_one(".specifications-title")
                value = row.select_one(".large-8 p")
                if title and value:
                    key = title.get_text(strip=True)
                    val = value.get_text(strip=True)
                    if key and val:
                        spec[key] = val

            if spec:
                return spec

            # 404 또는 스펙 없는 페이지
            if "404" in await page.title() or len(soup.get_text()) < 500:
                return {}

            print(f"    ⚠ 스펙 없음 (시도 {attempt+1}/{retries})")
            await asyncio.sleep(2)

        except Exception as e:
            print(f"    ⚠ 오류 (시도 {attempt+1}/{retries}): {e}")
            await asyncio.sleep(2 * (attempt + 1))

    return {}


# ─────────────────────────────────────────────
# 메인
# ─────────────────────────────────────────────
async def main():
    async with async_playwright() as p:
        browser = await p.chromium.launch(
            headless=False,
            args=["--disable-blink-features=AutomationControlled"]
        )
        context = await browser.new_context(
            user_agent="Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/136.0.0.0 Safari/537.36",
            locale="en-US",
        )
        await context.add_init_script("Object.defineProperty(navigator, 'webdriver', {get: () => undefined})")
        page = await context.new_page()

        # 1단계
        print("=== 1단계: 모델 목록 수집 ===")
        models = await get_all_models(page)
        print(f"총 {len(models)}개 모델\n")

        # 2단계
        print("=== 2단계: 상세 스펙 수집 ===")
        rows = []
        for i, model in enumerate(models):
            model_name = model.get("Model", "")
            detail_url = model.pop("detail_url")
            print(f"  [{i+1}/{len(models)}] {model_name}")

            detail = await get_detail_spec(page, detail_url)
            row = dict(model)
            # 상세 스펙 병합 (기존 값 없는 것만 추가)
            for k, v in detail.items():
                if k not in row or not row[k]:
                    row[k] = v

            rows.append(row)
            await asyncio.sleep(0.3)

        await browser.close()

        df = pd.DataFrame(rows)
        df.to_csv(OUTPUT_PATH, index=False, encoding="utf-8-sig")
        print(f"\n=== 완료: {OUTPUT_PATH} ({len(rows)}개 모델) ===")


if __name__ == "__main__":
    asyncio.run(main())