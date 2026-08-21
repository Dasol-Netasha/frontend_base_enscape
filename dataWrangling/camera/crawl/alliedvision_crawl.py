"""
Allied Vision 카메라 스펙 크롤러
==============================
설치:
    pip install playwright beautifulsoup4 pandas
    playwright install chromium

실행:
    python alliedvision_crawl.py

결과:
    alliedvision.csv
"""

import asyncio
import pandas as pd
from bs4 import BeautifulSoup
from playwright.async_api import async_playwright

BASE_URL    = "https://www.alliedvision.com"
OUTPUT_PATH = "alliedvision.csv"

# 수집할 최상위 카테고리
TOP_CATEGORIES = [
    "/ko/products/area-scan-cameras",
    "/ko/products/line-scan-cameras",
    "/ko/products/smart-cameras",
]


async def goto(page, url, wait=3):
    full_url = BASE_URL + url if url.startswith("/") else url
    await page.goto(full_url, wait_until="domcontentloaded", timeout=30000)
    await asyncio.sleep(wait)
    return full_url


def get_links_containing(soup, keyword, base=""):
    seen = set()
    results = []
    for a in soup.find_all("a", href=True):
        href = a["href"]
        if keyword in href and href not in seen:
            seen.add(href)
            full = BASE_URL + href if href.startswith("/") else href
            results.append(full)
    return results


# ─────────────────────────────────────────────
# 1단계: 카테고리 → 시리즈 링크
# ─────────────────────────────────────────────
async def get_series_links(page, cat_path, retries=3) -> list:
    for attempt in range(retries):
        try:
            await goto(page, cat_path)
            soup = BeautifulSoup(await page.content(), "html.parser")

            # 카테고리 페이지에서 하위 시리즈 링크 수집
            # cat_path보다 한 단계 더 깊은 링크만
            depth = cat_path.rstrip("/").count("/")
            links = []
            seen = set()
            for a in soup.find_all("a", href=True):
                href = a["href"]
                if (cat_path in href and
                    href.rstrip("/").count("/") == depth + 1 and
                    href not in seen):
                    seen.add(href)
                    links.append(href)

            if links:
                return links

            print(f"    ⚠ 시리즈 없음 (시도 {attempt+1}/{retries})")
            await asyncio.sleep(3)
        except Exception as e:
            print(f"    ⚠ 오류 (시도 {attempt+1}/{retries}): {e}")
            await asyncio.sleep(3)
    return []


# ─────────────────────────────────────────────
# 2단계: 시리즈 → 서브시리즈 링크
# ─────────────────────────────────────────────
async def get_subseries_links(page, series_path, retries=3) -> list:
    for attempt in range(retries):
        try:
            await goto(page, series_path)
            soup = BeautifulSoup(await page.content(), "html.parser")

            depth = series_path.rstrip("/").count("/")
            links = []
            seen = set()
            for a in soup.find_all("a", href=True):
                href = a["href"]
                if (series_path in href and
                    href.rstrip("/").count("/") == depth + 1 and
                    "/view/" not in href and
                    href not in seen):
                    seen.add(href)
                    links.append(href)

            if links:
                return links

            # 서브시리즈 없으면 이 페이지 자체가 모델 테이블
            return [series_path]

        except Exception as e:
            print(f"    ⚠ 오류 (시도 {attempt+1}/{retries}): {e}")
            await asyncio.sleep(3)
    return []


# ─────────────────────────────────────────────
# 3단계: 서브시리즈 → 모델 링크 (/view/숫자)
# ─────────────────────────────────────────────
async def get_model_links(page, subseries_path, retries=3) -> list:
    for attempt in range(retries):
        try:
            await goto(page, subseries_path)
            soup = BeautifulSoup(await page.content(), "html.parser")

            links = []
            seen = set()
            for a in soup.find_all("a", href=True):
                href = a["href"]
                if "/view/" in href and href not in seen:
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
# 4단계: 모델 상세 페이지 스펙 수집
# ─────────────────────────────────────────────
async def get_spec(page, model_path, retries=10) -> dict:
    for attempt in range(retries):
        try:
            await goto(page, model_path, wait=2)
            soup = BeautifulSoup(await page.content(), "html.parser")

            spec = {}
            for group in soup.select("details.spec-group"):
                for row in group.select("tr"):
                    title = row.select_one(".table_title")
                    value = row.select_one(".table_value")
                    if title and value:
                        key = title.get_text(strip=True).rstrip(":")
                        val = value.get_text(strip=True)
                        if key and val:
                            spec[key] = val

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
            locale="ko-KR",
        )
        await context.add_init_script("Object.defineProperty(navigator, 'webdriver', {get: () => undefined})")
        page = await context.new_page()

        # 1단계
        print("=== 1단계: 시리즈 링크 수집 ===")
        all_series = []
        seen_series = set()
        for cat in TOP_CATEGORIES:
            print(f"\n  {cat}")
            series = await get_series_links(page, cat)
            new = [s for s in series if s not in seen_series]
            for s in new:
                seen_series.add(s)
            all_series.extend(new)
            print(f"  {len(series)}개 시리즈 (신규 {len(new)}개)")
            await asyncio.sleep(1)

        print(f"\n총 {len(all_series)}개 시리즈\n")

        # 2단계
        print("=== 2단계: 서브시리즈 링크 수집 ===")
        all_subseries = []
        seen_subseries = set()
        for s in all_series:
            print(f"  {s.split('/')[-1]}")
            subseries = await get_subseries_links(page, s)
            new = [ss for ss in subseries if ss not in seen_subseries]
            for ss in new:
                seen_subseries.add(ss)
            all_subseries.extend(new)
            print(f"    {len(new)}개 서브시리즈")
            await asyncio.sleep(0.5)

        print(f"\n총 {len(all_subseries)}개 서브시리즈\n")

        # 3단계
        print("=== 3단계: 모델 링크 수집 ===")
        all_models = []
        seen_models = set()
        for ss in all_subseries:
            name = ss.rstrip("/").split("/")[-1]
            print(f"  {name}")
            models = await get_model_links(page, ss)
            new = [m for m in models if m not in seen_models]
            for m in new:
                seen_models.add(m)
                all_models.append({"path": m, "subseries": name})
            print(f"    {len(new)}개 모델")
            await asyncio.sleep(0.5)

        print(f"\n총 {len(all_models)}개 모델\n")

        # 4단계
        print("=== 4단계: 스펙 수집 ===")
        rows = []
        for i, model in enumerate(all_models):
            model_id = model["path"].rstrip("/").split("/")[-1]
            print(f"  [{i+1}/{len(all_models)}] {model['subseries']} / id={model_id}")
            spec = await get_spec(page, model["path"])
            row = {
                "brand": "Allied Vision",
                "subseries": model["subseries"],
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