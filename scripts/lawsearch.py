#!/usr/bin/env python3
"""국가법령정보센터 법령해석례·판례 검색과 원문 받기.
사용: lawsearch.py find expc|prec "<검색어>" [건수=20]   → 번호·제목 목록(본문 검색)
      lawsearch.py get  expc|prec <번호>                 → law_src/해석례/ 또는 law_src/판례/ 에 저장하고 앞부분 출력
expc = 법령해석례(법제처 해석, 부처 회신 포함), prec = 판례(대법원·하급심)"""
import sys,re,html,subprocess,os
BASE=os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
UA="Mozilla/5.0"
def curl(args): return subprocess.run(["curl","-s","-m","40","-A",UA]+args,capture_output=True).stdout.decode("utf-8","ignore")
def txt(h):
    h=re.sub(r'<(script|style).*?</(script|style)>','',h,flags=re.S); h=re.sub(r'<(br|/p|/div|/li|/tr)[^>]*>','\n',h,flags=re.I)
    h=re.sub(r'<[^>]+>',' ',h); h=html.unescape(h); h=re.sub(r'[ \t\xa0]+',' ',h); return re.sub(r'\n\s*\n+','\n',h).strip()
mode,kind=sys.argv[1],sys.argv[2]
if mode=="find":
    q=sys.argv[3]; n=sys.argv[4] if len(sys.argv)>4 else "20"
    ep={"expc":"expcScListR","prec":"precScListR"}[kind]
    h=curl(["-H","X-Requested-With: XMLHttpRequest","--data-urlencode",f"q={q}","--data",f"outmax={n}&pg=1&section=bdyText",f"https://www.law.go.kr/LSW/{ep}.do"])
    fn={"expc":"expcView","prec":"precView"}[kind]
    seen=set()
    for m in re.finditer(fn+r"\('(\d+)'\)[^>]*>(.*?)</a>",h,re.S):
        i=m.group(1)
        if i in seen: continue
        seen.add(i); print(i, re.sub(r'\s+',' ',txt(m.group(2)))[:220])
    tot=re.search(r'총\s*([\d,]+)\s*건',txt(h)); print("총",tot.group(1) if tot else "?","건")
else:
    i=sys.argv[3]
    url={"expc":f"https://www.law.go.kr/LSW/expcInfoR.do?expcSeq={i}","prec":f"https://www.law.go.kr/LSW/precInfoP.do?precSeq={i}"}[kind]
    t=txt(curl(["-e","https://www.law.go.kr/",url]))
    for k in ["【질의요지】","판시사항","【판시사항】"]:
        j=t.find(k)
        if j>0: t=t[max(0,j-300):]; break
    d=f"{BASE}/law_src/"+{"expc":"해석례","prec":"판례"}[kind]; os.makedirs(d,exist_ok=True)
    title=re.sub(r'[\\/:*?"<>|\n]',' ',t[:80]).strip()
    open(f"{d}/{kind}_{i}.txt","w",encoding="utf-8").write(f"원문: {url}\n\n{t}")
    print("저장:",f"law_src/{os.path.basename(d)}/{kind}_{i}.txt",len(t)); print(t[:1500])
