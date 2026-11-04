
// ── 업종별 화면 조정(판 8 → 판 9) — 요식업 말·칸을 업종에 맞추고, 업종별 법·위험을 기존 자리(「주의 사항」 탭, 도구의 근거 목록)에 넣음.
// 판 9: 새 경고 띠·빨간 상자·상태 배지를 만들지 않음. 자료: spec/업종_판8.json → D.ind8
const IP8=()=>{const X=D.ind8||{},ind=$("#in-ind").value,sub=($("#in-sub")||{}).value||"";for(const s of (X["세부"]||[])){try{if(s.ind.includes(ind)&&new RegExp(s.re).test(sub))return s}catch(e){}}return (X["업종"]||{})[ind]||null};
const deW=t=>String(t||"").replace(/^⚠\s*/,"");
function indLis(keys){return (keys||[]).filter(k=>D.law[k]).map(lawLi).join("")}
// 「주의 사항」 탭 끝에 기존 상자 모양으로 업종 항목
function indRisk(){const box=$("#tab-risk");if(!box||!CUR)return;box.querySelectorAll("[data-ind8]").forEach(x=>x.remove());const P=IP8();if(!P)return;
 const wrap=box.firstElementChild||box;const ks=(P["법"]||[]).filter(k=>D.law[k]);
 wrap.insertAdjacentHTML("beforeend",`<div class="note" data-ind8><b>${esc(P["이름"])} 업종에서 지킬 것</b>${P["한줄"]?` — ${esc(deW(P["한줄"]))}`:""}<ul class="clean" style="margin-top:4px">
 ${(P["막을행사"]||[]).map(x=>`<li>그대로 하지 않기: ${esc(deW(x))}</li>`).join("")}${(P["바꿀행사"]||[]).map(x=>`<li>대신 이렇게: ${esc(deW(x))}</li>`).join("")}</ul>
 ${ks.length?`<details><summary class="small">근거 법령 ${ks.length}개</summary><ul class="clean small">${indLis(ks)}</ul></details>`:""}</div>`)}
function indApply(){const P=IP8()||{};const W=P["말"]||{};
 const liq=$("#in-liq");if(liq){const lab=liq.closest("label");const off=P["술"]===false;if(lab)lab.hidden=off;if(off)liq.value="아니오"}
 document.querySelectorAll("label").forEach(l=>{const n=l.firstChild;if(n&&n.nodeType===3){if(!n.__o)n.__o=n.textContent;let t=n.__o;for(const [a,b] of Object.entries(W))t=t.split(a).join(b);n.textContent=t}});
 // 판 9: 요식업이 아니면 보이는 이름만 바꿈(값은 사례 분류와 이어져 있어 그대로)
 const food=$("#in-ind").value==="요식업";const VN={"신메뉴":"신상품·새 서비스","신메뉴알리기":"새 상품·서비스 알리기","포장배달":"포장·배달·택배","회전율":"손님 회전"};
 document.querySelectorAll("#in-st option").forEach(o=>{if(VN[o.value])o.textContent=food?o.value:VN[o.value]});
 document.querySelectorAll("#in-goals label").forEach(l=>{const i=l.querySelector("input");const n=[...l.childNodes].find(x=>x.nodeType===3);if(i&&n&&VN[i.value])n.textContent=food?i.value:VN[i.value]});
 indRisk()}
// 도구: 업종 항목을 그 도구의 기존 근거 목록(⚠ 상자) 안에 더함. 상자가 없는 도구는 더하지 않음
const _openTool8=openTool;openTool=function(k,q){_openTool8(k,q);const P=IP8();if(!P)return;const tb=$("#tool-body");if(!tb)return;
 if(k==="coupon"&&P["쿠폰예"]){const b=$("#cp-ben");if(b){b.placeholder="예: "+P["쿠폰예"];if(/사이드|접시/.test(b.value))b.value=P["쿠폰예"]}tb.querySelectorAll(".chips label, .chips span").forEach(x=>{if(x.textContent.includes("1테이블"))x.childNodes.forEach(n=>{if(n.nodeType===3)n.textContent=n.textContent.replace("1인·1테이블 1장","1인 1장")})})}
 if(k==="review"&&$("#in-ind").value!=="요식업")tb.querySelectorAll("textarea,pre,p,li").forEach(x=>{const f=x.tagName==="TEXTAREA"?"value":"textContent";if(x[f].includes("맛·서비스"))x[f]=x[f].split("맛·서비스").join("서비스·결과")});
 const ul=tb.querySelector(".note.bad ul");if(!ul)return;
 const w=(P["도구경고"]||{})[k];const ks=((P["도구법"]||{})[k]||[]).filter(x=>D.law[x]&&!ul.innerHTML.includes(esc(D.law[x].gist)));
 ul.insertAdjacentHTML("beforeend",(w?`<li>⚠ <b>${esc(P["이름"])}</b> — ${esc(deW(w))}</li>`:"")+indLis(ks))};
$("#in-ind").addEventListener("change",()=>setTimeout(indApply,0));$("#in-sub").addEventListener("change",()=>setTimeout(indApply,0));
document.addEventListener("click",e=>{if(e.target.closest("[data-sample],[data-pick],[data-tab]"))setTimeout(indApply,50)});
setTimeout(indApply,0);
