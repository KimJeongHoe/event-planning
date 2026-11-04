# EMP 수집 로그: 빈 조합(업종×성격×방식) 메우기
수집일: 2026-11-02 / 출력: raw/EMP.jsonl (66줄, 모두 kind=실제, verify_status=확인함, 응용 0)
모든 건은 `scripts/fetchtext.py`로 본문을 열어 확인했습니다(검색 요약만으로 넣은 건 없음).
WebSearch는 42회 썼습니다(한도 40회를 2회 넘김 — 마지막 묶음에서 세는 것을 놓침).

## 결과
- 기준: 작업 시작 시점 merged/통계.md 의 "비어 있는 조합" 125개(EMP·JP2 빼고 다시 계산해 125개로 확인, 작업 폴더 base125.txt)
- EMP 실제 사례로 채운 조합: **89개 / 125개**
- 주의: 작업 중(21:47) 누군가 merge.py를 다시 돌려 merged/통계.md 가 EMP 일부·JP2를 포함해 "비어 있음 42개"로 바뀌었음. 위 89개는 원래 125개 기준.

## 분포(66건)
- 업종: 병의원·약국 20(약국 9, 치과 6, 의원·병원 5), 학원·교육 14(과외·입시 7, 수학 3, 무용 2, 유아·방과후 2), 미용·뷰티 13, 소매 12(철물점 4, 편의점 2, 서점·잡화·장난감·스포츠·사탕·아동용품), 서비스업 7(세탁·빨래방 6, 세차 1)
- 국가: 미국 57, 기타 8(캐나다 6, 남아공 1, 호주 1), 영국 1. **한국 0건**(아래 참고)
- 성격: 리뉴얼·신메뉴 18, 양도·폐업정리 17, N주년 15, 위기회복 14, 오픈행사 7, 홍보형 3, 상시서비스 3, 가격구조형 2
- 방식: 현장연출 43, 동네매체 42, 제휴 33, 단골·관계 33, 사회공헌 25, 혜택 23, 체험·참여 22, 온라인 12

## 병의원 사례 처리
- 의료법 제27조 제3항(본인부담금 면제·금품 제공 유인 금지, 제1호 개별 사전승인 예외), 제56조 제2항(제2호 치료경험담, 제10호 기사형 광고, 제13호 비급여 할인 광고)을 law_src 원문에서 확인해 legal_risk·case_qna에 적음.
- 약국은 약사법 제47조 제1항 제4호 나목 + 약사법 시행규칙 제44조 제1항 제2호(경품류 제공·호객 금지)를 원문 확인.
- 해외 사례의 무료 진료·경품·처방 이전 혜택(EMP-013, 027, 028 등)은 "한국 기준 불가/확인 필요"로 적고 variants ①에 정보 제공·강좌형 '한국형(위험 줄인 안)'을 넣음.
- 학원은 학원법 제6·10·14조의2·15·18조(등록, 휴원·폐원 신고, 교습비 게시·초과징수 금지, 반환)를 원문 확인.

## 검색어(42회)
tutoring center grand re-opening ribbon cutting chamber / 학원 리모델링 재개원 기념 설명회 지역신문 / 병원 이전 개원 안내 건강강좌 공지사항 / pharmacy 50th anniversary health fair / learning center closing thanks families / medical clinic grand re-opening renovation open house / salon grand opening proceeds donated charity ribbon cutting / dry cleaner 50th anniversary / pharmacy anniversary free blood pressure screenings / dental office anniversary celebration / pharmacy closing transferring prescriptions / hardware store grand reopening remodel / daangn business-post 학원 리뉴얼 / tutoring center reopens after fire flood / salon grand opening DJ mini services open house / store grand reopening loyal customers appreciation / 학원 개원 기념 장학금 기탁 쌀 / Mathnasium grand opening / doctor retiring practice records transferred / medical clinic reopens after tornado / dance studio closing final recital / salon reopens after fire loyal clients / laundromat anniversary free laundry day / independent pharmacy grand opening health fair / salon anniversary proceeds donated / car wash anniversary charity / tutoring center anniversary donates school supplies / store closing donates inventory / "이전 개원" 의원 공지사항 / 태권도장 개관 기념 기부 쌀 / salon closing stylists moving / dry cleaner reopens after fire / hardware store free kids workshop / tutoring sliding scale pay what you can / pharmacy monthly free blood pressure clinic / salon remodel grand reopening charity raffle / retiring dentist donates equipment / bookstore flooded reopens volunteers / learning center anniversary scholarships / yarn shop free weekly knitting group / tutoring center grand opening donation PTA / family medical practice 25th anniversary open house

## 막힌 곳(우회하지 않음)
- 403 Cloudflare/Access Denied: members.williamsonchamber.com, mathnasium.com(지점 소식 페이지 전부), carwash.com, beckersdental.com, beckersasc.com, energeticcity.ca, nsnews.com, ksdk.com, hbsdealer.com
- 429: orlandoweekly.com, artsatl.org
- 410: cdispatch.com / 000: events.newhavenarts.org
- 404(삭제·이동): sowal.com 이벤트, newspressnow.com Goodwill 기사, katc.com, covnews.com, lakeorionreview.com ?p=40503, suffolktimes ?p=89308, premierhealth.com Trotwood 소식

## 본문 못 엶·제외한 후보
- macaronikid(Mathnasium Park Slope 재개장): 목록 페이지로 이동, 본문 없음
- shelf-awareness(Hooray for Books 재개장): 다른 호 기사로 이동
- idahofoodbank(Elevate Salon Institute 리모델링): 본문에 해당 내용 없음
- kpcnews(Fremont Hardware 재개장): 유료 벽, 사진 설명만
- Go2Grow 재개장(업종 불명), Huntington Learning Center Georgetown 5주년(내용 없음), Dawson Springs 병원 재건(행사 아님), Temple Terrace Ace(본문 일부 누락), Raggedy Anne 외 학습센터 폐원 다수(대형 체인 갑작스러운 폐업 등 행사 없음) 제외
- 한국: '학원 리모델링 재개원', '병원 이전 개원 공지', '당근 학원 리뉴얼', '학원 개원 기념 기부', '태권도장 개관 기념 기부' 검색에서 개인 학원·의원의 리뉴얼·이전·주년 행사 원문을 찾지 못함(도서관·학교 재개관, 연예인 의원 기사만 나옴). 당근 business-post 개별 글 URL도 검색에 잡히지 않음.

## 아직 비어 있는 조합(원래 125개 중 36개)
미용·뷰티×가격구조형×동네매체형, 미용·뷰티×가격구조형×현장연출형, 미용·뷰티×위기회복×혜택형, 병의원·약국×가격구조형×동네매체형, 병의원·약국×가격구조형×사회공헌형, 병의원·약국×리뉴얼·신메뉴×온라인형, 병의원·약국×상시서비스×온라인형, 병의원·약국×상시서비스×현장연출형, 병의원·약국×오픈행사×단골·관계형, 서비스업×N주년×체험·참여형, 서비스업×가격구조형×동네매체형, 서비스업×가격구조형×사회공헌형, 서비스업×가격구조형×현장연출형, 서비스업×리뉴얼·신메뉴×사회공헌형, 서비스업×양도·폐업정리×동네매체형, 서비스업×위기회복×온라인형, 소매×N주년×온라인형, 소매×가격구조형×사회공헌형, 소매×가격구조형×체험·참여형, 소매×양도·폐업정리×체험·참여형, 소매×위기회복×동네매체형, 소매×위기회복×사회공헌형, 요식업×N주년×동네매체형, 요식업×N주년×제휴형, 요식업×리뉴얼·신메뉴×동네매체형, 요식업×위기회복×체험·참여형, 학원·교육×N주년×사회공헌형, 학원·교육×가격구조형×제휴형, 학원·교육×가격구조형×체험·참여형, 학원·교육×가격구조형×현장연출형, 학원·교육×리뉴얼·신메뉴×단골·관계형, 학원·교육×상시서비스×현장연출형, 학원·교육×양도·폐업정리×사회공헌형, 학원·교육×양도·폐업정리×제휴형, 학원·교육×오픈행사×사회공헌형, 학원·교육×위기회복×단골·관계형

## 다음에 찾을 곳
- 한국 사례가 0건: 개별 학원·의원 홈페이지 '공지사항'(이전 개원·휴진 안내)은 검색에 잘 안 잡힘 → 네이버 플레이스 '소식'·병원 블로그의 이전 안내 글을 원장 이름 없이 찾거나, 지역 교육청 학원 소식지, 한국교육신문·에듀진 '학원가' 꼭지를 직접 목록 열람.
- 학원 가격구조(현장연출·체험·제휴), 학원 N주년·오픈 사회공헌: 미국 'Kumon/Sylvan/Huntington anniversary' 지점 보도자료(franchising.com, 1851franchise.com은 열림), 지역 Patch 커뮤니티 게시판.
- 병의원 상시(온라인·현장연출), 병의원 가격구조(동네매체·사회공헌): 미국 독립약국 'membership/cash price' 기사(지역 방송 사이트는 대부분 열림), 영국 지역지(oxfordmail 등)의 pharmacy 기사.
- 서비스업 가격구조(현장·동네·사회공헌)·N주년 체험: 빨래방 'pay what you can' 또는 'free laundry day monthly'(kshb.com, wvlt.tv 후보 미열람).
- 소매 위기회복×사회공헌·동네매체, 소매 N주년×온라인: 독립서점 재해 뒤 재개장 기사(vermontpublic.org Bear Pond Books, shastascout.org Cal's Books, king5 Kent 서점 — 미열람 후보).
- 요식업 4개 조합은 이번 범위 밖이라 찾지 않음.
