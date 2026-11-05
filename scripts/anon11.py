#!/usr/bin/env python3
"""판 11: 사례 실명 빼기·행사 방식 분류 결과(보조 작업 결과*.jsonl)를 모아
spec/사례_익명.json(손님 화면·내보내기용으로 바꾼 글), spec/사례_방식.json(사례 DB 「행사방식」 칸 값),
spec/업체명_사전.json(새는지 검사할 원래 이름 목록)을 만든다. 원본 raw·사례DB는 고치지 않는다(관리자판은 원래 이름).
사용: python3 -I scripts/anon11.py <결과 폴더>"""
import json,sys,os,glob,re
B=os.path.dirname(os.path.dirname(os.path.abspath(__file__)));S=sys.argv[1]
KEYS={m["키"] for m in json.load(open(f"{B}/spec/행사방식.json",encoding="utf-8"))["방식"]}
FMAP={"name":"n","summary":"s","condition":"c","benefit":"b","staging":"sg","variants":"va"}
orig={int(json.loads(l)["id"]):json.loads(l) for l in open(f"{B}/merged/사례DB.jsonl",encoding="utf-8")}
an,me,terms,bad={}, {}, set(), []
for f in sorted(glob.glob(f"{S}/결과*.jsonl")):
    for l in open(f,encoding="utf-8"):
        l=l.strip()
        if not l: continue
        try: o=json.loads(l)
        except ValueError: bad.append(f"{os.path.basename(f)}: JSON 아님"); continue
        i=int(o["id"]);me[i]=[k for k in (o.get("method") or []) if k in KEYS]
        a={FMAP[k]:o[k] for k in FMAP if isinstance(o.get(k),str) and o[k].strip() and o[k]!=orig.get(i,{}).get(k)}
        rep=[[x,y] for x,y in (o.get("replace") or []) if isinstance(x,str) and len(x.strip())>=2 and x!=y]
        if rep: a["rep"]=rep
        if o.get("closed_fix"): a["closed"]=True
        if a: an[i]=a
        for x,_ in rep: terms.add(x.strip())
miss=sorted(set(orig)-set(me))
# 이름 칸에서 사라진 영문·따옴표 고유명도 사전에 넣음(바꾼 이름 칸과 원래 이름 칸을 비교)
for i,a in an.items():
    if "n" in a:
        o=orig[i].get("name","")
        for t in re.findall(r"[A-Za-z][A-Za-z&'.\-]{2,}(?: [A-Z][A-Za-z&'.\-]+)*|[「'‘\"]([^」'’\"]{2,15})[」'’\"]",o):
            t=t if isinstance(t,str) else t[0]
            if t and t not in a["n"]: terms.add(t)
# 업체 실명이 아닌 것(공공 사업·프로그램 이름, 달력 도구의 날 이름, 일반 낱말, 자선단체) — 검사에서 뺌
GEN={"알림톡","배달특급","제로페이","좋은이웃가게","빼빼로데이","빼빼로","달고나","플레이스 노출","구세군","서울","부산","대구","인천","광주","대전","울산","세종","경기","강원","충북","충남","전북","전남","경북","경남","제주","한국","일본","미국","영국","중국","SNS","QR","PC","POS","CU","BTS","FIFA"}
PLAT=re.compile(r"인스타|카카오|카톡|네이버|배민|배달의민족|쿠팡|요기요|당근|비즈프로필|페이스북|유튜브|유튜버|LINE|라인|스마트스토어|기프티콘|틱톡|구글|SKT|KT|LG")
terms=sorted(t for t in terms if t not in GEN and not re.fullmatch(r"[\d\W]+",t) and not re.search(r"\d|폐업|폐점|폐원",t) and not PLAT.search(t))  # 플랫폼은 build의 PLAT 바꾸기·사례 전용 검사로
json.dump({"_설명":"판 11 손님 화면·내보내기용 사례 글. 원본(merged/사례DB)은 관리자판에서만. 칸: n 이름, s 한줄설명, c 조건, b 혜택, sg 연출, va 변형안, rep 나머지 칸 바꿀 짝, closed 폐업 단정 고침","사례":{str(k):v for k,v in sorted(an.items())}},open(f"{B}/spec/사례_익명.json","w",encoding="utf-8"),ensure_ascii=False,indent=0)
json.dump({"_설명":"판 11 사례 DB 「행사방식」 칸(보조 판단으로 분류, 키는 spec/행사방식.json)","사례":{str(k):v for k,v in sorted(me.items())}},open(f"{B}/spec/사례_방식.json","w",encoding="utf-8"),ensure_ascii=False,indent=0)
json.dump({"_설명":"판 11 새는지 검사할 원래 업체·브랜드·장소 이름(관리자 전용). 손님판·공개판·내보내기에 하나라도 나오면 만들기가 멈춤","이름":terms},open(f"{B}/spec/업체명_사전.json","w",encoding="utf-8"),ensure_ascii=False,indent=0)
print("결과 사례",len(me),"바꾼 사례",len(an),"폐업 단정 고침",sum(1 for a in an.values() if a.get("closed")),"사전 이름",len(terms),"빠진 사례",len(miss),"읽기 오류",len(bad))
