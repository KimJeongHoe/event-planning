
// ── 판 10: 기본 행사 방식 축 — 「어떤 방식이 있고 무엇이 많이 쓰이나」를 먼저 보고, 방식 → 실제 사례(2단계) → 행사안(3단계)으로 이어 감.
// 자료: spec/행사방식.json(scripts/methods10.py) → D.mtd, 사례마다 c.mt. 술 판정·법 근거·업종 경고는 기존 것을 그대로 씀.
window.MF=null;
const MT=D.mtd||{};const MTK=Object.fromEntries((MT["방식"]||[]).map(m=>[m["키"],m]));
const MLIQ={덤:"술은 덤·증정 금지(주류 거래 고시), 광고에도 못 씀",증정:"술 증정 금지(주류 거래 고시)",경품:"술을 경품으로 걸 수 없음",체험:"술 시음·무료 제공은 제한",할인:"술 할인은 광고물에 쓰지 않기",쿠폰:"술 쿠폰은 광고물에 쓰지 않기",도장:"적립 보상에 술을 넣지 않기"};
const MRISKY=["할인","쿠폰","덤","증정","경품","리뷰SNS"];          // 안내형 업종에서 뒤로 보내는 방식
const MGUIDE=/병의원|치과|한의원|약국|학원|교습|태권|동물병원|중개|휴대폰|노래/;   // 응용 예시 4차 「안내형」 업종
function mGuide(){const P=typeof IP8==="function"?IP8():null;return !!(P&&MGUIDE.test(P["이름"]||""))}
function mCard(m,I,risky){const ind=I.ind,u=ind&&m["업종별"]&&m["업종별"][ind];
 const ib=u?`<span class="badge b-info">${esc(ind)} 사례의 ${u["비중"]}%</span>`:"";
 const lq=I.liq==="예"&&MLIQ[m["키"]]?`<span class="badge b-bad">술 — ${esc(MLIQ[m["키"]])}</span>`:"";
 const rk=risky?`<span class="badge b-warn">이 업종은 가격 혜택 대신 안내형으로</span>`:"";
 const lis=(m["법"]||[]).map(lawLi).join("");
 return `<article class="plan"><div class="badges"><span class="badge b-info">실제 사례 ${m["실제"]}건 · ${m["비중"]}%</span>${ib}${rk}${lq}</div>
 <h3>${esc(m["이름"])}</h3><p class="small" style="margin:0">${esc(m["설명"])}</p>
 ${lis?`<details><summary class="small">지킬 것</summary><ul class="clean small">${lis}</ul></details>`:""}
 <div class="row" style="margin-top:6px"><button type="button" data-mf="${esc(m["키"])}">이 방식 사례 보기</button></div></article>`}
function mRender(){const box=$("#mlist");if(!box||!MT["방식"])return;const I=inp(),g8=mGuide();
 box.innerHTML=`<p class="small" style="margin:6px 0">실제 사례 ${MT["기준"]["실제사례"].toLocaleString()}건에서 많이 쓰인 기본 방식 ${MT["방식"].length}가지를 다섯 묶음으로 나눴습니다. 묶음은 실제 사례가 많은 순, 묶음 안은 비중이 큰 순입니다. 한 사례가 여러 방식에 들 수 있어 비중을 더하면 100%가 넘습니다.${I.ind?` 업종을 「${esc(I.ind)}」로 고르면 그 업종 사례 안의 비중도 함께 보입니다.`:""}</p>`+
 MT["묶음"].map(g=>{const ms=MT["방식"].filter(m=>m["묶음"]===g["이름"]).map(m=>[m,g8&&MRISKY.includes(m["키"])]).sort((a,b)=>(a[1]?1:0)-(b[1]?1:0)||b[0]["실제"]-a[0]["실제"]);
  return `<h3 style="margin-top:10px">${esc(g["이름"])} <span class="small">— ${esc(g["설명"])} · 실제 사례의 ${g["비중"]}%</span></h3><div class="plans">${ms.map(([m,r])=>mCard(m,I,r)).join("")}</div>`}).join("");
 box.querySelectorAll("[data-mf]").forEach(b=>b.addEventListener("click",()=>mGo(b.dataset.mf)))}
function mGo(k){window.MF=k;if(!$("#in-ind").value){$("#go-msg").textContent="업종을 고른 뒤 「이 방식 사례 보기」를 다시 누르세요";$("#in-ind").focus();return}run()}
// run() 끝에서 부름: 지금 보는 방식 알리기와 풀기
window.mfNote=()=>{if(!window.MF||!MTK[window.MF])return;const m=MTK[window.MF];const n=$("#plans").children.length+$("#explans").children.length;
 $("#s2-note").insertAdjacentHTML("afterbegin",`<b>「${esc(m["이름"])}」 방식 사례만 봅니다.</b> ${n?"":"이 업종·단계에 맞는 이 방식 사례가 없습니다. "}<button type="button" class="ghost" id="mf-x">모든 방식 보기</button><br>`);
 $("#mf-x").addEventListener("click",()=>{window.MF=null;run()})};
["#in-ind","#in-sub","#in-liq"].forEach(q=>{const e=$(q);if(e)e.addEventListener("change",()=>setTimeout(mRender,10))});
$("#mbox")&&$("#mbox").addEventListener("toggle",()=>{if($("#mbox").open)mRender()});
$("#nav-home").addEventListener("click",()=>{window.MF=null});
mRender();
