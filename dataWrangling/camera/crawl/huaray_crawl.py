"""
Teledyne Vision Solutions 카메라 스펙 크롤러
==============================
설치:
    pip install playwright beautifulsoup4 pandas
    playwright install chromium

실행:
    python teledyne_crawl.py

결과:
    teledyne.csv (스크립트 실행 경로)
"""

import asyncio
import pandas as pd
from bs4 import BeautifulSoup
from playwright.async_api import async_playwright

BASE_URL   = "https://www.teledynevisionsolutions.com"
LIST_URLS  = [
    ("https://www.teledynevisionsolutions.com/ko-kr/categories/cameras/", "Camera"),
]
OUTPUT_PATH = "teledyne.csv"


async def goto(page, url):
    await page.goto(url, wait_until="domcontentloaded", timeout=30000)
    await asyncio.sleep(2)


# ─────────────────────────────────────────────
# Product-Specifications 섹션 파싱 (dl.Spec-list)
# ─────────────────────────────────────────────
def parse_spec_section(soup) -> dict:
    spec = {}
    for dl in soup.select("div.Product-Specifications dl.Spec-list"):
        dt = dl.find("dt")
        dd = dl.find("dd")
        if dt and dd:
            key = dt.get_text(strip=True)
            value = dd.get_text(strip=True)
            if key and value:
                spec[key] = value
    return spec


# ─────────────────────────────────────────────
# 1단계: 목록에서 패밀리 링크 수집
# ─────────────────────────────────────────────
async def get_family_links(page, list_url, camera_type, retries=3) -> list:
    for attempt in range(retries):
        try:
            await goto(page, list_url)
            soup = BeautifulSoup(await page.content(), "html.parser")
            items = soup.select("div.Product-listItem")

            results = []
            seen = set()
            for item in items:
                a = item.find("a", href=True)
                if not a:
                    continue
                href = a["href"].split("?")[0]
                if href in seen:
                    continue
                seen.add(href)
                full_url = BASE_URL + href if href.startswith("/") else href
                # 패밀리명은 첫 번째 텍스트 덩어리
                text = item.get_text(" ", strip=True)
                family_name = text[:60]
                results.append({
                    "family_url": full_url,
                    "family_name": family_name,
                    "camera_type": camera_type,
                })

            if results:
                return results

            print(f"    ⚠ 링크 없음 (시도 {attempt+1}/{retries})")
            await asyncio.sleep(3)

        except Exception as e:
            print(f"    ⚠ 오류 (시도 {attempt+1}/{retries}): {e}")
            await asyncio.sleep(3)

    return []


# ─────────────────────────────────────────────
# 2단계: 패밀리 페이지 → 스펙 수집
# ─────────────────────────────────────────────
async def get_family_rows(page, family_url, family_name, camera_type, retries=3) -> list:
    for attempt in range(retries):
        try:
            await goto(page, family_url)
            soup = BeautifulSoup(await page.content(), "html.parser")

            # h1 모델명
            h1 = soup.select_one("h1")
            model_title = h1.get_text(strip=True) if h1 else family_name

            # ── 케이스 B: familySpecsSection 있으면 모델별로 한 번 더 접근 ──
            family_section = soup.select_one(".familySpecsSection")
            if family_section:
                # 공통 스펙
                common_spec = {}
                for row in family_section.select("tr"):
                    cells = row.find_all(["th", "td"])
                    if len(cells) >= 2:
                        key = cells[0].get_text(strip=True)
                        value = cells[1].get_text(strip=True)
                        if key and value:
                            common_spec[key] = value

                # 모델 테이블에서 개별 모델 링크 추출
                model_table = soup.select_one("table.ModelSelector-table")
                model_links = []
                if model_table:
                    headers = [th.get_text(strip=True) for th in model_table.select("thead th")]
                    for tr in model_table.select("tbody tr"):
                        cells = tr.find_all("td")
                        if not cells:
                            continue
                        # 첫 번째 셀에서 모델명 + 링크 추출
                        first_cell = cells[0]
                        a = first_cell.find("a", href=True)
                        if a:
                            href = a["href"]
                            model_url = BASE_URL + href if href.startswith("/") else href
                        else:
                            # 링크 없으면 ?model= 파라미터로 구성
                            # 두 번째 줄(부품번호)이 모델명인 경우
                            texts = first_cell.get_text("\n", strip=True).split("\n")
                            part_no = texts[1].strip() if len(texts) > 1 else ""
                            if part_no:
                                base = family_url.rstrip("/")
                                model_url = f"{base}/?model={part_no}"
                            else:
                                continue

                        model_name = first_cell.get_text(" ", strip=True).split("  ")[0][:80]
                        model_links.append({"url": model_url, "name": model_name})

                if not model_links:
                    # 모델 링크 못 찾으면 패밀리 스펙만 저장
                    row = {
                        "brand": "Teledyne Dalsa",
                        "model_name": model_title,
                        "camera_type": camera_type,
                        "family_name": model_title,
                    }
                    row.update(common_spec)
                    return [row]

                # 각 모델 상세 페이지 접근
                rows = []
                for ml in model_links:
                    print(f"      → {ml['name'][:40]}")
                    try:
                        await goto(page, ml["url"])
                        msoup = BeautifulSoup(await page.content(), "html.parser")
                        spec = parse_spec_section(msoup)

                        row = {
                            "brand": "Teledyne Dalsa",
                            "model_name": ml["name"],
                            "camera_type": camera_type,
                            "family_name": model_title,
                        }
                        row.update(common_spec)
                        row.update(spec)
                        rows.append(row)
                        await asyncio.sleep(0.5)
                    except Exception as e:
                        print(f"      ⚠ 모델 스펙 실패: {e}")

                if rows:
                    return rows

            # ── 케이스 A: 바로 Product-Specifications 읽기 ──
            spec = parse_spec_section(soup)
            if spec:
                row = {
                    "brand": "Teledyne Dalsa",
                    "model_name": model_title,
                    "camera_type": camera_type,
                    "family_name": model_title,
                }
                row.update(spec)
                return [row]

            print(f"    ⚠ 스펙 없음 (시도 {attempt+1}/{retries})")
            await asyncio.sleep(3)

        except Exception as e:
            print(f"    ⚠ 오류 (시도 {attempt+1}/{retries}): {e}")
            await asyncio.sleep(3)

    return []


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
        print("=== 1단계: 패밀리 링크 수집 ===")
        all_families = []
        seen_urls = set()
        for list_url, camera_type in LIST_URLS:
            print(f"\n  카테고리: {camera_type}")
            families = await get_family_links(page, list_url, camera_type)
            for f in families:
                if f["family_url"] not in seen_urls:
                    seen_urls.add(f["family_url"])
                    all_families.append(f)
            print(f"  {len(families)}개 패밀리 (누적 {len(all_families)}개)")

        print(f"\n총 {len(all_families)}개 패밀리\n")

        # 2단계
        print("=== 2단계: 패밀리별 스펙 수집 ===")
        all_rows = []
        for i, fam in enumerate(all_families):
            print(f"  [{i+1}/{len(all_families)}] {fam['family_name'][:50]}")
            rows = await get_family_rows(page, fam["family_url"], fam["family_name"], fam["camera_type"])
            all_rows.extend(rows)
            print(f"    → {len(rows)}개 모델")
            await asyncio.sleep(0.5)

        await browser.close()

        df = pd.DataFrame(all_rows)
        df.to_csv(OUTPUT_PATH, index=False, encoding="utf-8-sig")
        print(f"\n=== 완료: {OUTPUT_PATH} ({len(all_rows)}개 모델) ===")


if __name__ == "__main__":
    asyncio.run(main())