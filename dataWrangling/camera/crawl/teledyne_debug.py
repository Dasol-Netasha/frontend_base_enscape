import asyncio
from bs4 import BeautifulSoup
from playwright.async_api import async_playwright

URLS = [
    "https://www.teledynevisionsolutions.com/ko-kr/categories/cameras/",
    "https://www.teledynevisionsolutions.com/ko-kr/categories/cameras/industrial-cameras/",
    "https://www.teledynevisionsolutions.com/ko-kr/categories/cameras/scientific-cameras/",
]

async def main():
    async with async_playwright() as p:
        browser = await p.chromium.launch(headless=False)
        context = await browser.new_context(
            user_agent="Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 Chrome/136.0.0.0 Safari/537.36",
            locale="ko-KR",
        )
        page = await context.new_page()

        for url in URLS:
            await page.goto(url, wait_until="domcontentloaded", timeout=30000)
            await asyncio.sleep(3)
            soup = BeautifulSoup(await page.content(), "html.parser")
            items = soup.select("div.Product-listItem")
            links = list(dict.fromkeys([
                i.find("a", href=True)["href"].split("?")[0]
                for i in items if i.find("a", href=True)
            ]))
            print(f"\n{url}")
            print(f"  Product-listItem 수: {len(links)}")
            for l in links[:5]:
                print(f"  {l}")

        await browser.close()

asyncio.run(main())