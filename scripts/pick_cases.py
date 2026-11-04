#!/usr/bin/env python3
"""행사안 생성용 참고 자료 묶음 만들기(생성문 [1. 입력 속성]의 '참고 사례'를 채움).
사용: python3 scripts/pick_cases.py 생성/입력_예시.json [사례 수=30] → 생성/참고묶음_<업종>_<단계>.md
고르는 규칙(생성문 규칙과 같음): 참고제외 제외 → 업종·세부업종·단계·시점·상권·목표·대상 맞는 점수 → 원문 확인함·한국·실제 우대 → 유사묶음은 대표 우선·묶음당 2건 → 성격별로 고르게.
사례마다 근거수준·진행여부·안전운영조건·FAQ번호를 붙이고, 걸린 FAQ의 조건과 공지문 문구 은행 행을 함께 붙인다."""
import json,sys,os,re,collections
import pandas as pd
B=os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
inp=json.load(open(sys.argv[1],encoding="utf-8")); N=int(sys.argv[2]) if len(sys.argv)>2 else 20
d=pd.read_json(f"{B}/merged/사례DB.jsonl",lines=True,dtype=str).fillna("")
faq=pd.read_csv(f"{B}/merged/FAQ.csv",dtype=str).fillna("").set_index("FAQ번호")
bank=pd.read_csv(f"{B}/merged/다른도구용/공지문_문구은행.csv",dtype=str).fillna("")
d=d[d.ref_exclude.str.strip()==""].copy()
def has(col,v): return d[col].str.split("|").map(lambda xs: v in xs) if v else False
sc=pd.Series(0.0,index=d.index)
ind=inp.get("업종","")
sc+= (d.industry==ind)*3 + (d.industry=="공통")*1
if inp.get("세부업종"): sc+= d.sub_industry.str.contains(re.escape(inp["세부업종"]))*2
for col,key,w in [("stage","단계",2.5),("timing","시점",1.5),("district","상권",1)]:
    if inp.get(key): sc+= has(col,inp[key])*w
for g in inp.get("목표",[]): sc+= has("goals",g)*1
for t in inp.get("주 손님층",[]): sc+= has("target",t)*0.7
sc+= (d.verify_status=="확인함")*1 + (d.country=="한국")*1 + (d.kind=="실제")*0.5
sc+= (d.group_rep=="대표")*0.3
OPEN=("오픈전","가오픈","그랜드오픈","오픈N일","정착기")
if inp.get("단계") in OPEN:
    sc-= d.nature.str.contains("양도·폐업정리")*5 + d.nature.str.contains("위기회복")*2
if inp.get("단계")=="폐업정리": sc-= d.nature.str.contains("오픈행사")*3
elif inp.get("단계")!="양도": sc-= d.nature.str.contains("양도·폐업정리")*5  # 폐업·양도 단계가 아니면 폐업 감사·양도 사례를 뒤로(회차17: 비수기 입력에 섞이는 것을 발견)
if inp.get("주류 판매")=="아니오": sc-= d.legal_risk.str.contains("주류")*1
d["점수"]=sc
d=d.sort_values("점수",ascending=False)
pick=[]; per_group=collections.Counter(); per_nat=collections.Counter(); cap=max(3,N//4)
for _,r in d.iterrows():
    if len(pick)>=N: break
    g=r.similar_group
    if g and per_group[g]>=2: continue
    nat=r.nature.split("|")[0]
    if per_nat[nat]>=cap: continue
    pick.append(r); per_group[g]+=1 if g else 0; per_nat[nat]+=1
P=pd.DataFrame(pick)
def verdict(q):
    m=re.search(r"진행여부:\s*([^/]+)",q); return m.group(1).strip() if m else ""
fids=sorted(set(f for s in P.faq_ids for f in re.findall(r"F0\d\d",s)))
L=[f"# 참고 묶음 — {ind} {inp.get('세부업종','')} / {inp.get('단계','')} / {inp.get('상권','')} (사례 {len(P)}건, FAQ {len(fids)}문항)","",
   "※ 생성문 v4와 함께 쓴다. 사례 번호를 행사안에 적고 원문 문장을 베끼지 않는다. 법확인필요사유가 있는 사례는 안전운영조건을 행사안 조건에 그대로 붙인다.","",
   "## 입력","```json",json.dumps(inp,ensure_ascii=False,indent=1),"```",""]
miss=[k for k,v in inp.items() if not k.startswith("_") and (v=="" or v==[] or v=="모름")]
if miss: L+=["## 생성 전에 사장님께 물을 것(입력 빈칸)",""]+[f"- {k}" for k in miss]+[""]
# 달력: 날짜는 만들지 않는다. 사용자의 캘린더 도구가 준 생성/캘린더.csv만 읽고 '캘린더 ○○ 기준'으로 표시. 없거나 오래되면 '달력 자료 없음'.
import datetime
cal_path=f"{B}/생성/캘린더.csv"; CAL=["## 달력(날짜는 캘린더 도구 자료만 쓴다)",""]
if not os.path.exists(cal_path): CAL+=["- 달력 자료 없음 — 생성/캘린더.csv가 없다. 행사 날짜를 정하지 말고 '달력 자료 없음'으로 적는다(docs/캘린더_도구_요청목록.md)."]
else:
    try:
        cal=pd.read_csv(cal_path,dtype=str,encoding="utf-8-sig").fillna("")
        need={"날짜","이름","종류","지역 범위","출처","기준일"}
        if not need<=set(cal.columns): CAL+=[f"- 달력 자료 없음 — 캘린더.csv에 빠진 칸: {sorted(need-set(cal.columns))}"]
        else:
            today=datetime.date.today(); ok=[]; stale=0; nosrc=0
            for _,c in cal.iterrows():
                try: base_d=datetime.date.fromisoformat(c["기준일"][:10])
                except ValueError: stale+=1; continue
                if (today-base_d).days>90: stale+=1; continue
                if not c["출처"].strip(): nosrc+=1; continue
                try: dd=datetime.date.fromisoformat(c["날짜"][:10])
                except ValueError: continue
                if today<=dd<=today+datetime.timedelta(days=60): ok.append((dd,c))
            if not ok: CAL+=[f"- 달력 자료 없음 — 앞으로 60일 안의 쓸 만한 항목이 없다(기준일 90일 초과 {stale}건, 출처 빈칸 {nosrc}건)."]
            for dd,c in sorted(ok,key=lambda x:x[0]):
                st="" if c.get("확정 여부","확정") in ("","확정") else f" ({c['확정 여부']} — 행사안에 예정으로 표시)"
                CAL.append(f"- {dd} {c['이름']} [{c['종류']}·{c['지역 범위']}] — 캘린더 {c['기준일'][:10]} 기준, 출처 {c['출처']}{st}")
    except Exception as e: CAL+=[f"- 달력 자료 없음 — 캘린더.csv를 읽지 못함({type(e).__name__})"]
L+=CAL+[""]
L+=["## 참고 사례",""]
for _,r in P.iterrows():
    L+=[f"### {r['id']} {r['name']}  (점수 {r['점수']:.1f})",
        f"- 성격·방식: {r.nature} / {r.method} · 단계 {r.stage} · 시점 {r.timing} · 상권 {r.district} · {r.country} · 원문확인 {r.verify_status}",
        f"- 요약: {r.summary[:150]}",f"- 조건: {r.condition[:150]} / 혜택: {r.benefit[:150]} / 1회원가: {r.unit_cost[:80]}",
        f"- 진행여부(질문과 답): {verdict(r.case_qna)} · 근거수준: {r.evidence_level}" + (f" · {r.faq_evidence}" if r.faq_evidence else ""),
        f"- FAQ: {r.faq_ids}"]
    if r.legal_todo: L.append(f"- ⚠ 법확인필요사유: {r.legal_todo} → **안전운영조건(그대로 붙일 것)**: {r.safe_ops[:400]}")
    L.append("")
L+=["## 걸린 FAQ(조건·대안)",""]
for f in fids:
    if f in faq.index:
        x=faq.loc[f]; L+=[f"### {f} {x['질문']}",f"- 진행여부: {x['진행여부']} · 근거수준: {x['근거수준']}",f"- 조건: {x['조건(조건부일때)'][:300]}",f"- 대안: {x['대안'][:200]}",""]
txt=" ".join(P.name+" "+P.summary+" "+P.legal_risk)
topics=[t for t in bank["주제"].unique() if any(k in txt for k in re.split(r"[·()\s]+",t) if len(k)>=2)]
if inp.get("주류 판매")=="예" and "술 행사" not in topics: topics.append("술 행사")
if inp.get("단계","").find("오픈")>=0 and "개업 행사" not in topics: topics.append("개업 행사")
L+=["## 공지문 문구 은행(권장 / 피할 표현)",""]
for t in topics:
    for _,b in bank[bank["주제"]==t].iterrows():
        L.append(f"- [{t}] 권장: {b['권장 문구']} / 피할 것: {b['피해야 할 문구']} ({b['근거수준']})")
os.makedirs(f"{B}/생성",exist_ok=True)
out=f"{B}/생성/참고묶음_{ind}_{inp.get('단계','')}.md"
open(out,"w",encoding="utf-8").write("\n".join(L)+"\n")
print(out,"사례",len(P),"FAQ",len(fids),"문구 주제",len(topics),"성격분포",dict(per_nat))
