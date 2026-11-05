#!/usr/bin/env python3
"""행사안 미리보기 화면 만들기: 사례 DB·FAQ·문구 은행·캘린더를 JSON으로 넣은 한 장짜리 HTML → preview/행사안_미리보기.html
생성 모델을 부르지 않는다(자료에서 골라 조합). 숫자는 화면의 계산식으로만."""
import json,re,os,pandas as pd
B=os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
d=pd.read_json(f"{B}/merged/사례DB.jsonl",lines=True,dtype=str).fillna("")
ALL=len(d); NEX=int((d.ref_exclude!="").sum()); NBL=int(((d.ref_exclude=="")&(d.verify_status=="막힘")).sum())
d=d[(d.ref_exclude=="")&(d.verify_status.isin(["확인함","해당없음(응용)"]))]
HARD=re.compile(r"본사 ?(납품|공급|지원|부담|원육|육가공|프로모션|일괄|정책)|가맹본부|(전|모든) ?가맹점|가맹점 ?(전체|모두|공통)|전 매장|멤버스 앱|리워드 회원|자체 앱|CK|물류센터|복지카드|제휴 카드사|청구할인")
BIG=re.compile(r"프랜차이즈|가맹|체인|본사")
LIQ=re.compile(r"(?<![가-힣])(술|소주|맥주|생맥|막걸리|하이볼|와인|사케|샴페인|주류|양주|위스키|칵테일)")
PRO=re.compile(r"할인|증정|서비스|무료|쿠폰|1\+1|반값|특가|무제한|캐시백|리필|공짜")
def verdict(q):
    m=re.search(r"진행여부:\s*([^/]+)",q); return m.group(1).strip() if m else ""
def basis(q):
    m=re.search(r"근거:\s*(.+)",q); return m.group(1).strip()[:420] if m else ""
def url1(s):
    m=re.search(r"https?://\S+",s); return m.group(0).rstrip("|,;") if m else ""
import sys as _s; _s.path.insert(0,os.path.dirname(os.path.abspath(__file__)))
from case_kind import who as _who, kind as _kind
C=[]
for _,r in d.iterrows():
    tt=r.benefit+" "+r["name"]
    C.append(dict(i=int(r.id),n=r["name"],s=r.summary,ind=r.industry,sub=r.sub_industry,st=r.stage,tm=r.timing,na=r.nature,g=r.goals,t=r.target,
      c=r.condition,b=r.benefit,sg=r.staging,rs=r.resources,du=r.duration,li=r["limit"],kp=r.kpi,up=r.upsell_path,
      br=r.business_risk,orr=r.ops_risk,rr=r.reputation_risk,va=r.variants,so=r.safe_ops,ev=r.evidence_level,v=verdict(r.case_qna),qb=basis(r.case_qna),
      f=r.faq_ids,uc=r.unit_cost,cr=r.cost_ratio_level,k=r.kind,co=r.country,vs=r.verify_status,grp=r.similar_group,rep=r.group_rep,
      fr=2 if HARD.search(r["name"]+" "+r.summary+" "+r.condition+" "+r.benefit+" "+r.resources) else (1 if BIG.search(r["name"]+" "+r.summary) else 0),lq=1 if ((LIQ.search(tt) and PRO.search(tt)) or "F075" in r.legal_risk) else 0,u=url1(r.source_urls),bi=r.base_ids,wh=_who(r),kd=_kind(r)))
f=pd.read_csv(f"{B}/merged/FAQ.csv",dtype=str).fillna("")
cols=f.columns.tolist()
def col(*names):
    for n in names:
        for c in cols:
            if c.startswith(n): return c
    return None
F={r["FAQ번호"]:dict(q=r[col("질문")],v=r[col("진행여부")],c=r[col("조건")][:700] if col("조건") else "",a=r[col("대안")][:400] if col("대안") else "") for _,r in f.iterrows()}
bank=pd.read_csv(f"{B}/spec/공지문_문구은행.csv",dtype=str).fillna("").to_dict("records")
cal=[]
cp=f"{B}/생성/캘린더.csv"
if os.path.exists(cp):
    c=pd.read_csv(cp,dtype=str,encoding="utf-8-sig").fillna("")
    # 행사에 쓸 만한 날만(허용 목록). 추모·항쟁·안전·직군 기념일 등은 뺀다. ○○데이는 민간에서 부르는 날이라 출처 대신 그렇게 적는다
    OK={"공휴일":None,"시험":None,
     "명절·세시":{"설날","정월대보름","삼짇날","단오","초복","중복","말복","칠석","추석(한가위)","섣달그믐","부처님오신날"},
     "24절기":{"입춘","동지"},
     "국가기념일":{"가정의 날","노인의 날","농업인의 날","김치의 날","부부의 날","성년의 날","소비자의 날","소상공인의 날","스승의 날","어버이날","식목일","환경의 날","스포츠의 날","문화의 날","화장품의 날","청년의 날","임산부의 날","고향사랑의 날"},
     "○○데이":{"밸런타인데이","화이트데이","블랙데이","로즈데이","빼빼로데이","가래떡데이","삼겹살데이","오겹살데이","육육데이","고기데이","구구데이","치킨데이","오리데이","갈비데이","구이데이","오삼데이","백숙데이","추어탕데이","삼치데이","참치데이","김밥데이","라면데이","김치데이","쌀데이","사과데이","오이데이","쿠키데이","아이스크림데이","커피데이","커플데이","친구데이","고백데이"}}
    c=c[c.apply(lambda r:r["종류"] in OK and (OK[r["종류"]] is None or r["이름"] in OK[r["종류"]]),axis=1)].copy()
    c.loc[c["종류"]=="○○데이","출처"]="민간에서 부르는 날(공식 지정 아님)"
    c=c[c["출처"]!=""]
    cal=c[["날짜","이름","종류","출처","기준일","확정 여부"]].values.tolist()
def menus(p):
    j=json.load(open(p,encoding="utf-8")); return dict(m=[[x["이름"],x["판매가"],x["원가"],1 if x.get("주력") else 0] for x in j["메뉴"]],ag=j.get("객단가"))
S={"고깃집":dict(name="시험 고깃집",who="일반 손님",ind="요식업",sub="고깃집",st="그랜드오픈",g=["신규손님","재방문","리뷰수"],bud=500000,liq="예",**menus(f"{B}/생성/원가입력_고깃집.json")),
   "카페":dict(name="시험 카페",who="일반 손님",ind="요식업",sub="카페",st="비수기",g=["비수기채우기","재방문"],bud=300000,liq="아니오",**menus(f"{B}/생성/원가입력_카페.json")),
   "미용실":dict(name="시험 미용실",who="일반 손님",ind="미용·뷰티",sub="미용실",st="정착기",g=["재방문","객단가"],bud=200000,liq="아니오",**menus(f"{B}/생성/원가입력_미용실.json"))}
import sys; sys.path.insert(0,os.path.dirname(os.path.abspath(__file__)))
from sms_pick import load as _sms
SMS=_sms()
if SMS:
    fix=lambda t:re.sub(r"O{2,4}\s?님","고객님",t)
    SMS["start"]=[[fix(t),m,o,f] for t,m,o,f in SMS["start"]]; SMS["end"]=[[fix(t),m,o,f] for t,m,o,f in SMS["end"]]
# 응용 예시: 숫자 금지, 판정은 근거 사례 중 가장 엄격, 안전운영조건·FAQ는 근거 사례 합집합
EXJ=json.load(open(f"{B}/spec/응용예시.json",encoding="utf-8"))["items"]
import glob as _g
for _f in sorted(_g.glob(f"{B}/spec/응용예시_*차.json")): EXJ+=json.load(open(_f,encoding="utf-8"))["items"]  # 판 9: 2차, 판 10: 3차·4차(안내형)
byid={c["i"]:c for c in C}
RANK={"가능":0,"조건부":1,"확인":2,"불가":3}
def rank(v): return next((RANK[k] for k in ("불가","확인","조건부","가능") if v.startswith(k)),1)
BADX=re.compile(r"국내 ?최초|최저가|업계 ?1위|원조|몸에 ?좋|건강에 ?좋|다이어트|숙취|노키즈|환불 ?불가|복권|로또|무제한|한 ?잔 ?더|마시자")
EX=[];errs=[]
for e in EXJ:
    txt=" ".join([e["n"],e["s"],e["c"],e["b"]])
    if re.search(r"\d",txt): errs.append(f"{e['id']}: 숫자 있음")
    if e.get("형")=="안내형" and re.search(r"할인|증정|경품|사은품|무료|공짜|덤|쿠폰|추첨|적립|캐시백|반값|특가",e["n"]+" "+e["b"]): errs.append(f"{e['id']}: 안내형에 가격 혜택·경품 말 있음")
    if re.search(r"효과|매출 (증가|상승)|늘었|올랐",txt): errs.append(f"{e['id']}: 효과 표현")
    if BADX.search(txt): errs.append(f"{e['id']}: 피해야 할 표현 {BADX.search(txt).group(0)}")
    bases=[byid.get(b) for b in e["base"]]
    if any(b is None for b in bases): errs.append(f"{e['id']}: 근거 사례 없음/제외 {e['base']}"); continue
    vs=[b["v"] for b in bases if b["v"]]; v=max(vs,key=rank) if vs else "확인 필요"
    v={0:"가능",1:"조건부 가능",2:"확인 필요",3:"불가(근거 사례가 불가 — 바꾼 안도 확인 필요)"}[rank(v)]
    so=" ／ ".join(dict.fromkeys(x for b in bases for x in b["so"].split(" ／ ") if x))
    f="|".join(dict.fromkeys(x for b in bases for x in re.findall(r"F0\d\d",b["f"])))
    lq=1 if e.get("liq") else 0   # 응용 예시는 지정한 것만(설명 속 "술은 넣지 않는다"는 오탐)
    EX.append(dict(i=e["id"],n=e["n"],s=e["s"],c=e["c"],b=e["b"],sub=e["sub"],stg=e["st"],v=v,so=so,f=f,lq=lq,bi=e["base"],ref=e.get("ref",[]),tm=e.get("tm",""),k="응용예시",kd="행사",hy=e.get("형","행사"),wh="일반 손님",fr=0,
      ev="응용 예시 — 근거 사례 "+"·".join("#"+str(b) for b in e["base"])+"의 판정 중 가장 엄격한 것을 따름",qb="근거 사례: "+" / ".join(f"#{b['i']} {b['v']}" for b in bases),
      up="",va="",rs="",sg="",du="",li="",kp="",br=bases[0]["br"],orr=bases[0]["orr"],rr=bases[0]["rr"],u="",co="",vs="",grp="",rep="",uc="",cr="",g="",t="",ind="",st="",na="",tm2=""))
if errs: raise SystemExit("응용 예시 검사 실패:\n"+"\n".join(errs))
print("응용 예시",len(EX),"검사 통과(숫자 0·효과 0·피해야 할 표현 0), 판정",{k:sum(1 for e in EX if e["v"].startswith(k)) for k in ("가능","조건부","확인","불가")},"술 표시 주의",sum(e["lq"] for e in EX))
LP=f"{B}/spec/법근거_판8.json"  # 판 8: 판 7 키 + 재확인 + 업종별 항목
LAW={x["key"]:x for x in json.load(open(LP,encoding="utf-8"))["items"]} if os.path.exists(LP) else {}
LINKF={"copy":"문구기준","deliv":"배달요금표","open":"개업순서표"}  # 다른 도구 파일: spec/연동/<이름>.json (docs/연동파일_칸설명서.md)
LINKD={k:json.load(open(f"{B}/spec/연동/{v}.json",encoding="utf-8")) for k,v in LINKF.items() if os.path.exists(f"{B}/spec/연동/{v}.json")}
IP=f"{B}/spec/업종_판8.json"
IND=json.load(open(IP,encoding="utf-8")) if os.path.exists(IP) else {}
# ── 판 10: 기본 행사 방식 축(spec/행사방식.json, scripts/methods10.py) — 사례마다 mt(방식 키 목록), 응용 예시는 같은 낱말 규칙으로
MTD={}
if os.path.exists(f"{B}/spec/행사방식.json"):
    _m=json.load(open(f"{B}/spec/행사방식.json",encoding="utf-8"))
    _by={m["키"]:set(m["사례"]) for m in _m["방식"]}
    for c in C: c["mt"]=[k for k,v in _by.items() if c["i"] in v]
    for e in EX: e["mt"]=[m["키"] for m in _m["방식"] if re.search(m["규칙"]," ".join([e["n"],e["b"],e["c"]]),flags=re.I)]
    MTD={"묶음":_m["묶음"],"기준":_m["기준"],"방식":[{k:v for k,v in m.items() if k not in ("사례","규칙")} for m in _m["방식"]]}
    # 판 11: 쿠폰 체감 기준선 — 할인·쿠폰 방식 실제 사례의 혜택 글에 나온 할인율(%) 분포(출처 = 이 사례 DB)
    _p=sorted(float(x) for c in C if c.get("k")=="실제" and set(c.get("mt",[]))&{"할인","쿠폰"} for x in re.findall(r"(\d{1,2}(?:\.\d)?)\s?%",c.get("b","")) if 0<float(x)<=90)
    if _p: MTD["할인율"]={"건":len(_p),"하위25":_p[len(_p)//4],"중앙":_p[len(_p)//2]}
# ── 판 9: 화면용 글 다듬기 — 「확인 필요」 같은 덜 만든 표시는 화면에 내지 않음(원본 자료·장부에는 그대로). 판정값 v는 화면에서 「신중」으로 표시(template vClass)
def _scr(t):
    if not isinstance(t,str) or ("확인 필요" not in t and "확인필요" not in t and "미확인" not in t): return t
    t=t.replace("확인필요","확인 필요")
    t=re.sub(r"[^./]*?(원문을 확보하지 못해|원문 미확인|원문이 없어|원문을 확인하지 못)[^./]*\.?","공식 해석이 없어 꼭 지킬 조건을 따르세요.",t)
    t=t.replace("사실 확인 필요","보도 내용 기준")
    t=re.sub(r"\s*\(\s*확인 필요\s*\)","",t)
    t=re.sub(r"\(([^()]*?)[,·]?\s*확인 필요\)",r"(\1 — 미리 물어보세요)",t)
    t=re.sub(r"\s*[—-]+\s*확인 필요","",t)
    t=re.sub(r"(인지|는지|할지|될지)는? 확인 필요",r"\1 미리 물어보세요",t)
    t=re.sub(r"그래도 확인 필요","그래도 미리 물어보세요",t)
    t=t.replace("확인 필요","미리 확인하세요").replace("미확인","확인 전")
    return t
def _walk(o,skip=("v",)):
    if isinstance(o,dict): return {k:(v if k in skip else _walk(v,skip)) for k,v in o.items()}
    if isinstance(o,list): return [_walk(v,skip) for v in o]
    return _scr(o)
for x in C: x.update(_walk({k:v for k,v in x.items()}))
EX=[_walk(e) for e in EX]
F={k:_walk(v) for k,v in F.items()}
IND=_walk(IND,skip=())
LAW={k:{kk:(_scr(vv) if kk=="gist" else vv) for kk,vv in v.items() if kk in ("law","art","gist","num","key")} for k,v in LAW.items()}
# ── 판 9: 공개판(광고·유료 예정)은 출처 모르는 값·상업 이용 금지 자료를 뺌(spec/자료장부.json). 사용: build_preview.py --공개판 → preview/행사안_공개판.html
PUB="--공개판" in sys.argv
if PUB:
    _n=len(C);C=[c for c in C if not (c.get("k")=="실제" and not c.get("u"))];print("공개판: 출처 주소 없는 실제 사례",_n-len(C),"건 뺌")
IQ=json.load(open(f"{B}/spec/업종질문_판10.json",encoding="utf-8")) if os.path.exists(f"{B}/spec/업종질문_판10.json") else {}  # 판 10 업종 전용 질문
SETF=json.load(open(f"{B}/spec/설정.json",encoding="utf-8")) if os.path.exists(f"{B}/spec/설정.json") else {}  # 판 11 설정값
DATA=dict(set=SETF,iq=IQ,mtd=MTD,link=LINKD,ind8=IND,law=LAW,ex=EX,sms=SMS,all=ALL,nex=NEX,nbl=NBL,cases=C,faq=F,bank=bank,cal=cal,samples=S,built=pd.Timestamp.now(tz="Asia/Seoul").strftime("%Y-%m-%d"))
js=json.dumps(DATA,ensure_ascii=False,separators=(",",":")).replace("</","<\\/")
tpl=open(f"{B}/preview/template.html",encoding="utf-8").read()
out=tpl.replace("/*__DATA__*/null",js)
plus="\n".join(open(f"{B}/preview/{n}",encoding="utf-8").read() for n in ("vendor_qrcode.js","plus7.js","link8.js","ind8.js","method10.js","coupon10.js","plan11.js","qa11.js","set9.js") if os.path.exists(f"{B}/preview/{n}")).replace("</","<\\/")
out=out.replace("/*__PLUS__*/",plus)
open(f"{B}/preview/"+("행사안_공개판.html" if PUB else "행사안_미리보기.html"),"w",encoding="utf-8").write(out)
print("사례",len(C),"FAQ",len(F),"문구",len(bank),"달력",len(cal),"크기",len(out.encode())//1024,"KB")
