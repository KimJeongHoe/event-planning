#!/usr/bin/env python3
"""공식 판단 대기 목록: 공식 해석 원문이 없는 FAQ 쟁점과 FAQ에 안 묶인 적용 해석 사례를 한 표로. 기관은 질문·근거 낱말로 자동 분류(대략).
출력 merged/다른도구용/공식판단_대기목록.csv, docs/공식판단_대기목록.md (merge.py 뒤에 실행)"""
import pandas as pd, re, csv, os
B=os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
f=pd.read_csv(f"{B}/merged/FAQ.csv",dtype=str).fillna("")
d=pd.read_json(f"{B}/merged/사례DB.jsonl",lines=True,dtype=str).fillna("")
AG=[("선관위","선거|투표","선거법규포털 law.nec.go.kr 질의회답(이 환경에서 막힘) 또는 관할 선관위 서면 질의"),
("국세청","주류|소주|맥주|술","국세법령정보시스템 taxlaw.nts.go.kr 질의회신(막힘)·관할 세무서 소비세과"),
("인권위·복지부(장애·차별)","장애|차별|키오스크|무인정보|보조견|노키즈|시니어|휠체어","국가인권위원회 결정례(막힘)·보건복지부 장애인권익지원과"),
("개인정보위","개인정보|전화번호|CCTV|동의","개인정보보호위원회 법령해석·의결문"),
("복지부(의료·약국)","의료|환자|약국|약사","국가법령정보센터 법령해석례·보건복지부 질의"),
("식약처","식품|시식|위생|영업신고|조리","식품안전나라 민원 질의응답"),
("교육청","학원|교습","시·도교육청 학원 업무 매뉴얼·질의"),
("고용노동부","구인|채용|연령|근로|알바","고용노동부 행정해석/질의회시 메뉴·1350"),
("문체부","도서|출판|저작|음악|공연","문체부 출판인쇄독서진흥과·한국저작권위원회 상담"),
("행안부·지자체","기부|모금|도로|점용|옥외광고|조례|소음","1365 기부포털·관할 시군구 담당과"),
("소방청","소방|피난|화재","관할 소방서 예방과"),
("환경부","일회용|1회용|컵","기후에너지환경부·시군구 자원순환과"),
("공정위","경품|표시|광고|약관|가맹|담합|사업자단체|할인","공정위 의결서·해석(ftc.go.kr 막힘)")]
def agency(t):
    for a,p,w in AG:
        if re.search(p,t): return a,w
    return "기타","법제처 법령해석례·관할 부처 질의"
import json
FIX=json.load(open(f"{B}/spec/FAQ_기관.json",encoding="utf-8"))
WHERE={"공정위":"공정위 의결서·해석(ftc.go.kr 막힘)","국세청":"국세법령정보시스템 질의회신(막힘)·관할 세무서","인권위":"국가인권위원회 결정례(막힘)","개인정보위":"개인정보보호위원회 법령해석·의결문","선관위":"선거법규포털(막힘)·관할 선관위 서면 질의","금융위":"금융규제·법령해석포털 better.fsc.go.kr","식약처":"식품안전나라 민원 질의응답","경찰청":"관할 시·도경찰청(사행행위 영업 허가)","고용노동부":"고용노동부 행정해석/질의회시·1350","문체부":"문체부 담당과·한국저작권위원회","복지부":"보건복지부 담당과·국가법령정보센터 해석례","교육":"시·도교육청","소방청":"관할 소방서 예방과","기후에너지환경부":"기후에너지환경부·시군구 자원순환과","특허청":"특허청 상표 상담","행안부":"관할 시군구","국토부":"관할 시군구 도로과","기재부":"복권위원회","권익위":"국민권익위원회(막힘)","건강증진":"보건복지부 건강증진과·한국건강증진개발원(주류광고 해석)"}
def where(a):
    for k,v in WHERE.items():
        if k in a: return v
    return "관할 부처 질의"
rows=[]
pend=f[f["근거수준"].str.contains("공식 해석 원문 없음")]
for _,r in pend.iterrows():
    fid=r["FAQ번호"]
    cs=d[d.faq_ids.str.contains(fid)]
    open_cs=cs[cs.legal_todo!=""]
    a,w=(FIX[fid],where(FIX[fid])) if fid in FIX else agency(r["질문"]+" "+r["이유와근거"][:300])
    rows.append(["FAQ",fid,r["질문"],r["진행여부"],r["근거수준"],len(cs),len(open_cs),a,w,"FAQ "+fid+" 이유·조건·비고, 연결 사례 법 칸(안전운영조건)", "|".join(cs.orig_id.head(30))])
un=d[(d.legal_todo=="적용 해석") & ~d.legal_risk.str.contains(r"안전한 운영[^\]]*\(F0\d\d\)",regex=True)]
for _,r in un.iterrows():
    a,w=agency(r["name"]+" "+r["legal_risk"][:400])
    rows.append(["사례(FAQ 없음)",r["orig_id"],r["name"],"조건부(사례별 안전운영조건)",r["evidence_level"],1,1,a,w,"사례 법 칸","" ])
H=["구분","번호","쟁점·질문","진행여부","근거수준","연결 사례 수","사유 남은 사례 수","판단할 기관","받을 곳","공식 자료가 나오면 고칠 곳","연결 사례(앞 30개)"]
df=pd.DataFrame(rows,columns=H)
WT={"확인 필요":2,"조건부 가능":1,"불가":1}
df["우선점수"]=df.apply(lambda r:r["사유 남은 사례 수"]*WT.get(str(r["진행여부"]),1),axis=1)
df=df.sort_values(["구분","우선점수"],ascending=[True,False])
df.insert(0,"우선순위",range(1,len(df)+1))
QDOC={"F066":"docs/질의문안_투표인증할인.md","F051":"docs/질의문안_주류명목가.md","F067":"docs/질의문안_QR웹주문_의무자.md","F075":"docs/질의문안_술광고표시.md","F026":"docs/질의문안_선불권회수권_환불.md","F059":"docs/질의문안_손님제한_특정할인_차별.md"}
df["질의 문안"]=df["번호"].map(lambda x:QDOC.get(x,""))
for c in df.columns:
    df[c]=df[c].map(lambda v:("'"+v) if isinstance(v,str) and v[:1] in ("=","+","-","@") else v)
df.to_csv(f"{B}/merged/다른도구용/공식판단_대기목록.csv",index=False,encoding="utf-8-sig",quoting=csv.QUOTE_ALL)
L=["# 공식 판단 대기 목록 (merge 때마다 다시 만듦)","",f"**공식 판단 대기: FAQ 전체 {len(f)}문항 중 {len(pend)}문항(공식 해석 원문이 없는 문항), 사례 전체 {len(d):,}건 중 FAQ에 묶이지 않은 적용 해석 사례 {len(un)}건.** 아래 '사유 남은 사례 수'는 사례 전체 {len(d):,}건 중 법확인필요사유가 남은 건수이고 한 사례가 여러 FAQ에 걸리면 여러 번 셈. FAQ 기관은 사람이 지정(spec/FAQ_기관.json), FAQ 없는 사례만 낱말 자동 분류. 기관별로 공식 자료가 나오면 '고칠 곳'을 고친다.","","## 기관별 요약","",f"| 판단할 기관 | FAQ 수(대기 {len(pend)}문항 중) | 사유 남은 사례 수(중복 포함) | 우선점수 합 | 받을 곳 |","|---|---|---|---|---|"]
g=df.groupby("판단할 기관").agg(FAQ=("구분",lambda s:(s=="FAQ").sum()),사례=("사유 남은 사례 수","sum"),점수=("우선점수","sum"),곳=("받을 곳","first")).sort_values("점수",ascending=False)
for k,r in g.iterrows(): L.append(f"| {k} | {r.FAQ} | {r['사례']} | {r['점수']} | {r['곳']} |")
L+=["","## FAQ별(우선순위 순) — 우선점수 = 사유 남은 사례 수 × 가중치(확인 필요 2, 조건부 가능 1, 불가 1: 불가는 이미 '하지 마세요'로 정해져 공식 판단이 덜 급함)","","| 순위 | 번호 | 질문 | 진행여부 | 사유 남은 사례 | 점수 | 기관 | 질의 문안 |","|---|---|---|---|---|---|---|---|"]
for _,r in df[df["구분"]=="FAQ"].iterrows(): L.append(f"| {r['우선순위']} | {r['번호']} | {r['쟁점·질문'][:55]} | {r['진행여부']} | {r['사유 남은 사례 수']} | {r['우선점수']} | {r['판단할 기관']} | {r['질의 문안']} |")
open(f"{B}/docs/공식판단_대기목록.md","w").write("\n".join(L)+"\n")
print("FAQ",len(pend),"사례",len(un))
