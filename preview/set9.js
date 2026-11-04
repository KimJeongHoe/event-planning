
// ── 판 9 설정: 다른 도구가 할 기능은 지우지 않고 꺼 둠. 다시 켜려면 아래 목록에서 빼고 만들기만 다시 하면 됨.
// deliv = 배달앱 할인 실수령(→ 배달 실수령 도구: merged/다른도구용/배달실수령용_행사근거.json)
// open  = 개업 행사 한 묶음·D-데이 순서표(→ 개업 D-데이 순서표 도구: merged/다른도구용/개업순서표용_행사항목.json)
// link  = 연결 파일 시험(관리용. 받은 파일은 spec/연동/에 두면 화면에 들어감)
const SET9={끈도구:["deliv","open","link"]};
for(const k of SET9.끈도구){delete TOOLS[k];delete RENDER[k]}
toolGrid();
