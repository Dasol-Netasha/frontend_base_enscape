"""
Lucid Vision Labs 카메라 스펙 크롤러
==============================
설치:
    pip install playwright beautifulsoup4 pandas
    playwright install chromium

실행:
    python lucid_crawl.py

결과:
    lucid.csv
"""

import asyncio
import pandas as pd
from bs4 import BeautifulSoup
from playwright.async_api import async_playwright

BASE_URL    = "https://thinklucid.com"
LIST_URL    = "https://thinklucid.com/ko/lucid-machine-vision-cameras/"
OUTPUT_PATH = "lucid.csv"


async def goto(page, url, wait=3):
    full_url = BASE_URL + url if url.startswith("/") else url
    await page.goto(full_url, wait_until="domcontentloaded", timeout=30000)
    await asyncio.sleep(wait)


# ─────────────────────────────────────────────
# 1단계: 목록 페이지에서 대표 모델 링크 수집
# ─────────────────────────────────────────────
async def get_model_links(page, retries=3) -> list:
    for attempt in range(retries):
        try:
            await goto(page, LIST_URL, wait=5)
            soup = BeautifulSoup(await page.content(), "html.parser")

            models = []
            seen = set()

            # 모든 테이블 순회
            for table in soup.find_all("table"):
                headers = [th.get_text(strip=True) for th in table.select("th")]
                if not headers or "모델" not in headers[0]:
                    continue

                for tr in table.select("tbody tr"):
                    a = tr.find("a", href=True)
                    if not a or a["href"] in seen:
                        continue
                    seen.add(a["href"])

                    cells = tr.find_all("td")
                    row_data = {}
                    for i, header in enumerate(headers):
                        if i < len(cells) and header:
                            row_data[header] = cells[i].get_text(strip=True)

                    models.append({
                        "url": a["href"],
                        "list_data": row_data,
                    })

            if models:
                print(f"  {len(models)}개 대표 모델 수집")
                return models

            print(f"  ⚠ 모델 없음 (시도 {attempt+1}/{retries})")
            await asyncio.sleep(3)

        except Exception as e:
            print(f"  ⚠ 오류 (시도 {attempt+1}/{retries}): {e}")
            await asyncio.sleep(3)

    return []


# ─────────────────────────────────────────────
# 2단계: 상세 페이지에서 공통 스펙 + 파생 모델 수집
# ─────────────────────────────────────────────
async def get_detail(page, url, retries=10) -> dict:
    for attempt in range(retries):
        try:
            await goto(page, url, wait=2)
            soup = BeautifulSoup(await page.content(), "html.parser")

            # 공통 스펙 (techspecs 섹션 내 table.product-specs)
            common_spec = {}
            techspecs = soup.select_one("#techspecs")
            if techspecs:
                for table in techspecs.find_all("table", class_="product-specs"):
                    # 섹션명 (thead th)
                    section = table.select_one("thead th")
                    section_name = section.get_text(strip=True) if section else ""
                    for row in table.select("tbody tr"):
                        cells = row.find_all("td")
                        if len(cells) >= 2:
                            key = cells[0].get_text(strip=True)
                            value = cells[1].get_text(strip=True)
                            if key and value:
                                common_spec[key] = value

            # 파생 모델 테이블 (sku-table)
            sku_models = []
            sku_table = soup.select_one("table#sku-table")
            if sku_table:
                sku_headers = [td.get_text(strip=True) for td in sku_table.select("tr:first-child td")]
                for tr in sku_table.select("tr")[1:]:
                    cells = tr.find_all("td")
                    if not cells:
                        continue
                    sku_row = {}
                    for i, header in enumerate(sku_headers):
                        if i < len(cells) and header:
                            sku_row[header] = cells[i].get_text(strip=True)
                    if sku_row:
                        sku_models.append(sku_row)

            if common_spec or sku_models:
                return {"common_spec": common_spec, "sku_models": sku_models}

            print(f"    ⚠ 스펙 없음 (시도 {attempt+1}/{retries})")
            await asyncio.sleep(2)

        except Exception as e:
            print(f"    ⚠ 오류 (시도 {attempt+1}/{retries}): {e}")
            await asyncio.sleep(2 * (attempt + 1))

    return {"common_spec": {}, "sku_models": []}


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
            locale="ko-KR",
        )
        await context.add_init_script("Object.defineProperty(navigator, 'webdriver', {get: () => undefined})")
        page = await context.new_page()

        # 1단계
        print("=== 1단계: 대표 모델 링크 수집 ===")
        models = await get_model_links(page)
        print(f"총 {len(models)}개 대표 모델\n")

        # 2단계
        print("=== 2단계: 상세 스펙 + 파생 모델 수집 ===")
        rows = []
        for i, model in enumerate(models):
            rep_name = model["list_data"].get("모델", model["url"].split("/")[-2])
            print(f"  [{i+1}/{len(models)}] {rep_name}")

            detail = await get_detail(page, model["url"])
            common_spec = detail["common_spec"]
            sku_models = detail["sku_models"]

            # 대표 모델 row (목록 스펙 + 공통 스펙)
            base_row = {
                "brand": "Lucid Vision",
                "is_variant": "N",
            }
            base_row.update(model["list_data"])
            base_row.update(common_spec)
            rows.append(base_row)

            # 파생 모델 rows (공통 스펙 + 파생 스펙)
            for sku in sku_models:
                sku_row = {
                    "brand": "Lucid Vision",
                    "is_variant": "Y",
                    "parent_model": rep_name,
                }
                sku_row.update(common_spec)
                sku_row.update(sku)
                rows.append(sku_row)

            print(f"    → 파생 {len(sku_models)}개")
            await asyncio.sleep(0.3)

        await browser.close()

        df = pd.DataFrame(rows)
        df.to_csv(OUTPUT_PATH, index=False, encoding="utf-8-sig")
        print(f"\n=== 완료: {OUTPUT_PATH} ({len(rows)}개 모델) ===")


if __name__ == "__main__":
    asyncio.run(main())