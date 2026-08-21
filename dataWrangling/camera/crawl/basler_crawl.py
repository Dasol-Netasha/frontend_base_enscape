"""
Basler 카메라 스펙 크롤러
==============================
설치:
    pip install playwright beautifulsoup4 pandas
    playwright install chromium

실행:
    python basler_crawl.py

결과:
    basler.csv (스크립트 실행 경로)
"""

import asyncio
import re
import math
import pandas as pd
from bs4 import BeautifulSoup
from playwright.async_api import async_playwright

LIST_URL    = "https://www.baslerweb.com/ko-kr/cameras/?page={page}"
SHOP_URL    = "https://www.baslerweb.com/ko-kr/shop/{slug}/"
OUTPUT_PATH = "basler.csv"
ITEMS_PER_PAGE = 12


# ─────────────────────────────────────────────
# 공통: 제품 카드 로딩 대기
# ─────────────────────────────────────────────
async def wait_for_products(page):
    try:
        await page.wait_for_selector(
            "article.product-card:not(.product-card--is-loading)",
            timeout=30000
        )
    except Exception:
        pass
    await asyncio.sleep(3)


# ─────────────────────────────────────────────
# 현재 페이지에서 slug 읽기
# ─────────────────────────────────────────────
async def read_slugs_from_page(page) -> list:
    soup = BeautifulSoup(await page.content(), "html.parser")
    results = []
    for li in soup.select("li.products-list-grid__item"):
        a = li.find("a", href=lambda h: h and "/shop/" in h)
        if not a:
            continue
        href = a["href"]
        match = re.search(r"/shop/([^/]+)/", href)
        slug = match.group(1) if match else None
        raw = a.get_text(strip=True)
        model_name = raw.replace("Basler", "", 1).strip() if raw.startswith("Basler") else raw
        if slug and model_name:
            results.append({"model_name": model_name, "slug": slug})
    return results


# ─────────────────────────────────────────────
# 총 페이지 수 계산
# ─────────────────────────────────────────────
async def get_total_pages(page) -> int:
    # url = LIST_URL.format(page=1)
    # await page.goto(url, wait_until="domcontentloaded", timeout=60000)
    # await wait_for_products(page)

    # soup = BeautifulSoup(await page.content(), "html.parser")
    # meta = soup.select_one(".product-list-layout__meta-bar-info")
    # if meta:
    #     numbers = re.findall(r"\d+", meta.get_text(strip=True))
    #     if len(numbers) >= 2:
    #         total_items = int(numbers[-1])
    #         total_pages = math.ceil(total_items / ITEMS_PER_PAGE)
    #         print(f"  전체 제품 수: {total_items}개 → {total_pages}페이지")
    #         return total_pages

    print("  ⚠ 전체 페이지 수 파악 실패 → 55페이지로 설정")
    return 55


# ─────────────────────────────────────────────
# 1단계: 전체 목록 수집
# ─────────────────────────────────────────────
async def get_all_slugs(page, total_pages: int) -> list:
    all_slugs = []
    seen_slugs = set()
    prev_first_slug = None

    for page_num in range(1, total_pages + 1):
        print(f"  목록 {page_num}/{total_pages}페이지 수집 중...")

        url = LIST_URL.format(page=page_num)
        await page.goto(url, wait_until="domcontentloaded", timeout=60000)
        await wait_for_products(page)

        # 페이지가 실제로 바뀔 때까지 무한 대기
        if prev_first_slug:
            attempt = 1
            while True:
                slugs = await read_slugs_from_page(page)
                if slugs and slugs[0]["slug"] != prev_first_slug:
                    break
                print(f"    ⚠ 아직 이전 페이지 ({attempt}회), 3초 후 재시도...")
                await asyncio.sleep(3)
                attempt += 1
        else:
            slugs = await read_slugs_from_page(page)

        if not slugs:
            print(f"  {page_num}페이지 데이터 없음 → 스킵")
            continue

        # 신규 slug가 0개면 아직 이전 데이터 → 바뀔 때까지 재시도
        attempt = 1
        while True:
            new_slugs = [s for s in slugs if s["slug"] not in seen_slugs]
            if new_slugs:
                break
            print(f"    ⚠ 신규 0개 ({attempt}회), 3초 후 재시도...")
            await asyncio.sleep(3)
            slugs = await read_slugs_from_page(page)
            attempt += 1

        prev_first_slug = slugs[0]["slug"]

        for s in new_slugs:
            seen_slugs.add(s["slug"])
        all_slugs.extend(new_slugs)
        print(f"  {page_num}페이지: {len(new_slugs)}개 신규 (누적 {len(all_slugs)}개)")

    return all_slugs


# ─────────────────────────────────────────────
# 2단계: 상세 페이지에서 스펙 수집
# ─────────────────────────────────────────────
async def get_spec(page, slug: str, retries: int = 5) -> dict:
    url = SHOP_URL.format(slug=slug)

    for attempt in range(retries):
        try:
            await page.goto(url, wait_until="domcontentloaded", timeout=60000)
            await page.wait_for_selector(".product-specs", timeout=30000)
            await asyncio.sleep(3)

            soup = BeautifulSoup(await page.content(), "html.parser")
            spec = {}

            for row in soup.select(".product-specs__spec-table tr"):
                th = row.find("th")
                td = row.find("td")
                if not th or not td:
                    continue
                key = th.get_text(strip=True)
                lis = td.select("li")
                value = " / ".join(li.get_text(strip=True) for li in lis) if lis else td.get_text(strip=True)
                if key:
                    spec[key] = value

            checklist = soup.select(".product-specs__checklist-list-item")
            if checklist:
                spec["Conformity"] = ", ".join(li.get_text(strip=True) for li in checklist)

            if not spec:
                wait = 3 * (attempt + 1)
                print(f"    ⚠ 스펙 비어있음 (시도 {attempt+1}/{retries}), {wait}초 후 재시도...")
                await asyncio.sleep(wait)
                continue

            return spec

        except Exception as e:
            wait = 3 * (attempt + 1)
            print(f"    ⚠ 오류 (시도 {attempt+1}/{retries}): {e}")
            await asyncio.sleep(wait)

    print(f"    ✗ {slug} 수집 실패")
    return {}


# ─────────────────────────────────────────────
# 메인
# ─────────────────────────────────────────────
async def main():
    async with async_playwright() as p:
        browser = await p.chromium.launch(headless=False)
        context = await browser.new_context(
            user_agent="Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/124.0.0.0 Safari/537.36",
            locale="ko-KR",
            timezone_id="Asia/Seoul",
        )
        page = await context.new_page()

        print("=== 총 페이지 수 확인 ===")
        total_pages = await get_total_pages(page)

        print("\n=== 1단계: 모델 목록 수집 ===")
        slugs = await get_all_slugs(page, total_pages)
        print(f"총 {len(slugs)}개 모델\n")

        if not slugs:
            print("모델 없음 → 종료")
            await browser.close()
            return

        print("=== 2단계: 모델별 스펙 수집 ===")
        rows = []
        for i, item in enumerate(slugs):
            print(f"  [{i+1}/{len(slugs)}] {item['model_name']}")
            spec = await get_spec(page, item["slug"])
            row = {
                "brand": "Basler",
                "model_name": item["model_name"],
                "slug": item["slug"],
            }
            row.update(spec)
            rows.append(row)
            await asyncio.sleep(1)

        await browser.close()

        df = pd.DataFrame(rows)
        df.to_csv(OUTPUT_PATH, index=False, encoding="utf-8-sig")
        print(f"\n=== 완료: {OUTPUT_PATH} ({len(rows)}개 모델) ===")


if __name__ == "__main__":
    asyncio.run(main())