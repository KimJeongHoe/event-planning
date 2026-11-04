#!/usr/bin/env python3
"""국가법령정보센터(law.go.kr)에서 법령·행정규칙 본문을 받아 텍스트로 저장.
사용: python3 -I lawfetch.py <출력폴더> <법령|행정규칙|자치법규> <이름> [<이름>...]  (자치법규는 정확한 조례 이름 필요, 예: "서울특별시 옥외광고물 등의 관리와 옥외광고산업 진흥에 관한 조례")
결과: <출력폴더>/<이름>.txt (첫 줄: 원문 URL / 시행일 정보)"""
import sys, re, html, urllib.parse, subprocess, os
def get(url):
    return subprocess.run(["curl","-s","-m","40","-A","Mozilla/5.0",url],capture_output=True).stdout.decode("utf-8","ignore")
def text(h):
    h=re.sub(r'<script.*?</script>','',h,flags=re.S); h=re.sub(r'<style.*?</style>','',h,flags=re.S)
    h=re.sub(r'<(br|/p|/div|/li|/tr)[^>]*>','\n',h,flags=re.I); h=re.sub(r'<[^>]+>',' ',h)
    h=html.unescape(h); h=re.sub(r'[ \t ]+',' ',h); h=re.sub(r'\n\s*\n+','\n',h); return h.strip()
out, kind, names = sys.argv[1], sys.argv[2], sys.argv[3:]
os.makedirs(out, exist_ok=True)
for n in names:
    page=f"https://www.law.go.kr/{urllib.parse.quote(kind)}/{urllib.parse.quote(n)}"
    h=get(page)
    m=re.search(r'src="(/LSW//(lsInfoP|admRulInfoP|ordinInfoP)\.do\?[^"]+)"',h)
    if not m: print("실패(목록 없음):",n); continue
    src=html.unescape(m.group(1))
    body_url="https://www.law.go.kr"+src.replace("lsInfoP","lsInfoR").replace("urlMode=lsInfoP","urlMode=lsInfoR").replace("admRulInfoP","admRulInfoR").replace("ordinInfoP","ordinInfoR")
    t=text(get(body_url))
    if len(t)<500: print("본문 짧음:",n,len(t))
    open(f"{out}/{n.replace('/','_')}.txt","w",encoding="utf-8").write(f"원문: {page}\n본문: {body_url}\n\n{t}")
    print("저장:",n,len(t), t[:120].replace("\n"," "))
