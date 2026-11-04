#!/usr/bin/env python3
"""URL 원문을 받아 본문 텍스트로 저장·출력. 사용: fetchtext.py <url> [최대글자] [저장폴더]
출력 첫 줄: HTTP 코드, 최종 URL"""
import sys, subprocess, re, html, hashlib, os
url=sys.argv[1]; mx=int(sys.argv[2]) if len(sys.argv)>2 else 3000
r=subprocess.run(["curl","-sL","--compressed","-m","30","-A","Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 Chrome/124 Safari/537.36","-H","Accept-Language: ko,en;q=0.8,ja;q=0.6","-w","\n__CODE__%{http_code} %{url_effective}",url],capture_output=True)
raw=r.stdout; tail=raw.rsplit(b"\n__CODE__",1); body=tail[0]; code=tail[1].decode() if len(tail)>1 else "000"
m=re.search(rb'charset=["\']?([\w-]+)',body[:3000]); enc=(m.group(1).decode() if m else 'utf-8')
try: h=body.decode(enc,'ignore')
except Exception: h=body.decode('utf-8','ignore')
title=re.search(r'<title[^>]*>(.*?)</title>',h,re.S|re.I)
h=re.sub(r'<(script|style|noscript|svg)[^>]*>.*?</\1>','',h,flags=re.S|re.I)
h=re.sub(r'<(br|/p|/div|/li|/h\d|/tr)[^>]*>','\n',h,flags=re.I); h=re.sub(r'<[^>]+>',' ',h)
h=html.unescape(h); h=re.sub(r'[ \t ]+',' ',h); h=re.sub(r'\n\s*\n+','\n',h).strip()
print("CODE",code); print("TITLE",html.unescape(title.group(1).strip()) if title else "")
if len(sys.argv)>3:
    os.makedirs(sys.argv[3],exist_ok=True); fn=hashlib.md5(url.encode()).hexdigest()[:12]
    open(f"{sys.argv[3]}/{fn}.txt","w",encoding="utf-8").write(f"URL {url}\nCODE {code}\n\n{h}")
print(h[:mx])
