# INT 수집 로그 — 해외 사례(미국·영국·기타) · 2026-11-02

## 결과 요약
- 저장: `/home/user/event_db/raw/INT.jsonl` — **56건**, 전부 `kind=실제`, 각 줄 json.loads 검증 완료, 값 목록(nature·stage·timing·method·target·cost_structure·exposure·industry·district·scale·cost_ratio_level·cost_recovery·goals·source_types·era·country) 전수 검사 통과.
- 국가: 미국 42 · 영국 11 · 기타 3(UAE 두바이, 이탈리아 밀라노, 인도) · **일본 0** (아래 '막힌 원천' 참조).
- known_result(출처 수치) 있는 건: 33 / 56. 나머지는 빈칸.
- faq_ids·case_qna 모두 기재(56/56). variants 2개 이상(56/56).

## 사용한 검색어 (WebSearch standard, 30회 실행)
1. Chick-fil-A grand opening First 100 free meals for a year promotion history
2. Krispy Kreme National Donut Day free doughnut history promotion results
3. Taco Bell Steal a Base Steal a Taco World Series promotion history free taco
4. Chipotle BOGO nurses teachers healthcare workers promotion
5. Panera Cares pay what you want cafe closed results why
6. Groupon restaurant deal backfired small business loss case
7. Wendy's surge pricing backlash 2024 dynamic pricing menu boards
8. Eat Out to Help Out scheme results 2020 UK restaurants meals claimed
9. Papa John's free pizza when team wins promotion Papa Slam Nationals
10. Denny's free birthday Grand Slam history restaurant birthday freebies
11. NYC Restaurant Week history 1992 prix fixe results restaurants participating
12. Taco Tuesday origin Taco John's trademark Taco Bell petition 2023
13. Yelp check-in offer restaurant case example small business results
14. kids eat free night restaurant results Tuesday case study chain Applebee's IHOP
15. happy hour promotion restaurant case study sales results Toast Square blog
16. soft opening friends and family night restaurant example opened invited neighbors feedback
17. restaurant loyalty punch card results small business case study coffee shop repeat visits
18. Starbucks Rewards program members percentage of sales history stars
19. In-N-Out secret menu Animal Style history not-so-secret menu marketing
20. Panera Unlimited Sip Club subscription results members visits coffee subscription
21. Danny Meyer Hospitality Included no tipping experiment ended results Union Square Hospitality Group
22. restaurant service charge controversy lawsuit 20% mandatory diners backlash 2023
23. restaurant snow day special free coffee when it snows promotion example
24. Veterans Day free meals restaurants Applebee's history veterans served
25. Teacher Appreciation Week restaurant deals free meal teachers example chains
26. restaurant social media contest example results Instagram giveaway increased followers small restaurant case
27. Krispy Kreme Hot Light history hot now sign free doughnut marketing
28. pub quiz night Tuesday revenue boost pub example UK weekday trade
29. Tesco meal deal history price £3 sales per year popularity
30. Blue Monday restaurant deals UK January promotion examples

### 실행했으나 거부된 검색어 (검색 예산 소진)
31~40. ワンコインランチ 500円 飲食店 事例 集客 効果 / 半額デー 飲食店 事例 集客 売上 / スタンプカード 飲食店 効果 事例 リピート率 / オープン記念 飲食店 イベント 事例 行列 半額 / LINE公式アカウント クーポン 飲食店 事例 効果 友だち 来店 / 雨の日サービス 飲食店 事例 割引 / ランチパスポート 効果 飲食店 売上 掲載店 / 肉の日 29日 焼肉 割引 事例 牛角 / 福袋 飲食店 正月 スターバックス ミスド 事例 完売 / 閉店セール 飲食店 感謝祭 行列 事例
→ 모두 "web search budget is used up (limit: 200 WebSearch calls per turn, shared by every agent)"로 미실행.

## 막힌 원천
- **WebSearch 예산 한도(세션 전체 공유 200회)** 가 30회 실행 시점에 소진됨(다른 에이전트와 공유). 그 뒤 일본어 10개 검색이 모두 거부되어 **일본 담당 범위(ワンコインランチ·半額デー·スタンプカード·開店セール·LINEクーポン·雨の日·ランチパスポート·肉の日·福袋·閉店セール·子ども食堂·商店街スタンプラリー·お通し·回転寿司100円·コンビニ100円セール·大盛り無料·食べ放題·ボトルキープ·誕生日特典) 전부 미수집**. 중국 团购·抖音, 대만 統一發票, 홍콩·동남아도 미수집. 지침상 검색 결과에 없는 URL은 쓸 수 없어 기억으로 채우지 않음.
- WebFetch는 지침대로 사용하지 않음(허용 호스트 외). 검색 결과 요약·URL만으로 기록.
- 미실행 검색어(예산 복구 시 후속 권장): 위 일본어 10개 + "子ども食堂 事例", "商店街 スタンプラリー 事例", "居酒屋 お通し 料金 トラブル", "回転寿司 100円 値上げ 一皿", "コンビニ 100円セール おにぎり", "大盛り無料 ラーメン 事例", "ボトルキープ 居酒屋 常連", "誕生日特典 飲食店 事例", "台湾 統一發票 餐廳", "抖音 直播 团购券 餐饮 案例", "Toast restaurant marketing ideas examples", "Square restaurant promotion ideas case", "restaurant week results city", "dog-friendly patio restaurant promotion", "early bird special restaurant results", "pop-up collab restaurant results".

## 비어 있는 조합(업종 × 성격 × 방식)
- industry: 요식업 55 · 소매 1(테스코 밀딜). 미용·뷰티/병의원·약국/학원·교육/서비스업/공통 = 0 (담당 범위가 외식 중심이라 예상된 공백).
- nature: 오픈행사 2건(칙필레 First 100, MAD Social 소프트오픈)뿐. N주년 0, 양도·폐업정리 0(그루폰 폐업 사례는 위기회복으로 분류), 리뉴얼·신메뉴 1.
- method: 동네매체형 1(레스토랑 위크), 현장연출형 6. 전단·동네 매체형 해외 사례는 검색어를 못 돌림.
- timing: 명절·급여일·방학·시험·졸업·입학·연말송년회 = 0. 날씨 5, 스포츠경기 4, 사회이슈 4.
- target: 어르신·학생·외국인 사례 없음. 커플 1.
- sub_industry: 한식·중식·분식·고깃집(주류 아님)·횟집 등 한국형 세부업종은 당연히 적음. 주점·호프 6, 카페 8, 베이커리 9, 피자 6.
- scale: 개인매장 사례는 17건 내외, 나머지는 체인·대기업 — 소상공인 직접 사례가 더 필요(일본 사례가 이 공백을 메울 예정이었음).

## 느낀 점·메모
- 미국 사례는 '구조'가 명확해 한국 소상공인용 변형안을 만들기 좋음: (a) 결과 연동 증정(도루·만루홈런·동전·홈팀 승리), (b) 직군 감사(간호사·교사·군인), (c) 날씨 암호형(스노우데이 딜), (d) 구매 조건부 소액 증정(쿠키·음료), (e) 비수기 기념일 네이밍(블루 먼데이→핑크 먼데이).
- 실패·논란 사례(파네라 케어스, 그루폰 4건, 웬디스 서지, 노팁, 서비스차지 3건, 타코 튜즈데이 상표)는 한국 적용 시 **가격표시제(봉사료·시간대 가격·비밀메뉴), 사행행위(결과 연동·퀴즈 상금), 주류 온라인 광고, 청탁금지법(교사·공무원 무료 식사), 개인정보(접종 확인·생일·신청 폼)** 로 위험이 번역됨. 법 적용이 불확실한 부분은 모두 '확인 필요'로 적음.
- 수치는 대부분 회사 발표·벤더 사례(StampEzee·Cool Tabs·Social Perks)라 known_result에 출처 성격을 병기함. 영국 EOTHO만 정부 통계(HMRC).
- 같은 유형이 여러 체인에 걸친 경우(키즈 무료, 교사 할인, 런던 블루 먼데이 소형 가게) 2~3개 브랜드를 한 건으로 묶고 notes에 '묶음'이라 표시.
- 소셜커머스 사례 중 Chicago Sun-Times(링컨스퀘어 상인, 2011-12-12)·Westword(포틀랜드 카페)·Rice대 조사는 검색 요약에 세부가 없어 INT-009 notes·출처로만 활용.
- 후속 세션에서 검색 예산이 복구되면 일본 20여 개 주제 + 중국·대만을 INT-057부터 이어서 수집 권장.
