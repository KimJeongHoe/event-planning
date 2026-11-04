#!/usr/bin/env python3
"""FAQ 패치 반영: raw/FAQ*_faq.jsonl 의 칸을 고치고 raw/수정기록.jsonl 에 기록. 사용: apply_faq.py <패치파일>"""
import json,sys,os,glob,datetime
BASE=os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
ALLOW={"verdict","reason","conditions","alternatives","where_to_check","laws","precedents","source_urls","source_dates","notes"}
patch={}
for l in open(sys.argv[1],encoding="utf-8"):
    if l.strip(): x=json.loads(l); patch[x["faq_id"].upper()]=x.get("edits",[])
today=datetime.date.today().isoformat(); logs=[]; n=0
for fp in sorted(glob.glob(f"{BASE}/raw/*_faq.jsonl")):
    rows=[json.loads(l) for l in open(fp,encoding="utf-8") if l.strip()]
    for r in rows:
        for e in patch.get(r["faq_id"].upper(),[]):
            f=e.get("field")
            if f not in ALLOW or r.get(f,"")==e["after"]: continue
            logs.append({"date":today,"case":r["faq_id"],"field":f,"before":r.get(f,""),"after":e["after"],"reason":"FAQ 확인 필요 재판정(새 법령 원문)"+(" [확인 조항: "+e["laws_checked"]+"]" if e.get("laws_checked") else ""),"source_url":"law_src"})
            r[f]=e["after"]; n+=1
    with open(fp+".tmp","w",encoding="utf-8") as w:
        for r in rows: w.write(json.dumps(r,ensure_ascii=False)+"\n")
    os.replace(fp+".tmp",fp)
with open(f"{BASE}/raw/수정기록.jsonl","a",encoding="utf-8") as w:
    for l in logs: w.write(json.dumps(l,ensure_ascii=False)+"\n")
print("FAQ 수정",n)
