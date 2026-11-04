#!/usr/bin/env python3
"""판 8 업종 자료 만들기: 보조 조사 결과(업종A·업종B 결과.json)와 법 재확인(법확인8)을 합쳐
spec/업종_판8.json(화면 업종 조정)과 spec/법근거_판8.json(판 7 키 + 새 키)을 만든다. 새로 받은 법령은 law_src/로 복사.
사용: python3 -I scripts/make_ind8.py <scratchpad 폴더>"""
import sys,json,os,shutil,glob,re
B=os.path.dirname(os.path.dirname(os.path.abspath(__file__)));S=sys.argv[1]
law=json.load(open(f"{B}/spec/법근거_판7보관.json",encoding="utf-8"));items={x["key"]:x for x in law["items"]}
def rd(p):
    p=f"{S}/{p}";return json.load(open(p,encoding="utf-8")) if os.path.exists(p) else None
A,Bb,L=rd("업종A/결과.json"),rd("업종B/결과.json"),rd("법확인8/결과.json")
# 1) 확인 필요 재확인 결과로 덮어쓰기(같은 키) 또는 새 키
if L:
    for x in (L if isinstance(L,list) else L.get("items",[])):
        old=items.get(x["key"],{});y=dict(old);y.update({k:v for k,v in x.items() if v not in (None,"")});y["판8"]="재확인";items[x["key"]]=y
# 2) 업종 항목
SRC=[]
for R in (A,Bb):
    if not R: continue
    for x in R.get("items",[]): x=dict(x);x["판8"]="업종";items[x["key"]]=x;SRC.append(x)
# 3) 새로 받은 법령 복사(이미 있으면 그대로)
n=0
for d in ("법확인8","업종A","업종B"):
    for f in glob.glob(f"{S}/{d}/law_src_new/**/*.txt",recursive=True):
        rel=os.path.relpath(f,f"{S}/{d}/law_src_new");t=f"{B}/law_src/{rel}"
        if not os.path.exists(t): os.makedirs(os.path.dirname(t),exist_ok=True);shutil.copy(f,t);n+=1
law["기준"]="law_src 원문 대조(판 7 2026-11-04) + 판 8 재확인·업종별 항목(2026-11-04)";law["items"]=list(items.values())
json.dump(law,open(f"{B}/spec/법근거_판8.json","w",encoding="utf-8"),ensure_ascii=False,indent=1)
# 4) 업종 조정 자료: 화면 업종(6개) 안에서 세부 업종 낱말로 고름
TOOLK={"coupon":r"할인|유인|쿠폰|가격|요금|교습비|진료비|본인부담|덤핑|저가","review":r"후기|리뷰|경험담|추천|체험|전후","infl":r"후기|체험단|추천|경험담|인플루언서|협찬","draw":r"경품|사은품|추첨|증정|분양|금품","regular":r"회원|선불|이용권|정기|환불|개인정보|민감","open":r"광고|심의|게시|표시|등록|신고"}
SUBRE={"학원":(["학원·교육"],r"학원|교습|공부방|과외|도장|태권|스터디"),"병의원":(["병의원·약국"],r"병원|의원|치과|한의|안과|피부과|내과"),"약국":(["병의원·약국"],r"약국"),
 "안경원":(["병의원·약국","소매"],r"안경"),"동물병원":(["병의원·약국"],r"동물병원"),"미용":(["미용·뷰티"],r"미용|헤어|네일|피부관리|왁싱|이발|바버|체형"),
 "체육시설":(["서비스업","학원·교육"],r"헬스|필라테스|요가|체육|도장|피트니스"),"반려동물":(["서비스업","소매"],r"반려")}
BASE={"학원":dict(술=False,배달=False,말={"주력 메뉴 원가율":"주력 강좌 원가율(교재·재료)","메뉴":"강좌"},쿠폰예="무료 체험 수업 1회(교습비 게시 그대로)",위험="상"),
 "병의원":dict(술=False,배달=False,말={"주력 메뉴 원가율":"주력 진료 원가율","메뉴":"진료"},쿠폰예="",위험="상"),
 "약국":dict(술=False,배달=False,말={"메뉴":"상품"},쿠폰예="",위험="상"),"안경원":dict(술=False,배달=False,말={"메뉴":"상품"},쿠폰예="시력 검사 안내(가격 할인 아님)",위험="중"),
 "동물병원":dict(술=False,배달=False,말={"메뉴":"진료"},쿠폰예="",위험="상"),"미용":dict(술=False,배달=False,말={"주력 메뉴 원가율":"주력 시술 원가율(약제·소모품)","메뉴":"시술"},쿠폰예="첫 방문 커트 손님 트리트먼트 1회",위험="중"),
 "체육시설":dict(술=False,배달=False,말={"주력 메뉴 원가율":"이용권 원가율","메뉴":"이용권"},쿠폰예="1일 체험권",위험="중"),"반려동물":dict(술=False,말={"메뉴":"상품·서비스"},쿠폰예="목욕 1회 추가",위험="중")}
def prof(u,its,base):
    p=dict(base);p["이름"]=u.get("이름") or u["id"];p["막을행사"]=u.get("막아야 할 행사",[])[:8];p["바꿀행사"]=u.get("바꿔 쓸 행사",[])[:6]
    p["어색"]=u.get("요식업 화면에서 어색한 점",[]);p["법"]=[x["key"] for x in its]
    p["한줄"]=(its[0].get("screen") if its else "")or""
    p["도구법"]={t:[x["key"] for x in its if re.search(rx,x["key"]+x.get("gist",""))][:6] for t,rx in TOOLK.items()}
    p["도구경고"]={t:v[0] for t,v in {t:[x.get("screen","") for x in its if re.search(rx,x["key"]) and x.get("screen")] for t,rx in TOOLK.items()}.items() if v}
    return p
OUT={"기준":law["기준"],"세부":[],"업종":{}}
for R in (A,Bb):
    if not R: continue
    for u in R.get("업종",[]):
        m0=SUBRE.get(u["id"]) or (u.get("화면업종"),u.get("세부정규식"))
        toks=[t for t in re.split(r"[·,()\s/]+",(u.get("이름") or "")+" "+" ".join(u.get("포함",[]))) if len(t)>=2 and t not in ("가게","판매점","사무소")]
        rx=re.compile("|".join(map(re.escape,toks)) or "^$")
        def hit(x):
            i=x.get("ind") or ""
            if i==u["id"] or "모든 가게" in i: return True
            if "소매 공통" in i: return bool(m0 and m0[0] and "소매" in m0[0])
            return bool(rx.search(i))
        its=[x for x in R.get("items",[]) if hit(x)]
        f0=toks[0] if toks else "#"
        its.sort(key=lambda x:("공통" in (x.get("ind") or "") or "모든 가게" in (x.get("ind") or ""), f0[:2] not in (x.get("ind") or "")))  # 업종 고유 항목 먼저, 이름 첫 낱말 든 것 먼저
        m=SUBRE.get(u["id"]) or (u.get("화면업종"),u.get("세부정규식"))
        if not m or not m[0]: print("화면 업종 연결 없음:",u["id"]);continue
        p=prof(u,its,BASE.get(u["id"],u.get("기본",{})));p["ind"]=m[0];p["re"]=m[1];OUT["세부"].append(p)
json.dump(OUT,open(f"{B}/spec/업종_판8.json","w",encoding="utf-8"),ensure_ascii=False,indent=1)
print("법 근거",len(items),"키(판 7",len(json.load(open(f'{B}/spec/법근거_판7보관.json',encoding='utf-8'))['items']),") · 업종 세부",len(OUT["세부"])," · 새 법령 복사",n)
