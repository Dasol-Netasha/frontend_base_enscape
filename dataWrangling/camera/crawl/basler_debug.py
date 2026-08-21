"""
Basler 크롤러 디버그 스크립트 v5
실행: python basler_debug.py
"""

import asyncio
from bs4 import BeautifulSoup
from playwright.async_api import async_playwright

URL = "https://www.baslerweb.com/ko-kr/cameras/?page=1"

async def main():
    async with async_playwright() as p:
        browser = await p.chromium.launch(headless=False)  # 헤드리스 OFF → 실제 브라우저 화면 표시
        context = await browser.new_context(
            user_agent="Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/124.0.0.0 Safari/537.36",
            locale="ko-KR",
            timezone_id="Asia/Seoul",
        )
        page = await context.new_page()

        print(f"접속 중: {URL}")
        await page.goto(URL, wait_until="domcontentloaded", timeout=30000)

        # 로딩 완료 대기: is-loading 사라질 때까지 최대 30초
        print("카드 로딩 대기 중 (최대 30초)...")
        try:
            await page.wait_for_selector(
                "article.product-card:not(.product-card--is-loading)",
                timeout=30000
            )
            print("로딩 완료!")
        except Exception as e:
            print(f"대기 실패: {e}")

        html = await page.content()
        soup = BeautifulSoup(html, "html.parser")

        cards = soup.select("article.product-card")
        loading_cards = soup.select("article.product-card--is-loading")
        print(f"\n전체 카드 수: {len(cards)}")
        print(f"로딩 중인 카드 수: {len(loading_cards)}")

        # li 안의 /shop/ 링크
        print("\n=== li 안 /shop/ 링크 (최대 10개) ===")
        count = 0
        for li in soup.select("li.products-list-grid__item"):
            for a in li.find_all("a", href=True):
                if "/shop/" in a["href"]:
                    print(f"  href: {a['href']}")
                    print(f"  텍스트: {a.get_text(strip=True)[:80]}")
                    count += 1
                    break
            if count >= 10:
                break

        # li 텍스트 샘플
        print("\n=== li 텍스트 샘플 (첫 5개) ===")
        for i, li in enumerate(soup.select("li.products-list-grid__item")[:5]):
            print(f"  [{i+1}] {li.get_text(strip=True)[:100]}")

        await page.screenshot(path="basler_debug.png", full_page=False)
        print("\n스크린샷 저장: basler_debug.png")

        # 브라우저 5초 열어두기 (눈으로 확인)
        await asyncio.sleep(5)
        await browser.close()

asyncio.run(main())