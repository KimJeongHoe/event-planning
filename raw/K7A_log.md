# K7A 수집 로그: 실제 빈 조합 6개(학원·교육 4, 미용 1, 소매 1)
수집일: 2026-11-03 / 출력: raw/K7A.jsonl (20줄, 모두 kind=실제, verify_status=확인함, 응용 0)
한국 5건, 해외 15건(이름 앞 [해외]). 모든 건은 `scripts/fetchtext.py`로 본문을 열어 확인함. merged/사례DB.jsonl·raw/*.jsonl source_urls와 겹침 없음(사전 대조), 이름 키워드 중복 없음.

## 검색 방식과 횟수(웹 검색 29회)
- 네이버 뉴스 목록(search.naver.com where=news, 결과 목록에서 원문 URL만 확보) 20회: 학원 개원 기념 기부 / 폐원 피아노 기증 / 문 닫는 학원 기증 / 개관 기념 쌀 기탁 / 학원 오픈 기념 기부 / 도장 개관 이웃돕기 / 개원 축하 쌀 학원 / 개관식 쌀 도장(1쪽 + start=11·21 — 쪽 넘김이 안 먹고 같은 결과) / 개원식 화환 대신 쌀 / 폐원 학원 원생 인수 / 폐업 미용실 재개장 할인 / 서점 개점 주년 온라인 / 서점 주년 기념 이벤트 / 개점 주년 라이브커머스 / 출석 환급 수강료 / 미용실 화재 다시 영업 / 공부방 기탁 / 학원 새로 문 열어 기탁
  - 주의: 이번에는 네이버 뉴스 `start=` 쪽 넘김이 무시됨(같은 1쪽 반복). '개관식 쌀'·'화환 대신 쌀'은 병원·모델하우스 기사로 도배됨. '서점 주년'은 게임 기사로 도배.
- WebSearch 9회: salon reopens after fire discount / tutoring center closing students transferred (Mathnasium·Kumon·Sylvan) / music school closing donates pianos / independent bookstore anniversary virtual / 동네책방 개점 주년 온라인 북토크 / bookstore anniversary 2020·2021 virtual / salon reopening after flood % off
- 횟수에 안 센 것: thebk.co.kr `articleList.html?sc_word=`(재오픈·침수·화재) → 검색어 무시하고 최신 목록만 나옴(K6A 로그와 같은 ndsoft 문제)

## 열어 본 URL과 응답 코드
- 200(사례로 씀): headlinejeju 231628, news.tf.co.kr 2152554, lecturernews 197621, fntoday 396206, hansbiz 878210, edu.chosun 2026103080164, flaglerlive sylvan-learning-centers, globalnews 2117971, nbcconnecticut 1993161, communityimpact masters-touch, nbc26 rubble-to-reopening, thebusinessnews pulaski-salon, hyattsvillewire todays-hair-reopens, echolive arid-40133987, rochdaletowncentre flood-hit-hairdresser, wlos wink-salon, mmrmagazine 58056(→mmrmag.com), pasadenanow p=488540, shelf-awareness 2020-04-27(→issue 3726), thepianoshopbath p=12840, gazette-news 19918558
- 200이나 사례 아님/내용 부족: greatyarmouthmercury 21031188(할인 없음), wsiltv(→kfvs12 첫 화면으로 이동, 기사 없음), globalnews 3677989(퀘벡 침수 미용실 — 자비 재건 외 행사 없음, 안 넣음), jjan 20170903620156(책방 2주년 '앞둠'만), kyeonggi 201910231094112(칼럼), communityimpact sylvan-richardson(폐점 사실만)
- 본문 못 엶: jejusori 157588(000, 화북도장 같은 기사), news20.busan.com 20091015000041(000, '개원 축하 쌀 25포' 포토뉴스), mediahub.seoul.go.kr 2002993(000, 서울서점주간 인스타 라이브 북토크 목록), wemakenews 25763(200이나 본문 빈칸 — 리워드형 강의 환급 피해 기사), pressreader cape-breton-post 20171124(200이나 본문 없음 — Alma's 미용실 재개장 경품·선착순 200명 $50 이상 구매 시 선물 가방: **미용×위기회복×혜택형 후보지만 확인 못 함**), calgary.ctvnews 2478807(200이나 본문 비어 있음), comicsbeat(403 보안 확인 페이지)
- 막힌 곳(403): garstangcourier→lep.co.uk(403), clarendonlive.com(403), wcnc.com(403), comicsbeat.com(403). 404: aol.com pianos-sold-rock-bottom-prices, mountainlake.org we-are-instrumental
- 우회 시도 없음

## 분포(20건)
- 국가: 한국 5, 미국 9, 영국 4, 기타 2(아일랜드·캐나다)
- 업종: 학원·교육 9(검도 도장 1, 어린이집 1, 어학 인강 3, 보습 학습센터 3, 음악 1), 미용·뷰티 6, 소매 5(서점 3, 악기점 2)
- 성격: 위기회복 9, 양도·폐업정리 4, 가격구조형 3, N주년 3, 오픈행사 2, 홍보형행사 2
- 방식: 단골·관계형 11, 온라인형 10, 체험·참여형 5, 사회공헌형 4, 혜택형 3, 제휴형 3, 현장연출형 2
- 시대: 2020년대 13, 2010년대 6, 미상 1

## 맡은 6개 조합 결과 → 4개 채움(1개는 약함)
- 채움(한국): 학원·교육×오픈행사×사회공헌형 — K7A-001(해동검도 화북도장 이전 개관 축하 쌀·성금 기탁), K7A-002(바움 어린이집 개원식 화환 대신 쌀 — 어린이집이라 학원과 성격 다름 표기)
- 채움(한국): 학원·교육×가격구조형×체험·참여형 — K7A-003(해커스 출석 환급), 004(시원스쿨랩 300% 환급), 005(YBM 머니뱅크). 모두 대형 온라인 인강·홍보성 기사. 동네 학원 사례는 못 찾음
- 채움(해외): 학원·교육×양도·폐업정리×제휴형 — K7A-006(Sylvan 폐업 센터 학생을 이웃 지점이 수용+본사 온라인), 007(캘거리 재개장·타 지점·온라인 선납 인정). 단, 같은 브랜드 가맹점 사이 인계라 독립 학원 간 제휴는 아님
- 약하게 채움(해외): 소매×N주년×온라인형 — K7A-017(Pagination Bookshop 1주년 SNS 인사+온라인 주문). 행사 규모 작음
- 못 채움:
  - 학원·교육×양도·폐업정리×사회공헌형 → 폐원 학원 기증 원문 없음. 가까운 것: K7A-009(음악학원 폐원 정리 세일, 혜택형). 검색 요약에 악기점 폐업 악기 기증(미국 Barcone's Music)이 있었으나 원문 404
  - 미용·뷰티×위기회복×혜택형 → 원문 확인한 화재·침수 재개장 기사 7건 모두 할인·경품 없음(현장연출·단골·제휴·온라인형으로 넣음: K7A-010~014, 020). 유일한 혜택형 후보 Alma's(pressreader) 본문 못 엶

## 법 근거(law_src 원문에서 확인)
- 기부금품법 제2조 제3호(모집 정의), 제4조 제1항
- 학원법 제2조 제1호(원격 교습 포함, 평생교육시설 등 제외), 제15조 제3·4항, 제18조 제1항
- 학원법 시행령 제18조 제2항 제1의2호·제3항(폐지 시 5일 이내 반환), 제4항(운영에 지장 없는 범위 감면)
- 표시광고법 제3조 제1항
- 조문 대조 안 함(사례에 '확인 필요'로 적음): 공중위생관리법 영업소 외 시술, 출판문화산업 진흥법 도서정가, 청탁금지법, 정보통신망법 광고 전송, 환급금 세금

## 다음에 찾을 곳
- 미용×위기회복×혜택형: pressreader 대신 Cape Breton Post 자체 사이트(saltwire.com)에서 'Alma's Family Hair Salon grand reopening' 기사 찾기. 한국은 당근 비즈 소식 '재오픈' 글을 지역별로 직접 열기(뉴스엔 거의 없음)
- 학원 폐업×사회공헌: '교습소 폐업 책 기증', '공부방 정리 도서 기증 작은도서관' 같은 지역 도서관·아동센터 쪽 기사(기증받는 쪽 소식에 실림). 해외는 'tutoring center closing donates books library'
- 소매 N주년×온라인: 영미 독립서점 뉴스레터(Shelf Awareness 'anniversary' 꼭지)가 가장 가능성 있음 — 사이트 안 검색으로 'anniversary virtual' 훑기
- 학원 가격구조형×체험: 동네 학원의 '개근 장학금·출석 포인트' 기사(지역내일 학원 탐방)
- 네이버 뉴스 쪽 넘김이 안 되므로 검색어를 더 좁게(기관 유형+행위 2단어) 바꿔 여러 번
