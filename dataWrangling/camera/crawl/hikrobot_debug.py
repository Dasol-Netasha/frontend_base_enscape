"""
ID 추출 디버그
실행: python hikrobot_debug.py
"""

import asyncio
import re
from playwright.async_api import async_playwright

URL = "https://www.hikrobotics.com/en/machinevision/visionproduct?typeId=78&id=145&pageNumber=1&pageSize=50&showEol=false"

async def main():
    async with async_playwright() as p:
        browser = await p.chromium.launch(headless=False,
            args=["--disable-blink-features=AutomationControlled"])
        context = await browser.new_context(
            user_agent="Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/136.0.0.0 Safari/537.36",
            locale="en-US",
            viewport={"width": 1920, "height": 1080},
        )
        await context.add_init_script("Object.defineProperty(navigator, 'webdriver', {get: () => undefined})")
        page = await context.new_page()

        await page.goto(URL, wait_until="domcontentloaded", timeout=60000)
        await asyncio.sleep(8)

        content = await page.content()
        print(f"HTML 길이: {len(content)}")

        # 1. productdetail 포함 여부
        print(f"productdetail 포함: {'productdetail' in content}")

        # 2. firstModuleId 포함 여부
        print(f"firstModuleId 포함: {'firstModuleId' in content}")

        # 3. records 포함 여부
        print(f"records 포함: {'records' in content}")

        # 4. 7830 같은 product id 포함 여부
        print(f"'7830' 포함: {'7830' in content}")

        # 5. script 태그 내용 중 id 패턴 찾기
        ids_found = re.findall(r'"id"\s*:\s*(\d{4,5})', content)
        print(f"\n4-5자리 id 패턴 수: {len(ids_found)}")
        print(f"샘플: {ids_found[:10]}")

        # 6. window.__INITIAL_STATE__ 같은 전역변수 확인
        for keyword in ['__INITIAL', '__STATE', '__DATA', '__STORE', 'window.', 'nuxt']:
            if keyword in content:
                idx = content.index(keyword)
                print(f"\n'{keyword}' 발견 위치 {idx}:")
                print(content[idx:idx+200])
                break

        await browser.close()

asyncio.run(main())