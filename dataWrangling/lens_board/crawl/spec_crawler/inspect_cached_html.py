# -*- coding: utf-8 -*-
"""
캐시된 HTML 구조 분석 도구 (table 추출이 0건일 때 사용)

debug_target.py 로 저장된 page_*.html 파일은 로컬에만 있고 Claude는 접근할 수 없습니다.
대신 이 스크립트를 실행해서 "스펙처럼 보이는 텍스트" 주변의 실제 HTML 태그/class 구조를
출력하면, 그 결과를 Claude에게 보내서 전용 파서를 만들 수 있습니다.

사용법:
    python inspect_cached_html.py <html파일경로> [키워드1] [키워드2] ...

    # 예시
    python inspect_cached_html.py debug_output/euresys_grablink/page_03__en_products_frame-grabber_grablink-value_.html "Form factor"
    python inspect_cached_html.py debug_output/euresys_grablink/page_00__en_products_frame-grabber_grablink-full_.html "PCIe" "Connectors"

키워드를 안 주면 기본 키워드 세트(common spec label들)로 검색합니다.

각 키워드에 대해:
  - 그 텍스트를 포함하는 노드를 찾고
  - 조상(ancestor) 태그/class 체인을 출력
  - 그 노드를 포함하는 "컨테이너"의 HTML을 일부 출력 (구조 파악용)
  - 같은 class를 가진 "형제(sibling) 요소"가 몇 개 더 있는지 (반복 구조인지) 표시
"""

import sys
from bs4 import BeautifulSoup, NavigableString

DEFAULT_KEYWORDS = [
    "Form factor", "PCIe", "Connectors", "Cooling method", "Mounting",
    "Focal", "Mount", "Magnification", "Working distance", "Interface",
    "Resolution", "Channels", "Power",
]


def ancestor_chain(node, max_depth: int = 6) -> str:
    chain = []
    cur = node
    for _ in range(max_depth):
        if cur is None or cur.name is None:
            break
        attrs = {}
        if cur.get("class"):
            attrs["class"] = cur.get("class")
        if cur.get("id"):
            attrs["id"] = cur.get("id")
        chain.append(f"<{cur.name} {attrs}>" if attrs else f"<{cur.name}>")
        cur = cur.parent
    return " < ".join(chain)


def sibling_count_with_same_class(node):
    """node의 부모 기준, node와 같은 tag+class를 가진 형제(자기 포함) 개수"""
    parent = node.parent
    if parent is None:
        return 0
    target_class = node.get("class")
    target_tag = node.name
    count = 0
    for sib in parent.find_all(target_tag, recursive=False):
        if sib.get("class") == target_class:
            count += 1
    return count


def find_text_nodes(soup, keyword):
    return soup.find_all(string=lambda s: isinstance(s, NavigableString) and keyword in s)


def main():
    if len(sys.argv) < 2:
        print(__doc__)
        sys.exit(1)

    path = sys.argv[1]
    keywords = sys.argv[2:] if len(sys.argv) > 2 else DEFAULT_KEYWORDS

    with open(path, encoding="utf-8") as f:
        html = f.read()

    soup = BeautifulSoup(html, "lxml")

    title = soup.find("title")
    print(f"파일: {path}")
    print(f"title: {title.get_text(strip=True) if title else '(없음)'}")
    print(f"전체 <table> 개수: {len(soup.find_all('table'))}")
    print(f"전체 <dl> 개수: {len(soup.find_all('dl'))}")
    print("=" * 60)

    found_any = False
    for kw in keywords:
        matches = find_text_nodes(soup, kw)
        if not matches:
            continue
        found_any = True
        print(f"\n### 키워드 '{kw}' -> {len(matches)}개 매치")

        for i, m in enumerate(matches[:2]):
            node = m.parent
            print(f"\n--- match {i} : 텍스트 = {str(m).strip()[:50]!r}")
            print(f"조상 체인: {ancestor_chain(node)}")

            sib_count = sibling_count_with_same_class(node)
            print(f"같은 tag+class를 가진 형제 요소 개수: {sib_count} (2개 이상이면 반복되는 행/카드 구조일 가능성)")

            # 컨테이너 HTML 일부 출력: node에서 2단계 위 부모
            container = node
            for _ in range(2):
                if container.parent is not None:
                    container = container.parent
            snippet = str(container)
            if len(snippet) > 1500:
                snippet = snippet[:1500] + "\n... (truncated)"
            print("컨테이너 HTML (조상 2단계 위, 최대 1500자):")
            print(snippet)

    if not found_any:
        print("\n지정한 키워드들이 텍스트에서 전혀 발견되지 않았습니다.")
        print("=> 페이지에 스펙 텍스트 자체가 없거나(완전 JS 렌더링), 다른 키워드/언어로 표시될 수 있습니다.")
        print("   <body> 텍스트 일부 미리보기:")
        body = soup.find("body")
        if body:
            text = body.get_text(" ", strip=True)
            print(text[:1000])


if __name__ == "__main__":
    main()
