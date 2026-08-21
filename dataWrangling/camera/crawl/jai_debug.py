import asyncio
from bs4 import BeautifulSoup
from playwright.async_api import async_playwright

SELECTION_URL = "https://www.jai.com/products/camera-selection-guide/"

async def main():
    async with async_playwright() as p:
        browser = await p.chromium.launch(headless=False,
            args=["--disable-blink-features=AutomationControlled"])
        context = await browser.new_context(
            user_agent="Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/136.0.0.0 Safari/537.36",
            locale="en-US",
        )
        await context.add_init_script("Object.defineProperty(navigator, 'webdriver', {get: () => undefined})")
        page = await context.new_page()

        await page.goto(SELECTION_URL, wait_until="domcontentloaded", timeout=30000)
        await asyncio.sleep(5)

        soup = BeautifulSoup(await page.content(), "html.parser")

        # 테이블 헤더 확인
        print("=== 테이블 헤더 ===")
        for table in soup.find_all("table")[:1]:
            headers = [th.get_text(strip=True) for th in table.select("th")]
            print(f"헤더: {headers}")
            print("\n첫 3행:")
            for row in table.select("tbody tr")[:3]:
                cells = row.find_all("td")
                # 링크 확인
                a = row.find("a", href=True)
                print(f"  링크: {a['href'] if a else 'None'}")
                print(f"  셀: {[c.get_text(strip=True)[:30] for c in cells]}")

        # 상세 페이지 하나 확인
        detail_url = "https://www.jai.com/products/product-lines/gox-series-small-size-industrial-area-scan-cameras/ap-1600t-usb-lsx"
        print(f"\n=== 상세 페이지 구조: {detail_url} ===")
        await page.goto(detail_url, wait_until="domcontentloaded", timeout=30000)
        await asyncio.sleep(3)

        soup2 = BeautifulSoup(await page.content(), "html.parser")

        # 스펙 테이블
        print("테이블 (첫 2개):")
        for i, table in enumerate(soup2.find_all("table")[:2]):
            print(f"\n[테이블 {i+1}]")
            for row in table.select("tr")[:6]:
                cells = row.find_all(["th", "td"])
                if cells:
                    print("  " + " | ".join(c.get_text(strip=True)[:30] for c in cells))

        # spec 관련 class
        print("\n'spec' 또는 'product' 포함 class (최대 8개):")
        count = 0
        for tag in soup2.find_all(True):
            classes = " ".join(tag.get("class", []))
            if any(k in classes.lower() for k in ["spec", "product-detail", "tech"]):
                print(f"  <{tag.name} class='{classes}'> {tag.get_text(strip=True)[:50]}")
                count += 1
                if count >= 8:
                    break

        await browser.close()

asyncio.run(main())