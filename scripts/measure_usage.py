#!/usr/bin/env python3
"""세션 기록(jsonl)에서 토큰 사용량을 실측한다. 사용: measure_usage.py <세션 jsonl> [이름] [시작 문구] — 시작 문구가 든 첫 사용자 메시지부터만 센다(이번 회차만 재기)
- 응답(message id) 하나를 한 번만 센다(같은 응답이 여러 줄로 나뉘어 있어도 마지막 usage 하나만).
- 응답당 다시 읽는 양 = input_tokens + cache_read_input_tokens + cache_creation_input_tokens
- 새 창 이동 기준(숫자): 다시 읽는 양이 25만 이상이면 인계 준비, 40만 이상이면 회차 끝에 이동.
기록 파일이 없거나 usage가 없으면 '측정 불가'를 출력한다(추정값을 쓰지 않음)."""
import sys,json,os,csv,datetime
if len(sys.argv)<2 or not os.path.exists(sys.argv[1]): print("측정 불가: 세션 기록 파일이 없음"); sys.exit(3)
last={}; order=[]; MARK=sys.argv[3] if len(sys.argv)>3 else None; started=MARK is None
for l in open(sys.argv[1],encoding="utf-8"):
    try: o=json.loads(l)
    except ValueError: continue
    if not started and isinstance(o,dict) and o.get("type")=="user":
        c=(o.get("message") or {}).get("content")
        t=c if isinstance(c,str) else " ".join(x.get("text","") for x in c if isinstance(x,dict)) if isinstance(c,list) else ""
        if MARK in t: started=True
    if not started: continue
    m=o.get("message") if isinstance(o,dict) else None
    if not isinstance(m,dict) or o.get("type")!="assistant": continue
    u=m.get("usage")
    if not u: continue
    mid=m.get("id") or o.get("uuid")
    if mid not in last: order.append(mid)
    last[mid]=u
if not last: print("측정 불가: usage 기록이 없음"); sys.exit(3)
def g(u,k): return int(u.get(k) or 0)
rows=[(g(u,"input_tokens"),g(u,"cache_read_input_tokens"),g(u,"cache_creation_input_tokens"),g(u,"output_tokens")) for u in (last[i] for i in order)]
reread=[a+b+c for a,b,c,_ in rows]
tot=lambda k:sum(r[k] for r in rows)
print(f"응답 {len(rows)}개(응답 하나를 한 번만 셈)")
print(f"입력 새로 {tot(0):,} / 캐시 읽기 {tot(1):,} / 캐시 쓰기 {tot(2):,} / 출력 {tot(3):,} 토큰")
print(f"25만 이상인 응답 {sum(x>=250000 for x in reread)}개, 40만 이상인 응답 {sum(x>=400000 for x in reread)}개")
print(f"응답당 다시 읽는 양: 평균 {sum(reread)//len(reread):,} / 최대 {max(reread):,} / 마지막 {reread[-1]:,}")
st="인계 준비 기준(25만) 미만"
if reread[-1]>=400000: st="40만 이상 — 이번 회차 끝에 새 창으로 이동"
elif reread[-1]>=250000: st="25만 이상 — 인계 준비 시작"
print("판정(마지막 응답 기준):",st)
if len(sys.argv)>2:
    hp="reports/사용량_이력.csv"; new=not os.path.exists(hp)
    with open(hp,"a",encoding="utf-8-sig",newline="") as f:
        w=csv.writer(f)
        if new: w.writerow(["측정 시각","이름","응답 수","입력 새로","캐시 읽기","캐시 쓰기","출력","응답당 다시 읽는 양 평균","최대","마지막","판정"])
        w.writerow([datetime.datetime.now().strftime("%Y-%m-%d %H:%M"),sys.argv[2],len(rows),tot(0),tot(1),tot(2),tot(3),sum(reread)//len(reread),max(reread),reread[-1],st])
