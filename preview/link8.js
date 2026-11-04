
// ── 판 8: 다른 도구와 잇는 파일 3개(문구 기준·배달 요금표·개업 순서표) ──
// 받은 파일은 spec/연동/<종류>.json 에 두면 만들 때 D.link 로 들어옴. 받기 전에는 화면 「연결 파일」에서 불러와 시험(이 브라우저에만 보관).
// 칸 설명: docs/연동파일_칸설명서.md
const LK_NAME={copy:"구절 공방 문구 기준",deliv:"배달 실수령 요금표",open:"개업 D-데이 순서표"};
const LK_KIND={copy:"문구기준",deliv:"배달요금표",open:"개업순서표"};
const LK_CH={"전체":null,"매장":"store","인스타그램":"insta","플레이스":"place","카카오톡":"kakao","문자":"sms","배달앱":"deliv","당근":"daangn","현수막":"banner"};
const LINK={copy:null,deliv:null,open:null},LSRC={copy:"",deliv:"",open:""};
const isDate=s=>typeof s==="string"&&/^\d{4}-\d{2}-\d{2}$/.test(s);
const isNum=(v,a,b)=>typeof v==="number"&&isFinite(v)&&v>=a&&v<=b;
function lkCheck(k,j){const E=[];if(!j||typeof j!=="object"||Array.isArray(j))return["파일 맨 바깥이 { } 묶음이 아닙니다"];
 if(j["종류"]!==LK_KIND[k])E.push(`「종류」가 「${LK_KIND[k]}」가 아닙니다(지금: ${j["종류"]??"없음"})`);
 if(!isDate(j["기준일"]))E.push("「기준일」은 2026-11-04 모양이어야 합니다");
 if(!j["출처"]||typeof j["출처"]!=="string")E.push("「출처」(어느 도구·누가 만든 파일인지)가 없습니다");
 const PIIx=JSON.stringify(j).match(PII);if(PIIx)E.push("전화번호·주민번호·이메일 모양이 들어 있습니다: "+PIIx[0]);
 if(k==="copy"){const R=j["규칙"];if(!Array.isArray(R)||!R.length)E.push("「규칙」 목록이 비었습니다");else R.slice(0,500).forEach((r,i)=>{const at=`규칙 ${i+1}번째`;
   if(!r["번호"])E.push(at+": 「번호」 없음");if(!r["찾기"])E.push(at+": 「찾기」 없음");
   if(!["낱말","정규식"].includes(r["방식"]))E.push(at+": 「방식」은 낱말 또는 정규식");else if(r["방식"]==="정규식"){try{new RegExp(r["찾기"])}catch(e){E.push(at+": 정규식이 틀림")}}
   if(!["금지","주의"].includes(r["수준"]))E.push(at+": 「수준」은 금지 또는 주의");
   if(!Array.isArray(r["채널"])||!r["채널"].length||r["채널"].some(c=>!(c in LK_CH)))E.push(at+": 「채널」은 "+Object.keys(LK_CH).join("·")+" 중에서");
   if(!r["이유"])E.push(at+": 「이유」 없음")});if(R&&R.length>500)E.push("규칙은 500개까지만 읽습니다")}
 if(k==="deliv"){const R=j["요금"];if(!Array.isArray(R)||!R.length)E.push("「요금」 목록이 비었습니다");else R.slice(0,200).forEach((r,i)=>{const at=`요금 ${i+1}번째`;
   if(!r["앱"])E.push(at+": 「앱」 없음");if(!r["요금제"])E.push(at+": 「요금제」 없음");
   if(!isNum(r["중개수수료율"],0,50))E.push(at+": 「중개수수료율」은 0~50 사이 숫자(%)");
   if(!isNum(r["결제수수료율"],0,10))E.push(at+": 「결제수수료율」은 0~10 사이 숫자(%)");
   if(r["배달비_사장님부담"]!=null&&!isNum(r["배달비_사장님부담"],0,100000))E.push(at+": 「배달비_사장님부담」은 원 단위 숫자 또는 null");
   if(!["별도","포함"].includes(r["부가세"]))E.push(at+": 「부가세」는 별도 또는 포함");
   if(!["할인 전 금액","할인 뒤 금액"].includes(r["수수료기준"]))E.push(at+": 「수수료기준」은 할인 전 금액 또는 할인 뒤 금액");
   if(!isDate(r["확인일"]))E.push(at+": 「확인일」 없음(앱 화면·계약서에서 본 날)")})}
 if(k==="open"){const R=j["할일"];if(!Array.isArray(R)||!R.length)E.push("「할일」 목록이 비었습니다");else R.slice(0,300).forEach((r,i)=>{const at=`할일 ${i+1}번째`;
   if(!Number.isInteger(r["D"])||r["D"]<-90||r["D"]>90)E.push(at+": 「D」는 -90~90 정수(개업일=0)");
   if(!r["할일"])E.push(at+": 「할일」 없음");
   if(r["분류"]&&!["인허가","준비","홍보","행사","사후"].includes(r["분류"]))E.push(at+": 「분류」는 인허가·준비·홍보·행사·사후 중에서");
   if(r["도구"]&&!(r["도구"] in TOOLS))E.push(at+": 「도구」는 "+Object.keys(TOOLS).join("·")+" 중에서")})}
 return E}
function lkLoad(){const emb=(D.link||{});for(const k of Object.keys(LINK)){if(emb[k]&&!lkCheck(k,emb[k]).length){LINK[k]=emb[k];LSRC[k]="화면에 넣은 파일"}
  else{try{const j=JSON.parse(localStorage.getItem("p8link_"+k)||"null");if(j&&!lkCheck(k,j).length){LINK[k]=j;LSRC[k]="이 브라우저에서 불러온 시험 파일"}}catch(e){}}}}
const lkBadge=(k,admin)=>LINK[k]?`<span class="badge b-ok">연결됨</span> <span class="small">${esc(LSRC[k])} · 기준일 ${esc(LINK[k]["기준일"])} · ${esc(LINK[k]["출처"])}${LINK[k]["예시"]?" · <b>예시 파일(실제 값 아님)</b>":""}</span>`:(admin?`<span class="badge b-info">연결 대기</span> <span class="small">${esc(LK_NAME[k])} 파일을 받으면 연결합니다</span>`:"");  // 판 9: 사장님 화면에는 대기 표시 없음
// 홍보 글 검사에 문구 기준 규칙 더하기(template의 check()가 부름)
window.linkCopyCheck=(txt,W)=>{const C=LINK.copy;if(!C)return;const byLabel={};for(const [k,v] of Object.entries(CH))byLabel[v]=k;
 for(const [lab,t] of Object.entries(txt)){const ck=byLabel[lab];for(const r of C["규칙"].slice(0,500)){const chs=r["채널"];if(!(chs.includes("전체")||chs.some(c=>LK_CH[c]===ck)))continue;
  let re;try{re=r["방식"]==="정규식"?new RegExp(r["찾기"]):null}catch(e){continue}
  t.split(/\n|[.!]/).forEach(l=>{if(re?re.test(l):l.includes(r["찾기"]))W.push([lab,`${r["수준"]==="금지"?"⚠ ":""}${r["이유"]}${r["근거"]?" — "+r["근거"]:""}${r["바꿔쓰기"]?" · 바꿔 쓰기: "+r["바꿔쓰기"]:""} (문구 기준 ${r["번호"]})`,l])})}}};
// 개업 순서표에 줄 더하기(RENDER.open이 부름)
window.linkOpenRows=R=>{const C=LINK.open;if(!C)return;C["할일"].slice(0,300).forEach(r=>R.push([r["D"],esc(r["할일"])+` <span class="badge b-info">순서표 파일</span>`,[r["분류"],r["근거"]].filter(Boolean).map(esc).join(" · "),r["도구"]||""]));R.sort((a,b)=>a[0]-b[0])};
// 배달 계산에 요금표 고르기 더하기(RENDER.deliv 뒤에 붙음)
function linkDelivUI(){const box=document.createElement("div");box.className="note";box.id="dv-link";const C=LINK.deliv;
 box.innerHTML=C?`<div class="row" style="flex-wrap:wrap;gap:8px"><b>요금표에서 고르기</b><select id="dv-pick"><option value="">직접 넣기</option>${C["요금"].slice(0,200).map((r,i)=>`<option value="${i}">${esc(r["앱"])} · ${esc(r["요금제"])}${r["구간"]?" · "+esc(r["구간"]):""}</option>`).join("")}</select></div><div class="small">${lkBadge("deliv")}. 고르면 아래 칸을 채웁니다. 사장님 계약과 다르면 고쳐 넣으세요.</div><div class="small" id="dv-pick-src"></div>`:"";
 const tb=$("#tool-body");tb.insertBefore(box,tb.children[1]||null);
 const s=$("#dv-pick");if(s)s.addEventListener("change",()=>{const r=C["요금"][+s.value];if(!r){$("#dv-pick-src").textContent="";return}
  $("#dv-r").value=r["중개수수료율"];$("#dv-q").value=r["결제수수료율"];if(r["배달비_사장님부담"]!=null)$("#dv-f").value=r["배달비_사장님부담"];
  $("#dv-vat").value=r["부가세"]==="별도"?"더함":"안 더함(이미 포함)";$("#dv-base").value=r["수수료기준"];
  $("#dv-pick-src").innerHTML=`확인일 ${esc(r["확인일"])}${r["출처주소"]?` · <a href="${esc(r["출처주소"])}" target="_blank" rel="noopener">출처</a>`:""}${r["메모"]?" · "+esc(r["메모"]):""}`;$("#dv-r").dispatchEvent(new Event("input",{bubbles:true}))})}
const _rDeliv=RENDER.deliv;RENDER.deliv=()=>{_rDeliv();linkDelivUI()};
// 연결 파일 도구
TOOLS.link="연결 파일(다른 도구)";TOOLDESC.link="문구 기준·배달 요금표·개업 순서표 파일 연결 상태와 시험";
RENDER.link=()=>{body(`<p class="small" style="margin:0">다른 도구에서 받는 파일 3개의 연결 상태입니다. 파일을 받기 전에도 칸 설명서 모양대로 만든 JSON 파일을 불러와 시험할 수 있습니다. 시험 파일은 이 브라우저에만 남고 다른 사람에게 보이지 않습니다.</p>
 <div class="tw"><table><tr><th>파일</th><th>상태</th><th>쓰는 곳</th><th>시험</th></tr>${Object.keys(LINK).map(k=>`<tr><td><b>${esc(LK_NAME[k])}</b><br><span class="small">종류: ${LK_KIND[k]}</span></td><td>${lkBadge(k,1)}</td><td class="small">${{copy:"3단계 「홍보 글」 표현 검사에 규칙을 더함",deliv:"4단계 「배달앱 할인 실수령」에서 요금제를 골라 칸을 채움",open:"4단계 「개업 행사 한 묶음」 순서표에 할 일을 더함"}[k]}</td><td><label class="chip" style="cursor:pointer">불러오기<input type="file" data-lk="${k}" accept=".json,application/json" style="display:none"></label>${LSRC[k].startsWith("이 브라우저")?` <button type="button" class="ghost" data-lkx="${k}">시험 파일 지우기</button>`:""}</td></tr>`).join("")}</table></div>
 <div id="lk-msg"></div>
 <details><summary>파일 모양(칸 설명서 요약)</summary><div class="small">
 <p><b>공통</b>: UTF-8 JSON. 맨 바깥 { }에 「종류」(문구기준·배달요금표·개업순서표), 「기준일」(YYYY-MM-DD), 「출처」, 시험용이면 「예시」: true. 손님 개인정보·전화번호는 넣지 않음.</p>
 <p><b>문구기준</b>: 「규칙」 목록 — 번호, 찾기, 방식(낱말|정규식), 채널(전체·매장·인스타그램·플레이스·카카오톡·문자·배달앱·당근·현수막), 수준(금지|주의), 이유, 근거(선택), 바꿔쓰기(선택).</p>
 <p><b>배달요금표</b>: 「요금」 목록 — 앱, 요금제, 구간(선택), 중개수수료율(%), 결제수수료율(%), 배달비_사장님부담(원 또는 null), 부가세(별도|포함), 수수료기준(할인 전 금액|할인 뒤 금액), 확인일, 출처주소(선택), 메모(선택).</p>
 <p><b>개업순서표</b>: 「할일」 목록 — D(개업일 0 기준 −90~90 정수), 할일, 분류(인허가·준비·홍보·행사·사후, 선택), 근거(선택), 도구(coupon·review·infl·regular·draw·deliv·open·result·near, 선택).</p></div></details>`);
 document.querySelectorAll("[data-lk]").forEach(inp=>inp.addEventListener("change",async e=>{const k=inp.dataset.lk,f=e.target.files[0];if(!f)return;let j;
  try{j=JSON.parse(await f.text())}catch(err){$("#lk-msg").innerHTML=`<div class="note bad">JSON으로 읽을 수 없습니다(쉼표·따옴표 확인).</div>`;return}
  const E=lkCheck(k,j);if(E.length){$("#lk-msg").innerHTML=`<div class="note bad"><b>${esc(LK_NAME[k])}: 맞지 않는 곳 ${E.length}건</b><ul class="clean">${E.slice(0,20).map(x=>`<li>${esc(x)}</li>`).join("")}</ul></div>`;return}
  LINK[k]=j;LSRC[k]="이 브라우저에서 불러온 시험 파일";try{localStorage.setItem("p8link_"+k,JSON.stringify(j))}catch(err){}
  RENDER.link();$("#lk-msg").innerHTML=`<div class="note ok">${esc(LK_NAME[k])} 파일을 연결했습니다. ${k==="copy"?"홍보 글 검사":k==="deliv"?"배달 계산":"개업 순서표"}에서 확인하세요.</div>`}));
 document.querySelectorAll("[data-lkx]").forEach(b=>b.addEventListener("click",()=>{const k=b.dataset.lkx;try{localStorage.removeItem("p8link_"+k)}catch(e){}LINK[k]=null;LSRC[k]="";lkLoad();RENDER.link()}))};
lkLoad();window.lkBadge=lkBadge;
toolGrid();
