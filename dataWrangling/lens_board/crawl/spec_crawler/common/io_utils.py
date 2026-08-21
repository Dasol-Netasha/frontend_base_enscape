# -*- coding: utf-8 -*-
"""
파일 입출력 공통 유틸
- 크롤링한 raw HTML 캐시 저장 (재실행 시 재활용 가능)
- 레코드(dict) 리스트를 JSONL / CSV 로 저장
"""

import os
import json
import csv
from urllib.parse import urlparse


def safe_filename(s: str) -> str:
    return "".join(c if c.isalnum() or c in "-_." else "_" for c in s)[:120]


def save_raw_html(base_dir: str, target_key: str, url: str, html: str, prefix: str = "page") -> str:
    """raw_html/<target_key>/<prefix>__<path>.html 형태로 저장"""
    outdir = os.path.join(base_dir, target_key)
    os.makedirs(outdir, exist_ok=True)
    parsed = urlparse(url)
    fname = f"{prefix}__{safe_filename(parsed.path or 'root')}.html"
    fpath = os.path.join(outdir, fname)
    with open(fpath, "w", encoding="utf-8") as f:
        f.write(html)
    return fpath


def save_jsonl(records: list[dict], path: str):
    os.makedirs(os.path.dirname(path), exist_ok=True)
    with open(path, "w", encoding="utf-8") as f:
        for rec in records:
            f.write(json.dumps(rec, ensure_ascii=False) + "\n")


def save_records_csv(records: list[dict], path: str, priority_cols: list[str] | None = None):
    """
    records: dict 리스트 (각 dict는 키가 서로 다를 수 있음)
    priority_cols: 앞쪽에 고정으로 둘 컬럼 순서 (예: ["brand", "lens_type", "raw_category", "model"])

    모든 dict의 key 합집합을 컬럼으로 사용, 값이 dict/list인 경우 JSON 문자열로 변환.
    """
    os.makedirs(os.path.dirname(path), exist_ok=True)

    all_keys = []
    seen = set()
    priority_cols = priority_cols or []
    for c in priority_cols:
        if c not in seen:
            all_keys.append(c)
            seen.add(c)

    for rec in records:
        for k in rec.keys():
            if k not in seen:
                all_keys.append(k)
                seen.add(k)

    with open(path, "w", encoding="utf-8-sig", newline="") as f:
        writer = csv.DictWriter(f, fieldnames=all_keys, restval="")
        writer.writeheader()
        for rec in records:
            row = {}
            for k, v in rec.items():
                if isinstance(v, (dict, list)):
                    row[k] = json.dumps(v, ensure_ascii=False)
                else:
                    row[k] = v
            writer.writerow(row)
