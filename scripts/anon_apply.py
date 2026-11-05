#!/usr/bin/env python3
"""판 11: 사례 실명 빼기 공용 함수 — 손님판·공개판·다른 도구에 넘기는 파일이 같은 규칙을 쓰게 함.
spec/사례_익명.json(사례별 바꾼 글·바꿀 짝) + 플랫폼 이름 일반화, 출처 주소·메모 칸 비움. 관리자판·원본 DB는 이 함수를 쓰지 않음."""
import json,os
B=os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
_AN=json.load(open(f"{B}/spec/사례_익명.json",encoding="utf-8"))["사례"] if os.path.exists(f"{B}/spec/사례_익명.json") else {}
PLATR=[("인스타그램","SNS"),("인스타","SNS"),("카카오톡 채널","메신저 채널"),("카카오톡","메신저"),("카카오","메신저"),("카톡","메신저"),("네이버 스마트플레이스","지도 앱"),("네이버 플레이스","지도 앱"),("네이버 예약","예약 앱"),("네이버","포털"),("배달의민족","배달앱"),("배민","배달앱"),("쿠팡이츠","배달앱"),("요기요","배달앱"),("쿠팡","온라인 쇼핑몰"),("당근 비즈프로필","동네 앱 가게 소식"),("당근마켓","동네 앱"),("당근","동네 앱"),("페이스북","SNS"),("유튜버","영상 제작자"),("유튜브","영상 SNS"),("기프티콘","모바일 상품권"),("틱톡","짧은 영상 SNS"),("스마트스토어","온라인 쇼핑몰"),("LINE","메신저"),("트위터","SNS")]
RAWMAP={"n":"name","s":"summary","c":"condition","b":"benefit","sg":"staging","va":"variants"}
HIDE=("source_urls","source_flag","source_dates","source_types","notes","verify_note","src_file","orig_id","district")
def anon_raw(r):
    """원본 칸 이름(영문 키) 사례 한 건을 바꾼 사본으로 돌려줌"""
    r=dict(r);a=_AN.get(str(r.get("id")),{})
    for k,f in RAWMAP.items():
        if k in a: r[f]=a[k]
    for k,v in list(r.items()):
        if not isinstance(v,str) or k in HIDE: continue
        for x,y in a.get("rep",[]): v=v.replace(x,y)
        for x,y in PLATR: v=v.replace(x,y)
        r[k]=v
    for k in HIDE:
        if k in r: r[k]=""
    return r

# 사례에서 모은 「원래 이름 → 일반 표현」 짝(가장 먼저 나온 것). FAQ·안내 글 속 처분·사례 예시의 업체 이름에 씀(플랫폼·정책 이름은 그대로)
GMAP={}
for _a in _AN.values():
    for x,y in _a.get("rep",[]): GMAP.setdefault(x,y)
GMAP.setdefault("비알코리아","대형 프랜차이즈 본사")
def anon_text(t):
    if not isinstance(t,str): return t
    for x in sorted(GMAP,key=len,reverse=True):
        if x in t and not any(p in x for p,_ in PLATR): t=t.replace(x,GMAP[x])
    return t
