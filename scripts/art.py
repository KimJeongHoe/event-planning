#!/usr/bin/env python3
"""법령 텍스트에서 조문 뽑기. 사용: art.py <법령파일이름 일부> <조번호(예: 3, 50의2)> [최대글자]"""
import sys, glob, re, os
BASE=os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
fs=[f for f in glob.glob(f"{BASE}/law_src/*.txt") if sys.argv[1] in os.path.basename(f)]
fs.sort(key=lambda f: len(f))
t=open(fs[0],encoding='utf-8').read(); n=sys.argv[2]; n=(n.split('의')[0]+'조의'+n.split('의')[1]).replace('조의','\u0000') if '의' in n else n+'\u0001'; mx=int(sys.argv[3]) if len(sys.argv)>3 else 2500
print('##',os.path.basename(fs[0]))
pat=('제'+n.replace('\u0000','조의')+'\\(') if '\u0000' in n else ('제'+n[:-1]+'조\\(')
m=re.search(r'(?m)^\s*'+pat,t) or re.search(r'(?m)(^|\s)'+pat,t)
if not m: print('없음'); sys.exit()
s=m.start(); nxt=re.search(r'\s제\d+조(의\d+)?\(',t[s+5:])
print(t[s: s+5+(nxt.start() if nxt else mx)][:mx])
