#!/usr/bin/env python3
"""생성된 행사안 검사. 사용: python3 scripts/check_plan.py <행사안 파일> [참고 묶음 파일] [계산 결과 파일]
종료 코드: 0 통과 / 1 경고 있음 / 2 검사 대상이 없음(통과로 치지 않음)
검사: ① 술 거래·광고 표시(국세청 주류 경품 금지, 국민건강증진법 제8조의2 제2항 제1·2·5호) ② 최초·최저가·노키즈·환불 불가·리뷰 삭제·투표 인증·복권 ③ 술 혜택 안에 광고 표시 기준(F075) 언급 ④ 참고 사례 안전운영조건 누락 ⑤ 원가율·본전·할인율 숫자가 계산 결과에 있는지"""
import sys,re,os
if len(sys.argv)<2: sys.exit("사용: check_plan.py <행사안> [참고묶음] [계산결과]")
plan=open(sys.argv[1],encoding="utf-8").read()
pick=open(sys.argv[2],encoding="utf-8").read() if len(sys.argv)>2 and os.path.exists(sys.argv[2]) else ""
calc=open(sys.argv[3],encoding="utf-8").read() if len(sys.argv)>3 and os.path.exists(sys.argv[3]) else ""
lines=plan.split("\n")
# 검사 대상 확인: 안 제목이 하나도 없거나 너무 짧으면 실패
heads=[l for l in lines if re.match(r"\s*(#{1,4}\s|\d+[.)]\s|[①-⑩]\s|\*\*)",l)]
if len(plan.strip())<200 or len(heads)<3:
    print("경고 없음이 아니라 '검사 대상 없음': 행사안 본문이 너무 짧거나 안 제목을 찾지 못함(200자·제목 3개 미만)"); sys.exit(2)
LIQN=r"(?<![가-힣])(술|소주|맥주|생맥|막걸리|하이볼|와인|사케|샴페인|주류|양주|위스키|칵테일|호프)"
PROMO=r"할인|반값|특가|1\+1|\d\s?%|\d[\d,]*\s?원|기념가|무제한|무한|쿠폰|캐시백|증정|서비스|무료|공짜|한 ?잔 ?더|리필|덤"
GIVE=r"무료|공짜|서비스로?|증정|쿠폰|교환권|캐시백|덤"
AD=r"문구|카피|현수막|배너|X배너|포스터|문자|공지|게시|배달앱|전단|SNS|인스타|스레드|틱톡|블로그|입간판|홍보|알리기|[\"“”']"
W=[]
def skip(after): return re.search(r"대신|하지 않|하지 말|금지|빼고|말고|않음|않기|불가|피함|피하|쓰지|X\)",after)
# 면제는 둘뿐: ① '원안' 이 든 안 제목 아래의 설명 줄(거래 조건 설명만, 따옴표 속 알리는 문구 줄은 그대로 검사) ② 참고 묶음의 안전운영조건 원문과 앞 25자가 같은 '- 안전운영조건' 줄
_condkeys=[re.sub(r"\s+","",m.group(1))[:25] for m in re.finditer(r"안전운영조건\(그대로 붙일 것\)\*\*: ([^\n]+)",pick)]
def verbatim(l):
    m=re.match(r"\s*-\s*안전운영조건[^:：]*[:：]\s*(.+)",l)
    return bool(m) and re.sub(r"\s+","",m.group(1))[:25] in _condkeys
def clause_neg(l,pos):
    # 위치가 든 한 문장(. ; ／ — 로 나눈 토막) 안에 부정·금지 말이 있으면 쓰지 말라는 문장으로 본다
    parts=re.split(r"[.;／—]",l); n=0
    for part in parts:
        if n<=pos<=n+len(part): return bool(re.search(r"쓰지 않|않는다|않기|하지 말|금지|불가|피한다|피함|대신",part))
        n+=len(part)+1
    return False
in_orig=False
for i,l in enumerate(lines,1):
    if re.match(r"\s*#{1,4}\s",l): in_orig=("원안" in l)
    if verbatim(l): continue
    liq=re.search(LIQN,l)
    if liq and re.search(GIVE,l) and not (in_orig and not re.match(r"\s*-\s*알리는 문구",l)):
        for m in re.finditer(GIVE,l):
            if not any(abs(m.start()-q.start())<=26 for q in re.finditer(LIQN,l)): continue
            if skip(l[m.end():m.end()+14]) or skip(l[max(0,m.start()-14):m.start()]) or clause_neg(l,m.start()): continue
            W.append(f"{i}행: 술 증정·무료·쿠폰 — 주류 경품 금지(F004·F051)이고 광고에 쓰면 국민건강증진법 제8조의2 제2항 제1호에도 걸림 — …{l[max(0,m.start()-18):m.end()+14]}…"); break
    if liq and re.search(AD,l):
        for m in re.finditer(PROMO,l):
            if abs(m.start()-liq.start())>26: continue
            if skip(l[m.end():m.end()+14]) or skip(l[max(0,m.start()-14):m.start()]) or clause_neg(l,m.start()): continue
            W.append(f"{i}행: 술 광고 표시에 할인·증정·무제한 표현 — 국민건강증진법 제8조의2 제2항 제1호·제2호(F075), 가격은 메뉴판·가격표에만 — …{l[max(0,min(m.start(),liq.start())-8):max(m.end(),liq.end())+10]}…"); break
    for pat,why in [(r"마시자|마셔라|마셔 보|취하자|취해|한 ?잔 ?더|술 ?무제한|무제한 ?(술|맥주|소주)","음주 권유(제8조의2 제2항 제2호)"),
                    (r"숙취[^\n]{0,6}(없|해소|제로)|(건강에|몸에) ?좋은 (술|막걸리|와인|약술)|피로[^\n]{0,4}(풀|회복)[^\n]{0,8}(술|막걸리)","술의 건강 효과 표현(제8조의2 제2항 제5호)")]:
        if re.search(pat,l) and re.search(LIQN,l) and not skip(l): W.append(f"{i}행: {why} — …{l.strip()[:60]}…")
    for pat,why in [(r"국내 ?최초|최저가 ?보장|업계 ?1위|원조","최상급·최초 표현 — 근거 필요(F018)"),(r"노키즈|어린이 ?출입 ?금지","아동 출입 제한(F036·F059)"),
                    (r"환불 ?불가|절대 ?환불","일률적 환불 불가(F026·F027)"),(r"리뷰 ?삭제[^.\n]{0,10}(조건|하면)","리뷰 삭제 조건 보상(F048)"),
                    (r"투표 ?인증[^\n]{0,15}할인","투표 인증 할인 — 확인 필요(F066)"),(r"복권|로또","복권 경품(F001)")]:
        m=re.search(pat,l)
        if m and not skip(l[m.end():m.end()+12]): W.append(f"{i}행: {why} — …{l[max(0,m.start()-15):m.end()+12]}…")
# ③ 술 혜택이 있는 안에 광고 표시 기준 언급 여부
if re.search(LIQN,plan) and re.search(PROMO,"".join(l for l in lines if re.search(LIQN,l))) and not re.search(r"F075|제8조의2|건강증진법|술 광고",plan):
    W.append("술 혜택이 있는 행사안인데 술 광고 표시 기준(국민건강증진법 제8조의2, F075) 언급이 없음")
# ④ 안전운영조건 누락
if pick:
    for blk in re.finditer(r"### (\d+) [^\n]*\n(?:- [^\n]*\n)*?- ⚠ 법확인필요사유: [^→]*→ \*\*안전운영조건\(그대로 붙일 것\)\*\*: ([^\n]+)",pick):
        cid,cond=blk.group(1),blk.group(2)
        if re.search(rf"(?<!\d){cid}(?!\d)",plan):
            key=re.sub(r"\s+","",cond)[:25]
            if key and key not in re.sub(r"\s+","",plan): W.append(f"사례 {cid}를 참고했는데 그 안전운영조건이 행사안에 없음 — 앞부분: {cond[:40]}…")
# ⑤ 숫자 근거
NUM=[(r"원가율\s*[:=]?\s*약?\s*(\d+(?:\.\d+)?)\s*%","원가율"),(r"본전[^\d\n]{0,14}(\d+)\s*명","본전 손님 수"),(r"할인율\s*[:=]?\s*약?\s*(\d+(?:\.\d+)?)\s*%","할인율"),(r"(?:1회|1인|1건)\s*원가\s*[:=]?\s*약?\s*(\d[\d,]*)\s*원","1회 원가")]
cnums=set(re.findall(r"\d[\d,]*(?:\.\d+)?",calc)); cnums|={n.replace(",","") for n in cnums}
for _n in list(cnums):
    try: _f=float(_n.replace(",","")); cnums|={str(int(round(_f))),f"{_f:g}"}
    except ValueError: pass
for i,l in enumerate(lines,1):
    for pat,name in NUM:
        for m in re.finditer(pat,l):
            v=m.group(1).replace(",","")
            if not calc: W.append(f"{i}행: {name} {m.group(1)} — 계산 결과 파일 없이 쓴 숫자(scripts/calc_cost.py로 계산한 값만 쓸 것)")
            elif v not in cnums and str(round(float(v))) not in cnums: W.append(f"{i}행: {name} {m.group(1)} — 계산 결과에 없는 숫자(모델이 지어냈을 가능성)")
_skipped=[]
if not pick: _skipped.append("참고 사례 안전운영조건(참고 묶음 파일 없음)"); W.append("참고 묶음 파일이 없어 안전운영조건 누락 검사를 하지 못함 — 통과로 치지 않음")
if not calc and not re.search(r"원가율|본전|할인율|1회 원가",plan) is None: _skipped.append("숫자 근거(계산 결과 파일 없음)")
print(f"검사한 줄 {len(lines)}, 안 제목 {len(heads)}개 / 경고 {len(W)}건"); [print(" -",w) for w in W]; print("검사하지 못한 항목:",", ".join(_skipped) if _skipped else "없음")
sys.exit(1 if W else 0)
