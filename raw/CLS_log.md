# CLS 수집 로그 — 양도·폐업정리 (2026-11-02)
출력: raw/CLS.jsonl 39줄 = 실제 32(확인함) + 응용 7. 웹 검색은 PRE와 합쳐 40회 사용(예산 소진).

## 검색어(CLS 관련)
1. 폐업 정리 세일 허위 공정위 경고 "폐업" 문구 계속 영업 → 해외 처분(싱가포르·조지아·뉴욕) 다수
2. 식당 폐업 앞두고 단골 감사 마지막 영업 기사
3. 가게 양도 후 쿠폰 적립 승계 선불권 환불 분쟁 소비자원 → 직접 사례 없음
4. "폐업" 세일 현수막 몇 년째 영업 허위 폐업세일 논란 → 한국 결과 없음
5. 閉店セール 措置命令 景品表示法 閉店しない 有利誤認 → 消費者庁 Q&A 해설만, 措置命令 사례 미발견
6. 閉店感謝祭 飲食店 最終営業日 常連 感謝 半額
7. 헬스장 인수 기존 회원 승계 거부 체육시설법 새 업주 분쟁 기사 → 골프장 판례 위주
8. 미용실 폐업 선불 회원권 잠적 피해 기사 정액권
9. "폐업 앞두고" 식당 전 메뉴 할인 마지막 감사 이벤트 단골 → 해외 사례
10. restaurant new owners will honor gift cards loyalty punch cards change of ownership
11. "폐업" OR "점포정리" 세일 몇 달째 계속 영업 상술 (extended) → 한국 언론 3건 확보
12. 헬스장 양도 후 새 운영자 기존 회원권 인정 안해 피해 기사
13. 학원 갑자기 폐원 수강료 환불 못받아 학부모 피해 기사
14. restaurant final day closing "pay what you want" OR "everything free" ... news

## 열어 본 URL(응답 코드) — 사례로 쓴 것은 jsonl source_urls 참조
- 200: ccs.gov.sg, effinghamherald.net, wkbw.com, olshanlaw.com, furnituretoday.com, wikitree.co.kr, heraldk.com, koreadaily.com, valleynewslive.com, gedlingeye.co.uk(2건), wtoc.com, zaikei.co.jp, ryukyushimpo.jp, corporatecrimereporter.com(폐업 아님·미사용), gulfnews.com, thisweekinworcester.com, inquirer.com, bangordailynews.com, kswo.com, cbsnews.com(2건), munhwa.com, sidae.com, biz.sbs.co.kr, dt.co.kr(골프장 판결·소상공인 범위 밖이라 미사용), data-max.co.jp, news.sbs.co.kr(2건), cctoday.co.kr, idomin.com, imaeil.com, m.seoul.co.kr, magazine.hankyung.com, cleveland19.com, fox5ny.com
- 미사용(행사성 약함): valleynewslive Mango's(마지막 날 방문 권유만), corporatecrimereporter Hobby Lobby(상시 세일, 폐업 아님)

## 막힌 곳 / 본문 못 엶
- mcdn.i-scmp.com(SCMP, 홍콩 Pricerite 폐점 암시 마케팅) → 403 Cloudflare. 우회 안 함
- wtaw.com Readfield Meats(폐업 재고 정리·상품권 안내) → 404
- dailyherald.com(Palatine 핫도그집이 폐업 식당 상품권 받아줌) → 200이나 본문 비어 있음(JS) — 본문 못 엶
- patch.com Capitola(Fresh Choice 후속 업체 상품권 거부) → 압축/바이너리 응답, 본문 못 엶
- expressandstar(폐업 전 'friends' 특별 행사) → 응답 000
- 이미 알려진 막힌 곳(ftc.go.kr, donga 등)은 시도하지 않음

## 법 근거(law_src 확인)
표시광고법 제3조, 부당한 표시·광고행위의 유형 및 기준 지정고시(할인판매 등 — 점포정리판매), 상법 제41조·제42조(상호 속용 양수인 책임·면책 등기/통지), 체육시설법 제27조(영업 양수인 회원 약정 승계), 공중위생관리법 제3조의2, 식품위생법 제39조, 학원법 제18조, 할부거래법 제16조

## 비어 있는/약한 조합
- 한국 요식업 × 폐업정리 × 혜택형(폐업 감사 할인) 실제 사례: 기사 못 찾음 → 응용(CLS-037·039)으로 보충
- 한국 요식업 × 양도 × 쿠폰·적립 승계: 실제 사례 없음(해외만) → 응용 CLS-033
- 미용·학원 × 양도(긍정적 승계 사례): 실제는 모두 '먹튀' 분쟁형 → 응용 CLS-034·035
- 리브랜딩·상호 변경 전 재고 소진: 실제 사례 못 찾음(헬스클럽 재개장 판단 1건만) → 응용 CLS-036
- 일본 閉店セール 허위 措置命令 실사례: 미확인(消費者庁 Q&A 해설만)
- 소매 × 폐업정리 정상 사례(진짜 폐업 감사 세일): 없음(처분·논란만)

## 다음에 찾을 곳
- 소비자원 보도자료(kca.go.kr) '폐업 선불' 피해주의보 원문, 공정위 '점포정리' 표시광고 심결(ftc는 막힘 → case.ftc.go.kr 별도 확인 필요)
- 消費者庁 措置命令 一覧에서 '閉店' 키워드
- 지역 신문(경남도민일보·충청투데이 등)의 '○○년 노포 문 닫는 날' 기사 — 한국 요식업 폐업 감사 행사
- 상가 양도양수 커뮤니티(아프니까 사장이다 등) — 쿠폰 승계 실제 안내문(본문 공개 여부 확인)
