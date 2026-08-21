"""
Sentech (OMRON SENTECH) 카메라 스펙 크롤러
==============================
설치:
    pip install playwright beautifulsoup4 pandas
    playwright install chromium

실행:
    python sentech_crawl.py

결과:
    sentech.csv
"""

import asyncio
import pandas as pd
from bs4 import BeautifulSoup
from playwright.async_api import async_playwright

OUTPUT_PATH = "sentech.csv"

CATEGORIES = [
    "https://sentech.co.jp/en/products_cate/swir-camera",
    "https://sentech.co.jp/en/products_cate/3cmos-camera",
    "https://sentech.co.jp/en/products_cate/gvif-camera",
    "https://sentech.co.jp/en/products_cate/liquidlens-camera",
    "https://sentech.co.jp/en/products_cate/lenscontrol-camera",
    "https://sentech.co.jp/en/products_cate/line-camera",
    "https://sentech.co.jp/en/products_cate/coaxpress-camera",
    "https://sentech.co.jp/en/products_cate/gige-camera",
    "https://sentech.co.jp/en/products_cate/usb3vision-camera",
    "https://sentech.co.jp/en/products_cate/optclink-camera",
    "https://sentech.co.jp/en/products_cate/cameralink-camera",
    "https://sentech.co.jp/en/products_cate/hd-camera",
    "https://sentech.co.jp/en/products_cate/uvc-camera",
    "https://sentech.co.jp/en/products_cate/mipi-camera",
    "https://sentech.co.jp/en/products_cate/analog-camera",
    "https://sentech.co.jp/en/products_cate/usb-camera",
]


async def goto(page, url, wait=3):
    await page.goto(url, wait_until="domcontentloaded", timeout=30000)
    await asyncio.sleep(wait)


# ─────────────────────────────────────────────
# 1단계: 카테고리 → 서브카테고리 링크 수집
# ─────────────────────────────────────────────
async def get_subcategory_links(page, cat_url, retries=3) -> list:
    for attempt in range(retries):
        try:
            await goto(page, cat_url)
            soup = BeautifulSoup(await page.content(), "html.parser")

            links = []
            seen = set()
            for item in soup.select(".category-child-item"):
                a = item.select_one(".category-child-item-link a")
                if not a:
                    continue
                href = a["href"]
                name = item.select_one(".category-child-item-name")
                name = name.get_text(strip=True) if name else href
                if href not in seen:
                    seen.add(href)
                    links.append({"url": href, "name": name})

            if links:
                return links

            print(f"    ⚠ 서브카테고리 없음 (시도 {attempt+1}/{retries})")
            await asyncio.sleep(3)
        except Exception as e:
            print(f"    ⚠ 오류 (시도 {attempt+1}/{retries}): {e}")
            await asyncio.sleep(3)
    return []


# ─────────────────────────────────────────────
# 2단계: 서브카테고리 → 모델 링크 수집
# ─────────────────────────────────────────────
async def get_model_links(page, subcat_url, retries=3) -> list:
    for attempt in range(retries):
        try:
            await goto(page, subcat_url)
            soup = BeautifulSoup(await page.content(), "html.parser")

            links = []
            seen = set()
            table = soup.select_one(".l-products__list table")
            if table:
                for a in table.select("tbody a[href*='/products/']"):
                    href = a["href"]
                    if href not in seen:
                        seen.add(href)
                        links.append(href)

            if links:
                return links

            print(f"    ⚠ 모델 링크 없음 (시도 {attempt+1}/{retries})")
            await asyncio.sleep(3)
        except Exception as e:
            print(f"    ⚠ 오류 (시도 {attempt+1}/{retries}): {e}")
            await asyncio.sleep(3)
    return []


# ─────────────────────────────────────────────
# 3단계: 모델 상세 페이지에서 스펙 수집
# ─────────────────────────────────────────────
async def get_spec(page, url, retries=10) -> dict:
    for attempt in range(retries):
        try:
            await goto(page, url, wait=2)
            soup = BeautifulSoup(await page.content(), "html.parser")

            spec = {}
            spec_section = soup.select_one(".c-spec-sheet-tables, .spec-sheet")
            if spec_section:
                for table in spec_section.find_all("table"):
                    for row in table.select("tr"):
                        th = row.find("th")
                        td = row.find("td")
                        if th and td:
                            key = th.get_text(" ", strip=True)
                            value = td.get_text(" ", strip=True)
                            if key and value:
                                spec[key] = value

            if spec:
                return spec

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

        # 1단계: 서브카테고리 링크 수집
        print("=== 1단계: 서브카테고리 링크 수집 ===")
        all_subcats = []
        seen_subcats = set()
        for cat_url in CATEGORIES:
            cat_name = cat_url.rstrip("/").split("/")[-1]
            print(f"\n  {cat_name}")
            subcats = await get_subcategory_links(page, cat_url)
            new = [s for s in subcats if s["url"] not in seen_subcats]
            for s in new:
                seen_subcats.add(s["url"])
            all_subcats.extend(new)
            print(f"  {len(subcats)}개 서브카테고리 (신규 {len(new)}개, 누적 {len(all_subcats)}개)")
            await asyncio.sleep(1)

        print(f"\n총 {len(all_subcats)}개 서브카테고리\n")

        # 2단계: 모델 링크 수집
        print("=== 2단계: 모델 링크 수집 ===")
        all_models = []
        seen_models = set()
        for i, subcat in enumerate(all_subcats):
            print(f"  [{i+1}/{len(all_subcats)}] {subcat['name'][:50]}")
            models = await get_model_links(page, subcat["url"])
            new = [m for m in models if m not in seen_models]
            for m in new:
                seen_models.add(m)
                all_models.append({"url": m, "subcat": subcat["name"]})
            print(f"    {len(models)}개 모델 (신규 {len(new)}개, 누적 {len(all_models)}개)")
            await asyncio.sleep(0.5)

        print(f"\n총 {len(all_models)}개 모델\n")

        # 3단계: 스펙 수집
        print("=== 3단계: 스펙 수집 ===")
        rows = []
        for i, model in enumerate(all_models):
            model_name = model["url"].rstrip("/").split("/")[-1]
            print(f"  [{i+1}/{len(all_models)}] {model_name}")
            spec = await get_spec(page, model["url"])
            row = {
                "brand": "Sentech",
                "model_name": model_name,
                "subcategory": model["subcat"],
            }
            row.update(spec)
            rows.append(row)
            await asyncio.sleep(0.3)

        await browser.close()

        df = pd.DataFrame(rows)
        df.to_csv(OUTPUT_PATH, index=False, encoding="utf-8-sig")
        print(f"\n=== 완료: {OUTPUT_PATH} ({len(rows)}개 모델) ===")


if __name__ == "__main__":
    asyncio.run(main())