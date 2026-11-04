#!/usr/bin/env python3
"""원가·본전 계산 도우미. 사용: python3 scripts/calc_cost.py <원가 입력 json> → 생성/계산결과_<가게>.md
원칙: 입력에 없는 값은 지어내지 않고 '계산 불가(입력 없음: …)'로 낸다. 예상 참여 수·전환율은 입력(사장님 추정 또는 사례 근거)으로만 받는다.
입력 예시: 생성/원가입력_고깃집.json"""
import json,sys,os,math
B=os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
inp=json.load(open(sys.argv[1],encoding="utf-8"))
menu={m["이름"]:m for m in inp.get("메뉴",[])}
L=[f"# 계산 결과 — {inp.get('가게','')} (scripts/calc_cost.py, 입력: {os.path.basename(sys.argv[1])})","",
   "※ 이 표의 숫자만 행사안에 쓴다. '계산 불가'인 칸은 사장님께 입력을 받아 다시 계산한다.","","## 메뉴 원가율","","| 메뉴 | 판매가 | 원가 | 원가율 | 메뉴 1개당 이익 |","|---|---|---|---|---|"]
for m in menu.values():
    p,c=m.get("판매가"),m.get("원가")
    if p and c is not None: L.append(f"| {m['이름']} | {p:,}원 | {c:,}원 | {c/p*100:.1f}% | {p-c:,}원 |")
    else: L.append(f"| {m['이름']} | {p} | {c} | 계산 불가(입력 없음: 판매가·원가) | 계산 불가 |")
ag=inp.get("객단가"); acr=inp.get("평균원가율%")
if acr is None and menu:
    ws=[(m["판매가"],m["원가"]) for m in menu.values() if m.get("판매가") and m.get("원가") is not None and m.get("주력")]
    if ws: acr=round(sum(c for p,c in ws)/sum(p for p,c in ws)*100,1)
L+=["",f"- 객단가: {ag:,}원" if ag else "- 객단가: 계산 불가(입력 없음: 객단가)",
    f"- 평균 원가율(손님 1명당 이익 계산용): {acr}%" + ("" if inp.get('평균원가율%') is not None else "(주력 메뉴 합계 기준)") if acr is not None else "- 평균 원가율: 계산 불가(입력 없음)"]
per=None
if ag and acr is not None: per=ag*(1-acr/100); L.append(f"- 새 손님 1명당 이익(객단가×(1−평균 원가율)): {per:,.0f}원")
L+=["","## 행사안별 비용·본전","","| 안 | 1회 혜택 원가 | 예상 참여 수 | 혜택 총비용 | 고정비(인건비·인쇄·광고) | 총비용 | 추가 주문 이익 | 본전 필요 추가 손님 수 | 할인율 | 비고 |","|---|---|---|---|---|---|---|---|---|---|"]
notes=[]
for a in inp.get("안",[]):
    nm=a["이름"]; b=a.get("혜택",{}); why=[]
    # 1회 혜택 원가
    unit=None
    if b.get("유형")=="할인":
        base=menu.get(b.get("메뉴",""),{}); p=b.get("원래가") or base.get("판매가"); r=b.get("할인율%")
        if p and b.get("행사가") is not None: unit=p-b["행사가"]; r=unit/p*100; b["할인율%"]=round(r,1)
        elif p and r is not None: unit=p*r/100
        else: why.append("할인 금액(원래가·할인율 또는 행사가)")
    else:
        mi=menu.get(b.get("메뉴",""),{}); c=b.get("원가") if b.get("원가") is not None else mi.get("원가")
        if c is not None: unit=c*b.get("수량",1)
        else: why.append("혜택 메뉴 원가")
    n=a.get("예상 참여 수")
    if n is None: why.append("예상 참여 수(근거 필요)")
    fx=sum((a.get("고정비") or {}).values()) if a.get("고정비") is not None else None
    if fx is None: why.append("고정비")
    tot_b=unit*n if unit is not None and n is not None else None
    tot=tot_b+fx if tot_b is not None and fx is not None else None
    add=None; conv=a.get("추가 주문 전환율"); am=menu.get(a.get("추가 주문 메뉴",""),{})
    if conv is not None and am.get("판매가") and am.get("원가") is not None and n is not None:
        add=n*conv*(am["판매가"]-am["원가"])*a.get("추가 주문 수량",1)
    elif a.get("추가 주문 메뉴"): why.append("추가 주문 전환율·메뉴 원가")
    be=None
    if tot is not None and per:
        net=tot-(add or 0); be=max(0,math.ceil(net/per)) if net>0 else 0
    elif tot is not None: why.append("새 손님 1명당 이익(객단가·평균 원가율)")
    dr=None
    if b.get("유형")=="할인" and (b.get("원래가") or menu.get(b.get("메뉴",""),{}).get("판매가")) and b.get("할인율%") is not None: dr=f"{b['할인율%']}%"
    if b.get("유형")=="증정" and b.get("메뉴") and any(w in b["메뉴"] for w in ["술","소주","맥주","생맥","막걸리","와인","하이볼"]): notes.append(f"{nm}: 술 증정은 원안 불가(주류 경품 금지 F004·F051, 광고 표시는 F075) — 이 계산은 참고용")
    f=lambda x,s="원": "계산 불가" if x is None else f"{x:,.0f}{s}"
    addtxt="추가 주문 없음(입력 없음)" if not a.get("추가 주문 메뉴") else f(add)
    L.append(f"| {nm} | {f(unit)} | {'계산 불가' if n is None else str(n)+'명'} | {f(tot_b)} | {f(fx)} | {f(tot)} | {addtxt} | {'계산 불가' if be is None else str(be)+'명'} | {dr or '해당 없음'} | {'계산 불가(입력 없음: '+', '.join(why)+')' if why else ''} |")
if inp.get("할인 표시 주의") is not False and any((a.get('혜택') or {}).get('유형')=='할인' for a in inp.get('안',[])):
    notes.append("할인율을 광고에 쓰려면 '종전거래가격'(최근 20일 정도 실제 판매한 가격, 변동 시 최저가)을 기준으로 해야 함(부당한 표시·광고행위 지정고시 Ⅲ.3.나·라, F017). 개업·신제품은 20일 판매 기록이 없으면 할인율 표시를 쓰지 않는다.")
if notes: L+=["","## 주의",""]+[f"- {x}" for x in notes]
os.makedirs(f"{B}/생성",exist_ok=True)
out=f"{B}/생성/계산결과_{inp.get('가게','')}.md"; open(out,"w",encoding="utf-8").write("\n".join(L)+"\n"); print(out); print("\n".join(L[-(6+len(inp.get('안',[]))):]))
