#!/usr/bin/env python3
"""출처 주소 점검: 최종 주소의 도메인이 바뀌었는지, 도박·성인 사이트로 넘어갔는지.
사용: urlcheck.py <URL 한 개>  → TSV 한 줄 출력: url, code, final_url, 판정, 이유, 제목"""
import sys,subprocess,re,html
from urllib.parse import urlparse
u=sys.argv[1]
r=subprocess.run(["curl","-sL","--compressed","-m","25","-A","Mozilla/5.0 (Windows NT 10.0; Win64; x64) Chrome/124","-w","\n__E__%{http_code} %{url_effective}",u],capture_output=True)
b,_,e=r.stdout.rpartition(b"\n__E__"); e=e.decode("utf-8","ignore").split(" ",1)
code=e[0] if e and e[0] else "000"; fin=e[1] if len(e)>1 else ""
t=b[:600000].decode("utf-8","ignore")
vis=re.sub(r"<(script|style|noscript|iframe)[^>]*>.*?</\1>"," ",t,flags=re.S|re.I); vis=re.sub(r"<[^>]+>"," ",vis)
title=re.search(r"<title[^>]*>(.*?)</title>",t,re.S|re.I); title=html.unescape(title.group(1).strip())[:80] if title else ""
def reg(h):
    p=(h or "").lower().split(":")[0].split(".")
    if p and p[0]=="www": p=p[1:]
    return ".".join(p[-3:]) if len(p)>=3 and p[-2] in ("co","or","go","ne","ac","re","com","org","gov") else ".".join(p[-2:])
bad=re.compile(r"카지노|바카라|토토사이트|슬롯사이트|파워볼|홀덤사이트|온라인\s*카지노|\bcasino\b|\bbaccarat\b|slot\s*gacor|\bjudi\s+online\b|\btogel\b|\bsportsbook\b|オンラインカジノ|\bporn\b",re.I)
nbad=len(bad.findall(vis)); tbad=bool(bad.search(title))
o=reg(urlparse(u).netloc); f=reg(urlparse(fin).netloc) if fin else o
why=[]
if code!="200": why.append(f"응답{code}")
if fin and f!=o: why.append(f"도메인 바뀜 {o}→{f}")
if tbad or nbad>=3: why.append(f"도박·성인 표현 {nbad}회"+("(제목)" if tbad else ""))
SAME={("abcnews.go.com","abcnews.com")}
moved=bool(fin and f!=o and (o,f) not in SAME and not (o.endswith(f) or f.endswith(o)))
verdict="도박·성인 의심" if (tbad or nbad>=3) else ("내용 바뀜(다른 사이트로 이동)" if (moved and code=="200") else ("막힘" if code!="200" else "정상"))
print("\t".join([u,code,fin,verdict,"; ".join(why),title.replace("\t"," ")]))
