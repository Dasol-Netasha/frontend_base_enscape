# -*- coding: utf-8 -*-
"""
공통 HTTP 클라이언트
- 브라우저처럼 보이는 User-Agent / 헤더
- 자동 재시도 (네트워크 오류, 5xx)
- 요청 간 딜레이 (서버 부담 줄이기 + 차단 방지)

사용 예:
    from common.http_client import get_session, fetch

    session = get_session()
    resp = fetch(session, "https://example.com/page")
    html = resp.text
"""

import time
import random
import requests
from requests.adapters import HTTPAdapter
from urllib3.util.retry import Retry


DEFAULT_HEADERS = {
    "User-Agent": (
        "Mozilla/5.0 (Windows NT 10.0; Win64; x64) "
        "AppleWebKit/537.36 (KHTML, like Gecko) "
        "Chrome/124.0.0.0 Safari/537.36"
    ),
    "Accept": (
        "text/html,application/xhtml+xml,application/xml;"
        "q=0.9,image/avif,image/webp,*/*;q=0.8"
    ),
    "Accept-Language": "ko-KR,ko;q=0.9,en-US;q=0.8,en;q=0.7",
}


def get_session(extra_headers: dict | None = None) -> requests.Session:
    """재시도 로직이 포함된 requests.Session 생성"""
    session = requests.Session()
    headers = dict(DEFAULT_HEADERS)
    if extra_headers:
        headers.update(extra_headers)
    session.headers.update(headers)

    retry = Retry(
        total=3,
        backoff_factor=1.5,
        status_forcelist=[429, 500, 502, 503, 504],
        allowed_methods=["GET", "HEAD"],
    )
    adapter = HTTPAdapter(max_retries=retry)
    session.mount("http://", adapter)
    session.mount("https://", adapter)
    return session


def fetch(
    session: requests.Session,
    url: str,
    timeout: int = 20,
    min_delay: float = 0.8,
    max_delay: float = 2.0,
    **kwargs,
) -> requests.Response:
    """
    요청 사이에 랜덤 딜레이를 주고 GET 요청을 보낸다.
    실패 시 예외를 그대로 올린다 (호출부에서 try/except로 처리).
    """
    time.sleep(random.uniform(min_delay, max_delay))
    resp = session.get(url, timeout=timeout, **kwargs)
    # 인코딩 자동 감지가 틀리는 경우 방지
    # Content-Type에 charset이 명시되지 않은 경우 UTF-8로 강제
    # 단, EUC-KR 사이트(toptics.co.kr 등)는 bytes로 직접 처리하므로 건드리지 않음
    if resp.encoding and resp.encoding.lower() in ("iso-8859-1", "latin-1", "windows-1252"):
        # Content-Type에 euc-kr 명시 여부 확인
        ct = resp.headers.get("content-type", "").lower()
        if "euc-kr" not in ct and "euc_kr" not in ct:
            resp.encoding = "utf-8"
    return resp
