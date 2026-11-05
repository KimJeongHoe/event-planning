// 판 10 점검: 행사 방식 흐름·쿠폰 확인 글자·QR 인쇄·원가 인건비 계산. 사용: node 점검_판10.js <화면 html> [폭]
const {chromium}=require('playwright');
(async()=>{const b=await chromium.launch();const p=await b.newPage({viewport:{width:+process.argv[3]||1100,height:900}});const E=[];p.on('pageerror',e=>E.push(e.message));p.on('dialog',d=>d.accept());
await p.addInitScript(()=>{window.print=()=>{window.__printed=(window.__printed||0)+1}});
await p.goto((process.argv[2].startsWith('http')?process.argv[2]:'file://'+process.argv[2]));await p.waitForTimeout(500);const o={};
await p.click('#mbox summary');await p.waitForTimeout(100);o.방식카드=await p.$$eval('#mlist article',x=>x.length);
await p.click('[data-mf="쿠폰"]');await p.waitForTimeout(250);o.방식거름=await p.$eval('#s2-note',x=>x.innerText.slice(0,30));
await p.click('#plans [data-pick]');await p.waitForTimeout(200);
// 원가
await p.click('[data-tab="cost"]');await p.waitForTimeout(100);
await p.fill('#mn0','대표 메뉴');await p.fill('#mp0','10000');await p.fill('#mc0','3000');await p.check('#mk0');await p.dispatchEvent('#mn0','input');
await p.fill('#c-ag','30000');await p.selectOption('#c-type','증정');await p.selectOption('#c-menu','대표 메뉴').catch(()=>{});await p.fill('#c-q','1');await p.fill('#c-n','30');await p.fill('#c-fix','30000');
await p.fill('#c-min','40');await p.fill('#c-wage','12000');await p.fill('#c-hrs','6');await p.dispatchEvent('#c-hrs','input');await p.waitForTimeout(100);
o.원가=await p.$eval('#c-out',x=>x.innerText.replace(/\s+/g,' '));
// 쿠폰
await p.click('[data-tool="coupon"]');await p.waitForTimeout(150);await p.fill('#cp-ben','사이드 1접시 증정');await p.fill('#cp-n','5').catch(()=>{});await p.click('#cp-save');await p.waitForTimeout(250);
const g=await p.evaluate(()=>{const g=ST.rec.find(r=>r.t==="쿠폰");return {s1:serial(g,1),s2:serial(g,2),salt:!!g.salt,id:g.id}});o.번호=g.s1;
const use=async v=>{await p.fill(`[data-sn="${g.id}"]`,v);await p.click(`[data-use="${g.id}"]`);await p.waitForTimeout(200);return p.$eval(`[data-um="${g.id}"]`,x=>x.innerText).catch(()=>'')};
o.바꾼번호=await use(g.s1.slice(0,-2)+(g.s1.endsWith('AA')?'BB':'AA'));o.확인글자없음=await use(g.s1.slice(0,-3));
o.정상=await use('QR 읽음: '+g.s1+' ');o.두번째=await use(g.s1);
o.사용수=await p.evaluate(()=>Object.keys(ST.rec.find(r=>r.t==="쿠폰").used).length);
await p.click(`[data-pq="${g.id}"]`);await p.waitForTimeout(200);o.QR장=await p.$$eval('#cp-sheet .cpq svg',x=>x.length);o.인쇄호출=await p.evaluate(()=>window.__printed||0);
o.넘침=await p.evaluate(()=>document.documentElement.scrollWidth-innerWidth);o.오류=E;console.log(JSON.stringify(o,null,1));await b.close()})();
