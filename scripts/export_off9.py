#!/usr/bin/env python3
"""판 9: 꺼 둔 기능의 자료를 받을 도구가 쓸 파일로 내보냄.
- 배달 실수령 도구 → merged/다른도구용/배달실수령용_행사근거.json
- 개업 D-데이 순서표 도구 → merged/다른도구용/개업순서표용_행사항목.json
사용: python3 -I scripts/export_off9.py"""
import json,re,os,datetime
B=os.path.dirname(os.path.dirname(os.path.abspath(__file__)));O=f"{B}/merged/다른도구용";os.makedirs(O,exist_ok=True)
LAW={x["key"]:x for x in json.load(open(f"{B}/spec/법근거_판8.json",encoding="utf-8"))["items"]}
FAQ={}
import csv
for r in csv.DictReader(open(f"{B}/merged/FAQ.csv",encoding="utf-8-sig")):
    k=next((v for kk,v in r.items() if kk and kk.strip() in ("번호","id","FAQ번호")),None)
    if k: FAQ[k]=r
P=open(f"{B}/preview/plus7.js",encoding="utf-8").read()
law=lambda ks:[{k:LAW[x].get(k) for k in ("key","law","art","gist","status","note","file")} for x in ks if x in LAW]
faq=lambda ids:[FAQ.get(i,{"번호":i,"메모":"FAQ.csv에서 찾지 못함"}) for i in ids]
today=datetime.date.today().isoformat()
# 1) 배달 실수령
m=re.search(r'계산식: (.*?)</p>',P[P.index("RENDER.deliv"):]);
d={"종류":"행사도구_배달근거","기준일":today,"출처":"사장님 행사안 고르기(판 9에서 꺼 둔 「배달앱 할인 실수령」 기능)",
 "설명":"행사 도구에서 배달앱 할인 실수령 계산을 꺼 두고, 계산식·입력 칸·법 근거·FAQ를 배달 실수령 도구에 넘김. 요율 값은 넣지 않음(사장님 입력).",
 "계산식":re.sub(r"<[^>]+>","",m.group(1)) if m else "",
 "입력칸":["주문 금액(할인 전, 원)","사장님이 내는 할인(원)","앱이 내 주는 할인(원)","중개 수수료율(%)","결제 수수료율(%)","배달비 사장님 부담(원)","수수료 기준(할인 뒤 금액|할인 전 금액)","수수료·배달비 부가세 10%(더함|안 더함)","원가(원)"],
 "법근거":law(["술광고","술광고_주체","리뷰_배달앱정책","리뷰_배달앱정책_쿠팡이츠요기요","후기_공개","후기_표시법"]),"FAQ":faq(["F037","F041","F075"])}
json.dump(d,open(f"{O}/배달실수령용_행사근거.json","w",encoding="utf-8"),ensure_ascii=False,indent=1)
# 2) 개업 순서표
seg=P[P.index("const R=[[-30"):];seg=seg[:seg.index("]];")+3]
rows=[]
for mm in re.finditer(r'\[(-?\d+),"([^"]*)",(?:"([^"]*)"|[^\]]*?),"([a-z]*)"\]',seg):
    rows.append({"D":int(mm.group(1)),"할일":mm.group(2),"메모":mm.group(3) or "","도구":mm.group(4) or ""})
html=open(f"{B}/preview/행사안_미리보기.html",encoding="utf-8").read();mi=re.search(r'\{"link":',html);D=json.loads(html[mi.start():html.index("\n",mi.start())].rstrip(";"))
prep={}
for c in D["cases"]:
    if c.get("kd")=="준비·절차":
        for i in c["ind"].split("|"):
            if i: prep.setdefault(i,[]).append({"번호":c["i"],"이름":c["n"]})
o={"종류":"행사도구_개업항목","기준일":today,"출처":"사장님 행사안 고르기(판 9에서 꺼 둔 「개업 행사 한 묶음」 기능)",
 "설명":"개업일(D-day) 기준 행사 쪽 할 일 줄과, 업종별 준비·절차 사례 번호, 개업 행사에서 자주 걸리는 법 근거. 날짜·공휴일 겹침은 캘린더 도구 자료로 계산할 것.",
 "할일":rows,"업종별_준비절차_사례":{k:v[:12] for k,v in prep.items()},"법근거":law(["문자_동의","후기_공개","술광고","경품고시폐지"]),
 "업종별_주의":[{"업종":s["이름"],"화면업종":s["ind"],"막을행사":s.get("막을행사",[]),"바꿀행사":s.get("바꿀행사",[]),"법근거키":s.get("법",[])} for s in json.load(open(f"{B}/spec/업종_판8.json",encoding="utf-8"))["세부"]]}
json.dump(o,open(f"{O}/개업순서표용_행사항목.json","w",encoding="utf-8"),ensure_ascii=False,indent=1)
print("배달: 법근거",len(d["법근거"]),"FAQ",len(d["FAQ"]),"계산식",bool(d["계산식"]),"/ 개업: 할일",len(rows),"업종 준비 사례",len(prep),"업종 주의",len(o["업종별_주의"]))
