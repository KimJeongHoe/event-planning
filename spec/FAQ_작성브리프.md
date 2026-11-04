# FAQ 답 작성 브리프 (2026-11-02)

목표: spec/속성설명서.md 3절의 FAQ 질문(F001~F050) 중 맡은 번호의 답을 쓴다. 모든 칸을 채운다.

## 근거 원칙 (가장 중요)
- 법 근거는 **법령·고시 원문에서 직접 확인한 조항만** 쓴다. 원문은 `law_src/*.txt`(국가법령정보센터 본문, 첫 줄에 원문 URL)에 있다.
  - 조문 보기: `python3 -I scripts/art.py "<파일이름 일부>" <조번호> [최대글자]` (예: `art.py 여신전문금융업법 19`)
  - 없는 법령·고시 받기: `python3 -I scripts/lawfetch.py law_src 법령|행정규칙 "<정확한 이름>"` (이름이 틀리면 '실패'. 이름을 바꿔 다시 시도하거나 WebSearch로 정확한 이름을 찾는다)
  - 별표(과태료 금액표 등)는 본문에 없을 수 있다. 원문에서 못 본 수치는 쓰지 말고 "확인 필요".
- 처분·판례·유권해석은 원문(기사·보도자료·판결 페이지)을 **직접 열어** 확인한 것만 쓴다: `python3 -I scripts/fetchtext.py "<URL>" 4000`. 검색 결과 요약만으로 쓰지 않는다. WebSearch는 원문 URL을 찾는 용도로만 쓴다.
- 확실하지 않으면 verdict를 "확인 필요"로 하거나, 해당 부분에 "확인 필요"를 적는다. 단정 금지.
- 막힌 사이트(우회 금지, 시도 결과를 로그에 적기): ftc.go.kr, nts.go.kr, mfds.go.kr, ppc.go.kr, kipo.go.kr, donga.com, ce.baemin.com, web.archive.org, mk.co.kr, kukinews.com, i-boss.co.kr, qsrmagazine.com, squareup.com. 그 밖에 새로 막힌 곳(응답 코드 000/403/429/5xx)도 로그에 적는다. 프록시·미러·캐시로 우회하지 않는다.
- 사례DB의 관련 사례를 참고할 수 있다: `merged/사례DB.jsonl`(faq_ids에 해당 번호가 있는 사례, 특히 src_file이 LAW.jsonl인 위험 사례). 단 사례DB의 legal_risk 문장은 검색 요약 기반이라 그대로 믿지 말고 원문으로 다시 확인한다.

## 출력
- `raw/<파일명>_faq.jsonl` 에 한 줄에 JSON 하나(UTF-8). 키:
  faq_id, question(속성설명서 문장 그대로), verdict(가능|조건부 가능|불가|확인 필요), reason, conditions, alternatives, where_to_check, laws, precedents, case_ids(빈칸: 병합 때 자동), source_urls, source_dates, verified_date("2026-11-02"), notes
- reason: "법령명 제N조 제M항 제K호: 무엇을 금지/허용하는지 요약 → 그래서 이 질문은 …" 형태. 원문 문장 통째 복사 대신 요약(짧은 핵심 구절 인용은 가능).
- conditions: 조건부일 때 지킬 조건을 ①②③로.
- alternatives: 같은 효과를 내는 다른 방법 **2개 이상**(①②③), 질문마다 다르게. 음료 쿠폰 같은 같은 대안 반복 금지. 대안마다 남은 위험이 있으면 괄호로.
- where_to_check: 관할 기관 구체적으로(예: 관할 세무서 소비세 담당, 구청 옥외광고물 담당, 공정위 소비자정책총괄과 등)
- laws: "법령명(제N조)" 를 `|` 로.
- precedents: 원문 확인한 처분·판례·유권해석만. 사례DB 번호가 있으면 "(사례 123)". 없으면 빈칸.
- source_urls: law_src 파일 첫 줄의 원문 URL과 열람한 처분 원문 URL을 ` | `로. source_dates: 같은 순서로 시행일·기사일(모르면 빈칸 유지하며 개수 맞추기 불필요).
- notes: 확인 필요 항목, 지자체 조례마다 다른 점, 해석이 갈리는 점.
- 10문항마다 저장. 마지막에 각 줄 json.loads 검증.
- `raw/<파일명>_faq_log.md`: 열어 본 원문 URL, 막힌 곳(URL·응답코드), 확인 못 한 것.

## 최종 보고(짧게)
작성 문항 수, verdict 분포, "확인 필요"로 남긴 것과 이유, 막힌 사이트 목록.
