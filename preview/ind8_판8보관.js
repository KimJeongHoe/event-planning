
// ── 판 8: 업종별 화면 조정 — 요식업 말·칸을 업종에 맞추고, 업종별 ⚠ 법·위험을 띄움. 자료: spec/업종_판8.json → D.ind8 ──
const IP8=()=>{const X=D.ind8||{},ind=$("#in-ind").value,sub=($("#in-sub")||{}).value||"";for(const s of (X["세부"]||[])){try{if(s.ind.includes(ind)&&new RegExp(s.re).test(sub))return s}catch(e){}}return (X["업종"]||{})[ind]||null};
function indLaw(P){return (P["법"]||[]).filter(k=>D.law[k])}
function indBanner(){const P=IP8();if(!P)return"";const ks=indLaw(P);
 return `<div class="note ${P["위험"]==="상"?"bad":""}" data-ind8><b>⚠ ${esc(P["이름"]||$("#in-ind").value)} 업종에서 먼저 볼 것</b>${P["한줄"]?`<div>${esc(P["한줄"])}</div>`:""}
 ${(P["막을행사"]||[]).length?`<div class="small" style="margin-top:4px"><b>그대로 쓰면 위험한 행사</b>: ${P["막을행사"].map(esc).join(" · ")}</div>`:""}
 ${(P["바꿀행사"]||[]).length?`<div class="small"><b>대신 쓸 만한 것</b>: ${P["바꿀행사"].map(esc).join(" · ")}</div>`:""}
 ${ks.length?`<details><summary class="small">근거 조문 ${ks.length}개</summary><ul class="clean small">${ks.map(k=>{const L=D.law[k];return `<li>⚠ ${esc(L.gist)} — ${esc(L.law)} ${esc(L.art)} <span class="badge ${L.status==="확인함"?"b-ok":"b-info"}">${esc(L.status)}</span>${L.note&&L.status!=="확인함"?`<br><span class="small">${esc(L.note)}</span>`:""}</li>`}).join("")}</ul></details>`:""}</div>`}
function indApply(){const P=IP8()||{};const W=P["말"]||{};
 // 술 판매 칸: 술과 관계없는 업종은 숨기고 「아니오」로
 const liq=$("#in-liq");if(liq){const lab=liq.closest("label");const off=P["술"]===false;if(lab)lab.hidden=off;if(off)liq.value="아니오"}
 // 원가 탭 이름표
 document.querySelectorAll("label").forEach(l=>{const n=l.firstChild;if(n&&n.nodeType===3){if(!n.__o)n.__o=n.textContent;let t=n.__o;for(const [a,b] of Object.entries(W))t=t.split(a).join(b);n.textContent=t}});
 // 업종 경고 띠: 2단계 위
 document.querySelectorAll("[data-ind8]").forEach(x=>x.remove());const h=indBanner();const s2=$("#s2");if(h&&s2)s2.insertAdjacentHTML("afterbegin",h)}
// 도구 안 업종별 바꾸기(쿠폰 예·리뷰 예·배달 해당 없음)
const _openTool8=openTool;openTool=function(k,q){_openTool8(k,q);const P=IP8();if(!P)return;const tb=$("#tool-body");if(!tb)return;
 if(k==="deliv"&&P["배달"]===false)tb.insertAdjacentHTML("afterbegin",`<div class="note">이 업종은 배달앱 판매가 드뭅니다. 배달·포장 판매를 하지 않으면 이 도구는 건너뛰세요.</div>`);
 if(k==="coupon"&&P["쿠폰예"]){const b=$("#cp-ben");if(b){b.placeholder="예: "+P["쿠폰예"];if(/사이드|접시/.test(b.value))b.value=P["쿠폰예"]}document.querySelectorAll("#tool-body .chips label, #tool-body .chips span").forEach(x=>{if(x.textContent.includes("1테이블"))x.childNodes.forEach(n=>{if(n.nodeType===3)n.textContent=n.textContent.replace("1인·1테이블 1장","1인 1장")})})}
 if(P["도구경고"]&&P["도구경고"][k])tb.insertAdjacentHTML("afterbegin",`<div class="note bad">⚠ ${esc(P["도구경고"][k])}</div>`);
 const ks=(P["도구법"]||{})[k];if(ks&&ks.length&&typeof lawBox==="function")tb.insertAdjacentHTML("beforeend",lawBox((P["이름"]||$("#in-ind").value)+" 업종에서 이 도구를 쓸 때",ks.filter(x=>D.law[x])))};
$("#in-ind").addEventListener("change",()=>setTimeout(indApply,0));$("#in-sub").addEventListener("change",()=>setTimeout(indApply,0));
document.addEventListener("click",e=>{if(e.target.closest("[data-sample],#go,[data-pick]"))setTimeout(indApply,50)});
setTimeout(indApply,0);
