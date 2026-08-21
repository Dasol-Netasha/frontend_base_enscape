import asyncio
from bs4 import BeautifulSoup
from playwright.async_api import async_playwright

URL = "https://thinklucid.com/ko/lucid-machine-vision-cameras/"

async def main():
    async with async_playwright() as p:
        browser = await p.chromium.launch(headless=False,
            args=["--disable-blink-features=AutomationControlled"])
        context = await browser.new_context(
            user_agent="Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/136.0.0.0 Safari/537.36",
        )
        page = await context.new_page()
        await page.goto(URL, wait_until="domcontentloaded", timeout=30000)
        await asyncio.sleep(4)

        soup = BeautifulSoup(await page.content(), "html.parser")
        print(f"HTML 길이: {len(await page.content())}")

        # /product/ 링크
        print("\n=== /product/ 링크 (최대 10개) ===")
        seen = set()
        count = 0
        for a in soup.find_all("a", href=True):
            href = a["href"]
            if "/product/" in href and href not in seen:
                seen.add(href)
                print(f"  {href} | {a.get_text(strip=True)[:40]}")
                count += 1
                if count >= 10:
                    break

        print(f"\n총 /product/ 링크 수: {len([a for a in soup.find_all('a', href=True) if '/product/' in a['href']])}")

        # 테이블 구조
        print("\n=== 테이블 (첫 1개, 헤더+3행) ===")
        for table in soup.find_all("table")[:1]:
            headers = [th.get_text(strip=True) for th in table.select("th")]
            print(f"헤더: {headers[:8]}")
            for row in table.select("tbody tr")[:3]:
                cells = row.find_all("td")
                a = row.find("a", href=True)
                print(f"  링크: {a['href'] if a else 'None'} | {[c.get_text(strip=True)[:20] for c in cells[:6]]}")

        await browser.close()

asyncio.run(main())