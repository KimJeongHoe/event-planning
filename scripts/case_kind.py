#!/usr/bin/env python3
"""사례 파생 속성(원본 raw는 고치지 않음, build_preview.py가 씀)
① 혜택 받는 손님(who): 일반 손님 / 입점·가맹·임차 / 거래처 / 구직자 / 이웃·기관
   - 혜택 칸 앞 괄호 표시를 먼저 본다: (사업자 측)(점주)(양수인)·가맹점주·입주민=입점·가맹·임차, (기부)(기증)(후원)(수혜)=이웃·기관
   - 낱말: 공유주방·입점 업체 모집=입점 업체, 혜택·조건·대상 칸의 거래처·납품처·B2B=거래처, 이름의 구인·채용=구직자
② 사례 종류(kd): 행사 / 안내·참고(공지·회고·현상) / 준비·절차 / 주의 사례
   - 주의 사례: 혜택 칸이 처분·논란 설명(해당없음(공정위 시정…), (위험 사례))이거나, 이름이 ⚠로 시작하고 과태료·과징금·시정·적발·단속·철회·벌금이 있는 것
   - 준비·절차: 이름·요약에 제도·등록·지정·신고·허가·인증·점검이 있고 혜택 칸에 할인·무료·증정·쿠폰·적립 같은 혜택 낱말이 없는 것(예: 반려동물 동반 업소 등록)
   - 혜택이 없어도 성격이 오픈·홍보형·N주년·리뉴얼이면 행사(개업 연출·공연 등)
   - 안내·참고: 혜택이 해당없음·(혜택 없음)·(손님 혜택 없음)인 나머지(휴무·가격 인상 공지 등)
   - 행사: 나머지"""
import re
TEN=re.compile(r"공유주방|공유 주방|공유오피스|입점 ?(업체|사|자|셀러) ?(모집|지원|혜택)|입점업체|점주 모집|가맹점 모집|가맹 모집|창업자 모집|예비 창업자")
B2B=re.compile(r"거래처|납품(업체|처)|도매 ?고객|기업 고객|B2B|사업자 고객")
OFFER=re.compile(r"할인|무료|증정|쿠폰|적립|서비스|1\+1|%|사은|경품|추가 제공|업그레이드")
PROC=re.compile(r"제도|등록|업소 지정|지정 업소|신고|허가|의무화|법 시행|규제|실증제")
ENF=re.compile(r"과태료|과징금|시정|적발|단속|철회|벌금|처분|고발|제재|영업정지|권고")
def lead(b):
    m=re.match(r"^\(([^)]{1,30})\)",b); return m.group(1) if m else ""
def who(r):
    b=r["benefit"]; L=lead(b); t=" ".join([r["name"],r["summary"]])
    if L in ("사업자 측","점주","양수인") or TEN.search(t) or re.search(r"가맹점주|입주민|입점",r["benefit"]+" "+r["target"]): return "입점·가맹·임차"
    if B2B.search(" ".join([r["benefit"],r["condition"],r["target"]])): return "거래처"
    if re.search(r"구인 ?(공고|광고|POP|간판|글|문구)|구함|직원 모집|알바 모집|아르바이트 모집|채용 공고|수료 후 채용",r["name"]) and not re.search(r"휴무|휴업",r["name"]): return "구직자"
    if L in ("기부","기증","후원","수혜"): return "이웃·기관"
    return "일반 손님"
def kind(r):
    b=r["benefit"].strip(); L=lead(b); n=r["name"]; t=n+" "+r["summary"]
    if L=="위험 사례" or (b.startswith("해당없음(") and ENF.search(b[:40])) or (n.startswith("⚠") and ENF.search(n)): return "주의 사례"
    if PROC.search(t) and not OFFER.search(b) and not re.search(r"\d[\d,]*\s?원",b): return "준비·절차"
    if L in ("쟁점","실패","역방향","논란"): return "안내·참고"   # 분쟁·실패 이야기는 행사로 권하지 않음
    if re.search(r"오픈행사|홍보형행사|N주년|리뉴얼·신메뉴",r["nature"]): return "행사"   # 혜택이 없어도 개업 연출·홍보는 행사
    if re.match(r"^(해당없음|해당 없음|없음)",b) or L in ("혜택 없음","손님 혜택 없음","손님 혜택 아님","행사 혜택 없음","별도 혜택 없음","가게가 주는 혜택 없음","경제적 혜택 없음","구체 혜택 없음"): return "안내·참고"
    return "행사"
if __name__=="__main__":
    import pandas as pd
    d=pd.read_json("merged/사례DB.jsonl",lines=True,dtype=str).fillna("")
    d["who"]=d.apply(who,axis=1); d["kd"]=d.apply(kind,axis=1)
    print(d.who.value_counts().to_dict()); print(d.kd.value_counts().to_dict())
    for w in ["입점·가맹·임차","거래처","구직자"]: print("##",w,d[d.who==w]["name"].str[:40].tolist()[:8])
    for k in ["준비·절차","주의 사례","안내·참고"]: print("##",k,d[d.kd==k]["name"].str[:40].tolist()[:8])
