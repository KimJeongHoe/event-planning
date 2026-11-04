#!/usr/bin/env python3
"""다른 도구에 파일로 넘길 주제별 CSV 만들기 (도구와 직접 연결하지 않음).
사용: python3 scripts/export_tools.py <출력폴더>
- QR오더용_사례.csv : 테이블오더 개인정보 동의 / 현금가·셀프계산대 / 노쇼·예약금 / 키오스크·어르신 응대
- 디자인메이커_공지물용_사례.csv : 휴무·영업시간 변경 안내 / 원가 공개·가격 인상 안내 / 접근성 개선 공지
고른 기준: 그 주제로 모은 수집 묶음(수집ID 범위) + 이름·요약 낱말 검색. 한 사례가 여러 주제에 걸리면 주제 칸에 모두 적음.
맨 앞 칸: 주제, 고른근거. 참고제외 사례도 빼지 않고 그대로 두되 참고제외 칸을 보고 쓰지 않을 것.
엑셀 수식 실행 방지(=,+,-,@ 시작 칸 앞 ') 적용."""
import sys,os,re,json,csv
import pandas as pd
BASE=os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
sys.path.insert(0,f"{BASE}/scripts")
OUT=sys.argv[1] if len(sys.argv)>1 else f"{BASE}/merged"
cols=json.load(open(f"{BASE}/spec/columns.json",encoding="utf-8"))["case_columns"]
rs=[json.loads(l) for l in open(f"{BASE}/merged/사례DB.jsonl",encoding="utf-8")]
def rng(pre,a,b): return {f"{pre}-{i:03d}" for i in range(a,b+1)}
def ntype(pre,pat):  # 새 유형 묶음 안에서 주제 낱말로 고르기
    return lambda r: r["orig_id"].startswith(pre+"-") and re.search(pat,r["name"]+r["summary"]+r["notes"])
T={
 "QR오더용_사례":[
  ("테이블오더 개인정보 동의", rng("NT5",1,9), r"테이블\s?오더|QR\s?(주문|오더)|태블릿\s?(주문|메뉴)"),
  ("현금가·셀프계산대", rng("NT5",28,35), r"현금가|현금\s?결제.{0,6}(유도|할인)|셀프\s?계산|무인\s?계산|계좌이체.{0,8}(할인|깎)"),
  ("노쇼·예약금", rng("NT3",1,12)|{"NT3-044"}, r"노쇼|예약금|예약\s?보증금"),
  ("키오스크·어르신 응대", rng("NT3",24,34), r"키오스크|디지털\s?(격차|약자|안내사)"),
 ],
 "디자인메이커_공지물용_사례":[
  ("휴무·영업시간 변경 안내", rng("NT7",1,8)|rng("NT7",34,42), r"임시\s?휴(무|업)|휴무\s?(안내|공지)|휴업\s?(안내|공지)|영업\s?시간\s?(변경|단축|조정)|명절\s?휴무"),
  ("원가 공개·가격 인상 안내", rng("NT4",10,22)|rng("NT1",16,27), r"가격\s?인상|요금\s?인상|인상\s?안내|원가.{0,4}공개|중량.{0,4}축소"),
  ("접근성 개선 공지", rng("NT7",25,33), r"(장애인|고령자|어르신|노인|키오스크)\S{0,6}\s?접근성|접근성\s?(개선|평가)|휠체어|경사로|점자\s?(메뉴|안내|표기|블록|스티커)|배리어\s?프리|무장애|안내견|보조견|음성\s?지원"),
 ]}
NT7_TOPIC={"휴무·영업시간 변경 안내":r"휴무|영업\s?시간|휴업|정전|폭설|단축",
           "접근성 개선 공지":r"(장애인|고령자|어르신|노인|키오스크)\S{0,6}\s?접근성|접근성\s?(개선|평가)|휠체어|경사로|점자\s?(메뉴|안내|표기|블록|스티커)|배리어|장애|보조견|큰\s?글씨|음성"}

# 배지 표시 규칙(docs/배지_표시규칙.md)과 같은 값을 도구용 칸으로
VCOL={"가능":("초록","✓","해도 됩니다"),"조건부 가능":("파랑","ⓘ","조건을 지키면 됩니다"),"확인 필요":("주황","?","관할 기관 확인 후"),"불가":("빨강","✕","하지 마세요")}
def verdict_of(q):
    m=re.search(r"진행여부:\s*([^/]+)",q or "")
    if not m: return ""
    v=m.group(1).strip()
    for k in ("불가","확인 필요","조건부 가능","가능"):
        if v.startswith(k): return k
    return ""
ECOL=[("법령 원문 확인","진한 회색","법령 확인"),("공식 해석·판례 확인","남색","판례·해석"),("부처 공식 자료 확인","청록","부처 자료"),
      ("조문 해석만","주황 테두리","해석 없음"),("원문 없음","주황","원문 없음"),("사실 확인 필요","노랑","사실 확인"),("조례 예시만","노랑","조례 다름"),
      ("해외 법","회색","해외"),("FAQ 근거 따름","연회색","FAQ 참고"),("법 쟁점 적음","연회색","법 쟁점 적음"),("법적 의무 없음","연회색","법 쟁점 적음")]
def ev_badge(e):
    for k,c,t in ECOL:
        if (e or "").startswith(k): return c,t
    return "",""
def badge_cols(r):
    v=verdict_of(r.get("case_qna",""))
    vc=VCOL.get(v,("","",""))
    ec,et=ev_badge(r.get("evidence_level",""))
    return [v,vc[0],vc[1]+" "+vc[2] if v else "",et,ec,"관련 FAQ 해석 없음" if r.get("faq_evidence") else ""]
def clean(v):
    """공유용 CSV에는 내부 작업 표시(회차 번호, 사용자 결정, 다른 도구)를 넣지 않는다 — 원본(raw)은 그대로 둔다"""
    if not isinstance(v,str): return v
    v=re.sub(r"\[회차\d+(?:[·,]\d+)*\s*",lambda m:"[",v)
    v=re.sub(r"(?:\(|\s)회차\d+(?:[·,]\d+)*(?:\s?[가-힣]{0,6}\s?(?:검색|확인|재확인))?(?=[\s)·,.]|$)",lambda m:"",v)
    v=re.sub(r"회차\d+(?:[·,]\d+)*에(?=\s)","앞서",v)
    v=re.sub(r"[,，]?\s*사용자 결정(?:으로|에 따라)?","",v)
    v=v.replace("다른 도구가 확인, 이 도구 원문 미확인","다른 자료에서 확인했으나 원문은 확인하지 못함").replace("다른 도구","다른 자료").replace("이 도구","이 자료")
    return v.replace("()","")
LIQ_RE=re.compile(r"(?<![가-힣])(술|소주|맥주|생맥|막걸리|하이볼|와인|사케|샴페인|주류|양주|위스키|칵테일)")
LIQ_NO="해당 없음(이 사례에 술 혜택 없음)"
LIQ_YES="⚠ 술 혜택이 있는 사례 — 거래(국세청 고시 제2025-31호: 술 공짜·덤·쿠폰 금지)와 광고 표시(국민건강증진법 제8조의2 제2항 제1호: 술 광고에 경품·금품 제공 내용 표시 금지, 한국건강증진개발원은 할인·증정·쿠폰·캐시백 광고도 위반 사례로 안내)를 따로 지킬 것. 공지문·SNS·배달앱·현수막에는 술 할인·증정을 쓰지 않고 가격은 메뉴판에만 — 안전운영조건 칸과 FAQ F075 참고. 공식 해석 없음"
def liq_note(r):
    t=" ".join(r.get(k,"") for k in ("name","summary","condition","benefit","legal_risk","variants"))
    ben=bool(LIQ_RE.search(r.get("benefit","")+" "+r.get("name",""))) and bool(re.search(r"할인|증정|서비스|무료|쿠폰|1\+1|반값|특가|무제한|캐시백",r.get("benefit","")+" "+r.get("name","")))
    return LIQ_YES if (ben or "F075" in r.get("legal_risk","")) else LIQ_NO
BH=["진행여부(질문과 답)","진행여부_색","진행여부_표시","근거수준_짧은표시","근거수준_색","관련FAQ_보조배지"]

H=["주제","고른근거"]+[h for _,h in cols]+BH
KIOSK=("키오스크·테이블오더 접근성 의무(쉬운 말, 2026-11 원문 확인): 화면으로 주문·결제하는 기기를 두면 장애인·어르신도 똑같이 쓸 수 있게 해야 함. "
 "장애인(장애인차별금지법 시행령 별표 2의2): 직원 100명 미만 가게는 2025.1.28부터, 그 전에 설치한 기기는 2026.1.28부터 — 검증기준 맞는 기기 + 위치 음성안내. "
 "50㎡ 미만 가게·소상공인·소형 기기는 보조기기·소프트웨어나 도와줄 직원 + 호출벨로 갈음. "
 "어르신(노인복지법 시행령 제19조의2): 2025.10.23 이후 새로 설치한 기기는 설치일부터, 그 전 기기는 2026.1.28까지 도움 직원·음성 안내·검증 기기·호환 소프트웨어·보조 앱 중 하나. "
 "[공식 자료 확인] 테이블오더 태블릿도 대상 — 복지부 보도자료·Q&A(2026-01-28): 주문형 무인주문기 포함, 화면 대각선 28cm 이하 테이블 주문형 소형제품은 작은 가게 특례(보조기기·소프트웨어 또는 직원+호출벨). 안 지키면 인권위 진정→시정권고→법무부 시정명령→3천만원 이하 과태료. [공식 언급 없음] 손님 휴대폰 QR 주문은 Q&A·해석례에 언급 없음 — 기기(키오스크) 의무는 맞지 않고, 앱 설치를 요구하면 앱 접근성(장애인차별금지법 제21조 제2항, 100명 미만 사업자 2024.7.28~), QR 주문 화면을 만들어 배포하는 테이블오더 업체(법인)는 웹 접근성 의무 대상 소지(같은 조 제1항 — 법인은 2013.4.11부터, 같은 항 후단이 '자연인은 행위자에 포함되지 아니한다'고 해 개인사업자 가게는 명시적으로 빠짐) → 가게는 업체에 웹 접근성 준수 여부를 확인하고, 직원 주문·종이 메뉴판을 늘 열어 두기. 자세히: docs/키오스크_접근성_의무_쉬운설명.md")
UNSURE=("[불확실] 업체가 여러 가게에 주는 웹 주문 화면이 '업체가 생산·배포하는 정보'인지 '가게의 정보'인지 공식 해석이 없음 — 업체(법인)의 웹 접근성 의무일 소지가 크나(장애인차별금지법 제21조 제1항, 자연인 제외), 가게가 법인이면 가게에도 걸릴 수 있음. "
 "계약서에 '접근성 의무 이행·시정 비용은 업체 부담'을 적어 두기. 점검표: docs/테이블오더_계약_점검표.md")
ACCESS=("접근성 의무(쉬운 말, 2026-11 원문 확인): ① 안내견 등 보조견을 데려온 손님은 정당한 이유 없이 거부할 수 없음(장애인복지법 제40조 제3항, 위반 시 과태료). "
 "② 휠체어 등 보조기구 반입을 막거나 장애를 이유로 자리·서비스를 달리하면 차별(장애인차별금지법 제4조·제15조·제18조). "
 "③ 키오스크·테이블오더를 두면 장애인·어르신도 쓸 수 있게 해야 함 — 동네 가게·소상공인·화면 28cm 이하 테이블오더는 도와줄 직원 + 호출벨로 갈음 가능(장애인차별금지법 시행령 별표 2의2·제10조의2, 복지부 Q&A 2026-01-28, 노인복지법 시행령 제19조의2; 2026.1.28부터 기존 기기도 적용). "
 "④ 경사로 등 편의시설은 바닥면적 50㎡ 이상 음식점·소매점·미용실 등이 설치 대상(장애인등편의법 시행령 별표 1, 2022.5.1 전 설치 시설은 종전 기준). "
 "공지 문구 예: '안내견과 함께 오셔도 됩니다', '주문이 어려우시면 직원 호출벨을 눌러 주세요', '휠체어 이용 손님은 입구 쪽 넓은 자리로 안내해 드립니다', '경사로 이용 시 직원이 도와드립니다'. "
 "자세히: docs/키오스크_접근성_의무_쉬운설명.md")
for fname,topics in T.items():
    rows={}
    for topic,ids,pat in topics:
        for r in rs:
            why=None
            if r["orig_id"] in ids: why="주제 수집 묶음"
            elif re.search(pat,r["name"]+" "+r["summary"]): why="이름·요약 낱말"
            if not why: continue
            e=rows.setdefault(r["id"],{"주제":[],"고른근거":[],"r":r})
            if topic not in e["주제"]: e["주제"].append(topic); e["고른근거"].append(f"{topic}:{why}")
    out=[]
    for i in sorted(rows):
        e=rows[i]; row=[" | ".join(e["주제"])," | ".join(e["고른근거"])]+[e["r"].get(k,"") for k,_ in cols]+badge_cols(e["r"])
        if fname.startswith("QR"):
            kio=any(t in ("키오스크·어르신 응대","테이블오더 개인정보 동의") for t in e["주제"])
            row.append(KIOSK if kio else "")
            un=[]
            if kio: un.append(UNSURE)
            if "공식 해석 원문 없음" in e["r"].get("evidence_level","")+e["r"].get("faq_evidence",""): un.append("이 사례 또는 관련 FAQ에 공식 해석 원문 없는 쟁점이 있음 — 안전운영조건 칸을 따를 것")
            row.append(" / ".join(un))
        else: row.append(ACCESS if "접근성 개선 공지" in e["주제"] else "")
        row.append(liq_note(e["r"]))
        out.append(row)
    df=pd.DataFrame(out,columns=H+(["키오스크·테이블오더 접근성 의무(쉬운 말)","불확실한 부분(공식 해석 없음)"] if fname.startswith("QR") else ["접근성 의무(쉬운 말)·공지 문구 예"])+["술 광고 표시 주의(제8조의2)"])
    df=df.apply(lambda col:col.map(clean))
    for c in df.columns:
        df[c]=df[c].map(lambda v:("'"+v) if isinstance(v,str) and v[:1] in ("=","+","-","@","\t","\r") else v)
    p=f"{OUT}/{fname}.csv"; df.to_csv(p,index=False,encoding="utf-8-sig",quoting=csv.QUOTE_ALL)
    cnt={t:sum(1 for e in rows.values() if t in e["주제"]) for t,_,_ in topics}
    print(p,len(df),cnt)

fq=pd.read_csv(f"{BASE}/merged/FAQ.csv",dtype=str).fillna("")
fq["진행여부_색"]=fq["진행여부"].map(lambda v:VCOL.get(v,("","",""))[0])
fq["진행여부_표시"]=fq["진행여부"].map(lambda v:(VCOL[v][1]+" "+VCOL[v][2]) if v in VCOL else "")
fq["근거수준_짧은표시"]=fq["근거수준"].map(lambda e:ev_badge(e)[1]); fq["근거수준_색"]=fq["근거수준"].map(lambda e:ev_badge(e)[0])
fq=fq.apply(lambda col:col.map(clean))
for c in fq.columns: fq[c]=fq[c].map(lambda v:("'"+v) if isinstance(v,str) and v[:1] in ("=","+","-","@") else v)
fq.to_csv(f"{OUT}/FAQ_표시용.csv",index=False,encoding="utf-8-sig",quoting=csv.QUOTE_ALL); print(f"{OUT}/FAQ_표시용.csv",len(fq))
