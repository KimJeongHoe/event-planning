#!/usr/bin/env python3
"""raw/*.jsonl 의 사례 칸을 고치고 raw/수정기록.jsonl 에 기록한다.
사용: python3 -I scripts/edit_raw.py <edits.json>
edits.json = [{"case":"OPN-012" 또는 최종번호 "123", "field":"benefit", "after":"...", "reason":"...", "source_url":"...", "log":true}, ...]
 - field가 verify_status/verify_note/merged_into/merged_from 이면 log 기본 false(기록 생략), 그 밖은 항상 기록.
 - mode:"append" 이면 기존 값 뒤에 ' | ' 로 덧붙임."""
import json, sys, os, glob, datetime
BASE = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
RAW = f"{BASE}/raw"
idmap = json.load(open(f"{BASE}/merged/id_map.json", encoding="utf-8"))
num2key = {str(v): k for k, v in idmap.items()}
edits = json.load(open(sys.argv[1], encoding="utf-8"))
today = datetime.date.today().isoformat()
files = {}
def load(fn):
    if fn not in files:
        files[fn] = [json.loads(l) for l in open(f"{RAW}/{fn}", encoding="utf-8") if l.strip()]
    return files[fn]
logs, miss = [], []
for e in edits:
    c = str(e["case"]).strip()
    if c.isdigit():
        if c not in num2key: miss.append(c); continue
        fn, oid = num2key[c].split("::", 1)
    else:
        fn = None; oid = c
        pre = c.split("-")[0]
        fn = f"{pre}.jsonl"
    rows = load(fn)
    hit = [r for r in rows if str(r.get("id", "")).strip() == oid.split("#")[0]]
    if not hit: miss.append(c); continue
    r = hit[0]; f = e["field"]; before = r.get(f, "")
    after = e["after"]
    if e.get("mode") == "append" and str(before).strip():
        after = f"{before} | {after}"
    if before == after: continue
    r[f] = after
    quiet = f in ("verify_status", "verify_note", "merged_into", "merged_from")
    if e.get("log", not quiet):
        logs.append({"date": today, "case": oid, "field": f, "before": before, "after": after,
                     "reason": e.get("reason", ""), "source_url": e.get("source_url", "")})
for fn, rows in files.items():
    tmp = f"{RAW}/{fn}.tmp"
    with open(tmp, "w", encoding="utf-8") as w:
        for r in rows: w.write(json.dumps(r, ensure_ascii=False) + "\n")
    os.replace(tmp, f"{RAW}/{fn}")
with open(f"{RAW}/수정기록.jsonl", "a", encoding="utf-8") as w:
    for l in logs: w.write(json.dumps(l, ensure_ascii=False) + "\n")
print(f"적용 {len(edits)-len(miss)}건, 기록 {len(logs)}건, 못 찾음 {miss}")
