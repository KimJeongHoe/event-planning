// ───── 판 7: 행사안을 실제 홍보·실행까지 잇기 ─────
// 손님 개인정보는 받지도 저장하지도 않는다(가게가 직접 적는 숫자·메모만). 날짜는 D.cal(캘린더 jisik-dates에서 옮긴 것)만.
const LAWS=D.law||{};
const ymd=d=>d.getFullYear()+"-"+String(d.getMonth()+1).padStart(2,"0")+"-"+String(d.getDate()).padStart(2,"0");
const addD=(s,n)=>{const d=new Date(s+"T00:00:00");d.setDate(d.getDate()+n);return ymd(d)};
const TODAY=ymd(new Date());
const PII=/01[016789][-\s.]?\d{3,4}[-\s.]?\d{4}|\d{6}[-\s]?[1-4]\d{6}|[\w.+-]+@[\w-]+\.[a-z]{2,}/i;
const v7=q=>($(q)?.value||"").trim();
const n7=q=>{const s=v7(q).replace(/[^0-9.]/g,"");return s===""?null:+s};
// 판 9: 화면에는 상태 배지·미확인 메모를 내지 않음(상태는 spec/법근거_판8.json·docs/화면밖_확인필요_장부.md에만)
function lawLi(k){const L=LAWS[k];if(!L)return "";
 return `<li>⚠ <b>${esc(L.law)} ${esc(L.art)}</b> — ${esc(L.gist)}</li>`}
function lawBox(t,keys,extra){return `<div class="note bad"><b>⚠ ${esc(t)}</b><ul class="clean" style="margin-top:4px">${keys.map(lawLi).join("")}${extra||""}</ul></div>`}
function faqBox(ids){const h=ids.map(f=>{const q=D.faq[f];if(!q)return"";const [fc,ft]=vClass(q.v);return `<div class="faq"><div class="badges"><span class="badge ${fc}">${ft}</span><b class="small">${f}</b></div><p style="margin:4px 0">${esc(q.q)}</p>${q.c?`<details><summary>조건 보기</summary><p class="small" style="margin:4px 0 0">${esc(q.c)}</p></details>`:""}</div>`}).join("");return h?`<details><summary>관련 질문과 답 (FAQ ${ids.join("·")})</summary><div style="display:flex;flex-direction:column;gap:8px;margin-top:6px">${h}</div></details>`:""}
const CONFIRM=t=>"";  // 판 9: 원문 미확인 쟁점은 화면에 내지 않음(docs/화면밖_확인필요_장부.md)

// ── 저장(판 8): 가게 본인만 보는 개인 저장소(db의 data/users/내 번호). 안 되면 이 브라우저에만 ──
// 판 7 버그: 문서 이름을 「결과_…」처럼 한글로 만들어 저장소가 받지 않음(경로는 영문·숫자·_-.~:@+ 만). 판 8에서 영문 머리로 바꿈.
const ST={db:null,uid:null,mode:"확인 중",rec:[],dl:null,ro:false,err:""};
const IDP={"결과":"res","주변":"nb","쿠폰":"cp"};
const okId=s=>typeof s==="string"&&/^[A-Za-z0-9_\-.~:@+]{1,200}$/.test(s)&&s!=="."&&s!=="..";
const newId=t=>(IDP[t]||"rec")+"_"+Date.now().toString(36)+Math.random().toString(36).slice(2,6);
const withTimeout=(p,ms)=>Promise.race([p,new Promise((_,rej)=>setTimeout(()=>rej({code:"timeout"}),ms))]);
function setMode(){ST.mode=ST.db?(ST.ro?"내 계정 저장소 읽기만(쓰기 권한 없음) + 새 기록은 이 브라우저에":"내 계정 저장소(나만 봄)"):"이 브라우저에만(다른 기기·창에서는 안 보임)"+(ST.err?" — "+ST.err:"")}
async function stInit(){try{if(window.claude&&claude.use){const [db,user,dl]=await Promise.all([claude.use("db"),claude.use("user"),claude.use("downloads")]);ST.dl=dl;
  if(db&&user){const id=await user.id();if(id){ST.db=db;ST.uid=id;let w=null;try{w=await user.can("data.write")}catch(e){}if(w===false)ST.ro=true}}}}catch(e){}
 setMode();await recLoad();renderStore()}
function lsGet(){try{return JSON.parse(localStorage.getItem("p7rec")||"[]")}catch(e){return []}}
function lsPut(a){try{localStorage.setItem("p7rec",JSON.stringify(a));return true}catch(e){return false}}
async function recLoad(){const loc=lsGet().map(r=>Object.assign({},r,{loc:true}));
 if(ST.db){try{const s=await withTimeout(ST.db.collection("data/users/"+ST.uid).limit(500).get(),10000);const cl=s.docs.map(d=>Object.assign({},d.data(),{id:d.id}));const ids=new Set(cl.map(r=>r.id));ST.rec=cl.concat(loc.filter(r=>!ids.has(r.id)));return}
  catch(e){ST.err="저장소를 읽지 못함("+(e&&e.code||"오류")+")";ST.db=null;setMode()}}
 ST.rec=loc}
function toLocal(r){const L=lsGet().filter(x=>x.id!==r.id);const {loc,...b}=r;L.push(b);return lsPut(L)}
const DBFAIL=["invalid_argument","not_granted","revoked","capability_disabled","capability_removed","transform_error"];
async function recPut(r,quiet){const bad=JSON.stringify(r).match(PII);if(bad){if(!quiet)alert("전화번호·주민번호·이메일처럼 보이는 내용이 있어 저장하지 않았습니다. 손님 개인정보는 적지 마세요: "+bad[0]);return false}
 if(!okId(r.id))r.id=newId(r.t);r.at=r.at||new Date().toISOString();delete r.loc;const {id,...body}=r;
 let where="db";
 if(ST.db&&!ST.ro){try{await ST.db.collection("data/users/"+ST.uid).doc(id).set(body);lsPut(lsGet().filter(x=>x.id!==id))}
  catch(e){const c=e&&e.code||"오류";if(DBFAIL.includes(c)||e instanceof TypeError){ST.ro=true;setMode();where="loc";if(!quiet)alert("계정 저장소에 쓸 수 없어("+c+") 이 브라우저에 저장합니다. 다른 기기에서는 보이지 않습니다.")}
   else{if(!quiet)alert("저장하지 못했습니다("+c+"). 잠시 뒤 다시 눌러 주세요.");return false}}}
 else where="loc";
 if(where==="loc"){if(!toLocal(r)){if(!quiet)alert("이 브라우저에도 저장할 수 없습니다(사생활 보호 창일 수 있음). 「기록 내려받기」로 따로 보관하세요.");}r.loc=true}
 const i=ST.rec.findIndex(x=>x.id===id);if(i>=0)ST.rec[i]=r;else ST.rec.push(r);renderStore();return true}
async function recDel(id){const r=ST.rec.find(x=>x.id===id);if(r&&!r.loc&&ST.db){try{await ST.db.collection("data/users/"+ST.uid).doc(id).delete()}catch(e){alert("지우지 못했습니다("+(e&&e.code||"오류")+")");return}}
 if(r&&r.loc)lsPut(lsGet().filter(x=>x.id!==id));ST.rec=ST.rec.filter(x=>x.id!==id);renderStore()}
// 이 브라우저에 남은 기록을 계정 저장소로 옮기기(판 7 때 실패해 브라우저에 남은 것 포함)
async function recMigrate(){if(!ST.db||ST.ro)return 0;let n=0;for(const r of ST.rec.filter(x=>x.loc)){const old=r.id;const c=Object.assign({},r);delete c.loc;if(!okId(c.id))c.id=newId(c.t);const {id,...b}=c;
  try{await ST.db.collection("data/users/"+ST.uid).doc(id).set(b);lsPut(lsGet().filter(x=>x.id!==old));Object.assign(r,c);delete r.loc;n++}catch(e){break}}renderStore();return n}
async function saveFile(name,text){if(ST.dl){try{await ST.dl.save({filename:name,data:text})}catch(e){if(e&&e.code==="declined")return}return}
 try{const a=document.createElement("a");a.href=URL.createObjectURL(new Blob(["﻿"+text],{type:"text/plain"}));a.download=name;document.body.appendChild(a);a.click();a.remove()}catch(e){alert("이 화면에서는 내려받기를 할 수 없습니다")}}
const csvc=v=>{v=String(v??"");if(/^[=+\-@]/.test(v))v="'"+v;return /[",\n]/.test(v)?`"${v.replace(/"/g,'""')}"`:v};
const toCSV=rows=>rows.map(r=>r.map(csvc).join(",")).join("\n");
function renderStore(){const el=$("#store-mode");if(el)el.textContent=`기록 저장: ${ST.mode} · 결과 ${ST.rec.filter(r=>r.t==="결과").length} · 주변 가게 ${ST.rec.filter(r=>r.t==="주변").length} · 쿠폰 묶음 ${ST.rec.filter(r=>r.t==="쿠폰").length}`;
 if(TOOL==="mine")openTool("mine",true);if(!$("#s2").hidden)myBox()}

// 지난 결과를 다음 기획에: 같은 사례를 해 봤으면 표시하고 순서를 조금 바꾼다
window.P7ADJ=c=>{const r=ST.rec.find(x=>x.t==="결과"&&x.ci===String(c.i));return !r?0:r.ev==="좋았음"?2:r.ev==="별로"?-3:0};
function myBadge(c){const r=ST.rec.find(x=>x.t==="결과"&&x.ci===String(c.i));return r?`<span class="badge ${r.ev==="좋았음"?"b-ok":r.ev==="별로"?"b-bad":"b-info"}">해 본 안 — ${esc(r.ev||"평가 없음")}</span>`:""}
function myBox(){const I=inp(),box=$("#mybox");if(!box)return;const res=ST.rec.filter(r=>r.t==="결과"),nb=ST.rec.filter(r=>r.t==="주변"&&(!r.ind||r.ind===I.ind));
 if(!res.length&&!nb.length){box.innerHTML=`<h3>내 기록</h3><p class="empty">아직 저장한 행사 결과·주변 가게 기록이 없습니다. 행사가 끝나면 「행사 도구 → 결과 기록·전후 비교」에 적어 두면 여기와 행사안 카드에 나옵니다.</p>`;return}
 const same=res.filter(r=>r.ind===I.ind),other=res.filter(r=>r.ind!==I.ind);
 box.innerHTML=`<h3>내 기록 <span class="small">${esc(ST.mode)}</span></h3>${(same.length?same:other).slice(-4).reverse().map(r=>`<div class="faq" style="margin-top:6px"><div class="badges"><span class="badge ${r.ev==="좋았음"?"b-ok":r.ev==="별로"?"b-bad":"b-info"}">${esc(r.ev||"평가 없음")}</span><b class="small">${esc(r.name)}</b><span class="small">${esc(r.sub||r.ind||"")} · ${esc(r.st||"")} · ${esc(r.s1||"")}~${esc(r.s2||"")}</span></div><p class="small" style="margin:4px 0 0">${esc(resSum(r))}${r.memo?" — 다음에: "+esc(r.memo):""}</p></div>`).join("")}${same.length?"":res.length?`<p class="small">같은 업종 기록이 없어 다른 업종 기록을 보여 줍니다.</p>`:""}
 ${nb.length?`<details style="margin-top:8px"><summary>주변 가게 행사 기록 ${nb.length}건</summary><div class="tw"><table><tr><th>업종·위치</th><th>행사</th><th>기간</th><th>본 곳</th></tr>${nb.slice(-8).reverse().map(r=>`<tr><td>${esc(r.ind2||"")} ${esc(r.loc||"")}</td><td>${esc(r.what)}${r.ben?" — "+esc(r.ben):""}</td><td class="small">${esc(r.s1||"")}~${esc(r.s2||"")}</td><td class="small">${esc(r.seen||"")}</td></tr>`).join("")}</table></div><p class="small">참고만 하세요. 이웃 가게와 가격·할인율을 함께 정하면 공정거래법 문제가 될 수 있습니다(행사 도구 → 주변 가게 기록).</p></details>`:""}`}
function resSum(r){const p=(a,b)=>a&&b!=null?((b-a)/a*100).toFixed(0)+"%":"계산 불가";const out=[];if(r.c0||r.c1)out.push(`손님 ${r.c0??"?"}→${r.c1??"?"}명(${p(r.c0,r.c1)})`);if(r.m0||r.m1)out.push(`매출 ${won(r.m0)}→${won(r.m1)}(${p(r.m0,r.m1)})`);if(r.rv0!=null||r.rv1!=null)out.push(`리뷰 ${r.rv0??"?"}→${r.rv1??"?"}개`);if(r.cost!=null&&r.m0!=null&&r.m1!=null)out.push(`늘어난 매출 − 쓴 돈 ${won(r.m1-r.m0-r.cost)}`);return out.join(" · ")||"숫자 없음"}

// ── 1·3. 채널별 홍보 글, 채널 추천 ──
const CH={store:"매장 안 안내문",insta:"인스타그램 글",place:"네이버 플레이스 소식",kakao:"카카오톡 채널 메시지",sms:"문자",deliv:"배달앱 가게 공지",daangn:"당근 비즈프로필 소식",banner:"현수막·입간판"};
const CHNOTE={sms:"수신 동의한 손님에게만(F015). 맨 앞에 「(광고)」·가게 이름·전화번호, 끝에 무료 수신 거부 방법(시행령 별표 6). 「(광 고)」처럼 띄우거나 기호를 넣으면 안 됨. 오후 9시~다음 날 오전 8시에는 따로 동의한 손님에게만.",kakao:"친구 추가만으로 광고 수신 동의가 된다고 보지 말고 따로 동의를 받으세요(F054). 광고 메시지는 「(광고)」 표시.",deliv:"술 할인·증정 문구 금지(F041·F075). 배달가와 매장가가 다르면 알리기(F037). 리뷰 이벤트는 별점 조건 없이, 앱 운영정책을 지켜서.",insta:"협찬·체험단 글이면 첫 부분에 대가 받은 사실 표시(F006). 해시태그는 사실인 것만.",place:"리뷰 이벤트를 걸면 별점·좋은 내용 조건 금지(F007).",daangn:"동네 사람에게 보이는 글. 최초·최저가 같은 표현 피하기(F018).",banner:"멀리서 읽히게 짧게. 할인율을 쓰면 실제로 팔던 값 기준(F017). 옥외광고물 설치는 구청에 허가·신고 대상인지 먼저 물어보세요.",store:"계산대·테이블에 붙이는 글. 조건·기간·한도를 빠짐없이."};
function recCh(I,c){const r={};const add=(k,w)=>{(r[k]=r[k]||[]).includes(w)||(r[k]=r[k]||[]).push(w)};const st=I.st,g=I.g;
 add("store","매장에 온 손님은 누구나 봄");
 if(/오픈/.test(st)||g.includes("신규손님")){add("place","처음 찾는 손님이 지도·검색에서 봄");add("insta","사진으로 처음 알림");add("daangn","가까운 동네 사람에게");add("banner","지나가는 사람에게")}
 if(g.includes("재방문")||["정착기","위기회복","N주년","상시"].includes(st)){add("sms","이미 와 본 손님(수신 동의한 분만)");add("kakao","채널 친구에게")}
 if(g.includes("비피크채우기")||g.includes("비수기채우기")){add("kakao","한가한 시간대에 바로 알림");add("sms","한가한 날 앞두고 알림(동의 손님만)")}
 if(g.includes("포장배달"))add("deliv","배달·포장 손님은 앱에서 봄");
 if(g.includes("SNS노출")||g.includes("리뷰수")){add("insta","사진·후기가 퍼지는 곳");add("place","리뷰가 쌓이는 곳")}
 if(g.includes("지역관계")){add("daangn","동네 사람에게");add("banner","골목 오가는 사람에게")}
 if(g.includes("신메뉴알리기")){add("insta","새 메뉴 사진");add("store","주문할 때 보이게")}
 if(I.who==="구직자")add("daangn","동네 구인 글(구인 공고 기준 F068)");
 if(Object.keys(r).length<4){add("insta","사진으로 알림");add("place","검색하는 손님에게")}
 return r}
function chTexts(x){const {nm,head,benefit,cond,dur,lim,sub}=x;const tag=["#"+(nm||"우리가게").replace(/\s/g,""),sub?"#"+sub.replace(/\s/g,""):"","#"+head.replace(/\s/g,"")].filter(Boolean).join(" ");
 return{store:x.store,
 insta:`${nm} ${head} 🎉\n\n${benefit?benefit+"\n":""}${cond?"조건: "+cond+"\n":""}기간: ${dur}${lim?"\n한도: "+lim:""}\n\n${tag}`,
 place:`[${head}] ${benefit||"행사 소식"}\n${cond?cond+"\n":""}기간 ${dur}${lim?" · "+lim:""}\n자세한 내용은 매장에서 안내해 드립니다.`,
 kakao:`(광고) ${nm} ☎ ○○○-○○○○-○○○○\n${head} 소식입니다.\n${benefit?"▶ "+benefit+"\n":""}${cond?"▶ "+cond+"\n":""}▶ 기간 ${dur}\n\n채널 차단으로 수신을 거부할 수 있습니다.`,
 sms:x.sms,
 deliv:`[${head}] ${benefit||"행사 안내"}${cond?"\n조건: "+cond:""}\n기간: ${dur}${lim?"\n한도: "+lim:""}`,
 daangn:`안녕하세요, 동네 ${sub||"가게"} ${nm}입니다. ${head} 소식 전해요.\n${benefit?benefit+"\n":""}${cond?"조건: "+cond+"\n":""}기간 ${dur}`,
 banner:`${nm} ${head}${benefit?" · "+benefit.split(/[,.]/)[0].slice(0,18):""}`}}
let CHSEL=null;
function chRender(x){const c=CUR,I=inp();const rec=recCh(I,c);if(!CHSEL)CHSEL=new Set(Object.keys(rec));const T=chTexts(x);
 $("#ch-pick").innerHTML=`<details open><summary>어느 채널로 알릴까 — 이 행사·손님에 맞는 채널</summary><div class="tw" style="margin-top:6px"><table><tr><th>채널</th><th>왜</th><th>주의</th></tr>${Object.keys(CH).filter(k=>rec[k]).map(k=>`<tr><td><b>${CH[k]}</b></td><td class="small">${esc(rec[k].join(", "))}</td><td class="small">${esc(CHNOTE[k])}</td></tr>`).join("")}</table></div><p class="small" style="margin:4px 0">가게 목표·단계·손님 종류로 고른 일반 안내입니다(사례 근거가 아님). ${c.lq?"<b>술 혜택은 어느 채널에도 쓰지 않습니다.</b>":""}</p></details>
 <div class="chips" style="margin-top:6px">${Object.keys(CH).map(k=>`<label class="chip"><input type="checkbox" data-ch="${k}" ${CHSEL.has(k)?"checked":""}>${CH[k]}${rec[k]?" ★":""}</label>`).join("")}</div><p class="small" style="margin:4px 0 0">★ 추천 채널. 고른 채널마다 글을 만들고, 한 곳을 고치면 「다른 채널에도 반영」으로 혜택·조건·기간을 맞출 수 있습니다.</p>`;
 $("#ch-box").innerHTML=Object.keys(CH).map(k=>`<label ${CHSEL.has(k)?"":"hidden"} data-chbox="${k}">${CH[k]}<textarea class="nt" data-l="${CH[k]}" id="nt-${k}">${esc(T[k])}</textarea><span class="small" id="cnt-${k}"></span><span class="small">${esc(CHNOTE[k])}</span><span class="row"><button type="button" class="ghost" data-copy="${k}">복사</button></span></label>`).join("")+`<div class="row" style="grid-column:1/-1"><button type="button" id="ch-sync">기간·혜택 다시 맞추기(처음 초안으로)</button><span class="small">고친 글은 지워지니 먼저 복사해 두세요.</span></div>`;
 $("#ch-pick").querySelectorAll("[data-ch]").forEach(i=>i.addEventListener("change",()=>{i.checked?CHSEL.add(i.dataset.ch):CHSEL.delete(i.dataset.ch);$(`[data-chbox="${i.dataset.ch}"]`).hidden=!i.checked;check()}));
 $("#ch-box").querySelectorAll("[data-copy]").forEach(b=>b.addEventListener("click",async()=>{const t=$("#nt-"+b.dataset.copy).value;try{await navigator.clipboard.writeText(t);b.textContent="복사됨"}catch(e){$("#nt-"+b.dataset.copy).select();b.textContent="선택됨 — 길게 눌러 복사"}setTimeout(()=>b.textContent="복사",1600)}));
 $("#ch-sync").addEventListener("click",()=>notice())}
function chCount(){Object.keys(CH).forEach(k=>{const t=$("#nt-"+k);if(!t)return;const n=[...t.value].length;$("#cnt-"+k).textContent=`${n.toLocaleString()}자`+(k==="insta"&&n>2200?" — 인스타그램 글 한도(2,200자)를 넘음":"")+(k==="banner"&&n>25?" — 현수막은 더 짧게":"")})}

// ── 4. 예고부터 마감 알림까지 ──
function schedule(){const I=inp(),c=CUR;const s=v7("#sc-s")||"",e=v7("#sc-e")||"";const has=s&&e&&e>=s;
 const d=(base,n)=>has?addD(base,n):"";const R=[
  ["예고",d(s,-7),"D-7","insta·place·store","행사 예고(혜택은 짧게, 기간 꼭)"],
  ["자세한 안내",d(s,-3),"D-3","kakao·daangn","조건·한도·기간 자세히"],
  ["하루 전 알림",d(s,-1),"D-1","sms·kakao","수신 동의 손님에게만, 오전 8시~오후 9시 사이에"],
  ["시작 알림",s,"시작일","insta·place·deliv·store","오늘 시작 — 매장 안내문 붙이기, 포스 할인 등록 확인"],
  ["마감 하루 전",d(e,-1),"끝 D-1","insta·kakao","내일 끝난다는 알림(같은 내용 반복은 1번만)"],
  ["마감",e,"끝날","store·place","오늘 마감 — 끝나면 안내물 바로 떼기"],
  ["끝난 뒤",d(e,1),"끝 D+1","insta·place·store","감사 인사, 결과 기록하기(행사 도구)"]];
 const cal=has?D.cal.filter(r=>r[0]>=addD(s,-7)&&r[0]<=addD(e,1)):[];
 $("#tab-plan").innerHTML=`<div style="display:flex;flex-direction:column;gap:12px">
 <div class="grid"><label>행사 시작일<input type="date" id="sc-s" value="${esc(s)}"></label><label>행사 끝날<input type="date" id="sc-e" value="${esc(e)}"></label></div>
 ${s&&e&&e<s?`<div class="note bad">끝날이 시작일보다 앞입니다.</div>`:""}
 <div class="tw"><table><tr><th>언제</th><th>무엇을</th><th>어디에</th><th>할 일</th><th></th></tr>${R.map(r=>`<tr><td class="num">${r[1]?esc(r[1]):esc(r[2])}</td><td><b>${r[0]}</b></td><td class="small">${r[3].split("·").map(k=>CH[k]).join(", ")}</td><td class="small">${esc(r[4])}</td><td><button type="button" class="ghost" data-goch="${r[3].split("·")[0]}">글 보기</button></td></tr>`).join("")}</table></div>
 ${has?(cal.length?`<div class="note"><b>이 기간에 걸친 날(캘린더 ${esc(D.cal[0][4])} 기준)</b><ul class="clean">${cal.map(r=>`<li>${esc(r[0])} ${esc(r[1])} (${esc(r[2])}${r[5]!=="확정"?", 예정":""})${r[2]==="공휴일"?" — 쉬는 날이면 문자·영업시간 다시 보기":""}</li>`).join("")}</ul></div>`:`<p class="small">이 기간에 캘린더 자료의 공휴일·기념일이 없습니다.</p>`):`<p class="small">날짜를 넣으면 실제 날짜와 겹치는 공휴일·기념일(캘린더 자료)을 보여 줍니다. 날짜는 캘린더 파일만 씁니다.</p>`}
 ${lawBox("문자·카톡 보낼 때",["문자_동의","문자_야간","문자_표시"])}
 <div class="row"><button type="button" id="sc-copy">순서표 복사</button>${c.lq?`<span class="small">술 혜택은 어느 알림에도 넣지 않습니다(F075).</span>`:""}</div></div>`;
 ["#sc-s","#sc-e"].forEach(q=>$(q).addEventListener("change",schedule));
 document.querySelectorAll("[data-goch]").forEach(b=>b.addEventListener("click",()=>{const k=b.dataset.goch;CHSEL.add(k);tab("notice");const i=$(`[data-ch="${k}"]`);if(i){i.checked=true;$(`[data-chbox="${k}"]`).hidden=false}$("#nt-"+k)?.focus()}));
 $("#sc-copy").addEventListener("click",async()=>{const t=R.map(r=>`${r[1]||r[2]} ${r[0]} — ${r[3].split("·").map(k=>CH[k]).join(", ")}: ${r[4]}`).join("\n");try{await navigator.clipboard.writeText(t);$("#sc-copy").textContent="복사됨"}catch(e){alert(t)}})}

// ── 행사 도구 ──
const TOOLS={coupon:"행사용 쿠폰 만들기",review:"리뷰 이벤트",infl:"체험단·인플루언서",regular:"단골 만들기",draw:"경품·추첨",deliv:"배달앱 할인 실수령",open:"개업 행사 한 묶음",result:"결과 기록·전후 비교",near:"주변 가게 행사 기록",mine:"내 기록·백업"};
const TOOLDESC={coupon:"종류·혜택·유효기간·조건·번호·사용 기록·디자인",review:"별점 조건 없이, 대가 표시까지",infl:"협찬 표시 안내문과 점검표",regular:"도장 카드·재방문 쿠폰·생일 혜택",draw:"경품 세금과 사행성 점검",deliv:"수수료·배달비 빼고 남는 돈",open:"개업일 기준 D-30 ~ D+30",result:"행사 전과 후 숫자 비교·저장",near:"이웃 가게 행사 메모",mine:"저장한 기록 보기·내려받기"};
let TOOL=null;
function toolGrid(){$("#toolgrid").innerHTML=Object.keys(TOOLS).map(k=>`<button type="button" class="toolbtn" data-tool="${k}" aria-pressed="${TOOL===k}"><b>${TOOLS[k]}</b><span class="small">${TOOLDESC[k]}</span></button>`).join("");
 document.querySelectorAll("[data-tool]").forEach(b=>b.addEventListener("click",()=>openTool(b.dataset.tool)))}
function openTool(k,quiet){TOOL=k;const p=$("#toolpanel");p.hidden=false;p.innerHTML=`<div class="row" style="justify-content:space-between"><h3>${TOOLS[k]}</h3><button type="button" class="ghost" id="tool-close">닫기</button></div><div id="tool-body" style="display:flex;flex-direction:column;gap:12px;margin-top:8px"></div>`;
 RENDER[k]();$("#tool-close").addEventListener("click",closeTool);toolGrid();if(!quiet){navPush("tool");p.scrollIntoView({behavior:matchMedia("(prefers-reduced-motion: reduce)").matches?"auto":"smooth",block:"start"})}}
function closeTool(){TOOL=null;$("#toolpanel").hidden=true;toolGrid()}
const body=h=>{$("#tool-body").innerHTML=h};
const curB=()=>CUR?stripLiq(CUR.b).t:"";
const shopNm=()=>inp().name||"○○";
const RENDER={};

// 14. 쿠폰
RENDER.coupon=(st)=>{st=st||{};const I=inp();const bt=st.ben??(curB()||"");
 body(`<p class="small" style="margin:0">${CUR?`고른 행사안 「${esc(CUR.n)}」의 혜택을 넣어 두었습니다. `:""}숫자(금액·할인율)는 사장님이 넣습니다. 손님 이름·전화번호 칸은 없습니다.</p>
 <div class="grid">
  <label>종류<select id="cp-kind">${["금액 할인","% 할인","증정","업그레이드","적립 도장","재방문"].map(x=>`<option ${st.kind===x?"selected":""}>${x}</option>`).join("")}</select></label>
  <label>혜택<input id="cp-ben" value="${esc(bt)}" placeholder="예: 사이드 1접시 증정"></label>
  <label>유효기간 시작<input type="date" id="cp-s" value="${esc(st.s||TODAY)}"></label>
  <label>유효기간 끝<input type="date" id="cp-e" value="${esc(st.e||addD(TODAY,30))}"></label>
  <label>최소 주문(원, 없으면 비움)<input id="cp-min" inputmode="numeric" value="${esc(st.min||"")}"></label>
  <label>쓸 수 있는 메뉴·요일·시간<input id="cp-when" value="${esc(st.when||"")}" placeholder="예: 평일 오후 2~5시"></label>
  <label>번호 앞글자(영문·숫자)<input id="cp-pre" value="${esc(st.pre||"CP")}" maxlength="6"></label>
  <label>발급 수(장)<input id="cp-n" inputmode="numeric" value="${esc(st.n||50)}"></label>
  <label>디자인 색<select id="cp-col">${[["남색","#24447a"],["초록","#1d6b44"],["갈색","#7a4a24"],["흑백 인쇄","#222222"]].map(([a,b])=>`<option value="${b}" ${st.col===b?"selected":""}>${a}</option>`).join("")}</select></label>
  <label>크기<select id="cp-size"><option value="card" ${st.size==="card"?"selected":""}>명함(90×50mm)</option><option value="a6" ${st.size==="a6"?"selected":""}>A6(105×148mm)</option></select></label>
 </div>
 <div class="chips">${[["one","1인·1테이블 1장"],["dup","다른 할인과 함께 못 씀"],["cash","현금으로 바꿔 주지 않음"],["liqx","술은 제외"]].map(([k,l])=>`<label class="chip"><input type="checkbox" id="cp-${k}" ${st[k]===false?"":"checked"}>${l}</label>`).join("")}</div>
 <div id="cp-warn"></div>
 <div class="cp-wrap"><div id="cp-card"></div></div>
 <div class="row"><button type="button" class="main" id="cp-save">쿠폰 묶음 저장(번호 만들기)</button><button type="button" id="cp-print">인쇄</button><button type="button" id="cp-csv1">인쇄용 CSV</button><span class="small" id="cp-msg"></span></div>
 <div id="cp-list"></div>
 ${faqBox(["F027","F039","F041","F014"])}`);
 const upd=()=>{const g=cpGet();const W=[];
  if(hasLiq(g.ben))W.push(lawLi("술광고")+`<li>⚠ 술을 공짜·쿠폰으로 주는 것 자체가 주류 경품 제공 금지(국세청 고시 — 사례 DB F004·F051)에 걸릴 수 있습니다. 술은 쿠폰 혜택에서 빼세요.</li>`);
  if(!g.e)W.push(`<li>유효기간 끝날이 비었습니다. 쿠폰 앞면에 날짜로 적으세요(F027).</li>`);else if(g.e<g.s)W.push(`<li>끝날이 시작일보다 앞입니다.</li>`);
  if(/\d\s?%/.test(g.ben)||g.kind==="% 할인")W.push(`<li>할인율을 쓰면 최근 실제로 팔던 값 기준이어야 합니다(F017).</li>`);
  if(/무제한|최저가|최초/.test(g.ben))W.push(`<li>무제한·최저가·최초 같은 표현은 피하세요(F018).</li>`);
  $("#cp-warn").innerHTML=(W.length?`<div class="note bad"><b>⚠ 쿠폰 점검 ${W.length}건</b><ul class="clean">${W.join("")}</ul></div>`:`<div class="note ok">술 혜택·유효기간·할인율 표시·최상급 표현 점검을 통과했습니다.</div>`)+lawBox("쿠폰 유효기간·사용 조건 표시",["쿠폰_분쟁기준","상품권약관","쿠폰_표시"]);
  const conds=[g.min?`${won(g.min)} 이상 주문 시`:"",g.when,g.one?"1인·1테이블 1장":"",g.dup?"다른 할인과 중복 불가":"",g.cash?"현금 교환 불가":"",g.liqx?"주류 제외":""].filter(Boolean);
  $("#cp-card").className="cp "+(g.size==="a6"?"a6":"card");$("#cp-card").style.setProperty("--cpc",g.col);
  $("#cp-card").innerHTML=`<div class="cp-top">${esc(shopNm())} · ${esc(g.kind)}</div><div class="cp-ben">${esc(g.ben||"혜택을 넣으세요")}</div><div class="cp-cond">${esc(conds.join(" · "))}</div><div class="cp-foot"><span>유효기간 ${esc(g.s)} ~ ${esc(g.e||"○")}</span><span>No. ${esc(g.pre)}-${esc((g.s||TODAY).replace(/-/g,""))}-0001</span></div>`};
 $("#tool-body").addEventListener("input",upd);$("#tool-body").addEventListener("change",upd);upd();
 $("#cp-print").addEventListener("click",()=>{document.body.classList.add("print-cp");try{print()}catch(e){alert("이 화면에서는 인쇄를 열 수 없습니다. 인쇄용 CSV를 디자인 도구로 보내세요.")}setTimeout(()=>document.body.classList.remove("print-cp"),500)});
 $("#cp-csv1").addEventListener("click",()=>{const g=cpGet();saveFile("쿠폰_인쇄.csv",toCSV([["쿠폰 종류","앞면 문구","뒷면 주의 문구","유효기간 시작","유효기간 끝","크기","일련번호 시작","일련번호 끝"],[g.kind,`${shopNm()} ${g.ben}`,$("#cp-card .cp-cond").textContent,g.s,g.e,g.size==="a6"?"A6":"명함",serial(g,1),serial(g,g.n)]]))});
 $("#cp-save").addEventListener("click",async()=>{const g=cpGet();if(!g.ben||!g.e||g.e<g.s||!g.n||g.n>2000){$("#cp-msg").textContent="혜택·유효기간·발급 수(2,000장 이하)를 확인하세요";return}if(hasLiq(g.ben)&&!confirm("술이 들어간 혜택입니다. 그래도 저장할까요?"))return;
  if(await recPut(Object.assign({t:"쿠폰",name:`${g.kind} ${g.ben}`.slice(0,40),used:{}},g))){$("#cp-msg").textContent="저장했습니다. 아래 목록에서 사용 처리합니다.";cpList()}});
 cpList()};
function cpGet(){return{kind:v7("#cp-kind"),ben:v7("#cp-ben"),s:v7("#cp-s"),e:v7("#cp-e"),min:n7("#cp-min"),when:v7("#cp-when"),pre:(v7("#cp-pre")||"CP").replace(/[^A-Za-z0-9]/g,"").toUpperCase()||"CP",n:Math.floor(n7("#cp-n")||0),col:v7("#cp-col"),size:v7("#cp-size"),one:$("#cp-one").checked,dup:$("#cp-dup").checked,cash:$("#cp-cash").checked,liqx:$("#cp-liqx").checked}}
const serial=(g,i)=>`${g.pre}-${(g.s||"").replace(/-/g,"")}-${String(i).padStart(4,"0")}`;
function cpState(g,sn){return g.used&&g.used[sn]?"사용":(g.e<TODAY?"만료":"발급")}
function cpList(){const L=ST.rec.filter(r=>r.t==="쿠폰");const el=$("#cp-list");if(!el)return;if(!L.length){el.innerHTML=`<p class="empty">저장한 쿠폰 묶음이 없습니다.</p>`;return}
 el.innerHTML=`<h3>사용 기록</h3>`+L.map(g=>{const u=Object.keys(g.used||{}).length;return `<div class="faq" style="margin-top:6px"><div class="badges"><b class="small">${esc(g.name)}</b><span class="badge b-info">${esc(g.s)}~${esc(g.e)}</span><span class="badge ${g.e<TODAY?"b-bad":"b-ok"}">${g.e<TODAY?"기간 끝":"쓰는 중"}</span><span class="small">발급 ${g.n}장 · 사용 ${u}장${g.n?` (${(u/g.n*100).toFixed(0)}%)`:""}</span></div>
 <div class="row" style="margin-top:6px"><input placeholder="${esc(serial(g,1))}" data-sn="${g.id}" style="max-width:220px"><button type="button" data-use="${g.id}">사용 처리</button><button type="button" class="ghost" data-csv="${g.id}">발급 목록 CSV</button><button type="button" class="ghost" data-del="${g.id}">묶음 지우기</button><span class="small" data-um="${g.id}"></span></div>
 ${u?`<details><summary>사용한 번호 ${u}개</summary><p class="small">${Object.entries(g.used).slice(-30).map(([k,t])=>esc(k)+" ("+esc(t.slice(0,16).replace("T"," "))+")").join(", ")}</p></details>`:""}</div>`}).join("");
 el.querySelectorAll("[data-use]").forEach(b=>b.addEventListener("click",async()=>{const g=ST.rec.find(r=>r.id===b.dataset.use);const sn=el.querySelector(`[data-sn="${g.id}"]`).value.trim().toUpperCase();const m=el.querySelector(`[data-um="${g.id}"]`);
  const ok=new RegExp(`^${g.pre}-${g.s.replace(/-/g,"")}-(\\d{4})$`).exec(sn);if(!ok||+ok[1]<1||+ok[1]>g.n){m.textContent="이 묶음의 번호가 아닙니다";return}
  if(g.used[sn]){m.textContent="이미 쓴 번호입니다("+g.used[sn].slice(0,10)+")";return}if(g.e<TODAY){m.textContent="유효기간이 지났습니다";return}if(g.s>TODAY){m.textContent="아직 시작 전입니다";return}
  g.used[sn]=new Date().toISOString();if(await recPut(g)){cpList();}}));
 el.querySelectorAll("[data-csv]").forEach(b=>b.addEventListener("click",()=>{const g=ST.rec.find(r=>r.id===b.dataset.csv);const rows=[["일련번호","쿠폰 종류","혜택","조건","유효기간 시작","유효기간 끝","상태","사용 일시"]];for(let i=1;i<=g.n;i++){const sn=serial(g,i);rows.push([sn,g.kind,g.ben,[g.min?won(g.min)+" 이상":"",g.when].filter(Boolean).join(" "),g.s,g.e,cpState(g,sn),(g.used[sn]||"").replace("T"," ").slice(0,16)])}saveFile("쿠폰_발급목록.csv",toCSV(rows))}));
 el.querySelectorAll("[data-del]").forEach(b=>b.addEventListener("click",async()=>{if(confirm("이 쿠폰 묶음과 사용 기록을 지울까요?")){await recDel(b.dataset.del);cpList()}}))}

// 7. 리뷰 이벤트
RENDER.review=()=>{body(`<div class="grid"><label>혜택<input id="rv-ben" value="${esc(curB()||"")}" placeholder="예: 음료 1잔"></label><label>어디 리뷰<select id="rv-ch"><option>네이버 플레이스</option><option>배달앱</option><option>지도앱·기타</option></select></label><label>혜택 주는 때<select id="rv-when"><option>리뷰를 쓴 손님에게(쓴 화면 확인)</option><option>리뷰와 관계없이 오늘 온 손님 모두</option></select></label></div>
 <label>안내 문구(고칠 수 있음)<textarea id="rv-txt" class="nt2"></textarea></label><div id="rv-chk"></div>
 <div class="note"><b>지킬 것</b><ul class="clean"><li>별점·좋은 내용을 조건으로 걸지 않기(「5점 주면」「좋은 리뷰」 금지).</li><li>리뷰를 쓴 손님이 「혜택을 받고 썼다」는 사실을 리뷰에 적도록 안내하기.</li><li>나쁜 리뷰를 지우는 조건으로 혜택 주지 않기(F048).</li><li>사진 리뷰를 요구하면 손님 얼굴·다른 손님이 찍히지 않게 안내.</li></ul></div>
 ${lawBox("리뷰 대가",["후기_표시법","후기_공개","고객유인","리뷰_배달앱정책","리뷰_네이버정책","리뷰_배달앱정책_쿠팡이츠요기요"],CONFIRM("배민 「리뷰관리정책」 세부 기준(사장님광장 막힘)·쿠팡이츠·요기요 리뷰 정책(원문 접속 거부) — 배민·네이버 운영정책 원문에는 리뷰 이벤트·별점 조건을 직접 정한 문구가 없음"))}
 ${faqBox(["F007","F048","F006"])}`);
 const mk=()=>{const b=v7("#rv-ben")||"○○",all=v7("#rv-when").startsWith("리뷰와");$("#rv-txt").value=all?`오늘 오신 모든 분께 ${b}을(를) 드립니다.\n리뷰는 자유롭게 남겨 주세요. 혜택과 상관없습니다.`:`${v7("#rv-ch")}에 리뷰를 남겨 주시면 ${b}을(를) 드립니다.\n별점과 내용은 솔직하게 자유롭게 써 주세요(좋은 리뷰만 받지 않습니다).\n리뷰에 「${b}을(를) 받고 작성」이라고 적어 주세요.`;chk()};
 const chk=()=>{const t=$("#rv-txt").value;const W=[];if(/5\s?점|만점|별\s?다섯|좋은 ?리뷰(?!만 받지)|칭찬|긍정/.test(t))W.push("별점·좋은 내용 조건으로 읽힐 수 있음");if(/삭제|지워/.test(t))W.push("리뷰 삭제 조건(F048)");if(!/받고|혜택과 상관없/.test(t))W.push("혜택 받은 사실 표시 안내가 없음");if(hasLiq(t))W.push("술 혜택(F075)");
  $("#rv-chk").innerHTML=W.length?`<div class="note bad">⚠ ${W.map(esc).join(" / ")}</div>`:`<div class="note ok">별점 조건·삭제 조건·표시 안내·술 점검 통과</div>`};
 ["#rv-ben","#rv-ch","#rv-when"].forEach(q=>$(q).addEventListener("change",mk));$("#rv-ben").addEventListener("input",mk);$("#rv-txt").addEventListener("input",chk);mk()};

// 8. 체험단·인플루언서
RENDER.infl=()=>{body(`<div class="grid"><label>주는 것<select id="if-give"><option>무료 식사·이용</option><option>원고료(돈)</option><option>할인</option><option>제품 선물</option></select></label><label>어디에 올림<select id="if-ch"><option>블로그</option><option>인스타그램</option><option>유튜브·짧은 영상</option></select></label><label>모으는 방법<select id="if-how"><option>직접 모집</option><option>체험단 업체를 통해</option></select></label></div>
 <label>체험단에게 보낼 안내(고칠 수 있음)<textarea id="if-txt"></textarea></label>
 <div class="note"><b>계약·안내 점검표</b><ul class="clean"><li>☐ 대가(무엇을 받았는지)를 글의 제목이나 첫 부분에 쉽게 보이게 적기로 했나</li><li>☐ 좋은 내용만 쓰라거나 나쁜 점을 빼라고 요구하지 않았나</li><li>☐ 원고를 미리 고쳐 달라고 할 때 사실과 다른 내용을 넣지 않았나</li><li>☐ 「직접 사서 먹은 것처럼」 쓰게 하지 않았나</li><li>☐ 체험단 연락처는 연락 목적에만 쓰고 행사 뒤 지우기(이 화면에는 적지 않음)</li>${$("#if-how")?"":""}<li>☐ 체험단 업체를 통하면 표시 의무를 계약서에 넣었나(업체가 했더라도 가게 광고이므로 가게도 책임질 수 있다고 보고 챙기세요)</li></ul></div>
 ${lawBox("체험단·협찬 표시",["후기_공개","후기_위치","후기_문구","후기_기만"])}
 ${faqBox(["F006"])}`);
 const mk=()=>{const g=v7("#if-give"),ch=v7("#if-ch");$("#if-txt").value=`${shopNm()} 체험단 안내\n\n제공: ${g}\n올릴 곳: ${ch}\n\n꼭 지켜 주세요\n· 「체험단」이라고만 쓰면 표시로 보지 않습니다. 글의 제목이나 첫 부분(사진 글은 첫 해시태그 #협찬 도 됨)에 「${shopNm()}로부터 ${g}을(를) 받고 쓴 글입니다」처럼 대가를 받은 사실을 적어 주세요.${ch!=="블로그"?"\n· 영상·사진 글은 첫 화면이나 글 첫 줄에 표시해 주세요.":""}\n· 맛·서비스는 느낀 대로 솔직하게 써 주세요. 좋은 내용만 써 달라고 요청하지 않습니다.\n· 다른 손님 얼굴이 나오지 않게 찍어 주세요.`};
 ["#if-give","#if-ch","#if-how"].forEach(q=>$(q).addEventListener("change",mk));mk()};

// 9. 단골 만들기
RENDER.regular=()=>{body(`<p class="small" style="margin:0">손님 정보를 받지 않는 장치부터 보여 줍니다. 이 화면은 손님 이름·전화번호·생일을 받지도 저장하지도 않습니다.</p>
 <div class="cols">
 <div class="faq"><h3>① 도장 카드 <span class="badge b-ok">개인정보 없음</span></h3><div class="grid" style="margin-top:6px"><label>도장 수<input id="rg-n" inputmode="numeric" value="10"></label><label>다 모으면<input id="rg-b" value="${esc(curB()||"")}" placeholder="예: 음료 1잔"></label><label>유효기간 끝<input type="date" id="rg-e" value="${addD(TODAY,180)}"></label></div><p id="rg-card" style="margin:6px 0 0"></p><button type="button" data-tool2="coupon">도장 카드 쿠폰으로 만들기</button></div>
 <div class="faq"><h3>② 다음 방문 쿠폰 <span class="badge b-ok">개인정보 없음</span></h3><p class="small">영수증·포장 봉투에 다음 방문 때 쓰는 쿠폰을 넣습니다. 번호·사용 기록은 쿠폰 도구에서 관리합니다.</p><button type="button" data-tool2="coupon">재방문 쿠폰 만들기</button></div>
 <div class="faq"><h3>③ 생일 혜택 <span class="badge b-warn">개인정보 주의</span></h3><p class="small"><b>권장:</b> 생일을 받아 두지 말고 「생일이 있는 달에 오시면 말씀해 주세요(날짜가 보이는 것을 보여 주시면 됩니다)」로 그때 확인. <b>받아 둔다면</b> 아래 동의서를 쓰고, 장부는 가게가 따로 잠가 관리합니다(이 화면·백업에는 넣지 않음).</p><details><summary>생일 혜택 동의서 문안</summary><textarea id="rg-agree" style="min-height:220px"></textarea></details></div>
 <div class="faq"><h3>④ 문자·카톡 소식 <span class="badge b-warn">수신 동의</span></h3><p class="small">광고 문자를 받겠다는 동의를 따로 받고, 2년마다 동의를 다시 확인합니다. 오후 9시~오전 8시에 보내려면 그 동의를 또 따로 받습니다.</p></div>
 </div>
 ${lawBox("생일·연락처를 받을 때",["개인정보_수집","개인정보_최소","개인정보_구분동의","개인정보_파기","개인정보_아동"])}
 ${lawBox("광고 문자·카톡",["문자_동의","문자_재동의","문자_야간","문자_표시"])}
 ${faqBox(["F015","F014","F054","F065"])}`);
 const mk=()=>{$("#rg-card").innerHTML=`<b>도장 카드 앞면:</b> ${esc(shopNm())} 도장 ${esc(v7("#rg-n")||"○")}개 모으면 ${esc(v7("#rg-b")||"○○")} · ${esc(v7("#rg-e"))}까지 · 현금 교환 불가${hasLiq(v7("#rg-b"))?` <span class="badge b-bad">술 혜택 — 빼세요(F004·F075)</span>`:""}`};
 $("#tool-body").addEventListener("input",mk);mk();
 $("#rg-agree").value=`[${shopNm()}] 생일 혜택 안내를 위한 개인정보 수집·이용 동의\n\n1. 받는 항목: 휴대전화번호, 생일(월·일) — 이름·나이는 받지 않습니다\n2. 쓰는 목적: 생일이 있는 달에 생일 혜택 문자 보내기\n3. 보관 기간: 동의를 거두실 때까지, 늦어도 마지막 방문 뒤 1년 안에 지웁니다\n4. 동의하지 않으셔도 가게 이용과 다른 혜택에는 아무 불이익이 없습니다\n\n□ 위 내용에 동의합니다\n\n[따로] 광고성 정보(행사·할인 소식) 문자 수신 동의\n□ 동의합니다  □ 동의하지 않습니다\n□ 오후 9시~오전 8시 사이에도 받겠습니다\n\n만 14세 미만은 보호자 동의가 필요하므로 받지 않습니다.\n작성일: ____년 __월 __일`;
 document.querySelectorAll("[data-tool2]").forEach(b=>b.addEventListener("click",()=>openTool(b.dataset.tool2)))};

// 10. 경품·추첨
RENDER.draw=()=>{body(`<div class="grid"><label>경품 이름<input id="dr-nm" placeholder="예: 식사권"></label><label>경품 1개 값(원)<input id="dr-v" inputmode="numeric" placeholder="예: 50000"></label><label>개수<input id="dr-n" inputmode="numeric" value="1"></label><label>참가 조건<select id="dr-how"><option>구매와 관계없이 누구나</option><option>구매한 손님만</option><option>참가비를 받음</option></select></label><label>세금은 누가<select id="dr-tax"><option>가게가 대신 냄(경품값에 더함)</option><option>당첨자가 냄</option></select></label><label>발표일<input type="date" id="dr-d"></label></div>
 <div class="out" id="dr-out"></div><div id="dr-warn"></div>
 <label>응모 안내 문구<textarea id="dr-txt"></textarea></label>
 ${lawBox("경품 세금",["경품_소득","경품_최저한","경품_세율","경품_원천"],CONFIRM("경품을 시가로 얼마로 볼지, 지급명세서 제출 기한은 세무사에게 확인"))}
 ${lawBox("경품 크기·사행성",["경품고시폐지","고객유인","사행","사행_허가"])}
 ${faqBox(["F012","F013","F062","F001","F046","F014"])}`);
 const up=()=>{const v=n7("#dr-v"),n=n7("#dr-n")||1,how=v7("#dr-how"),shop=v7("#dr-tax").startsWith("가게");const L=LAWS;const lim=+(L.경품_최저한?.num||50000),rate=+(L.경품_세율?.num||0.22);
  const tax=v!=null&&v>lim?Math.floor(v*rate/10)*10:0;
  $("#dr-out").innerHTML=[["경품 총값",v!=null?won(v*n):"계산 불가"],["1개당 원천징수(지방소득세 포함)",v==null?"계산 불가":v>lim?won(tax):`없음(${won(lim)} 이하)`],["가게가 쓰는 돈",v==null?"계산 불가":won((v+(shop?tax:0))*n)]].map(([a,b])=>`<div><span>${a}</span><b>${b}</b></div>`).join("");
  const W=[];if(how==="참가비를 받음")W.push("참가비를 받고 추첨하면 사행행위(복권 비슷한 것)로 볼 수 있어 하지 마세요");if(v!=null&&v>lim)W.push(`1개 값이 ${won(lim)}를 넘어 가게가 세금을 떼어(원천징수) 신고해야 할 수 있습니다. 당첨자 신원 확인이 필요해져 개인정보를 다루게 됩니다(F013·F014)`);if(hasLiq(v7("#dr-nm")))W.push("술 경품은 주류 경품 제공 금지(F004·F022)");if(v!=null&&v>=1000000)W.push("비싼 경품은 부당한 고객 유인으로 볼 수 있어 줄이는 것이 안전합니다(F062)");
  $("#dr-warn").innerHTML=W.length?`<div class="note bad"><b>⚠ 경품 점검</b><ul class="clean">${W.map(w=>`<li>${esc(w)}</li>`).join("")}</ul></div>`:`<div class="note ok">참가비·세금 기준·술·고가 경품 점검 통과</div>`;
  $("#dr-txt").value=`${shopNm()} 경품 추첨 안내\n경품: ${v7("#dr-nm")||"○○"} ${n}개\n응모: ${how==="구매한 손님만"?"구매 영수증으로 응모":"매장 방문 손님 누구나(구매와 관계없음)"}\n발표: ${v7("#dr-d")||"○월 ○일"} 매장 안내판(당첨자 이름·연락처는 공개하지 않고 응모권 번호로 발표)\n${v!=null&&v>lim?(shop?"제세공과금은 가게가 부담합니다.\n":"제세공과금(경품값의 22%)은 당첨자 부담입니다.\n"):""}응모권에 적은 연락처는 당첨 안내에만 쓰고 발표 뒤 바로 지웁니다.`};
 $("#tool-body").addEventListener("input",e=>{if(e.target.id!=="dr-txt")up()});$("#tool-body").addEventListener("change",e=>{if(e.target.id!=="dr-txt")up()});up()};

// 11. 배달앱 실수령
RENDER.deliv=()=>{body(`<p class="small" style="margin:0">요율은 앱·요금제·매출 구간마다 다르고 자주 바뀝니다. 사장님 앱의 정산 내역이나 계약서에 있는 값을 넣으세요(이 화면은 요율을 미리 넣지 않습니다).</p>
 <div class="grid"><label>주문 금액(할인 전, 원)<input id="dv-p" inputmode="numeric"></label><label>사장님이 내는 할인(원)<input id="dv-d" inputmode="numeric" value="0"></label><label>앱이 내 주는 할인(원)<input id="dv-a" inputmode="numeric" value="0"></label><label>중개 수수료율(%)<input id="dv-r" inputmode="decimal"></label><label>결제 수수료율(%)<input id="dv-q" inputmode="decimal"></label><label>사장님이 내는 배달비(원)<input id="dv-f" inputmode="numeric" value="0"></label><label>수수료 매기는 기준<select id="dv-base"><option>할인 뒤 금액</option><option>할인 전 금액</option></select></label><label>수수료·배달비 부가세 10%<select id="dv-vat"><option>더함</option><option>안 더함(이미 포함)</option></select></label><label>음식 원가+포장비(원)<input id="dv-c" inputmode="numeric"></label></div>
 <div class="out" id="dv-out"></div>
 <p class="small" style="margin:0">계산식: 손님 결제액 = 주문 금액 − 사장님 할인 − 앱 할인. 수수료 = 기준 금액 × (중개+결제 수수료율). 실수령 = 주문 금액 − 사장님 할인 − 수수료 − 배달비(− 부가세). 할인으로 떠안는 돈 = 할인 없을 때 실수령 − 할인 있을 때 실수령. 앱이 낸 할인은 정산 때 가게에 돌아온다고 보고 계산합니다(앱마다 다르니 정산 내역으로 맞춰 보세요).</p>
 ${lawBox("배달앱 행사",["술광고","술광고_주체","리뷰_배달앱정책","리뷰_배달앱정책_쿠팡이츠요기요"],CONFIRM("앱별 할인 부담·정산 방식(앱 계약서·정산 내역으로 확인)")+`<li>배달가와 매장가가 다르면 알리기 — F037</li>`)}
 ${faqBox(["F037","F041","F075"])}`);
 const up=()=>{const p=n7("#dv-p"),d=n7("#dv-d")||0,a=n7("#dv-a")||0,r=n7("#dv-r"),q=n7("#dv-q"),f=n7("#dv-f")||0,c=n7("#dv-c"),vat=v7("#dv-vat")==="더함"?1.1:1,pre=v7("#dv-base")==="할인 전 금액";
  const NA="계산 불가";if(p==null||r==null||q==null){$("#dv-out").innerHTML=`<div style="grid-column:1/-1"><span>계산 불가(입력 없음)</span><b style="font-size:.9rem;font-weight:500">${[p==null?"주문 금액":"",r==null?"중개 수수료율":"",q==null?"결제 수수료율":""].filter(Boolean).join(", ")}</b></div>`;return}
  const net=(dd,aa)=>{const base=pre?p:p-dd-aa;const fee=base*(r+q)/100;return{fee,got:p-dd-(fee+f)*vat-(vat>1?0:0),pay:p-dd-aa}};
  const w=net(d,a),o=net(0,0);const loss=o.got-w.got;
  $("#dv-out").innerHTML=[["손님 결제액",won(w.pay)],["수수료(부가세 반영)",won(w.fee*vat)],["배달비(부가세 반영)",won(f*vat)],["실수령",won(w.got)],["실수령률(주문 금액 대비)",(w.got/p*100).toFixed(1)+"%"],["할인 없을 때 실수령",won(o.got)],["할인으로 떠안는 돈",won(loss)],["원가 빼고 남는 돈",c==null?NA:won(w.got-c)]].map(([x,y])=>`<div><span>${x}</span><b>${y}</b></div>`).join("")+(c!=null&&w.got-c<0?`<div style="grid-column:1/-1" class="note bad">이 할인으로 주문 1건마다 ${won(c-w.got)} 손해입니다.</div>`:"")};
 $("#tool-body").addEventListener("input",up);$("#tool-body").addEventListener("change",up);up()};

// 12. 개업 한 묶음
RENDER.open=()=>{const I=inp();const sub=SUBMAP(I.sub||"");const ex=st=>D.ex.filter(e=>e.sub===(sub||(I.ind==="요식업"?"고깃집":"__없음"))&&e.stg===st).slice(0,2);
 const prepC=D.cases.filter(c=>c.kd==="준비·절차"&&(c.ind.split("|").includes(I.ind||"요식업"))).slice(0,4);
 body(`<div class="grid"><label>개업일(그랜드오픈)<input type="date" id="op-d"></label></div><p class="small" style="margin:0">${sub?"":I.ind==="요식업"?"세부 업종을 고르지 않아 고깃집 예시로 보여 줍니다. ":"이 업종의 응용 예시는 아직 없어(2차 범위 결정 대기) 예시 칸은 비어 있습니다. "}날짜를 넣으면 실제 날짜와 캘린더의 공휴일·기념일을 함께 보여 줍니다.</p><div id="op-t"></div>
 ${lawBox("개업 행사에서 자주 걸리는 것",["문자_동의","후기_공개","술광고","경품고시폐지"])}`);
 const up=()=>{const d0=v7("#op-d");const dt=n=>d0?addD(d0,n):(n<0?"D"+n:"D+"+n);const exl=(st)=>ex(st).map(e=>`「${esc(e.n)}」`).join(", ")||"예시 없음";
  const R=[[-30,"인허가·영업 신고 확인, 준비·절차 사례 읽기",prepC.map(c=>`#${c.i} ${esc(c.n)}`).join(" / ")||"",""],[-21,"네이버 플레이스·지도 등록, 사진 찍기","",""],[-21,"체험단 모으기(대가 표시 안내)","","infl"],[-14,"쿠폰·도장 카드 인쇄, 수신 동의 받을 종이 준비","","coupon"],[-10,"가오픈 준비 — 응용 예시: "+exl("오픈전"),"",""],[-7,"예고 글(채널별)","","sched"],[-3,"가오픈(지인·이웃) — 의견 받기","",""],[0,"그랜드오픈 — 응용 예시: "+exl("그랜드오픈"),"",""],[1,"리뷰 이벤트 시작(별점 조건 없이)","","review"],[7,"첫 주 숫자 적기(손님·매출)","","result"],[14,"재방문 쿠폰·도장 카드 돌리기","","regular"],[30,"정착기 행사 고르기 — 응용 예시: "+exl("정착기"),"",""]];
  if(window.linkOpenRows)linkOpenRows(R);
  const cal=d0?D.cal.filter(r=>r[0]>=addD(d0,-30)&&r[0]<=addD(d0,30)&&(r[2]==="공휴일"||r[2]==="명절·세시")):[];
  $("#op-t").innerHTML=`<div class="tw"><table><tr><th>언제</th><th>할 일</th><th></th></tr>${R.map(r=>`<tr><td class="num">${esc(dt(r[0]))}${d0?`<br><span class="small">${r[0]<0?"D"+r[0]:r[0]?"D+"+r[0]:"D-day"}</span>`:""}</td><td>${r[1]}${r[2]?`<br><span class="small">${r[2]}</span>`:""}</td><td>${r[3]?`<button type="button" class="ghost" data-op="${r[3]}">열기</button>`:""}</td></tr>`).join("")}</table></div>${cal.length?`<div class="note"><b>개업 앞뒤 30일의 공휴일·명절(캘린더 자료)</b><ul class="clean">${cal.map(r=>`<li>${esc(r[0])} ${esc(r[1])}</li>`).join("")}</ul></div>`:""}`;
  document.querySelectorAll("[data-op]").forEach(b=>b.addEventListener("click",()=>{const k=b.dataset.op;if(k==="sched"){if(CUR){tab("plan");$("#s3").scrollIntoView()}else alert("먼저 2단계에서 행사안을 고르면 알림 순서표가 나옵니다.")}else openTool(k)}))};
 $("#op-d").addEventListener("change",up);up()};

// 5·6. 결과 기록·전후 비교
RENDER.result=()=>{const I=inp();body(`<p class="small" style="margin:0">행사 기간과 <b>같은 길이·같은 요일 수</b>의 바로 전 기간을 비교하세요. 날씨·공휴일·근처 공사 같은 다른 이유도 메모에 적습니다. 손님 이름·연락처는 적지 않습니다.</p>
 <div class="grid"><label>행사 이름<input id="rs-name" value="${esc(CUR?CUR.n:"")}"></label><label>시작일<input type="date" id="rs-s1"></label><label>끝날<input type="date" id="rs-s2"></label><label>평가<select id="rs-ev"><option>좋았음</option><option>보통</option><option>별로</option></select></label></div>
 <div class="tw"><table><tr><th></th><th class="num">행사 전(같은 길이)</th><th class="num">행사 중</th></tr>${[["손님 수(명)","c"],["매출(원)","m"],["리뷰 수(개)","rv"]].map(([l,k])=>`<tr><td>${l}</td><td><input id="rs-${k}0" inputmode="numeric"></td><td><input id="rs-${k}1" inputmode="numeric"></td></tr>`).join("")}<tr><td>쿠폰 회수(장)</td><td></td><td><input id="rs-cp" inputmode="numeric"></td></tr><tr><td>행사에 쓴 돈(원)</td><td></td><td><input id="rs-cost" inputmode="numeric"></td></tr></table></div>
 <div class="out" id="rs-out"></div>
 <label>다음에 바꿀 점·다른 이유 메모<textarea id="rs-memo" style="min-height:80px"></textarea></label>
 <div class="row"><button type="button" class="main" id="rs-save">결과 저장</button><span class="small" id="rs-msg"></span></div>
 <p class="small" style="margin:0">저장하면 다음에 행사안을 볼 때 「내 기록」과 같은 안의 카드에 「해 본 안」으로 나오고, 좋았던 안은 조금 앞으로, 별로였던 안은 뒤로 갑니다. ${CUR?`(사례 ${CUR.k==="응용예시"?CUR.i:"#"+CUR.i}와 연결)`:"(행사안을 고르고 기록하면 그 안과 연결됩니다)"}</p>`);
 const g=()=>({t:"결과",name:v7("#rs-name"),s1:v7("#rs-s1"),s2:v7("#rs-s2"),ev:v7("#rs-ev"),c0:n7("#rs-c0"),c1:n7("#rs-c1"),m0:n7("#rs-m0"),m1:n7("#rs-m1"),rv0:n7("#rs-rv0"),rv1:n7("#rs-rv1"),cp:n7("#rs-cp"),cost:n7("#rs-cost"),memo:v7("#rs-memo"),ci:CUR?String(CUR.i):"",ind:I.ind,sub:I.sub,st:I.st});
 const up=()=>{const r=g();const pc=(a,b)=>a&&b!=null?((b-a)/a*100).toFixed(1)+"%":"계산 불가";const ag=(m,c)=>m!=null&&c?won(m/c):"계산 불가";
  $("#rs-out").innerHTML=[["손님 변화",pc(r.c0,r.c1)],["매출 변화",pc(r.m0,r.m1)],["객단가 전→중",ag(r.m0,r.c0)+" → "+ag(r.m1,r.c1)],["리뷰 늘어난 수",r.rv0!=null&&r.rv1!=null?(r.rv1-r.rv0)+"개":"계산 불가"],["늘어난 매출 − 쓴 돈",r.m0!=null&&r.m1!=null&&r.cost!=null?won(r.m1-r.m0-r.cost):"계산 불가"],["쿠폰 1장당 쓴 돈",r.cost!=null&&r.cp?won(r.cost/r.cp):"계산 불가"]].map(([a,b])=>`<div><span>${a}</span><b>${b}</b></div>`).join("")+`<div style="grid-column:1/-1"><span>읽는 법</span><b style="font-size:.85rem;font-weight:500">「늘어난 매출 − 쓴 돈」은 매출 기준이라 원가를 빼지 않았습니다. 남는 돈은 원가 확인 탭의 「손님 1명당 이익」으로 다시 보세요.</b></div>`};
 $("#tool-body").addEventListener("input",up);up();
 $("#rs-save").addEventListener("click",async()=>{const r=g();if(!r.name){$("#rs-msg").textContent="행사 이름을 넣으세요";return}if(await recPut(r)){$("#rs-msg").textContent="저장했습니다";myBox()}})};

// 13. 주변 가게
RENDER.near=()=>{body(`<p class="small" style="margin:0">근처 가게가 하는 행사를 메모합니다. 가게 주인·손님 이름, 전화번호, 사진은 넣지 않습니다.</p>
 <div class="grid"><label>업종<select id="nb-ind">${IND.map(x=>`<option ${x===inp().ind?"selected":""}>${x}</option>`).join("")}</select></label><label>어떤 가게(세부)<input id="nb-ind2" placeholder="예: 길 건너 카페"></label><label>위치(대략)<input id="nb-loc" placeholder="예: 같은 골목"></label><label>행사<input id="nb-what" placeholder="예: 평일 오후 할인"></label><label>혜택<input id="nb-ben"></label><label>시작<input type="date" id="nb-s1"></label><label>끝<input type="date" id="nb-s2"></label><label>본 곳<select id="nb-seen"><option>현수막·매장 앞</option><option>SNS</option><option>배달앱</option><option>당근</option><option>전단</option></select></label></div>
 <label>메모<input id="nb-memo"></label><div class="row"><button type="button" class="main" id="nb-save">기록 저장</button><span class="small" id="nb-msg"></span></div>
 ${lawBox("이웃 가게와 함께 할 때",["공동행위","사업자단체"],`<li>같이 하는 골목 행사라도 가격·할인율·영업시간은 가게마다 따로 정하세요. 「다 같이 ○% 할인」「가격을 맞추자」 같은 합의 문구는 쓰지 않습니다.</li>`)}
 ${faqBox(["F073","F039"])}<div id="nb-list"></div>`);
 const list=()=>{const L=ST.rec.filter(r=>r.t==="주변");$("#nb-list").innerHTML=L.length?`<div class="tw"><table><tr><th>가게</th><th>행사</th><th>기간</th><th></th></tr>${L.slice().reverse().map(r=>`<tr><td>${esc(r.ind2||r.ind)} <span class="small">${esc(r.loc||"")}</span></td><td>${esc(r.what)} ${esc(r.ben||"")}<br><span class="small">${esc(r.memo||"")}</span></td><td class="small">${esc(r.s1||"")}~${esc(r.s2||"")}</td><td><button type="button" class="ghost" data-nd="${r.id}">지우기</button></td></tr>`).join("")}</table></div>`:`<p class="empty">기록 없음</p>`;
  document.querySelectorAll("[data-nd]").forEach(b=>b.addEventListener("click",async()=>{await recDel(b.dataset.nd);list()}))};list();
 $("#nb-save").addEventListener("click",async()=>{const r={t:"주변",ind:v7("#nb-ind"),ind2:v7("#nb-ind2"),loc:v7("#nb-loc"),what:v7("#nb-what"),ben:v7("#nb-ben"),s1:v7("#nb-s1"),s2:v7("#nb-s2"),seen:v7("#nb-seen"),memo:v7("#nb-memo")};if(!r.what){$("#nb-msg").textContent="행사 내용을 넣으세요";return}
  if(/같이|함께|맞추|담합/.test(r.memo+r.what)&&/가격|할인율|%/.test(r.memo+r.what))alert("이웃 가게와 가격·할인율을 함께 정하는 내용으로 읽힙니다. 공정거래법(부당한 공동행위) 위험이 있으니 각자 정하세요.");
  if(await recPut(r)){$("#nb-msg").textContent="저장했습니다";list()}})};

// 내 기록·백업
RENDER.mine=()=>{const L=ST.rec;body(`<p class="small" style="margin:0">저장 위치: <b>${esc(ST.mode)}</b>. 저장하는 것은 가게가 적은 숫자·메모·쿠폰 번호뿐이고, 손님 개인정보는 저장할 때 막습니다(전화번호·주민번호·이메일 모양 검사).</p>
 ${ST.rec.some(x=>x.loc)&&ST.db&&!ST.ro?`<div class="row"><button type="button" class="main" id="mn-mig">이 브라우저 기록 ${ST.rec.filter(x=>x.loc).length}건을 내 계정으로 옮기기</button></div>`:""}
 <div class="tw"><table><tr><th>종류</th><th>이름</th><th>저장 날짜</th><th>위치</th><th></th></tr>${L.length?L.slice().reverse().map(r=>`<tr><td>${esc(r.t)}</td><td>${esc(r.name||r.what||"")}</td><td class="small">${esc((r.at||"").slice(0,10))}</td><td class="small">${r.loc?"이 브라우저":"내 계정"}</td><td><button type="button" class="ghost" data-md="${r.id}">지우기</button></td></tr>`).join(""):`<tr><td colspan="5" class="empty">기록 없음</td></tr>`}</table></div>
 <div class="row"><button type="button" id="mn-dl">기록 내려받기(JSON)</button><label class="chip" style="cursor:pointer">불러오기<input type="file" id="mn-up" accept=".json,application/json" style="display:none"></label><span class="small" id="mn-msg"></span></div>`);
 document.querySelectorAll("[data-md]").forEach(b=>b.addEventListener("click",async()=>{if(confirm("지울까요?")){await recDel(b.dataset.md)}}));
 $("#mn-dl").addEventListener("click",()=>saveFile("행사기록_백업.json",JSON.stringify({ver:8,rec:ST.rec.map(r=>{const {loc,...b}=r;return b})},null,1)));
 const mg=$("#mn-mig");if(mg)mg.addEventListener("click",async()=>{mg.disabled=true;const n=await recMigrate();$("#mn-msg").textContent=n+"건을 내 계정으로 옮겼습니다";RENDER.mine()});
 $("#mn-up").addEventListener("change",async e=>{const f=e.target.files[0];if(!f)return;try{const j=JSON.parse(await f.text());let n=0;for(const r of (j.rec||[]))if(r&&["결과","주변","쿠폰"].includes(r.t)&&await recPut(Object.assign({},r),true))n++;$("#mn-msg").textContent=n+"건 불러옴(개인정보 모양이 있는 기록은 건너뜀)";RENDER.mine()}catch(err){$("#mn-msg").textContent="파일을 읽지 못했습니다"}})};

// ── 처음으로 · 이전 단계 ──
const NAV=[];
function navPush(k){if(NAV[NAV.length-1]!==k)NAV.push(k);navShow()}
function navShow(){const w={s2:"2 맞는 행사안",s3:"3 고른 행사안",tool:"4 행사 도구"};$("#nav-where").textContent=NAV.length?"지금: "+w[NAV[NAV.length-1]]:"지금: 1 가게 정보";$("#nav-back").disabled=!NAV.length}
const goto=el=>el.scrollIntoView({behavior:matchMedia("(prefers-reduced-motion: reduce)").matches?"auto":"smooth",block:"start"});
$("#nav-back").addEventListener("click",()=>{const k=NAV.pop();if(k==="tool"){closeTool();const p=NAV[NAV.length-1];goto(p?$("#"+p):$("#s1"))}else if(k==="s3"){$("#s3").hidden=true;CUR=null;document.querySelectorAll(".plan").forEach(p=>p.classList.remove("sel"));goto($("#s2"))}else if(k==="s2"){$("#s2").hidden=true;$("#s3").hidden=true;CUR=null;goto($("#s1"))}navShow()});
$("#nav-home").addEventListener("click",()=>{NAV.length=0;closeTool();$("#s2").hidden=true;$("#s3").hidden=true;CUR=null;CHSEL=null;goto($("#s1"));navShow()});
toolGrid();navShow();stInit();
