# -*- coding: utf-8 -*-
"""
Vico AJAX 엔드포인트 디버그 스크립트.
실행: python debug_vico_ajax.py

브라우저 쿠키를 아래 BROWSER_COOKIES에 붙여넣고 실행하세요.
Chrome: F12 → Network → admin-ajax.php → Request Headers → Cookie 값 복사
"""

import re
from common.http_client import get_session

CATEGORY_URL = "https://vicoimaging.com/product-category/matrix-bi-telecentric-lenses/"
AJAX_URL = "https://vicoimaging.com/wp-admin/admin-ajax.php"

# ★ Chrome에서 복사한 Cookie 헤더 값을 여기에 붙여넣으세요 ★
# 예: "wordpress_logged_in_xxx=yyy; woocommerce_cart_hash=zzz; ..."
BROWSER_COOKIES = "gclid=undefined; sbjs_migrations=1418474375998%3D1; sbjs_current_add=fd%3D2026-06-15%2007%3A31%3A18%7C%7C%7Cep%3Dhttps%3A%2F%2Fvicoimaging.com%2F%7C%7C%7Crf%3D%28none%29; sbjs_first_add=fd%3D2026-06-15%2007%3A31%3A18%7C%7C%7Cep%3Dhttps%3A%2F%2Fvicoimaging.com%2F%7C%7C%7Crf%3D%28none%29; sbjs_current=typ%3Dtypein%7C%7C%7Csrc%3D%28direct%29%7C%7C%7Cmdm%3D%28none%29%7C%7C%7Ccmp%3D%28none%29%7C%7C%7Ccnt%3D%28none%29%7C%7C%7Ctrm%3D%28none%29%7C%7C%7Cid%3D%28none%29%7C%7C%7Cplt%3D%28none%29%7C%7C%7Cfmt%3D%28none%29%7C%7C%7Ctct%3D%28none%29; sbjs_first=typ%3Dtypein%7C%7C%7Csrc%3D%28direct%29%7C%7C%7Cmdm%3D%28none%29%7C%7C%7Ccmp%3D%28none%29%7C%7C%7Ccnt%3D%28none%29%7C%7C%7Ctrm%3D%28none%29%7C%7C%7Cid%3D%28none%29%7C%7C%7Cplt%3D%28none%29%7C%7C%7Cfmt%3D%28none%29%7C%7C%7Ctct%3D%28none%29; _gcl_au=1.1.1162669743.1781508678; _ga=GA1.1.870343310.1781508679; cmplz_rt_consented_services=; cmplz_rt_policy_id=33; cmplz_rt_marketing=allow; cmplz_rt_statistics=allow; cmplz_rt_preferences=allow; cmplz_rt_functional=allow; cmplz_rt_banner-status=dismissed; vicoimaging-_zldp=vDnWmyRlSzMV8KqkCGxRGsx81LUkSr4bJTjDXo%2FC8FC0ysrcJZW6wWFQVNlWU6FaodoRkLyJC2Y%3D; vicoimaging-_zldt=c10deed0-4590-46e2-9cc6-02c68f5b8502-2; _hjSessionUser_3920643=eyJpZCI6ImYyNzg3ZDkxLTRjMjgtNTljNy1iMDY2LTFlZTE4MTVjYzUyYyIsImNyZWF0ZWQiOjE3ODE1MDg2NzgzOTksImV4aXN0aW5nIjp0cnVlfQ==; _hjSession_3920643=eyJpZCI6IjBhMzQ3N2MzLWRiNWYtNDkwYy1iNzE4LWZhZjg5ODU0NTI4MyIsImMiOjE3ODE1NzQzMzIyMzgsInMiOjEsInIiOjEsInNiIjowLCJzciI6MCwic2UiOjAsImZzIjowLCJzcCI6MH0=; sbjs_udata=vst%3D2%7C%7C%7Cuip%3D%28none%29%7C%7C%7Cuag%3DMozilla%2F5.0%20%28Windows%20NT%2010.0%3B%20Win64%3B%20x64%29%20AppleWebKit%2F537.36%20%28KHTML%2C%20like%20Gecko%29%20Chrome%2F149.0.0.0%20Safari%2F537.36; woolentor_viewed_products_list_1=a%3A1%3A%7Bi%3A1781574417%3Bi%3A8514%3B%7D; woolentor_already_views_count_product_1=a%3A1%3A%7Bi%3A1781574417%3Bi%3A8514%3B%7D; _ga_8PVLH837FH=GS2.1.s1781574331%24o2%24g1%24t1781575741%24j29%24l0%24h0; sbjs_session=pgs%3D18%7C%7C%7Ccpg%3Dhttps%3A%2F%2Fvicoimaging.com%2Fproduct-category%2Fultra-resolution-bi-telecentric-lenses%2F"

session = get_session()

# 브라우저 쿠키가 있으면 세션에 주입
if BROWSER_COOKIES.strip():
    for part in BROWSER_COOKIES.split(";"):
        part = part.strip()
        if "=" in part:
            k, v = part.split("=", 1)
            session.cookies.set(k.strip(), v.strip(), domain="vicoimaging.com")
    print(f"  쿠키 {len(list(session.cookies))}개 주입됨")
else:
    print("  [INFO] BROWSER_COOKIES 미설정 — 쿠키 없이 시도")

print("=== 카테고리 페이지 fetch ===")
resp = session.get(CATEGORY_URL, timeout=15)
print(f"  status: {resp.status_code}, html: {len(resp.text)}자")
html = resp.text

nonce_m = re.search(r'wdtNonceFrontendServerSide_(\d+)[^>]*value="([a-f0-9]+)"', html)
if not nonce_m:
    print("  [ERROR] nonce 추출 실패")
    exit(1)
table_id, nonce = nonce_m.group(1), nonce_m.group(2)
print(f"  table_id={table_id}, nonce={nonce}")

# 기본 POST (쿠키 없이도 동작할 수 있는 공개 테이블이라면)
post_data = {
    "action": "get_wdtable",
    "table_id": table_id,
    "draw": "1",
    "start": "0",
    "length": "5",
    "search[value]": "",
    "search[regex]": "false",
    "order[0][column]": "0",
    "order[0][dir]": "asc",
    f"wdtNonceFrontendServerSide_{table_id}": nonce,
    "_wp_http_referer": "/product-category/matrix-bi-telecentric-lenses/",
}

print("\n=== AJAX POST ===")
r = session.post(AJAX_URL, data=post_data, headers={
    "Content-Type": "application/x-www-form-urlencoded; charset=UTF-8",
    "Referer": CATEGORY_URL,
    "X-Requested-With": "XMLHttpRequest",
}, timeout=30)

print(f"  status: {r.status_code}, length: {len(r.text)}")
print(f"  응답: {repr(r.text[:500])}")

if r.text.strip():
    try:
        j = r.json()
        print(f"\n  ✓ JSON 파싱 성공!")
        print(f"  recordsTotal: {j.get('recordsTotal')}")
        print(f"  rows: {len(j.get('data', []))}")
        if j.get('data'):
            print(f"  첫 row: {j['data'][0][:6]}")
    except Exception as e:
        print(f"  JSON 파싱 실패: {e}")
else:
    print("\n  응답이 비어있어요.")
    print("  → Chrome에서 F12 > Network > admin-ajax.php 요청을 찾아")
    print("    Request Headers의 Cookie 값을 BROWSER_COOKIES에 붙여넣고 재실행하세요.")


