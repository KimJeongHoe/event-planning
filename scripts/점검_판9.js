const {chromium}=require('playwright');
(async()=>{const b=await chromium.launch();const W=+process.argv[3]||1100;const p=await b.newPage({viewport:{width:W,height:900}});const errs=[];
p.on('pageerror',e=>errs.push('오류 '+e.message));p.on('console',m=>{if(m.type()==='error')errs.push('콘솔 '+m.text())});
await p.goto('file://'+process.argv[2]);await p.waitForTimeout(500);
const r={};
await p.click('[data-sample="고깃집"]');await p.waitForTimeout(300);
r.ex=await p.$$eval('#explans .plan',x=>x.length);r.plans=await p.$$eval('#plans .plan',x=>x.length);r.side=await p.$$eval('#side .plan',x=>x.length);
await p.click('#plan-0 [data-pick]');await p.waitForTimeout(300);
r.ch=await p.$$eval('#ch-box label:not([hidden])',x=>x.length);r.check=await p.$eval('#nt-check',x=>x.innerText.slice(0,80));
r.greet=await p.$$eval('[data-ins]',x=>x.length);
await p.click('[data-tab="plan"]');await p.fill('#sc-s','2026-11-20');await p.dispatchEvent('#sc-s','change');await p.fill('#sc-e','2026-11-30');await p.dispatchEvent('#sc-e','change');
r.sched=await p.$eval('#tab-plan',x=>x.innerText.slice(0,300));
await p.click('[data-tab="cost"]');await p.fill('#c-n','30');await p.fill('#c-add','20');await p.dispatchEvent('#c-add','input');
r.cost=await p.$eval('#c-out',x=>x.innerText.replace(/\n/g,' ').slice(0,400));
for(const k of ['coupon','review','infl','regular','draw','result','near','mine']){await p.click(`[data-tool="${k}"]`);await p.waitForTimeout(150);r['t_'+k]=(await p.$eval('#tool-body',x=>x.innerText.length));}
await p.click('[data-tool="coupon"]');await p.fill('#cp-ben','사이드 1접시 증정');await p.click('#cp-save');await p.waitForTimeout(200);
await p.fill('[data-sn]', 'CP-'+(new Date().toISOString().slice(0,10).replace(/-/g,''))+'-0003');await p.click('[data-use]');await p.waitForTimeout(200);
r.cplist=await p.$eval('#cp-list',x=>x.innerText.slice(0,160));
await p.click('[data-tool="result"]');await p.fill('#rs-c0','100');await p.fill('#rs-c1','130');await p.fill('#rs-m0','2000000');await p.fill('#rs-m1','2600000');await p.fill('#rs-cost','200000');await p.click('#rs-save');await p.waitForTimeout(200);
await p.click('#nav-back');await p.waitForTimeout(100);await p.click('#nav-back');await p.waitForTimeout(100);r.afterBack=await p.$eval('#s3',x=>x.hidden);
await p.click('#go');await p.waitForTimeout(300);r.mybox=await p.$eval('#mybox',x=>x.innerText.slice(0,160));r.badge=await p.$$eval('.plan .badge',x=>x.filter(y=>y.textContent.includes('해 본 안')).length);
await p.click('#nav-home');r.home=await p.$eval('#s2',x=>x.hidden);
r.hscroll=await p.evaluate(()=>document.documentElement.scrollWidth-window.innerWidth);
console.log(JSON.stringify(r,null,0));console.log(errs.join('\n')||'오류 없음');
if(process.argv[4]){await p.click('[data-sample="카페"]');await p.click('#plan-0 [data-pick]');await p.waitForTimeout(300);await p.screenshot({path:process.argv[4],fullPage:false});}
await b.close()})();
