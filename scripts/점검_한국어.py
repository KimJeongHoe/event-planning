#!/usr/bin/env python3
"""판 11: 영어 문장 잡아내기. 진행 글(세션 기록의 어시스턴트 글)과 문서(.md)에서 영어 낱말이 4개 이상 이어진 문장을 찾는다.
코드 블록·`코드`·주소·파일 경로·영문 고유명(도구 이름 표 등 허용 목록)은 뺀다.
사용: python3 -I scripts/점검_한국어.py [--기록 <세션.jsonl> [시작 문구]] [파일·폴더 ...]  → 걸린 줄을 출력하고, 있으면 종료 코드 1"""
import sys,re,json,os,glob
ALLOW=re.compile(r"(Claude|Opus|Sonnet|Co-Authored-By|Claude-Session|noreply@anthropic\.com|Generated with)")
def clean(t):
    t=re.sub(r"```.*?```"," ",t,flags=re.S);t=re.sub(r"`[^`]*`"," ",t);t=re.sub(r"https?://\S+"," ",t)
    t=re.sub(r"[\w./-]+\.(py|js|json|jsonl|md|csv|html|txt|sh)\b"," ",t);t=re.sub(r"\[[^\]]*\]\([^)]*\)"," ",t)
    return t
EN=re.compile(r"(?:\b[A-Za-z][A-Za-z'’-]*\b[ ,]+){3,}\b[A-Za-z][A-Za-z'’-]*\b")
def scan(text,where):
    out=[]
    for ln in clean(text).splitlines():
        if ALLOW.search(ln): continue
        m=EN.search(ln)
        if m and all(w.isupper() and len(w)<=4 for w in re.findall(r"[A-Za-z]+",m.group(0))): continue  # 대문자 약어 목록(접두어 등)은 문장이 아님
        if m and len(m.group(0))>=18: out.append(f"{where}: {ln.strip()[:120]}")
    return out
args=sys.argv[1:];hits=[]
if args[:1]==["--기록"]:
    p=args[1];mark=args[2] if len(args)>2 and not os.path.exists(args[2]) else None;args=args[3 if mark else 2:]
    started=mark is None
    for l in open(p,encoding="utf-8"):
        try:o=json.loads(l)
        except ValueError:continue
        msg=o.get("message") or {}
        if not started and o.get("type")=="user":
            c=msg.get("content");t=c if isinstance(c,str) else " ".join(x.get("text","") for x in c if isinstance(x,dict)) if isinstance(c,list) else ""
            if mark in t: started=True
            continue
        if started and o.get("type")=="assistant":
            for b in msg.get("content") or []:
                if isinstance(b,dict) and b.get("type")=="text": hits+=scan(b["text"],"진행 글")
for a in args:
    fs=[a] if os.path.isfile(a) else glob.glob(os.path.join(a,"**","*.md"),recursive=True)
    for f in fs: hits+=scan(open(f,encoding="utf-8").read(),os.path.relpath(f))
print("\n".join(hits) if hits else "영어 문장 없음");sys.exit(1 if hits else 0)
