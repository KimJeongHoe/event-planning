#!/usr/bin/env python3
"""merge.py 뒤 자동 검사: ① 시행일 점검 목록 — 다음 확인 날짜가 지났거나 30일 안이면 경고 ② 공지문 문구 은행 ③ 사례 변형안·질문과 답 대안·디자인 메이커 공지 문구 예 — 근거 FAQ 존재·'불가' FAQ 인용·근거수준 불일치·피해야 할 낱말이 권장 문구에 들어갔는지.
원본: spec/시행일_점검목록.csv, spec/공지문_문구은행.csv → merged/다른도구용/에 복사, 결과는 merged/통계.md 맨 앞 '자동 경고'와 merged/자동검사.md"""
import pandas as pd, re, os, datetime, shutil
B=os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
today=datetime.date.today(); W=[]
# ① 시행일
t=pd.read_csv(f"{B}/spec/시행일_점검목록.csv",dtype=str).fillna("")
for _,r in t.iterrows():
    m=re.match(r"(\d{4})-(\d{2})-(\d{2})",r["다음 확인 날짜"])
    if not m: continue
    dt=datetime.date(*map(int,m.groups())); left=(dt-today).days
    if left<0: W.append(f"[시행일] 확인 날짜 지남({r['다음 확인 날짜']}): {r['규정']} — {r['확인할 곳']}")
    elif left<=30: W.append(f"[시행일] {left}일 뒤 확인({r['다음 확인 날짜']}): {r['규정']}")
shutil.copy(f"{B}/spec/시행일_점검목록.csv",f"{B}/merged/다른도구용/시행일_점검목록.csv")
# ② 문구 은행
bank=pd.read_csv(f"{B}/spec/공지문_문구은행.csv",dtype=str).fillna("")
EXC=set()
for l in open(f"{B}/spec/검사_예외.txt",encoding="utf-8"):
    if not l.strip() or l.startswith("#"): continue
    parts=[x.strip() for x in l.split("|")]
    EXC.add(parts[0].split(" ")[0])
    m=re.match(r"(\d{4})-(\d{2})-(\d{2})",parts[1] if len(parts)>1 else "")
    if not m: W.append(f"[검사 예외] 확인 날짜가 없음: {parts[0]}")
    elif (today-datetime.date(*map(int,m.groups()))).days>365: W.append(f"[검사 예외] 확인한 지 1년 지남({parts[1]}): {parts[0]} — 다시 확인")
faq=pd.read_csv(f"{B}/merged/FAQ.csv",dtype=str).fillna("").set_index("FAQ번호")
BAD=[(r"(술|소주|맥주|생맥|막걸리|하이볼|와인|사케)[^.。]{0,12}(무료|공짜|서비스로|증정|드립니다)", "술 무료·증정 표현(주류 경품 금지, F004·F051)"),
     (r"국내 ?최초|최저가|원조|업계 ?1위|1등|최고의", "최상급·최초 표현(근거 없으면 표시광고법, F018)"),
     (r"노키즈|어린이 ?출입 ?금지|아이 ?출입 ?불가", "아동 출입 제한 표현(차별 소지, F036·F059)"),
     (r"환불 ?불가|절대 ?환불|어떤 경우에도 ?환불", "일률적 환불 불가(약관·소비자분쟁해결기준, F026·F027)"),
     (r"리뷰 ?삭제[^.]{0,10}(조건|하면)", "리뷰 삭제 조건 보상(F048)")]
for i,r in bank.iterrows():
    tag=f"[문구 은행 {i+2}행 {r['주제']}]"
    for fid in sorted(set(re.findall(r"F0\d\d",r["근거"]))):
        if fid not in faq.index: W.append(f"{tag} 근거 {fid}가 FAQ에 없음"); continue
        if faq.loc[fid,"진행여부"]=="불가" and f"문구은행:{i+2}:{fid}" not in EXC: W.append(f"{tag} 근거 {fid}의 진행여부가 '불가' — 권장 문구가 그 행위를 권하지 않는지 확인")
        if r["근거수준"].startswith("법령 원문") and not re.search(r"제\d+조|별표|고시",r["근거"]) and "공식 해석 원문 없음" in faq.loc[fid,"근거수준"]:
            W.append(f"{tag} 근거수준 '법령 원문 확인'인데 근거가 FAQ {fid}(공식 해석 원문 없음)뿐")
    for pat,why in BAD:
        if re.search(pat,r["권장 문구"]): W.append(f"{tag} 권장 문구에 피해야 할 표현: {why}")
shutil.copy(f"{B}/spec/공지문_문구은행.csv",f"{B}/merged/다른도구용/공지문_문구은행.csv")
# ③ 사례의 권장 쪽 문구(변형안·질문과 답의 대안)와 디자인 메이커 공지 문구 예
LIQ=r"((?<![가-힣])술|소주|맥주|생맥|막걸리|하이볼|와인|사케|주류)'?\s?(\d+\s?(잔|병|cc|ml)'?\s?)?(무료|공짜|서비스로|증정)|(무료|증정|서비스)[^.。/②③④]{0,6}((?<![가-힣])술|소주|맥주|생맥|막걸리|하이볼|와인)"
CBAD=[(LIQ,"술 무료·증정(F051)"),(r"국내 ?최초|최저가 ?보장|업계 ?1위","최상급·최저가 표현(F018)"),(r"노키즈|어린이 ?출입 ?금지","아동 출입 제한(F036·F059)"),(r"환불 ?불가|절대 ?환불","일률적 환불 불가(F026·F027)")]
d=pd.read_json(f"{B}/merged/사례DB.jsonl",lines=True,dtype=str).fillna("")
for _,r in d.iterrows():
    alt=" ".join(re.findall(r"대안:\s*([^/]+)",r.case_qna))
    for fld,txt in [("변형안",r.variants),("질문과 답 대안",alt)]:
        for pat,why in CBAD:
            for m in re.finditer(pat,txt):
                after=txt[m.end():m.end()+12]
                if re.search(r"대신|하지|금지|빼|말고|않|불가|주문 ?시|구매 ?시|X",after): continue
                if f"사례:{r.orig_id}:{fld}" in EXC: continue
                W.append(f"[사례 {r.orig_id} {fld}] 권장 쪽 문구에 피해야 할 표현: {why} — …{txt[max(0,m.start()-20):m.end()+10]}…")
import importlib.util
spec=importlib.util.spec_from_file_location("ex",f"{B}/scripts/export_tools.py")
src=open(f"{B}/scripts/export_tools.py",encoding="utf-8").read()
m=re.search(r"ACCESS=\((.*?)\)\n",src,re.S)
if m:
    acc=eval("("+m.group(1)+")")
    for q in re.findall(r"'([^']+)'",acc.split("공지 문구 예:")[-1]):
        for pat,why in CBAD:
            if re.search(pat,q): W.append(f"[디자인 메이커 공지 문구 예] '{q}' — {why}")
# ⑤ 혜택·조건·이름에 술 무료·증정이 있는데 국세청 원문 판정 블록이 없는 사례
LIQB=r"((?<![가-힣])술|소주|맥주|생맥|막걸리|하이볼|와인|사케|샴페인|주류)'?\s?(\d+\s?(잔|병|cc|ml|L)'?\s?)?(무료|공짜|서비스|증정)|(무료|증정|서비스로?)[^.。/\n]{0,8}((?<![가-힣])술|소주|맥주|생맥|막걸리|하이볼|와인|샴페인|주류)"
for _,r in d.iterrows():
    tt=r.benefit+" "+r.condition+" "+r["name"]
    if re.search(LIQB,tt) and "국세청 원문 확인(회차8" not in r.legal_risk and f"사례:{r.orig_id}:술" not in EXC:
        W.append(f"[사례 {r.orig_id}] 술 무료·증정이 혜택에 있는데 국세청 원문 판정(주류 경품 금지)이 법 칸에 없음")
# ④ 도구용 CSV에 따옴표 하나만 든 칸(빈칸 처리 오류)이 있는지
import glob as _g
for fp in _g.glob(f"{B}/merged/다른도구용/*.csv")+[f"{B}/merged/사례DB.csv",f"{B}/merged/FAQ.csv"]:
    try: x=pd.read_csv(fp,dtype=str,keep_default_na=False)
    except Exception as ex: W.append(f"[CSV] 읽기 실패 {os.path.basename(fp)}: {ex}"); continue
    n=int((x=="'").sum().sum())
    if n: W.append(f"[CSV] {os.path.basename(fp)}: 따옴표 하나만 든 칸 {n}개(빈칸 처리 오류)")
# ⑥ 판정 칸이 빈 사례·FAQ(빈 값이 '가능'으로 읽힐 위험)
def _verdict(q):
    m=re.search(r"진행여부:\s*([^/]+)",q or ""); return m.group(1).strip() if m else ""
for _,r in d.iterrows():
    if not _verdict(r.case_qna): W.append(f"[판정 빈칸] 사례 {r.orig_id}: 질문과 답에 진행여부가 없음 — 빈 값을 가능으로 읽을 수 있음")
for fid,r in faq.iterrows():
    if not str(r["진행여부"]).strip(): W.append(f"[판정 빈칸] FAQ {fid}: 진행여부가 비어 있음")
for _c,_nm in (("legal_risk","법 위험"),("business_risk","사업 위험"),("ops_risk","운영 위험"),("reputation_risk","평판 위험")):
    for _,r in d.iterrows():
        if not str(r[_c]).strip(): W.append(f"[위험 칸 빈칸] 사례 {r.orig_id}: {_nm} 칸이 비어 있음 — '없음(이유)'로 적을 것(빈칸은 문제 없음으로 읽힘)")
# ⑦ 술 혜택(혜택·이름에 술류 + 할인·증정류, F075 낱말은 보지 않고 독립 감지)이 있는데 술 광고 표시(제8조의2) 블록이 없는 사례
_L=r"(?<![가-힣])(술|소주|맥주|생맥|막걸리|하이볼|와인|사케|샴페인|주류|양주|위스키|칵테일)"
_P=r"할인|증정|서비스|무료|쿠폰|1\+1|반값|특가|무제한|캐시백|리필|공짜"
LIQN_CASES=[]
for _,r in d.iterrows():
    tt=r.benefit+" "+r["name"]
    if re.search(_L,tt) and re.search(_P,tt):
        LIQN_CASES.append(r.orig_id)
        if "술 광고 표시(회차17" not in r.legal_risk and f"사례:{r.orig_id}:술표시" not in EXC:
            W.append(f"[술 광고 표시] 사례 {r.orig_id}: 술 혜택이 있는데 국민건강증진법 제8조의2 표시 기준(F075) 블록이 법 칸에 없음")
# ⑧ 공유용 CSV: 내부 작업 표시가 섞여 나가지 않는지, 술 광고 표시 주의 칸이 비어 있거나 어긋나지 않는지
INTERNAL=re.compile(r"회차\s*\d+|다른 도구|이 도구|사용자 결정|TODO")
SHARED=["QR오더용_사례","디자인메이커_공지물용_사례","FAQ_표시용","공지문_문구은행","소상공인_확인표","시행일_점검목록","테이블오더_계약_점검표","칸_설명"]
for nm in SHARED:
    fp=f"{B}/merged/다른도구용/{nm}.csv"
    if not os.path.exists(fp): W.append(f"[공유 CSV] {nm}.csv 가 없음 — 검사하지 못함"); continue
    x=pd.read_csv(fp,dtype=str,keep_default_na=False,encoding="utf-8-sig")
    if len(x)==0: W.append(f"[공유 CSV] {nm}.csv 가 0행 — 통과로 치지 않음"); continue
    n=sum(bool(INTERNAL.search(v)) for c in x.columns for v in x[c])
    if n: W.append(f"[공유 CSV] {nm}.csv: 내부 작업 표시(회차 번호·사용자 결정·다른 도구) {n}칸")
    if "술 광고 표시 주의(제8조의2)" in x.columns:
        col=x["술 광고 표시 주의(제8조의2)"]
        if (col.str.strip()=="").any(): W.append(f"[공유 CSV] {nm}.csv: 술 광고 표시 주의 칸 빈칸 {(col.str.strip()=='').sum()}행(빈칸 금지 — 해당 없음도 적을 것)")
        idc="번호" if "번호" in x.columns else None
        if idc:
            bad=x[(x[idc].isin([str(i) for i in LIQN_CASES]))&(~col.str.startswith("⚠"))]
            if len(bad): W.append(f"[공유 CSV] {nm}.csv: 술 혜택 사례인데 술 광고 표시 주의가 ⚠가 아닌 행 {len(bad)}개")
    elif nm in ("QR오더용_사례","디자인메이커_공지물용_사례"): W.append(f"[공유 CSV] {nm}.csv: 술 광고 표시 주의 칸이 없음")
# ⑨ 상시 문서 크기와 한국어로만 쓰기(보고·인수인계·행사안에 영어 문장이 섞이지 않았는지)
DOCSZ={"인수인계.md":80000,"spec/생성문_v4.txt":40000,"spec/속성설명서.md":40000,"docs/행사안_만들기_사용법.md":20000}
for rel,lim in DOCSZ.items():
    fp=f"{B}/{rel}"
    if os.path.exists(fp):
        n=len(open(fp,encoding="utf-8").read())
        if n>lim: W.append(f"[문서 크기] {rel} {n:,}자 > 기준 {lim:,}자 — 줄이거나 나누기")
import glob as _g2
_rep=sorted(_g2.glob(f"{B}/reports/회차보고_*.md"),key=lambda p:int(re.search(r"_(\d+)\.md",p).group(1)))
for fp in ([f"{B}/인수인계.md"]+_rep[-1:]):
    if not os.path.exists(fp): continue
    fence=False
    for ln,l in enumerate(open(fp,encoding="utf-8"),1):
        if l.strip().startswith("```"): fence=not fence; continue
        if fence or "http" in l or "`" in l: continue
        m=re.search(r"(?:\b[A-Za-z]*[a-z][A-Za-z'-]{1,}\s+){3}[A-Za-z]{3,}\b",l)
        if m: W.append(f"[한국어로만] {os.path.basename(fp)} {ln}행에 영어 문장: …{m.group(0)[:40]}…")
txt="## 자동 경고 (scripts/checks.py)\n"+("\n".join("- "+w for w in W) if W else "- 경고 없음")+"\n"
open(f"{B}/merged/자동검사.md","w").write(f"# 자동 검사 ({today})\n\n"+txt)
# 이력 쌓기(reports/자동검사_이력.csv): 날짜·시각, 경고 수, 종류별 수
import csv as _csv, collections as _c
hp=f"{B}/reports/자동검사_이력.csv"; kinds=_c.Counter(re.match(r"\[([^\] ]+)",w).group(1) if re.match(r"\[([^\] ]+)",w) else "기타" for w in W)
new=not os.path.exists(hp)
with open(hp,"a",encoding="utf-8-sig",newline="") as fh:
    wr=_c and _csv.writer(fh)
    if new: wr.writerow(["실행 시각","경고 수","종류별","사례 수","FAQ 수"])
    wr.writerow([datetime.datetime.now().strftime("%Y-%m-%d %H:%M"),len(W),"; ".join(f"{k} {v}" for k,v in kinds.items()) or "없음",len(d),len(faq)])
p=f"{B}/merged/통계.md"; s=open(p).read()
s=re.sub(r"## 자동 경고 \(scripts/checks.py\)\n(?:- .*\n)*","",s)
lines=s.split("\n",2); s=lines[0]+"\n\n"+txt+"\n"+(lines[2] if len(lines)>2 else "")
open(p,"w").write(s); print(len(W),"경고"); [print(" ",w) for w in W[:20]]
