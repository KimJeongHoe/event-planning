#!/usr/bin/env python3
"""캘린더 도구(지식 달력)가 준 jisik-dates CSV → 생성/캘린더.csv (이 도구가 읽는 칸으로 바꿈). 날짜는 만들지 않고 받은 값만 옮긴다.
사용: import_calendar.py <jisik-dates csv>
- 행사 기획과 관계 있는 종류만: 공휴일·명절·국가기념일·○○데이·시험·세무·절기. 외국 국경일·일본·세계·기타 기념일은 뺀다.
- 확정 여부: trust가 law/agency면 확정, 그 밖(list·folk·unverified)은 예정(행사안에 예정으로 표시).
- 출처: basis(없으면 source_url). 둘 다 비면 출처 빈칸 → pick_cases가 쓰지 않는다."""
import sys,os,pandas as pd
B=os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
d=pd.read_csv(sys.argv[1],dtype=str,encoding="utf-8-sig").fillna("")
KEEP={"holiday","folk","national","day","exam","tax","tax_term","term"}
d=d[d.kind.isin(KEEP)].copy()
o=pd.DataFrame({"날짜":d.date,"이름":d.name,"종류":d.kind_ko,"지역 범위":d.scope_ko,
 "출처":d.apply(lambda r:r.basis or r.source_url,axis=1),"기준일":d["asof"],
 "확정 여부":d.trust.map(lambda t:"확정" if t in("law","agency") else "예정"),"신뢰":d.trust,"휴일 여부":d.day_off})
o.to_csv(f"{B}/생성/캘린더.csv",index=False,encoding="utf-8-sig")
print("저장",len(o),"행 / 확정",(o["확정 여부"]=="확정").sum(),"/ 예정",(o["확정 여부"]=="예정").sum(),"/ 출처 빈칸",(o["출처"]=="").sum(),"/ 종류",o["종류"].value_counts().to_dict())
