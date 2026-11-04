#!/usr/bin/env python3
"""같은 주소가 다른 기사로 바뀌었는지 점검(제목·날짜·사례 낱말).
사용: samecheck.py <현재본문폴더> <출력tsv>   (현재 본문은 fetchtext.py로 <현재본문폴더>/<md5>.txt 에 저장돼 있어야 함)"""
import json,sys,os,re,hashlib
BASE=os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
cur,out=sys.argv[1],sys.argv[2]
rows=[json.loads(l) for l in open(f"{BASE}/merged/사례DB.jsonl",encoding="utf-8")]
def md5(u): return hashlib.md5(u.encode()).hexdigest()[:12]
def load(p):
    if not os.path.exists(p): return None
    t=open(p,encoding="utf-8",errors="ignore").read(); return t
def title(t):
    m=re.search(r"^TITLE (.*)$",t,re.M); return (m.group(1).strip() if m else "")
def toks(s):
    return {w for w in re.findall(r"[가-힣]{2,}|[A-Za-z]{4,}|\d[\d,.]{2,}",s) if w not in ("사례","행사","할인","무료","제공","손님","가게","원문","기사")}
def years(t): return set(re.findall(r"(?<!\d)(19[89]\d|20[0-2]\d)(?!\d)",t[:4000]))
res=[]
for r in rows:
    if r["kind"]!="실제": continue
    ks=toks(r["name"]+" "+r["summary"]+" "+r["benefit"])
    for u in [x.strip() for x in r["source_urls"].split("|") if x.strip().startswith("http")]:
        c=load(f"{cur}/{md5(u)}.txt"); old=load(f"{BASE}/src_cache/{md5(u)}.txt")
        if not c or "CODE 200" not in c[:300]: continue
        body=c.split("\n",2)[-1]
        cov=len([k for k in ks if k in body])/max(len(ks),1)
        tt=title(c); tin=None
        if old and tt:
            core=re.split(r"\s[|\-–:]\s",tt)[0][:30]
            tin=core in old
        sy=set(re.findall(r"(19[89]\d|20[0-2]\d)",r["source_dates"]))
        ym=bool(sy) and not (sy & years(body))
        flag=[]
        if cov<0.2: flag.append(f"사례 낱말 {cov:.0%}만 남음")
        if tin is False: flag.append("처음 받은 원문에 지금 제목 없음")
        if ym and cov<0.5: flag.append(f"출처날짜 연도 {','.join(sorted(sy))} 본문에 없음")
        if flag: res.append((r["orig_id"],r["verify_status"],u,tt[:80],f"{cov:.2f}","; ".join(flag)))
with open(out,"w",encoding="utf-8") as w:
    w.write("수집ID\t원문확인\t주소\t지금 제목\t사례낱말비율\t의심 이유\n")
    for x in res: w.write("\t".join(x)+"\n")
print("의심",len(res))
