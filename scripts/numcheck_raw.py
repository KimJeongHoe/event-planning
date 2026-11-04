#!/usr/bin/env python3
"""의심 숫자를 원문 HTML 전체(태그만 제거)에서 다시 찾기. 사용: numcheck_raw.py <tsv>"""
import json,sys,os,re,subprocess,glob
BASE=os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
rows={}
for fp in glob.glob(f"{BASE}/raw/*.jsonl"):
    if "수정기록" in fp or fp.endswith("_faq.jsonl"): continue
    for l in open(fp,encoding="utf-8"):
        r=json.loads(l); rows[r["id"]]=r
Z=str.maketrans("０１２３４５６７８９，","0123456789,")
for line in open(sys.argv[1],encoding="utf-8").read().splitlines()[1:]:
    cid,_,miss=line.split("\t"); r=rows[cid]; t=""
    for u in r["source_urls"].split("|"):
        u=u.strip()
        if u.startswith("http"):
            h=subprocess.run(["curl","-sL","-m","30","-A","Mozilla/5.0",u],capture_output=True).stdout.decode("utf-8","ignore")
            t+=re.sub(r"<[^>]+>"," ",h)
    t=t.translate(Z); t2=t.replace(",","")
    res=[]
    for m in miss.split("; "):
        f,n=m.split(":",1); x=n.replace(",","")
        cands={n,x}
        if x.isdigit():
            i=int(x)
            if 1000<=i<100000 and i%1000: cands.add(f"{i//1000}천{i%1000}")
            if 1000<=i<100000 and i%1000==0: cands.add(f"{i//1000}천")
            if 100<=i<1000: cands.add(f"{i//100}백{i%100 or ''}")
            if 1900<=i<=2029: cands.add(f"{str(i)[2:]}년"); cands.add(f"'{str(i)[2:]}")
            if i>=10000: cands.add(f"{i//10000}만{(str(i%10000)) if i%10000 else ''}")
        ok=any(c in t or c in t2 for c in cands)
        res.append(f"{m}={'있음' if ok else '없음'}")
    print(cid,len(t),"; ".join(res))
