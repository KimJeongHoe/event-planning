
// ── 판 10: 쿠폰 QR 사용 처리 — 쿠폰마다 번호(확인 글자 포함)를 QR로 찍어 인쇄하고, 사용 처리 때 휴대폰 카메라 앱으로 읽은 번호를 붙여 넣거나
// (기기가 지원하면) 화면에서 카메라로 바로 읽음. QR 그리기: preview/vendor_qrcode.js(MIT).
(function(){const st=document.createElement("style");st.textContent=`#cp-sheet{display:none}
body.print-sheet *{visibility:hidden}body.print-sheet #cp-sheet,body.print-sheet #cp-sheet *{visibility:visible}
body.print-sheet #cp-sheet{display:grid;position:absolute;left:0;top:0;width:100%;grid-template-columns:repeat(2,1fr);gap:4mm}
.cpq{border:1px dashed #888;padding:3mm;display:flex;gap:3mm;align-items:center;break-inside:avoid;background:#fff;color:#000;font:11px/1.35 sans-serif}
.cpq svg{width:22mm;height:22mm;flex:none}.cpq b{display:block;font-size:13px}.cpq .no{font-family:monospace;font-size:11px}`;document.head.appendChild(st)})();
function qrSvg(t){try{const q=qrcode(0,"M");q.addData(t);q.make();return q.createSvgTag({cellSize:2,margin:1,scalable:true})}catch(e){return""}}
function cpSheet(g){const N=Math.min(g.n||0,300);const conds=[g.min?won(g.min)+" 이상 구매 시":"",g.when,g.one?"1인 1장":"",g.dup?"다른 할인과 중복 불가":"",g.cash?"현금으로 바꿀 수 없음":""].filter(Boolean).join(" · ");
 let el=$("#cp-sheet");if(!el){el=document.createElement("div");el.id="cp-sheet";document.body.appendChild(el)}
 el.innerHTML=Array.from({length:N},(_,j)=>{const sn=serial(g,j+1);return `<div class="cpq">${qrSvg(sn)}<div><b>${esc(shopNm())} · ${esc(g.kind)}</b>${esc(g.ben)}<br><span>${esc(conds)}</span><br>유효기간 ${esc(g.s)} ~ ${esc(g.e||"")}<br><span class="no">No. ${esc(sn)}</span></div></div>`}).join("");
 document.body.classList.add("print-sheet");try{print()}catch(e){alert("이 화면에서는 인쇄를 열 수 없습니다. 「발급 목록 CSV」를 디자인 도구로 보내 인쇄하세요.")}setTimeout(()=>document.body.classList.remove("print-sheet"),800);
 return N<(g.n||0)?`한 번에 ${N}장까지 인쇄합니다. 나머지는 발급 목록 CSV를 쓰세요.`:""}
const CAN_SCAN=!!(window.BarcodeDetector&&navigator.mediaDevices&&navigator.mediaDevices.getUserMedia);
async function cpScan(id,btn){const box=document.querySelector(`[data-sn="${id}"]`),msg=document.querySelector(`[data-um="${id}"]`);let s;
 try{s=await navigator.mediaDevices.getUserMedia({video:{facingMode:"environment"}})}catch(e){if(msg)msg.textContent="이 화면에서는 카메라를 쓸 수 없습니다. 휴대폰 카메라 앱으로 QR을 찍어 나온 번호를 칸에 붙여 넣으세요.";return}
 const v=document.createElement("video");v.setAttribute("playsinline","");v.muted=true;v.srcObject=s;v.style.cssText="width:100%;max-width:320px;display:block;margin-top:6px;border-radius:8px";btn.closest(".row").after(v);
 const stop=()=>{s.getTracks().forEach(t=>t.stop());v.remove()};try{await v.play()}catch(e){stop();return}
 const det=new BarcodeDetector({formats:["qr_code"]}),t0=Date.now();
 const loop=async()=>{if(Date.now()-t0>20000){stop();if(msg)msg.textContent="QR을 찾지 못했습니다. 번호를 직접 넣으세요.";return}
  try{const r=await det.detect(v);if(r&&r[0]){box.value=r[0].rawValue;stop();document.querySelector(`[data-use="${id}"]`).click();return}}catch(e){}requestAnimationFrame(loop)};loop()}
const _cpList10=cpList;cpList=function(){_cpList10();const el=$("#cp-list");if(!el)return;
 el.querySelectorAll("[data-use]").forEach(b=>{const id=b.dataset.use,g=ST.rec.find(r=>r.id===id);if(!g||b.parentNode.querySelector("[data-pq]"))return;
  b.insertAdjacentHTML("afterend",`${CAN_SCAN?` <button type="button" data-scan="${esc(id)}">카메라로 읽기</button>`:""} <button type="button" class="ghost" data-pq="${esc(id)}">번호·QR 넣어 인쇄</button>`)});
 el.querySelectorAll("[data-pq]").forEach(b=>b.addEventListener("click",()=>{const g=ST.rec.find(r=>r.id===b.dataset.pq);if(!g)return;const t=cpSheet(g);const m=document.querySelector(`[data-um="${g.id}"]`);if(m&&t)m.textContent=t}));
 el.querySelectorAll("[data-scan]").forEach(b=>b.addEventListener("click",()=>cpScan(b.dataset.scan,b)));
 el.querySelectorAll("[data-sn]").forEach(i=>{i.placeholder="번호 또는 QR로 읽은 글을 붙여 넣기"})};
