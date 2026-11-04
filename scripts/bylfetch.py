#!/usr/bin/env python3
"""국가법령정보센터 별표·서식 PDF 받기 → 텍스트 저장.
사용: bylfetch.py list <law_src 파일이름 일부>            # 받을 수 있는 별표 목록
      bylfetch.py get  <law_src 파일이름 일부> <별표번호...> # 예: get "식품위생법 시행규칙" 14 17
결과: law_src/별표/<법령>__별표<N>.txt (첫 줄: 원문 PDF 주소, 본문 주소, 제목·개정일)"""
import sys,os,re,glob,html,subprocess,tempfile
BASE=os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
UA="Mozilla/5.0 (Windows NT 10.0; Win64; x64) Chrome/124"
def curl(url,out=None,ref="https://www.law.go.kr/"):
    a=["curl","-s","-L","-m","60","-A",UA,"-e",ref]+(["-o",out] if out else [])+[url]
    r=subprocess.run(a,capture_output=True); return r.stdout.decode("utf-8","ignore") if not out else None
mode,key=sys.argv[1],sys.argv[2]; want=sys.argv[3:]
fs=sorted([f for f in glob.glob(f"{BASE}/law_src/*.txt") if key in os.path.basename(f)],key=len)
if not fs: sys.exit("law_src에 없음: "+key)
src=fs[0]; lawname=os.path.basename(src)[:-4]
body=open(src,encoding="utf-8").readline() and open(src,encoding="utf-8").read().splitlines()[1].replace("본문: ","").strip()
h=curl(body)
items=[]
for m in re.finditer(r"\[(별표|서식)\s*([0-9]+(?:의[0-9]+)?)\]\s*([^<]{0,200})",h):
    kind,no,title=m.groups(); seg=h[m.end():m.end()+1500]
    nxt=re.search(r"\[(별표|서식)\s*[0-9]",seg)
    if nxt: seg=seg[:nxt.start()]
    links=dict((alt,(fl,cd)) for fl,cd,alt in re.findall(r'flDownload\.do\?(?:gubun=&amp;)?flSeq=(\d+)(?:&amp;flNm=[^&"]*)?&amp;bylClsCd=(\d+)"[^>]*>\s*<img[^>]*?alt="([^"]+)"',seg))
    pdf=next(((fl,cd) for alt,(fl,cd) in links.items() if "PDF" in alt),None)
    if kind=="별표" and not any(i[1]==no for i in items):
        items.append((kind,no,html.unescape(title).strip(),pdf))
if mode=="list":
    for k,no,t,p in items: print(f"{lawname}\t별표 {no}\t{t}\t"+(f"https://www.law.go.kr/LSW/flDownload.do?gubun=&flSeq={p[0]}&bylClsCd={p[1]}" if p else "PDF 없음"))
    sys.exit()
for k,no,t,p in items:
    if want and no not in want: continue
    if not p: print("PDF 없음:",lawname,no); continue
    url=f"https://www.law.go.kr/LSW/flDownload.do?gubun=&flSeq={p[0]}&bylClsCd={p[1]}"
    d=tempfile.mkdtemp(); pdf=f"{d}/a.pdf"; curl(url,pdf,ref=body)
    if not open(pdf,"rb").read(5).startswith(b"%PDF"): print("받기 실패(PDF 아님):",lawname,no); continue
    subprocess.run(["pdftotext","-layout",pdf,f"{d}/a.txt"])
    txt=open(f"{d}/a.txt",encoding="utf-8",errors="ignore").read()
    out=f"{BASE}/law_src/별표/{lawname}__별표{no}.txt"
    open(out,"w",encoding="utf-8").write(f"원문PDF: {url}\n본문: {body}\n제목: [별표 {no}] {t}\n\n{txt}")
    print("저장:",os.path.basename(out),len(txt),txt.strip().splitlines()[0][:80] if txt.strip() else "(텍스트 없음 — 이미지 PDF일 수 있음)")
