#!/usr/bin/env python3
"""원문 확인용 묶음 만들기: 실제 사례마다 사례 내용 + 출처 원문 발췌.
사용: build_packets.py <캐시폴더> <출력폴더> <묶음수>"""
import json, sys, os, re, hashlib, csv
BASE=os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
cache, out, n = sys.argv[1], sys.argv[2], int(sys.argv[3])
os.makedirs(out, exist_ok=True)
status={}
for l in open(f"{cache}/status.tsv",encoding="utf-8"):
    p=l.rstrip("\n").split("\t")
    if len(p)>=2:
        m=re.match(r"CODE (\d+)",p[1]); status[p[0]]=m.group(1) if m else "000"
rows=[json.loads(l) for l in open(f"{BASE}/merged/사례DB.jsonl",encoding="utf-8")]
rows=[r for r in rows if r["kind"]=="실제" and r["verify_status"]!="확인함"]
def excerpt(t, r, mx=3500):
    body=t.split("\n\n",1)[-1]
    lines=[x.strip() for x in body.split("\n") if len(x.strip())>25]
    keys=set(re.findall(r"[가-힣A-Za-z]{2,}|\d[\d,.]*",(r["name"]+" "+r["summary"]+" "+r["benefit"]+" "+r["known_result"])))
    keys={k for k in keys if len(k)>=2}
    scored=[(sum(1 for k in keys if k in x),i,x) for i,x in enumerate(lines)]
    top=sorted([s for s in scored if s[0]>0],key=lambda s:-s[0])[:40]
    pick=sorted(top,key=lambda s:s[1])
    txt="\n".join(x for _,_,x in pick)
    return txt[:mx], len(body)
packs=[[] for _ in range(n)]
for i,r in enumerate(rows):
    srcs=[]
    for u in [x.strip() for x in str(r["source_urls"]).split("|") if x.strip()][:3]:
        fn=f"{cache}/{hashlib.md5(u.encode()).hexdigest()[:12]}.txt"
        code=status.get(u,"미시도")
        if os.path.exists(fn):
            ex,ln=excerpt(open(fn,encoding="utf-8").read(),r)
        else: ex,ln="",0
        srcs.append({"url":u,"code":code,"본문길이":ln,"발췌":ex})
    case={k:r[k] for k in ["id","orig_id","name","summary","condition","benefit","staging","duration","limit","known_result","source_dates","country","era","sub_industry","scale","notes"]}
    packs[i%n].append({"case":case,"sources":srcs})
for j,p in enumerate(packs):
    with open(f"{out}/packet_{j+1:02d}.jsonl","w",encoding="utf-8") as w:
        for x in p: w.write(json.dumps(x,ensure_ascii=False)+"\n")
    print(j+1,len(p),os.path.getsize(f"{out}/packet_{j+1:02d}.jsonl"))
