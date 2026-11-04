#!/usr/bin/env python3
"""확인함 사례의 숫자가 원문 본문에 있는지 자동 점검(의심 목록만 출력, 고치지 않음).
사용: numcheck.py <접두어,...> [출력tsv]"""
import json, sys, os, re, hashlib, subprocess
BASE=os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
pre=set(sys.argv[1].split(","))
out=sys.argv[2] if len(sys.argv)>2 else None
Z=str.maketrans("０１２３４５６７８９，","0123456789,")
def text(u):
    fn=f"{BASE}/src_cache/{hashlib.md5(u.encode()).hexdigest()[:12]}.txt"
    if not os.path.exists(fn):
        subprocess.run([sys.executable,"-I",f"{BASE}/scripts/fetchtext.py",u,"0",f"{BASE}/src_cache"],capture_output=True)
    return open(fn,encoding="utf-8",errors="ignore").read() if os.path.exists(fn) else ""
def variants(n):
    v={n}; x=n.replace(",","")
    v.add(x)
    try:
        i=int(x)
        v.add(f"{i:,}")
        if i>=10000 and i%10000==0: v.add(f"{i//10000}万"); v.add(f"{i//10000}만")
    except: pass
    return v
rows=[]
for fn in sorted(os.listdir(f"{BASE}/raw")):
    if not fn.endswith(".jsonl") or fn.split(".")[0] not in pre: continue
    for l in open(f"{BASE}/raw/{fn}",encoding="utf-8"):
        r=json.loads(l)
        if r.get("kind")!="실제": continue
        t="".join(text(u.strip()) for u in str(r.get("source_urls","")).split("|") if u.strip().startswith("http")).translate(Z)
        t2=t.replace(",","")
        miss=[]
        for f in (os.environ.get("NUMCHECK_FIELDS","summary,condition,benefit,limit,duration,known_result").split(",")):
            for m in re.finditer(r"\d[\d,]*(?:\.\d+)?",str(r.get(f,""))):
                n=m.group(0).rstrip(",")
                if len(n.replace(",",""))<2: continue
                if not any(v in t or v in t2 for v in variants(n)): miss.append(f"{f}:{n}")
        if miss: rows.append((r["id"],len(t),"; ".join(sorted(set(miss)))))
for x in rows: print("\t".join(map(str,x)))
print(f"의심 {len(rows)}건", file=sys.stderr)
if out: open(out,"w",encoding="utf-8").write("수집ID\t본문길이\t원문에서 못 찾은 숫자\n"+"\n".join("\t".join(map(str,x)) for x in rows))
