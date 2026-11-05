#!/usr/bin/env python3
"""판 11: 규칙 문서를 코드·설정에서 자동으로 만든다 → docs/규칙_자동.md, docs/화면밖_확인필요_장부.md
손으로 고치지 말고 이 스크립트를 다시 돌린다. 사용: python3 -I scripts/rules_doc.py"""
import json,os,re,datetime
B=os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
J=lambda p:json.load(open(f"{B}/{p}",encoding="utf-8"))
today=datetime.datetime.now(datetime.timezone(datetime.timedelta(hours=9))).date().isoformat()
T=open(f"{B}/preview/template.html",encoding="utf-8").read();P7=open(f"{B}/preview/plus7.js",encoding="utf-8").read()
M=J("spec/행사방식.json");S=J("spec/설정.json");Q=J("spec/업종질문_판10.json")
L=[f"# 규칙 문서(자동 생성, {today})","","scripts/rules_doc.py가 코드·설정에서 뽑아 만든 문서입니다. 고칠 때는 아래 「원본」 파일을 고친 뒤 다시 만듭니다.",""]
L+=["## 1. 기본 행사 방식(원본: scripts/methods10.py → spec/행사방식.json)","",f"- 실제 사례 {M['기준']['실제사례']}건 기준, 어느 방식에도 안 드는 사례 {M['기준']['어느방식에도안듦']}건","","| 묶음 | 방식 | 실제 사례 | 비중 | 지킬 법 키 |","|---|---|---|---|---|"]
L+=[f"| {m['묶음']} | {m['이름']} | {m['실제']} | {m['비중']}% | {', '.join(m['법'])} |" for m in M["방식"]]
L+=["","## 2. 홍보 글 표현 검사(원본: preview/template.html check())",""]
for pat in re.findall(r"\[/(.+?)/,\"([^\"]+)\"\]",T): L.append(f"- `{pat[0][:80]}` → {pat[1]}")
pro=re.search(r"const PRO=/(.+?)/g",T);L.append(f"- 술과 가까이(26자 안) 나오면 경고하는 혜택 낱말: `{pro.group(1) if pro else ''}`")
L.append("- 「※」로 시작하는 줄은 이 도구가 넣은 안내·부인 문장이라 검사하지 않음")
L+=["","## 3. 세부 업종 → 응용 예시 업종(원본: template SUBMAP, 앞에서부터 처음 맞는 것)",""]
sm=re.search(r"const SUBMAP=s=>\{const R=(\[.*?\]\]);",T)
if sm:
    for a,b in re.findall(r"\[/(.+?)/,\"(.+?)\"\]",sm.group(1)): L.append(f"- `{a}` → {b}")
L+=["","## 4. 업종 전용 질문(원본: spec/업종질문_판10.json)",""]+[f"- ({q['re']}) {q['q']} → 「예」면: {q['예']}" for q in Q["질문"]]
L+=["","## 5. 설정값(원본: spec/설정.json)",""]
L+=[f"- 생성 모델: 사용 {S['AI']['사용']}, 모델 {S['AI']['모델']}",f"- 조회 제한: 하루 사례 보기 {S['조회제한']['하루_사례_보기']}건, 한 번 목록 {S['조회제한']['한번_목록']}건",f"- 백업 권장: {S['백업_권장_일수']}일"]
L+=["","## 6. 꺼 둔 기능(원본: spec/설정.json 끈기능, preview/set9.js)","","| 번호 | 이름 | 이유 | 켜는 조건 |","|---|---|---|---|"]+[f"| {x['번호']} | {x['이름']} | {x['이유']} | {x['켜는 조건']} |" for x in S["끈기능"]]
L+=["","## 7. 실명 빼기(원본: scripts/anon11.py·anon_apply.py, spec/사례_익명.json, spec/업체명_사전.json)","","- 실패·성공 사례 속 가게·업체 이름만 일반 표현(업종·규모·상권 유형)으로. 법령·고시·심사지침, 플랫폼 운영정책·약관 이름, 기관·공공 사업명, 출처 표기는 그대로",
 "- 사례 글 속 플랫폼 이름은 일반 표현(배달앱·메신저·지도 앱·동네 앱·SNS)으로, 우리 안내 글·FAQ·법 근거의 채널·정책 이름은 그대로",
 "- 사례 출처 주소는 관리자판(`build_preview.py --관리자판`)에만. 손님판·공개판·다른 도구용 파일에 사전 이름이 나오면 만들기가 멈춤",
 f"- 업체명 사전 {len(J('spec/업체명_사전.json')['이름'])}개, 실명을 바꾼 사례 {len(J('spec/사례_익명.json')['사례'])}건"]
open(f"{B}/docs/규칙_자동.md","w",encoding="utf-8").write("\n".join(L)+"\n")
# 화면 밖 확인 필요 장부
LAW=J("spec/법근거_판8.json")["items"]+(J("spec/법근거_판11_추가.json")["items"] if os.path.exists(f"{B}/spec/법근거_판11_추가.json") else [])
U=[x for x in LAW if x.get("status")!="확인함"];C=sorted(set(re.findall(r'CONFIRM\("([^"]+)"\)',P7)))
V=[x for x in J("spec/영상사례_판11.json")["items"]] if os.path.exists(f"{B}/spec/영상사례_판11.json") else []
O=[f"# 화면 밖 「확인 필요」 장부(자동 생성, {today})","","사장님 화면에는 덜 만든 표시를 내지 않는다. 화면은 안전한 쪽(하지 않기·미리 물어보기·꼭 지킬 조건)만 보여 주고, 미확인 쟁점은 여기와 법 근거 파일 status에만 둔다. 질의 문안: docs/질의문안_판10_목록.md(제출은 하지 않음).","",
 f"## 1. 법 근거 중 원문으로 확정하지 못한 것({len(U)}건)","","| 키 | 법·지침 | 조문 | 이유 |","|---|---|---|---|"]+[f"| {x['key']} | {x.get('law','')} | {x.get('art','')} | {(x.get('note') or '').replace('|','/')[:180]} |" for x in U]
O+=["",f"## 2. 화면 도구에서 뺀 쟁점({len(C)}건)",""]+[f"- {c}" for c in C]
O+=["",f"## 3. 영상 사례(주장) {len(V)}건 — 실제 사례 비중에서 빼고 공개판에서도 뺌","",*[f"- {v['id']} {v['이름']} — 판정 {v['진행여부']}" for v in V]]
open(f"{B}/docs/화면밖_확인필요_장부.md","w",encoding="utf-8").write("\n".join(O)+"\n")
print("규칙 문서·장부 만듦: 미확인 법",len(U),"도구 쟁점",len(C),"영상",len(V))
