
// ── 판 11: 공통 품질 — 다시 뽑기·이전·원본으로, 결과 화면에서 바로 다시 고르기, 사례 검색(즉시 거르기·기능 이름으로 이동·조회 제한),
// 처음 쓰는 가게(기본 정보 한 번·처음 순서·업종별 샘플·샘플 저장 막기), 저장(백업 알림·형식 판·가져오기 수·다시 검사·CSV 가져오기),
// 날씨·내 기록 값, 개선 제안 칸. 설정값: D.set(spec/설정.json)
const SET=D.set||{};const LIM=SET["조회제한"]||{"하루_사례_보기":600,"한번_목록":20,"하루_내려받기":20};
const lsJ=(k,d)=>{try{return JSON.parse(localStorage.getItem(k)||"null")??d}catch(e){return d}};const lsS=(k,v)=>{try{localStorage.setItem(k,JSON.stringify(v))}catch(e){}};

// 1) 다시 뽑기·이전·원본으로(채택 = 카드의 「이 안으로」)
const DRW={h:[],i:-1,busy:false};
window.afterRun=()=>{const ids=PICKS.filter(c=>c.k!=="응용예시").map(c=>c.i);
 if(!DRW.busy){DRW.h=[ids];DRW.i=0}else{DRW.h=DRW.h.slice(0,DRW.i+1);DRW.h.push(ids);DRW.i++}DRW.busy=false;
 const s2=$("#s2");let bar=$("#drw-bar");if(!bar){s2.querySelector(".sh").insertAdjacentHTML("afterend",`<div class="row" id="drw-bar"><button type="button" id="drw-new">다시 뽑기</button><button type="button" id="drw-prev">이전</button><button type="button" id="drw-org">원본으로</button><label class="small">단계<select id="drw-st"></select></label><label class="small">예산(원)<input id="drw-bud" inputmode="numeric" style="max-width:120px"></label><span class="small" id="drw-n"></span></div>`);bar=$("#drw-bar");
  $("#drw-st").innerHTML=$("#in-st").innerHTML;
  $("#drw-new").addEventListener("click",()=>{const ex=new Set(DRW.h.slice(0,DRW.i+1).flat());window.EXCL=ex;DRW.busy=true;run();window.EXCL=null;if(!PICKS.some(c=>c.k!=="응용예시"&&c.kd==="행사"))$("#drw-n").textContent="더 뽑을 사례가 없습니다. 「원본으로」를 누르세요."});
  $("#drw-prev").addEventListener("click",()=>{if(DRW.i<=0){$("#drw-n").textContent="첫 뽑기입니다";return}const tgt=DRW.i-1;window.EXCL=new Set(DRW.h.slice(0,tgt).flat());const keep=DRW.h;run();window.EXCL=null;DRW.h=keep;DRW.i=tgt;$("#drw-n").textContent=`뽑기 ${DRW.i+1}/${DRW.h.length}`});
  $("#drw-org").addEventListener("click",()=>{window.EXCL=null;run()});
  $("#drw-st").addEventListener("change",()=>{$("#in-st").value=$("#drw-st").value;$("#in-st").dispatchEvent(new Event("change"));run()});
  $("#drw-bud").addEventListener("change",()=>{$("#in-bud").value=$("#drw-bud").value;run()})}
 $("#drw-st").value=$("#in-st").value;$("#drw-bud").value=$("#in-bud").value;$("#drw-n").textContent=`뽑기 ${DRW.i+1}/${DRW.h.length}`};

// 2) 사례 검색 — 고르는 즉시 결과 수·목록이 바뀜, 기능 이름을 치면 그 화면으로, 하루 조회 수 제한(유출 방지)
const FEAT=()=>[...Object.entries(TOOLS).map(([k,n])=>({n,d:TOOLDESC[k]||"",go:()=>openTool(k),w:"4단계 행사 도구 「"+n+"」"})),
 ...[["notice","홍보 글"],["plan","알림 순서"],["prep","준비할 것"],["risk","주의 사항"],["cost","원가·남는지"]].map(([k,n])=>({n,d:"3단계 탭",go:()=>{if(!CUR){alert("먼저 행사안을 하나 고르세요");return}tab(k);$("#s3").scrollIntoView()},w:"3단계 「"+n+"」 탭"})),
 {n:"행사 방식부터 보기",d:"기본 방식 12가지 비중",go:()=>{$("#mbox").open=true;mRender();$("#mbox").scrollIntoView()},w:"1단계 「행사 방식부터 보기」"}];
function viewOk(n){const k="p11view",d=lsJ(k,{d:"",n:0});if(d.d!==TODAY){d.d=TODAY;d.n=0}if(d.n+n>LIM["하루_사례_보기"])return false;d.n+=n;lsS(k,d);return true}
RENDER.find=()=>{const MS=(D.mtd&&D.mtd["방식"])||[];body(`<div class="grid"><label>찾을 말(사례 낱말 또는 기능 이름)<input id="fd-q" placeholder="예: 대목, 도장, 쿠폰 만들기"></label>
 <label>업종<select id="fd-i"><option value="">전체</option>${IND.map(i=>`<option>${i}</option>`).join("")}</select></label>
 <label>행사 방식<select id="fd-m"><option value="">전체</option>${MS.map(m=>`<option value="${esc(m["키"])}">${esc(m["이름"])}</option>`).join("")}</select></label>
 <label>판정<select id="fd-v"><option value="">전체</option><option value="가능">가능</option><option value="조건부">조건부</option><option value="확인">신중</option><option value="불가">불가</option></select></label>
 <label>자료 종류<select id="fd-k"><option value="">전체</option><option value="실제">실제 사례</option><option value="응용">응용</option><option value="영상">영상 사례(주장)</option></select></label></div>
 <div id="fd-go"></div><p class="small" id="fd-n" style="margin:0"></p><div class="plans" id="fd-list"></div>`);
 const up=()=>{const q=v7("#fd-q"),i=v7("#fd-i"),m=v7("#fd-m"),v=v7("#fd-v"),k=v7("#fd-k");
  const F=q?FEAT().filter(f=>(f.n+" "+f.d).includes(q)||q.split(/\s+/).every(w=>w&&(f.n+f.d).includes(w))):[];
  $("#fd-go").innerHTML=F.length?`<div class="row"><span class="small">기능:</span>${F.slice(0,4).map((f,j)=>`<button type="button" data-fg="${j}">${esc(f.w)}로 가기</button>`).join("")}</div>`:"";
  $("#fd-go").querySelectorAll("[data-fg]").forEach(b=>b.addEventListener("click",()=>F[+b.dataset.fg].go()));
  const L=D.cases.filter(c=>(!i||c.ind.split("|").includes(i))&&(!m||(c.mt||[]).includes(m))&&(!v||String(c.v).startsWith(v))&&(!k||c.k===k)&&(!q||(c.n+" "+c.s+" "+c.b+" "+c.c).includes(q)));
  const show=L.slice(0,LIM["한번_목록"]);
  $("#fd-n").textContent=`맞는 사례 ${L.length.toLocaleString()}건${L.length>show.length?` — 앞의 ${show.length}건만 보여 줍니다. 조건을 더 좁혀 보세요.`:""}`;
  if(!viewOk(show.length)){$("#fd-list").innerHTML=`<p class="empty">오늘 볼 수 있는 사례 수(${LIM["하루_사례_보기"]}건)를 다 봤습니다. 내일 다시 볼 수 있습니다.</p>`;return}
  $("#fd-list").innerHTML=show.map((c,j)=>{const [vc,vt]=vClass(c.v);return `<article class="plan"><div class="badges"><span class="badge ${vc}">${vt}</span>${c.k==="영상"?`<span class="badge b-info">영상 사례(주장)</span>`:""}${c.lq?`<span class="badge b-bad">술 혜택 — 광고에 쓰면 안 됨</span>`:""}</div><h3>${esc(c.n)}</h3><p class="small" style="margin:0">${esc(c.s)}</p><div class="row"><button type="button" data-fp="${c.i}">이 사례로 행사안 보기</button></div></article>`}).join("")||`<p class="empty">맞는 사례가 없습니다. 조건을 넓혀 보세요.</p>`;
  $("#fd-list").querySelectorAll("[data-fp]").forEach(b=>b.addEventListener("click",()=>{const c=D.cases.find(x=>String(x.i)===b.dataset.fp);if(!c)return;PICKS.push(c);pick(PICKS.length-1)}))};
 let tm=null;$("#tool-body").addEventListener("input",()=>{clearTimeout(tm);tm=setTimeout(up,150)});$("#tool-body").addEventListener("change",up);up()};

// 3) 처음 쓰는 가게 — 기본 정보 한 번, 처음 순서, 업종별 샘플(표시·한 번에 숨기기), 샘플은 저장·게시 막기
const SAMPLES={"요식업":{name:"동네고깃집",sub:"고깃집",st:"그랜드오픈"},"소매":{name:"골목편의점",sub:"편의점",st:"정착기"},"서비스업":{name:"동네세탁소",sub:"세탁",st:"상시"},"학원·교육":{name:"우리동네학원",sub:"학원",st:"오픈전"},"미용·뷰티":{name:"골목미용실",sub:"미용실",st:"정착기"},"병의원·약국":{name:"동네약국",sub:"약국",st:"그랜드오픈"}};
window.isSampleShop=()=>/^\(샘플\)/.test(($("#in-name")||{}).value||"");
(function(){const row=document.querySelector("#s1 [data-sample]").parentNode;
 row.insertAdjacentHTML("beforeend",`<select id="smp-ind" aria-label="업종별 샘플"><option value="">업종별 샘플</option>${Object.keys(SAMPLES).map(k=>`<option>${k}</option>`).join("")}</select><button type="button" class="ghost" id="smp-clear">샘플 지우기</button>`);
 $("#s1 .panel").insertAdjacentHTML("beforebegin",`<div class="note" id="first-guide" hidden><b>처음 쓰는 가게라면</b><ul class="clean small"><li>① 아래 가게 정보를 한 번 넣고 「행사안 보기」를 누르면 다음부터 자동으로 채워집니다</li><li>② 「행사 방식부터 보기」로 많이 쓰는 방식을 훑기</li><li>③ 맞는 행사안을 골라 홍보 글·주의 사항·원가 보기</li><li>④ 행사 도구로 쿠폰·달력·결과 기록 준비</li></ul></div>`);
 const mark=()=>{const n=$("#in-name");if(n.value&&!isSampleShop())n.value="(샘플) "+n.value};
 document.querySelectorAll("[data-sample]").forEach(b=>b.addEventListener("click",()=>setTimeout(mark,0)));
 $("#smp-ind").addEventListener("change",()=>{const k=$("#smp-ind").value,s=SAMPLES[k];if(!s)return;$("#in-ind").value=k;$("#in-ind").dispatchEvent(new Event("change"));setTimeout(()=>{$("#in-name").value="(샘플) "+s.name;const o=[...$("#in-sub").options].find(o=>o.value.includes(s.sub));if(o)$("#in-sub").value=o.value;$("#in-sub").dispatchEvent(new Event("change"));$("#in-st").value=s.st;$("#smp-ind").value=""},20)});
 $("#smp-clear").addEventListener("click",()=>{["#in-name","#in-bud"].forEach(q=>$(q).value="");document.querySelectorAll("#in-goals input").forEach(i=>i.checked=false);$("#s2").hidden=true;$("#s3").hidden=true;CUR=null})})();
const _recPut11=recPut;recPut=async(r,q)=>{if(isSampleShop()){if(!q)alert("샘플 가게 정보로는 저장할 수 없습니다. 가게 이름에서 「(샘플)」을 지우고 실제 값으로 바꾼 뒤 저장하세요.");return false}return _recPut11(r,q)};
const _saveFile11=saveFile;saveFile=async(n,t)=>{if(isSampleShop()&&!/^행사기록_백업|^행사안_고르기|모두내보내기/.test(n)){alert("샘플 가게 정보로 만든 글·파일은 내려받을 수 없습니다. 가게 이름을 실제 값으로 바꾸세요.");return}lsS("p11dl",(()=>{const d=lsJ("p11dl",{d:"",n:0});if(d.d!==TODAY){d.d=TODAY;d.n=0}d.n++;return d})());return _saveFile11(n,t)};
document.addEventListener("click",e=>{const b=e.target.closest("[data-copy]");if(b&&isSampleShop()){e.stopImmediatePropagation();e.preventDefault();alert("샘플 가게 정보로 만든 글은 복사·게시하지 않습니다. 가게 이름을 실제 값으로 바꾸세요.")}},true);
async function shopSave(){if(isSampleShop())return;const I=inp();if(!I.name)return;const old=ST.rec.find(r=>r.t==="가게");if(old&&old.name===I.name&&old.ind===I.ind&&old.sub===I.sub)return;await _recPut11({id:"shop_profile",t:"가게",name:I.name,ind:I.ind,sub:I.sub,st:I.st},true)}
$("#go").addEventListener("click",shopSave);
function shopLoad(){const s=ST.rec.find(r=>r.t==="가게");$("#first-guide").hidden=!!s||ST.rec.length>0;if(!s||$("#in-name").value)return;$("#in-name").value=s.name||"";if(s.ind){$("#in-ind").value=s.ind;$("#in-ind").dispatchEvent(new Event("change"))}setTimeout(()=>{if(s.sub)$("#in-sub").value=s.sub;if(s.st)$("#in-st").value=s.st;$("#in-sub").dispatchEvent(new Event("change"))},20)}

// 4) 저장 — 다시 열 때 망가진 기록 거르기·지금 기준 다시 검사, 백업 알림·형식 판·가져오기 수, CSV 가져오기(인코딩 자동), 모두 내보내기
const BKVER=11,BKLOG=["7: 결과·주변·쿠폰","8: 계정 저장소 영문 문서 이름(res_·nb_·cp_)","11: 계획·가게·제안 기록, 결과에 날씨(wx), 쿠폰 확인 글자(salt)"];
const TYPES=["결과","주변","쿠폰","계획","가게","제안"];
const _recLoad11=recLoad;recLoad=async()=>{try{await _recLoad11()}catch(e){ST.rec=[]}
 const bad=[];ST.rec=ST.rec.filter(r=>{const ok=r&&typeof r==="object"&&TYPES.includes(r.t);if(!ok)bad.push(r);return ok});
 ST.recheck={bad:bad.length,pii:ST.rec.filter(r=>PII.test(JSON.stringify(r))).length,exp:ST.rec.filter(r=>r.t==="쿠폰"&&r.e&&r.e<TODAY).length};
 setTimeout(shopLoad,0)};
function bkDue(){const b=lsJ("p11bk","");return ST.rec.filter(r=>r.t!=="가게").length>=3&&(!b||(new Date(TODAY)-new Date(b))/864e5>(SET["백업_권장_일수"]||14))}
const _rs11=renderStore;renderStore=function(){_rs11();const el=$("#store-mode");if(el&&bkDue())el.textContent+=" · 백업 권장"};
const _mine11=RENDER.mine;RENDER.mine=()=>{_mine11();const tb=$("#tool-body");const rc=ST.recheck||{};
 tb.insertAdjacentHTML("afterbegin",`${bkDue()?`<div class="note"><b>백업 권장</b> — 마지막 백업 뒤 ${SET["백업_권장_일수"]||14}일이 지났거나 아직 백업하지 않았습니다. 「기록 내려받기(JSON)」를 눌러 보관하세요.</div>`:""}<p class="small" style="margin:0">지금 기준으로 다시 검사: 읽지 못한 기록 ${rc.bad||0}건, 개인정보 모양 ${rc.pii||0}건, 기간이 지난 쿠폰 묶음 ${rc.exp||0}개. 백업 형식 판 ${BKVER}(옛 판 파일도 받음).</p>`);
 const dl=$("#mn-dl");if(dl){const n=dl.cloneNode(true);dl.replaceWith(n);n.addEventListener("click",()=>{_saveFile11(`행사기록_백업_${TODAY}.json`,JSON.stringify({ver:BKVER,변경기록:BKLOG,만든날:TODAY,rec:ST.rec.map(r=>{const {loc,...b}=r;return b})},null,1));lsS("p11bk",TODAY);RENDER.mine()})}
 const upl=$("#mn-up");if(upl){const n=upl.cloneNode(true);upl.replaceWith(n);n.addEventListener("change",async e=>{const f=e.target.files[0];if(!f)return;let j;try{j=JSON.parse(await f.text())}catch(err){$("#mn-msg").textContent="JSON으로 읽을 수 없는 파일입니다";return}
  const L=Array.isArray(j)?j:(j.rec||[]);if(j.ver&&j.ver>BKVER){$("#mn-msg").textContent=`더 새 판(${j.ver}) 백업입니다. 화면을 새로 고친 뒤 다시 불러오세요.`;return}let a=0,b=0;
  for(const r of L){if(r&&TYPES.includes(r.t)&&r.t!=="가게"&&await _recPut11(Object.assign({},r),true))a++;else b++}$("#mn-msg").textContent=`들어온 기록 ${a}건, 버린 기록 ${b}건(종류가 맞지 않거나 개인정보 모양)`})}
 tb.insertAdjacentHTML("beforeend",`<div class="row"><label class="chip" style="cursor:pointer">결과 기록 CSV 불러오기<input type="file" id="mn-csv" accept=".csv,text/csv" style="display:none"></label><button type="button" id="mn-all">모두 내보내기(그만 쓸 때·기기 옮길 때)</button><button type="button" class="ghost" id="mn-page">이 화면을 파일로 저장(인터넷 없이 열기)</button><span class="small" id="mn-msg2"></span></div><p class="small" style="margin:0">CSV 칸: 행사 이름, 시작, 끝, 행사 전 손님, 행사 중 손님, 행사 전 매출, 행사 중 매출, 쓴 돈, 날씨(엑셀에서 저장한 한글 CSV도 읽습니다)</p>`);
 $("#mn-csv").addEventListener("change",async e=>{const f=e.target.files[0];if(!f)return;const buf=new Uint8Array(await f.arrayBuffer());let txt;
  try{txt=new TextDecoder("utf-8",{fatal:true}).decode(buf)}catch(err){try{txt=new TextDecoder("euc-kr").decode(buf)}catch(e2){$("#mn-msg2").textContent="글자 인코딩을 알 수 없습니다";return}}
  txt=txt.replace(/^﻿/,"");const rows=txt.split(/\r?\n/).filter(Boolean).map(l=>l.split(",").map(x=>x.replace(/^"|"$/g,"").replace(/^'(?=[=+\-@])/,"").trim()));let a=0,b=0;
  for(const r of rows.slice(1)){const num=x=>{const s=(x||"").replace(/[^0-9.]/g,"");return s===""?null:+s};const o={t:"결과",name:r[0],s1:r[1]||"",s2:r[2]||"",c0:num(r[3]),c1:num(r[4]),m0:num(r[5]),m1:num(r[6]),cost:num(r[7]),wx:r[8]||""};
   const odd=[o.c0,o.c1,o.m0,o.m1,o.cost].some(v=>v!=null&&(v<0||v>1e10));if(!o.name||odd){b++;continue}if(await _recPut11(o,true))a++;else b++}
  $("#mn-msg2").textContent=`들어온 기록 ${a}건, 버린 줄 ${b}건(이름 없음·이상한 숫자·개인정보 모양)`});
 $("#mn-all").addEventListener("click",()=>{_saveFile11(`행사기록_모두내보내기_${TODAY}.json`,JSON.stringify({ver:BKVER,변경기록:BKLOG,만든날:TODAY,rec:ST.rec},null,1));
  const by=t=>ST.rec.filter(r=>r.t===t);if(by("결과").length)_saveFile11(`결과기록_모두내보내기_${TODAY}.csv`,toCSV([["행사 이름","시작","끝","행사 전 손님","행사 중 손님","행사 전 매출","행사 중 매출","쓴 돈","날씨"],...by("결과").map(r=>[r.name,r.s1,r.s2,r.c0,r.c1,r.m0,r.m1,r.cost,r.wx||""])]));lsS("p11bk",TODAY)});
 $("#mn-page").addEventListener("click",()=>_saveFile11("행사안_고르기.html","<!doctype html>\n"+document.documentElement.outerHTML))};

// 5) 날씨·내 기록 값 — 기록이 쌓이면 가게 값이 기본값을 대신
window.myAvg=()=>{const R=ST.rec.filter(r=>r.t==="결과"&&r.c1&&r.m1);const ag=R.length?R.reduce((a,r)=>a+r.m1,0)/R.reduce((a,r)=>a+r.c1,0):null;const wx={};
 ST.rec.filter(r=>r.t==="결과"&&r.wx&&r.c0&&r.c1).forEach(r=>{(wx[r.wx]=wx[r.wx]||[]).push(r.c1/r.c0)});return{ag,n:R.length,wx:Object.fromEntries(Object.entries(wx).map(([k,v])=>[k,{x:v.reduce((a,b)=>a+b,0)/v.length,n:v.length}]))}};
const _cost11=cost;cost=function(){_cost11();const a=myAvg();const ag=$("#c-ag");if(ag&&!ag.value&&a.ag){ag.value=Math.round(a.ag);ag.title="내 결과 기록 평균"}
 const add=$("#c-add");if(add&&!$("#c-wx")){add.closest("label").insertAdjacentHTML("afterend",`<label>행사 날 날씨<select id="c-wx"><option value="">모름</option>${["맑음","흐림","비","눈","폭염","한파"].map(w=>`<option>${w}</option>`).join("")}</select></label><label>날씨에 따른 손님 배수<input id="c-wxm" inputmode="decimal" placeholder="내 기록이 없으면 직접"></label>`);
  $("#c-wx").addEventListener("change",()=>{const w=myAvg().wx[$("#c-wx").value];$("#c-wxm").value=w?w.x.toFixed(2):"";$("#c-wxm").title=w?`내 결과 기록 ${w.n}건 평균`:"";calc()})}};
const _calc11=calc;calc=function(){_calc11();const m=n7("#c-wxm"),add=n7("#c-add"),out=$("#c-out");if(!out||m==null||add==null)return;
 out.insertAdjacentHTML("beforeend",`<div><span>날씨 반영 새 손님(${esc(v7("#c-wx")||"직접")} × ${m})</span><b>${Math.round(add*m)}명</b></div>`)};

// 6) 개선 제안 칸 — 이미 있는 기능이면 「있음」과 위치 안내, 없으면 내 기록에 남김
RENDER.idea=()=>{const mine=ST.rec.filter(r=>r.t==="제안");body(`<label>바라는 기능이나 고칠 점<textarea id="id-t" placeholder="예: 쿠폰을 엑셀로 받고 싶어요"></textarea></label><div class="row"><button type="button" class="main" id="id-go">찾아보고 남기기</button></div><div id="id-out"></div>
 ${mine.length?`<details><summary>남긴 제안 ${mine.length}개</summary><ul class="clean small">${mine.map(r=>`<li>${esc(r.name)} <span class="small">(${esc((r.at||"").slice(0,10))})</span></li>`).join("")}</ul></details>`:""}`);
 $("#id-go").addEventListener("click",async()=>{const t=v7("#id-t");if(!t){$("#id-out").innerHTML=`<p class="small">내용을 적어 주세요.</p>`;return}
  const ws=t.split(/[\s,.]+/).filter(w=>w.length>=2);const F=FEAT().map(f=>[f,ws.filter(w=>(f.n+f.d).includes(w)).length]).filter(x=>x[1]).sort((a,b)=>b[1]-a[1]);
  if(F.length){$("#id-out").innerHTML=`<div class="note"><b>있음</b> — 비슷한 기능이 이미 있습니다: ${F.slice(0,3).map(([f],j)=>`<button type="button" data-ig="${j}">${esc(f.w)}</button>`).join(" ")}<br><button type="button" class="ghost" id="id-keep">그래도 제안으로 남기기</button></div>`;
   $("#id-out").querySelectorAll("[data-ig]").forEach(b=>b.addEventListener("click",()=>F[+b.dataset.ig][0].go()));$("#id-keep").addEventListener("click",save)}else save();
  async function save(){if(await recPut({t:"제안",name:t.slice(0,300)}))$("#id-out").innerHTML=`<p class="small">남겼습니다. 「내 기록·백업」의 내보내기에 함께 들어갑니다.</p>`}})};

Object.assign(TOOLS,{find:"사례 검색",idea:"개선 제안"});Object.assign(TOOLDESC,{find:"업종·방식·판정·자료 종류로 바로 거르기, 기능 이름으로 이동",idea:"바라는 기능을 적으면 이미 있는지 찾아 줌"});

// 저장소 없이 열린 화면은 기록 읽기가 이 파일보다 먼저 끝나므로 한 번 더 읽음(기록 검사·가게 정보 채우기)
setTimeout(()=>{recLoad().then(()=>{renderStore();if(TOOL==="mine")openTool("mine",true)})},0);
