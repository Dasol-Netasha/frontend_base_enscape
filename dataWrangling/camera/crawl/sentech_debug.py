import asyncio
from bs4 import BeautifulSoup
from playwright.async_api import async_playwright

URL = "https://sentech.co.jp/en/products_cate/gige-camera"

async def main():
    async with async_playwright() as p:
        browser = await p.chromium.launch(headless=False)
        context = await browser.new_context(
            user_agent="Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 Chrome/136.0.0.0 Safari/537.36",
            locale="en-US",
        )
        page = await context.new_page()
        await page.goto(URL, wait_until="domcontentloaded", timeout=30000)
        await asyncio.sleep(3)

        soup = BeautifulSoup(await page.content(), "html.parser")

        # main/article 영역만 확인
        print("=== main 또는 article 태그 내 /products/ 링크 ===")
        main = soup.select_one("main, article, #main, .main, [role='main']")
        if main:
            links = [(a["href"], a.get_text(strip=True)[:40])
                     for a in main.find_all("a", href=True)
                     if "/en/products/" in a["href"]]
            print(f"main 내 링크 수: {len(links)}")
            for href, text in links[:10]:
                print(f"  {href} | {text}")
        else:
            print("main 태그 없음")

        # 제품 카드 컨테이너 찾기
        print("\n=== 제품 목록 컨테이너 후보 ===")
        for tag in soup.find_all(True):
            classes = " ".join(tag.get("class", []))
            if any(k in classes.lower() for k in ["product-list", "products", "cate", "lineup", "list"]):
                links_in = tag.find_all("a", href=lambda h: h and "/en/products/" in h)
                if links_in:
                    print(f"  <{tag.name} class='{classes}'> → {len(links_in)}개 링크")
                    for a in links_in[:3]:
                        print(f"    {a['href']} | {a.get_text(strip=True)[:40]}")

        await browser.close()

asyncio.run(main())