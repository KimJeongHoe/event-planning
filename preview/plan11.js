
// ── 판 11: 행사 기획 기능 — 경품 안내문, 방식 나란히 비교·대목 인력, 올해 행사 달력, 공동구매, 손님 제한 정책, 동네 코스 안내문,
// 다른 도구에 넘기는 파일(쿠폰 번호·QR, 문자 발송용, 발주용, 지도용). 「권장」 표시는 하지 않음 — 판단은 사장님.
const P11={};
const lawKeysBy=re=>Object.keys(D.law).filter(k=>re.test(k+" "+(D.law[k].law||"")+" "+(D.law[k].gist||"")));
const lawUl=(t,ks)=>{const l=ks.filter(k=>D.law[k]).map(lawLi).join("");return l?lawBox(t,ks.filter(k=>D.law[k])):""};
const fileJSON=(name,obj)=>saveFile(name,JSON.stringify(obj,null,1));
const SAMPLE_GUARD=()=>window.isSampleShop&&isSampleShop();

// 1) 경품 행사 안내문(응모 기간·당첨 발표·제세공과금·개인정보 처리)
const _rDraw11=RENDER.draw;RENDER.draw=()=>{_rDraw11();const box=$("#dr-txt");if(!box)return;const lab=box.closest("label");
 lab.insertAdjacentHTML("beforebegin",`<div class="grid">
  <label>응모 시작<input type="date" id="dr-s"></label><label>응모 끝<input type="date" id="dr-e"></label>
  <label>응모 방법<select id="dr-way"><option>매장 응모함에 응모권 넣기</option><option>영수증 번호 적기</option><option>매장에서 이름만 적기</option></select></label>
  <label>발표 방법<select id="dr-ann"><option>매장 게시판에 당첨 번호 게시</option><option>당첨자에게만 개별 연락</option></select></label>
  <label>경품 받는 기한(발표 뒤 며칠)<input id="dr-keep" inputmode="numeric" placeholder="예: 14"></label>
  <label>연락처를 받나요<select id="dr-pi"><option>받지 않음(번호로만 발표)</option><option>받음(당첨 연락용)</option></select></label>
  <label>연락처 보관 기간(발표 뒤 며칠)<input id="dr-pd" inputmode="numeric" placeholder="예: 30"></label></div>
  <div class="row"><button type="button" class="main" id="dr-make">경품 행사 안내문 만들기</button><span class="small" id="dr-mm"></span></div>`);
 $("#dr-make").addEventListener("click",()=>{const v=n7("#dr-v"),n=n7("#dr-n")||1,nm=v7("#dr-nm"),s=v7("#dr-s"),e=v7("#dr-e"),d=v7("#dr-d"),keep=n7("#dr-keep"),pi=v7("#dr-pi").startsWith("받음"),pd=n7("#dr-pd");
  const miss=[!nm&&"경품 이름",!s&&"응모 시작",!e&&"응모 끝",!d&&"발표일",pi&&pd==null&&"연락처 보관 기간"].filter(Boolean);
  if(miss.length){$("#dr-mm").textContent="먼저 넣을 것: "+miss.join(", ");return}
  if(hasLiq(nm)){$("#dr-mm").textContent="술은 경품으로 걸 수 없습니다. 경품을 바꿔 주세요.";return}
  if(v7("#dr-how")==="참가비를 받음"){$("#dr-mm").textContent="참가비를 받는 추첨은 안내문을 만들지 않습니다. 참가 조건을 바꿔 주세요.";return}
  const lim=+((LAWS.경품_최저한||{}).num||50000),shop=v7("#dr-tax").startsWith("가게");
  const tax=v!=null&&v>lim?(shop?"제세공과금(경품값의 22%)은 가게가 부담합니다.":"제세공과금(경품값의 22%)은 당첨자가 부담하며, 경품을 받을 때 신분 확인이 필요합니다."):"경품 1개 값이 5만 원 이하라 제세공과금이 없습니다.";
  const L=[`[${shopNm()} 경품 행사 안내]`,`· 경품: ${nm} ${n}개${v!=null?` (1개 시가 ${won(v)})`:""}`,`· 응모 기간: ${s} ~ ${e}`,`· 응모 방법: ${v7("#dr-way")} (${v7("#dr-how")}, 참가비 없음)`,`· 당첨자 발표: ${d}, ${v7("#dr-ann")}`,keep!=null?`· 경품 수령: 발표일부터 ${keep}일 안에 매장에서 받기(기한이 지나면 당첨이 취소될 수 있습니다)`:"",`· ${tax}`,
   pi?`· 개인정보 수집·이용 안내: 받는 항목 — 이름·연락처 / 목적 — 당첨 연락과 경품 전달${v!=null&&v>lim?"·제세공과금 신고":""} / 보관 기간 — 발표일부터 ${pd}일 뒤 바로 파기 / 동의하지 않을 수 있으며, 동의하지 않으면 당첨 연락을 받을 수 없습니다. 만 14세 미만은 보호자 동의가 있어야 응모할 수 있습니다.`:"· 연락처는 받지 않습니다. 응모권 번호로만 발표합니다.",
   "· 이 행사는 구매·방문 여부와 관계없이 공정하게 추첨합니다."].filter(Boolean);
  box.value=L.join("\n");box.dispatchEvent(new Event("input",{bubbles:true}));$("#dr-mm").textContent="만들었습니다. 가게 사정에 맞게 고쳐 쓰세요."})};

// 2) 방식 나란히 비교 + 대목 인력 운영 나란히
const CMP=[
 {k:"할인",nm:"가격 할인",f:[["d","할인율(%)"]],u:(I,x)=>x.d!=null?I.ag*x.d/100:null,staff:"계산·가격 안내 외에는 일손이 크게 늘지 않음",back:"할인이 끝나면 정가에도 다시 오는지가 관건. 자주 하면 할인 때만 오는 손님이 늘 수 있음"},
 {k:"덤",nm:"1+1·세트",f:[["p","덤으로 주는 상품 판매가(원)"]],u:(I,x)=>x.p!=null&&I.cr!=null?x.p*I.cr/100:null,staff:"덤 상품 준비량만큼 일손이 늘어남",back:"한 번에 더 사 가므로 다음 방문 간격이 길어질 수 있음"},
 {k:"증정",nm:"덤·증정",f:[["g","증정품 원가(원)"]],u:(I,x)=>x.g,staff:"증정품 준비·전달 일손",back:"증정을 기대하게 되면 증정이 없을 때 덜 올 수 있음"},
 {k:"체험",nm:"공짜 판촉(시식·무료 체험)",f:[["f","1명 무료 제공 원가(원)"],["r","무료로 받은 사람 중 사는 비율(%)"]],u:(I,x)=>x.f,staff:"시식·체험 진행 일손이 따로 필요",back:"공짜에 익숙해져 정가 방문을 미루는 위험(경고 신호 참고)",free:1},
 {k:"도장",nm:"재방문 장치(도장·적립)",f:[["rw","보상 원가(원)"],["nv","보상까지 방문 횟수"]],u:(I,x)=>x.rw!=null&&x.nv?x.rw/x.nv:null,staff:"도장·적립 확인 일손(계산 때 잠깐)",back:"방문 간격을 줄이는 쪽으로 짠 방식. 보상까지 횟수가 너무 많으면 힘이 약해짐"},
 {k:"경품",nm:"참여 이벤트(경품·추첨)",f:[["pz","경품 총값(원)"]],u:(I,x)=>x.pz!=null&&I.n?x.pz/I.n:null,staff:"응모 받기·추첨·발표 일손",back:"한 번 참여로 끝나기 쉬움. 다음 방문 조건(쿠폰 등)을 붙여야 재방문으로 이어짐"}];
const CMPG={"신규 유입":["할인","덤","증정","체험","경품"],"재방문":["도장","할인","증정","경품"],"객단가 올리기":["덤","증정","할인"],"한가한 시간 채우기":["할인","체험","증정","경품"]};
RENDER.cmp=()=>{const I0=inp();body(`<p class="small" style="margin:0">같은 목표를 이루는 방식들을 같은 숫자로 나란히 놓습니다. 순서는 실제 사례에서 많이 쓰인 순이고, 어느 것이 낫다고 표시하지 않습니다. 판단은 사장님이 합니다.</p>
 <div class="grid"><label>목표<select id="cm-goal">${Object.keys(CMPG).map(g=>`<option>${g}</option>`).join("")}</select></label>
 <label>객단가(원)<input id="cm-ag" inputmode="numeric"></label><label>대표 상품 원가율(%)<input id="cm-cr" inputmode="numeric" placeholder="예: 35"></label>
 <label>행사 참여 손님 수(명)<input id="cm-n" inputmode="numeric"></label><label>시간당 인건비(원)<input id="cm-w" inputmode="numeric"></label>
 <label>본사·가맹 행사에 참여<select id="cm-hq"><option>아니오</option><option>예</option></select></label><label>본사 행사일 때 가게 부담 비율(%)<input id="cm-hqs" inputmode="numeric" placeholder="예: 50"></label></div>
 <div id="cm-in"></div><div class="tw" id="cm-out"></div><div id="cm-sig"></div>
 <h3 style="margin-top:12px">대목 인력 운영 나란히</h3>
 <div class="grid"><label>평소 하루 손님(명)<input id="st-b" inputmode="numeric"></label><label>대목 예상 배수(사장님 짐작)<input id="st-m" inputmode="decimal" placeholder="예: 2"></label>
 <label>직원 1명이 1시간에 받는 손님(명)<input id="st-c" inputmode="numeric"></label><label>영업시간(시간)<input id="st-h" inputmode="numeric"></label>
 <label>지금 인원(명)<input id="st-s" inputmode="numeric"></label><label>추가할 인원(명)<input id="st-x" inputmode="numeric" placeholder="예: 1"></label>
 <label>예약으로 받을 최대 손님(명)<input id="st-r" inputmode="numeric"></label><label>메뉴 줄이면 처리량이 늘어나는 비율(%)<input id="st-u" inputmode="numeric" placeholder="사장님 짐작"></label></div>
 <div class="tw" id="st-out"></div>
 <p class="small" style="margin:0">평소 인력으로 몇 배 손님을 받다가 대기·품절·불친절 후기로 번진 사례가 있습니다(사례 검색에서 「대목」). 숫자는 모두 사장님이 넣은 값으로만 계산합니다.</p>`);
 const ag=$("#cm-ag");if(I0&&!ag.value&&window.myAvg){const a=myAvg();if(a.ag)ag.value=Math.round(a.ag)}
 const drawIn=()=>{const ks=CMPG[v7("#cm-goal")].slice().sort((a,b)=>((MTK[b]||{})["실제"]||0)-((MTK[a]||{})["실제"]||0));P11.ks=ks;
  $("#cm-in").innerHTML=`<div class="grid">${ks.map(k=>CMP.find(c=>c.k===k)).map(c=>c.f.map(([id,l])=>`<label>${esc(c.nm)} — ${esc(l)}<input data-cm="${c.k}.${id}" inputmode="decimal"></label>`).join("")+`<label>${esc(c.nm)} — 더 드는 일손(시간)<input data-cm="${c.k}.hrs" inputmode="decimal"></label>`).join("")}</div>`};
 const calc=()=>{const I={ag:n7("#cm-ag"),cr:n7("#cm-cr"),n:n7("#cm-n"),w:n7("#cm-w")},hq=v7("#cm-hq")==="예",hqs=n7("#cm-hqs"),liq=inp().liq==="예";const NA="넣지 않음";
  const per=I.ag!=null&&I.cr!=null?I.ag*(1-I.cr/100):null;const P=n7("#cm-n");const sig=[];const rate=(D.mtd||{})["할인율"];
  const rows=(P11.ks||[]).map(k=>{const c=CMP.find(x=>x.k===k),x={};document.querySelectorAll(`[data-cm^="${k}."]`).forEach(i=>{const s=i.value.replace(/[^0-9.]/g,"");x[i.dataset.cm.split(".")[1]]=s===""?null:+s});
   let u=c.u(I,x);if(u!=null&&hq&&hqs!=null)u=u*hqs/100;const lab=x.hrs!=null&&I.w!=null?x.hrs*I.w:0;
   const tot=u!=null&&I.n!=null?u*I.n+lab:null;let be=tot!=null&&per?Math.ceil(tot/per):null;
   if(c.free&&tot!=null&&per&&x.r!=null&&I.n!=null){const buy=Math.round(I.n*x.r/100);be=Math.max(0,Math.ceil((tot-buy*per)/per))}
   if((k==="할인"||k==="증정")&&u!=null&&I.ag&&rate){const pct=u/I.ag*100;if(pct<rate["하위25"])sig.push(`${c.nm}: 혜택이 객단가의 ${pct.toFixed(1)}%로, 이 도구 사례 DB 할인·쿠폰 사례 ${rate["건"]}건의 하위 25%(${rate["하위25"]}%)보다 작습니다. 손님이 혜택을 거의 못 느낄 수 있습니다.`)}
   if(c.free)sig.push(`${c.nm}: 공짜로 받은 손님이 정가 방문을 미루는 위험이 있습니다(영상 사례 「공짜 판촉 역효과」는 주장 단계 자료). 무료 대상을 처음 오는 손님으로 좁히고 다음 방문 조건을 붙이는 방법을 함께 보세요.`);
   const m=MTK[k]||{};const laws=(m["법"]||[]).filter(q=>D.law[q]).map(q=>`${esc(D.law[q].law)} ${esc(D.law[q].art)}`).slice(0,3).join("<br>");
   return [c.nm,u!=null?won(u):NA,tot!=null?won(tot):NA,be!=null?be+"명":NA,lab?won(lab):"넣지 않음",c.staff,c.back,(liq&&MLIQ[k]?`술: ${esc(MLIQ[k])}<br>`:"")+(laws||"—"),m["비중"]!=null?m["비중"]+"%":""]});
  if(hq)sig.push("본사·가맹 행사: 혜택 원가 중 가게 부담분과 더 드는 일손을 넣어 계산했습니다. 본사 공문에 가게 부담 비율이 없으면 먼저 받아 두세요.");
  const H=["방식","1명당 혜택 원가","총비용(혜택+일손)","본전 추가 손님","일손 값","필요 인력","재방문 주기에 미칠 영향","지킬 법","실제 사례 비중"];
  $("#cm-out").innerHTML=`<table><tr>${H.map(h=>`<th>${h}</th>`).join("")}</tr>${rows.map(r=>`<tr>${r.map((v,i)=>`<td${i<5?' class="num"':''}>${i===7?v:esc(v)}</td>`).join("")}</tr>`).join("")}</table>`;
  $("#cm-sig").innerHTML=sig.length?`<div class="note"><b>경고 신호</b><ul class="clean">${sig.map(s=>`<li>${esc(s)}</li>`).join("")}</ul></div>`:"";
  // 대목 인력
  const b=n7("#st-b"),mm=n7("#st-m"),cp=n7("#st-c"),h=n7("#st-h"),s=n7("#st-s"),xx=n7("#st-x"),rr=n7("#st-r"),up=n7("#st-u"),w=I.w,ag2=I.ag;
  if(b==null||mm==null||cp==null||h==null||s==null){$("#st-out").innerHTML=`<p class="small">평소 하루 손님, 예상 배수, 1명이 받는 손님, 영업시간, 지금 인원을 넣으면 네 가지 운영을 나란히 계산합니다.</p>`;return}
  const dem=Math.round(b*mm),cap0=s*cp*h;const opt=[["지금 인원",cap0,0],["추가 인원",xx!=null?(s+xx)*cp*h:null,xx!=null&&w!=null?xx*h*w:null],["예약 제한",rr!=null?Math.min(rr,cap0):null,0],["메뉴 축소",up!=null?Math.round(cap0*(1+up/100)):null,0]];
  const sv0=Math.min(dem,cap0);
  $("#st-out").innerHTML=`<table><tr><th>운영</th><th>받을 수 있는 손님</th><th>못 받는 손님(대기·이탈 짐작)</th><th>추가 인건비</th><th>지금 인원 대비 매출 차이</th></tr>${opt.map(([n,cap,cost])=>{if(cap==null)return `<tr><td>${n}</td><td colspan="4" class="small">값을 넣으면 계산</td></tr>`;const sv=Math.min(dem,cap);return `<tr><td>${n}</td><td class="num">${sv}명</td><td class="num">${dem-sv}명</td><td class="num">${cost==null?"시급 필요":won(cost)}</td><td class="num">${ag2!=null?won((sv-sv0)*ag2-(cost||0)):"객단가 필요"}</td></tr>`}).join("")}</table><p class="small">예상 손님 ${dem}명(평소 × 배수). 예약 제한은 미리 알린 거절이라 현장 항의가 줄 수 있고, 메뉴 축소는 처리량이 늘어나는 대신 고를 메뉴가 줄어듭니다.</p>`};
 drawIn();$("#cm-goal").addEventListener("change",()=>{drawIn();calc()});$("#tool-body").addEventListener("input",calc);$("#tool-body").addEventListener("change",calc);calc()};

// 3) 올해 행사 달력 — 날짜는 캘린더 도구 파일(D.cal)만. 대목은 달력 종류로 고름. 사장님 계획·이슈 시점·매주 이벤트는 내 기록에 저장
const BIG=r=>r[2]==="명절·세시"||(r[2]==="공휴일"&&/설|추석|어린이날|성탄|크리스마스|연휴/.test(r[1]))||/크리스마스|성탄|빼빼로|화이트|발렌타인|밸런타인/.test(r[1]);
RENDER.year=()=>{const y0=TODAY.slice(0,7),months=[...Array(12).keys()].map(i=>{const d=new Date(y0+"-01T00:00:00");d.setMonth(d.getMonth()+i);return d.getFullYear()+"-"+String(d.getMonth()+1).padStart(2,"0")});
 const plans=ST.rec.filter(r=>r.t==="계획");
 body(`<p class="small" style="margin:0">날짜는 캘린더 도구가 내보낸 파일에서만 가져옵니다(${esc((D.cal[0]||[])[4]||"")} 기준). 대목에는 준비 점검표가 붙고, 고른 행사안·이슈 시점(영화·방송·계절)·매주 하는 이벤트를 직접 올릴 수 있습니다.</p>
 <div class="grid"><label>날짜<input type="date" id="yr-d" value="${TODAY}"></label><label>종류<select id="yr-k"><option>행사</option><option>이슈 시점(영화·방송·계절)</option><option>매주 하는 이벤트</option></select></label>
 <label>이름<input id="yr-n" value="${esc(CUR?CUR.n:"")}" placeholder="예: 매주 목요일 뽑기"></label><label>메모<input id="yr-m" placeholder="예: 인원 1명 더"></label></div>
 <div class="row"><button type="button" class="main" id="yr-add">달력에 올리기</button><button type="button" id="yr-csv">계획 CSV 내려받기</button><span class="small" id="yr-msg"></span></div>
 ${months.map(m=>{const cal=D.cal.filter(r=>r[0].startsWith(m));const mine=plans.filter(p=>p.d&&p.d.startsWith(m));const wk=plans.filter(p=>p.k==="매주 하는 이벤트");
  if(!cal.length&&!mine.length)return "";
  return `<details${m===y0?" open":""}><summary><b>${m.replace("-","년 ")}월</b> <span class="small">날 ${cal.length}개${mine.length?` · 내 계획 ${mine.length}개`:""}</span></summary><ul class="clean small">
  ${cal.map(r=>`<li>${esc(r[0].slice(5))} ${esc(r[1])} <span class="small">(${esc(r[2])})</span>${BIG(r)?` <b>대목</b><details><summary class="small">대목 준비 점검</summary><ul class="clean small"><li>예상 손님 배수를 정하고 「방식 나란히 비교」의 대목 인력 운영으로 지금 인원·추가 인원·예약 제한·메뉴 축소를 비교</li><li>인력 증원·근무표를 일주일 전에 확정</li><li>특별 메뉴는 이 날짜 앞뒤로 알리기(메뉴 개발은 다른 도구 몫)</li><li>처음 온 손님을 단골로 만드는 장치(도장 카드·다음 방문 쿠폰)를 준비</li><li>실패 사례 보기: 사례 검색에서 「대목」</li></ul></details>`:""}</li>`).join("")}
  ${mine.map(p=>`<li><b>${esc(p.d.slice(5))} ${esc(p.name)}</b> <span class="small">(${esc(p.k)})${p.memo?" · "+esc(p.memo):""}</span> <button type="button" class="ghost" data-yrx="${esc(p.id)}">지우기</button></li>`).join("")}
  ${wk.length?`<li class="small">매주: ${wk.map(p=>esc(p.name)).join(" · ")}</li>`:""}</ul></details>`}).join("")}`);
 $("#yr-add").addEventListener("click",async()=>{const d=v7("#yr-d"),n=v7("#yr-n");if(!d||!n){$("#yr-msg").textContent="날짜와 이름을 넣으세요";return}
  if(await recPut({t:"계획",d,name:n,k:v7("#yr-k"),memo:v7("#yr-m"),ci:CUR?String(CUR.i):""}))RENDER.year()});
 document.querySelectorAll("[data-yrx]").forEach(b=>b.addEventListener("click",async()=>{await recDel(b.dataset.yrx);RENDER.year()}));
 $("#yr-csv").addEventListener("click",()=>{const rows=[["날짜","종류","이름","메모","달력 날"]];ST.rec.filter(r=>r.t==="계획").sort((a,b)=>a.d<b.d?-1:1).forEach(p=>rows.push([p.d,p.k,p.name,p.memo||"",(D.cal.find(r=>r[0]===p.d)||[])[1]||""]));saveFile(`행사계획_${TODAY}.csv`,toCSV(rows))})};

// 4) 공동구매 행사 설계 — 발주 쪽과는 파일로만
RENDER.gb=()=>{body(`<div class="grid"><label>상품 이름<input id="gb-nm" placeholder="예: 김장 양념 세트"></label><label>낱개 정상가(원)<input id="gb-p" inputmode="numeric"></label>
 <label>묶음 수량(개)<input id="gb-u" inputmode="numeric" placeholder="예: 3"></label><label>묶음 판매가(원)<input id="gb-bp" inputmode="numeric"></label><label>개당 원가(원)<input id="gb-c" inputmode="numeric"></label>
 <label>샘플(시식·견본) 개수<input id="gb-sm" inputmode="numeric" value="0"></label><label>최소 성립 묶음 수<input id="gb-min" inputmode="numeric"></label>
 <label>모집 시작<input type="date" id="gb-s"></label><label>주문 마감<input type="date" id="gb-e"></label><label>손님 수령일<input type="date" id="gb-r"></label>
 <label>지금까지 모인 묶음 수<input id="gb-o" inputmode="numeric" value="0"></label></div>
 <div class="out" id="gb-out"></div><div id="gb-sch"></div>
 <div class="row"><button type="button" id="gb-file">발주용 파일 내려받기</button><span class="small" id="gb-msg"></span></div>
 ${lawUl("공동구매에서 지킬 것",lawKeysBy(/전자상거래|통신판매|택배|낱개|표시/).slice(0,5))}`);
 const up=()=>{const p=n7("#gb-p"),u=n7("#gb-u"),bp=n7("#gb-bp"),c=n7("#gb-c"),sm=n7("#gb-sm")||0,mn=n7("#gb-min"),o=n7("#gb-o")||0;const NA="계산 불가";
  const each=bp!=null&&u?bp/u:null,ep=each!=null&&c!=null?each-c:null,bpf=ep!=null?ep*u:null,dc=p&&each!=null?(1-each/p)*100:null,smc=c!=null?sm*c:null,be=bpf&&bpf>0&&smc!=null?Math.ceil(smc/bpf):null;
  $("#gb-out").innerHTML=[["낱개로 따진 할인율",dc!=null?dc.toFixed(1)+"%":NA],["개당 이익",ep!=null?won(ep):NA],["묶음당 이익",bpf!=null?won(bpf):NA],["샘플 비용",smc!=null?won(smc):NA],["샘플 비용 본전 묶음 수",be!=null?be+"묶음":NA],["최소 성립 때 이익",bpf!=null&&mn!=null&&smc!=null?won(bpf*mn-smc):NA],["지금 모인 묶음",`${o}묶음${mn?(o>=mn?" — 성립":` — ${mn-o}묶음 더 필요`):""}`]].map(([a,b])=>`<div><span>${a}</span><b>${b}</b></div>`).join("")+(ep!=null&&ep<=0?`<div style="grid-column:1/-1"><span>주의</span><b>묶음 판매가가 원가보다 낮아 팔수록 손해입니다</b></div>`:"");
  const s=v7("#gb-s"),e=v7("#gb-e"),r=v7("#gb-r");
  $("#gb-sch").innerHTML=s&&e&&r?`<div class="tw"><table><tr><th>날짜</th><th>할 일</th></tr><tr><td>${s}</td><td>모집 시작 — 샘플 내놓기, 묶음 가격·수령일·취소 조건 알리기</td></tr><tr><td>${e}</td><td>주문 마감 — 성립 여부 알리기, 발주용 파일 보내기</td></tr><tr><td>${addD(e,1)}</td><td>발주(파일로만 전달)</td></tr><tr><td>${r}</td><td>손님 수령 — 한꺼번에 내주기, 남은 수량 정리</td></tr></table></div>${e>=r?`<p class="small">수령일이 마감보다 늦어야 합니다.</p>`:""}`:""};
 $("#tool-body").addEventListener("input",up);up();
 $("#gb-file").addEventListener("click",()=>{const nm=v7("#gb-nm"),u=n7("#gb-u"),o=n7("#gb-o")||0;if(!nm||!u||!o){$("#gb-msg").textContent="상품 이름·묶음 수량·모인 묶음 수를 넣으세요";return}
  fileJSON(`공동구매_발주_${TODAY}.json`,{종류:"공동구매발주",기준일:TODAY,출처:"사장님 행사안 고르기",품목:nm,묶음수량:u,묶음수:o,낱개합계:u*o,주문마감:v7("#gb-e"),수령일:v7("#gb-r"),메모:"손님 이름·연락처는 넣지 않음"});$("#gb-msg").textContent="내려받았습니다. 발주 쪽 도구에 이 파일을 넘기세요."})};

// 5) 손님 제한 정책 행사 — 예상 이탈, 항의 대응 문구, 차별 경고
const LIMT={"아이 동반 제한(노키즈)":"안전사고 위험 때문에 ○○ 시간대(공간)에는 만 ○세 미만 손님을 받지 않습니다. 다른 시간대에는 어린이 손님도 환영합니다.","특정 시간대 단체 제한":"○○시~○○시에는 ○명 이상 단체 예약을 받지 않습니다. 그 밖의 시간에는 예약해 주시면 자리를 마련하겠습니다.","예약 손님만":"재료 준비 때문에 ○○일은 예약하신 손님만 모십니다. 예약은 ○○로 받습니다.","특정 메뉴 안 팔기":"재료 사정으로 ○○ 메뉴는 당분간 팔지 않습니다. 대신 ○○를 준비했습니다."};
RENDER.lim=()=>{body(`<div class="grid"><label>정책<select id="lm-t">${Object.keys(LIMT).map(k=>`<option>${k}</option>`).join("")}</select></label><label>평소 하루 손님(명)<input id="lm-b" inputmode="numeric"></label><label>정책에 걸리는 손님 비중(%, 짐작)<input id="lm-s" inputmode="numeric"></label><label>객단가(원)<input id="lm-a" inputmode="numeric"></label></div>
 <div class="out" id="lm-out"></div><label>안내·항의 대응 문구<textarea id="lm-txt"></textarea></label>
 <div class="note"><b>지킬 것</b><ul class="clean small"><li>장애인 보조견을 데려온 손님은 어떤 정책이든 거절하지 않습니다.</li><li>나이·국적·성별·장애 등을 이유로 한 일률적 거절은 차별 진정 대상이 될 수 있어, 이유(안전·공간)와 대안(다른 시간대·공간)을 함께 적습니다.</li><li>항의에는 정책 이유와 대안을 같은 말로 차분히 되풀이하고, 손님을 탓하는 말은 쓰지 않습니다.</li></ul></div>
 ${lawUl("손님 제한 정책 관련 법",lawKeysBy(/차별|보조견|인권|장애/).slice(0,6))}${faqBox(["F036","F059"])}`);
 const up=()=>{const b=n7("#lm-b"),s=n7("#lm-s"),a=n7("#lm-a");const out=b!=null&&s!=null?Math.round(b*s/100):null;
  $("#lm-out").innerHTML=[["하루 예상 이탈 손님",out!=null?out+"명(짐작)":"계산 불가"],["하루 줄어드는 매출",out!=null&&a!=null?won(out*a):"계산 불가"]].map(([x,y])=>`<div><span>${x}</span><b>${y}</b></div>`).join("")};
 const tx=()=>{$("#lm-txt").value=`[안내] ${LIMT[v7("#lm-t")]}\n장애인 보조견과 함께 오시는 분은 언제든 들어오실 수 있습니다.\n\n[항의를 받았을 때] 불편을 드려 죄송합니다. ${v7("#lm-t").includes("노키즈")?"좁은 공간에서 뜨거운 음식을 다뤄 안전을 위해 정한 것입니다. ○○ 시간대에는 함께 오실 수 있습니다.":"가게 사정으로 정한 것이라 양해 부탁드립니다. 대신 ○○를 안내해 드리겠습니다."}`};
 $("#lm-t").addEventListener("change",tx);$("#tool-body").addEventListener("input",up);tx();up()};

// 6) 동네 문화공간 행사·동네 코스 안내문 — 지도 도구에는 파일로만
RENDER.course=()=>{body(`<p class="small" style="margin:0">가게를 작은 전시·원데이 클래스·낭독회·동네 장터 같은 문화공간 행사에 열거나, 이웃 가게와 걷는 코스를 묶어 안내문을 만듭니다. 장소 이름은 사장님이 넣은 값만 씁니다.</p>
 <div class="grid"><label>코스 이름<input id="co-n" placeholder="예: 골목 한 바퀴"></label><label>문화공간 행사(선택)<select id="co-e"><option value="">없음</option><option>작은 전시</option><option>원데이 클래스</option><option>낭독회·작은 공연</option><option>동네 장터</option></select></label></div>
 <div id="co-rows"></div><div class="row"><button type="button" id="co-add">장소 더하기</button><button type="button" class="main" id="co-make">안내문 만들기</button><button type="button" id="co-file">지도용 파일 내려받기</button><span class="small" id="co-msg"></span></div>
 <label>코스 안내문<textarea id="co-txt"></textarea></label>
 <div class="note"><b>지킬 것</b><ul class="clean small"><li>현수막·입간판·전단은 구청 신고·지정 게시대 대상일 수 있습니다.</li><li>음식을 나눠 주거나 팔면 영업 신고 범위를 넘지 않는지 확인하세요.</li><li>음악을 틀거나 공연하면 저작권 사용료 대상인지 살피세요.</li><li>이웃 가게와 같은 할인율을 함께 정하지 마세요(공동행위).</li></ul></div>${lawUl("관련 법",lawKeysBy(/옥외|공동행위|사업자단체/).slice(0,4))}`);
 const row=i=>`<div class="grid" data-co="${i}"><label>${i+1}. 장소 이름<input data-cf="n"></label><label>한 줄 소개<input data-cf="d"></label><label>주소(지도 도구용)<input data-cf="a"></label><label>다음 장소까지 걸어서(분)<input data-cf="w" inputmode="numeric"></label></div>`;
 P11.co=P11.co||3;$("#co-rows").innerHTML=[...Array(P11.co).keys()].map(row).join("");
 $("#co-add").addEventListener("click",()=>{P11.co++;$("#co-rows").insertAdjacentHTML("beforeend",row(P11.co-1))});
 const get=()=>[...document.querySelectorAll("[data-co]")].map(g=>{const o={};g.querySelectorAll("[data-cf]").forEach(i=>o[i.dataset.cf]=i.value.trim());return o}).filter(o=>o.n);
 $("#co-make").addEventListener("click",()=>{const L=get();if(L.length<2){$("#co-msg").textContent="장소를 두 곳 이상 넣으세요";return}
  $("#co-txt").value=`[${v7("#co-n")||"동네 코스"}]${v7("#co-e")?` — ${shopNm()}에서 ${v7("#co-e")}`:""}\n`+L.map((o,i)=>`${i+1}. ${o.n}${o.d?" — "+o.d:""}${o.w&&i<L.length-1?` (다음 곳까지 걸어서 ${o.w}분)`:""}`).join("\n")+`\n코스를 돌며 각 가게에서 확인 도장을 받아 보세요.`;$("#co-msg").textContent="만들었습니다"});
 $("#co-file").addEventListener("click",()=>{const L=get();if(!L.length){$("#co-msg").textContent="장소를 넣으세요";return}fileJSON(`동네코스_${TODAY}.json`,{종류:"동네코스",기준일:TODAY,출처:"사장님 행사안 고르기",이름:v7("#co-n"),행사:v7("#co-e"),장소:L.map((o,i)=>({순서:i+1,이름:o.n,소개:o.d,주소:o.a,다음까지_걸어서_분:o.w?+o.w:null}))});$("#co-msg").textContent="내려받았습니다. 지도 도구에 이 파일을 넘기세요."})};

// 7) 쿠폰 번호·QR을 다른 도구가 읽는 파일로(도구끼리 직접 잇지 않음)
const _cpList11=cpList;cpList=function(){_cpList11();const el=$("#cp-list");if(!el)return;
 el.querySelectorAll("[data-pq]").forEach(b=>{const id=b.dataset.pq;if(b.parentNode.querySelector("[data-cpx]"))return;b.insertAdjacentHTML("afterend",` <button type="button" class="ghost" data-cpx="${esc(id)}">다른 도구용 파일</button>`)});
 el.querySelectorAll("[data-cpx]").forEach(b=>b.addEventListener("click",()=>{const g=ST.rec.find(r=>r.id===b.dataset.cpx);if(!g)return;const L=[];for(let i=1;i<=g.n;i++){const sn=serial(g,i);L.push({번호:sn,확인글자:g.salt?sn.slice(-2):"",QR글:sn,상태:cpState(g,sn),사용일시:(g.used[sn]||"")})}
  fileJSON(`쿠폰발급목록_${TODAY}.json`,{종류:"쿠폰발급목록",판:1,기준일:TODAY,출처:"사장님 행사안 고르기",묶음:{종류:g.kind,혜택:g.ben,시작:g.s,끝:g.e,조건:[g.min?won(g.min)+" 이상":"",g.when,g.one?"1인 1장":"",g.dup?"중복 불가":""].filter(Boolean).join(" · ")},번호:L,설명:"QR글은 QR 안에 담긴 글 그대로. 확인 글자는 번호 끝 두 글자이며 비밀값은 넘기지 않음"})}))};

// 8) 문자 발송용 파일 — 특정 발송 사업자에 묶지 않은 일반 형식(이 도구는 손님에게 직접 보내지 않음)
function smsFile(){const t=($("#nt-sms")||{}).value||"";if(!t.trim()){alert("문자 글이 비어 있습니다");return}
 saveFile(`문자발송용_${TODAY}.csv`,toCSV([["본문","바이트","광고 표시","무료 수신거부","보낼 수 없는 시간","받는 사람"],[t,bytes(t),/^\(광고\)/.test(t.trim())?"있음":"없음",/수신 ?거부/.test(t)?"있음":"없음","오후 9시~다음 날 오전 8시(따로 동의한 손님 제외)","발송 도구에서 수신 동의한 손님만 고르기"]]))}
document.addEventListener("click",e=>{if(e.target.closest("[data-tab='notice']"))setTimeout(()=>{const c=$("#nt-check");if(c&&!$("#sms-file")){c.insertAdjacentHTML("beforebegin",`<div class="row"><button type="button" id="sms-file">문자 발송용 파일 내려받기</button><span class="small">문자 발송 도구가 읽는 일반 CSV입니다. 이 도구는 손님에게 직접 보내지 않습니다.</span></div>`);$("#sms-file").addEventListener("click",smsFile)}},50)});

Object.assign(TOOLS,{cmp:"방식 나란히 비교",year:"올해 행사 달력",gb:"공동구매 행사",lim:"손님 제한 정책",course:"동네 코스·문화공간"});
Object.assign(TOOLDESC,{cmp:"같은 목표의 방식들을 원가·본전·인력·재방문·법으로 나란히, 대목 인력 운영 비교",year:"캘린더 파일의 날과 대목 점검표, 내 계획·이슈 시점·매주 이벤트",gb:"묶음 수량·할인가·개당 이익·샘플·일정과 발주용 파일",lim:"예상 이탈·항의 대응 문구·차별 관련 지킬 것",course:"이웃 가게와 걷는 코스 안내문과 지도용 파일"});
