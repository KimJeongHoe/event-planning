#!/usr/bin/env python3
"""생성 결과 검사(check_plan.py)가 실제로 잡는지 보는 시험. 멀쩡한 행사안에 일부러 문제 문구를 넣은 '고장 사본'을 매번 새로 만들어 돌린다.
통과 기준: 고장 사본은 모두 경고(종료 1) 또는 검사 대상 없음(종료 2)이어야 하고, 멀쩡한 사본은 0이어야 한다. 하나라도 어긋나면 종료 1.
지난 결과를 쓰지 않는다(매번 새로 만들어 돌림). 시험 건수가 기대보다 적으면 실패. 결과는 reports/시험_이력.csv에 쌓는다."""
import subprocess,tempfile,os,sys,csv,datetime
B,P,C="생성/행사안_고깃집.md","생성/참고묶음_요식업_그랜드오픈.md","생성/계산결과_시험_고깃집.md"
for f in (B,P,C):
    if not os.path.exists(f): sys.exit(f"시험 실패(멈춤): {f} 없음")
base=open(B,encoding="utf-8").read()
def rep(a,b): 
    def f(t):
        assert a in t, f"시험 재료를 못 찾음: {a[:20]}"; return t.replace(a,b,1)
    return f
def cut(t): return "\n".join(l for l in t.split("\n") if not l.startswith("- 안전운영조건(사례 389"))
CASES=[
 ("광고 문구에 술 증정",rep('① "5인분 이상 단체 손님께 껍데기와 음료 서비스"','① "5인분 이상이면 소주 1병 서비스"'),1),
 ("광고 문구에 술 할인",rep('③ "회식·모임 단체 예약 받아요"','③ "오픈 기념 소주 반값 특가 2,000원 현수막"'),1),
 ("음주 권유 문구",rep('② "단체 예약 환영, 5인분 이상이면 사이드 한 접시"','② "오늘은 취하자, 맥주 한 잔 더 마시자 문구"'),1),
 ("술 건강 효과 문구",rep('③ "오픈 인사드립니다. 선착순 20테이블, 껍데기 한 접시"','③ "숙취 해소에 좋은 막걸리 SNS 문구"'),1),
 ("지어낸 원가율·본전",rep("1회 원가: 400원 (","1회 원가: 350원, 원가율 31%, 본전 필요 추가 손님 7명 ("),1),
 ("안전운영조건 빠짐",cut,1),
 ("짧은 본문(검사 대상 없음)",lambda t:"# 행사안\n껍데기 서비스 한다.\n",2),
 ("원안 표시 없는 술 서비스",rep("(사례 389 원안)",""),1),
 ("최저가·노키즈",rep("## 안 3.","- 노키즈존으로 운영하고 동네 최저가 보장\n## 안 3."),1),
 ("멀쩡한 사본(통과해야 함)",lambda t:t,0),
]
rows=[];bad=0
with tempfile.TemporaryDirectory() as d:
    for i,(name,fn,want) in enumerate(CASES,1):
        fp=os.path.join(d,f"{i}.md"); open(fp,"w",encoding="utf-8").write(fn(base))
        r=subprocess.run([sys.executable,"scripts/check_plan.py",fp,P,C],capture_output=True,text=True)
        ok=(r.returncode==want); bad+=0 if ok else 1
        n=sum(1 for l in r.stdout.split("\n") if l.startswith(" -"))
        rows.append((name,want,r.returncode,n,"맞음" if ok else "어긋남"))
        print(f"{'맞음  ' if ok else '어긋남'} {name}: 기대 종료 {want}, 실제 {r.returncode}, 경고 {n}건")
# 참고 묶음이 없으면 통과로 치지 않는지
r=subprocess.run([sys.executable,"scripts/check_plan.py",B],capture_output=True,text=True)
ok=(r.returncode==1); bad+=0 if ok else 1; rows.append(("참고 묶음·계산 결과 없이 돌림(통과로 치면 안 됨)",1,r.returncode,0,"맞음" if ok else "어긋남"))
print(f"{'맞음  ' if ok else '어긋남'} 참고 묶음·계산 결과 없이 돌림: 기대 종료 1, 실제 {r.returncode}")
assert len(rows)==len(CASES)+1
os.makedirs("reports",exist_ok=True); new=not os.path.exists("reports/시험_이력.csv")
with open("reports/시험_이력.csv","a",encoding="utf-8-sig",newline="") as f:
    w=csv.writer(f)
    if new: w.writerow(["시각","시험 건수","어긋남","비고"])
    w.writerow([datetime.datetime.now().strftime("%Y-%m-%d %H:%M"),len(rows),bad,"check_plan 고장 사본 시험"])
print(f"\n시험 {len(rows)}건, 어긋남 {bad}건"); sys.exit(1 if bad else 0)
