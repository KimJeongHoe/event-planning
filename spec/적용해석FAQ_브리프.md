# '적용 해석' 묶음 FAQ 브리프 (회차 6)

입력 `legal_packets/interp_all.jsonl`(법 칸 '확인 필요' 사유가 '적용 해석'인 197건). 같은 쟁점이 반복된다(예: 음식점이 주는 무료 술 한 잔이 '주류 경품'인지, 가게 앞 대기 줄이 도로 '점용'인지, 판촉이 사행행위 '영업'인지, 카톡 채널 추가가 광고 '명시적 사전 동의'인지 등).
1. 197건을 쟁점별로 묶어 반복 쟁점 상위 8~15개를 뽑는다(쟁점마다 해당 사례 orig_id 목록).
2. 쟁점마다 새 FAQ 문항(F051부터)을 spec/FAQ_작성브리프.md 형식으로 작성: question(사장님 말투), verdict, reason, conditions, alternatives(2개 이상), where_to_check, laws, precedents, source_urls, source_dates, verified_date, notes.
   - 근거: law_src 조문(`scripts/art.py`), 별표(`law_src/별표`), 그리고 **공식 해석 원문**: 법제처 법령해석례(law.go.kr의 해석례 페이지·moleg.go.kr), 국세청·공정위·식약처·개인정보위 질의회신·보도자료 중 열리는 것(`scripts/fetchtext.py`로 직접 열기; 막힌 곳 우회 금지). WebSearch는 원문 주소를 찾는 용도로만(25회 이내).
   - 공식 해석이 없으면 verdict '확인 필요'로 두고, 조문상 두 가지 해석과 안전한 운영 방법을 conditions·alternatives에 쓴다. notes에 "[확인 필요 사유: 적용 해석 — 공식 해석 없음]".
3. 출력: `raw/FAQ5_faq.jsonl`(새 문항), `faq_results/interp_links.jsonl`(한 줄에 사례 하나: {"case":"<orig_id>","edits":[{"field":"faq_ids","after":"<기존 faq_ids>|F05x"}]} — 기존 값 뒤에 붙인 전체 값), `faq_results/interp_log.md`(쟁점별 사례 목록·열어 본 해석 원문·막힌 곳).
4. 공식 해석으로 결론이 나는 쟁점은 해당 사례 legal_risk도 고칠 수 있다: interp_links.jsonl 같은 줄 edits에 {"field":"legal_risk","after":"…"},{"field":"legal_todo","after":""} 추가.
최종 보고: 만든 FAQ 문항(번호·질문·verdict), 쟁점별 사례 수, 해소된 사례 수, 열어 본 공식 해석.
