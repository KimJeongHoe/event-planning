// 판 11 점검(판정만 하고 결과는 reports/점검결과_판11.json에 남김). 사용: node 점검_판11.js <화면 주소(http://127.0.0.1:포트/...)> [폭]
const {chromium}=require('playwright');const fs=require('fs');const path=require('path');
(async()=>{const W=+process.argv[3]||1100;const b=await chromium.launch();const ctx=await b.newContext({acceptDownloads:true});const p=await ctx.newPage({viewport:{width:W,height:900}});await p.setViewportSize({width:W,height:900});
const E=[],A=[],DL=[];p.on('pageerror',e=>E.push(e.message));p.on('dialog',async d=>{A.push(d.message().slice(0,50));await d.accept()});p.on('download',d=>DL.push(d.suggestedFilename()));
await p.addInitScript(()=>{window.print=()=>{}});
const u=process.argv[2];await p.goto(u.startsWith('http')?u:'file://'+u);await p.waitForTimeout(700);const o={};const ok=(k,v)=>{o[k]=v};
const tool=async k=>{await p.click(`[data-tool="${k}"]`);await p.waitForTimeout(120)};
// 샘플 막기
await p.click('[data-sample="고깃집"]');await p.waitForTimeout(150);ok('샘플표시',(await p.inputValue('#in-name')).startsWith('(샘플)'));
await p.click('#plan-0 [data-pick]');await p.waitForTimeout(150);await tool('coupon');await p.fill('#cp-ben','음료 1잔');await p.click('#cp-save');await p.waitForTimeout(150);ok('샘플저장막힘',A.some(a=>a.includes('샘플')));
await p.fill('#in-name','우리고깃집');
// 다시 뽑기
await p.click('#go');await p.waitForTimeout(250);const first=await p.$$eval('#plans h3',x=>x.map(y=>y.innerText).join('|'));await p.click('#drw-new');await p.waitForTimeout(250);const second=await p.$$eval('#plans h3',x=>x.map(y=>y.innerText).join('|'));
await p.click('#drw-prev');await p.waitForTimeout(250);const back=await p.$$eval('#plans h3',x=>x.map(y=>y.innerText).join('|'));ok('다시뽑기',first!==second&&back===first);
await p.click('#plans [data-pick]');await p.waitForTimeout(150);
// 경품 안내문
await tool('draw');await p.fill('#dr-nm','식사권');await p.fill('#dr-v','60000');await p.fill('#dr-n','2');await p.fill('#dr-s','2026-12-01');await p.fill('#dr-e','2026-12-10');await p.fill('#dr-d','2026-12-12');await p.selectOption('#dr-pi','받음(당첨 연락용)');await p.fill('#dr-pd','30');await p.click('#dr-make');await p.waitForTimeout(100);
const dt=await p.inputValue('#dr-txt');ok('경품안내문',['응모 기간','당첨자 발표','제세공과금','개인정보'].every(w=>dt.includes(w)));
// 방식 나란히
await tool('cmp');await p.fill('#cm-ag','20000');await p.fill('#cm-cr','35');await p.fill('#cm-n','50');await p.fill('#cm-w','12000');await p.fill('[data-cm="할인.d"]','5');await p.fill('[data-cm="증정.g"]','800');await p.fill('[data-cm="체험.f"]','1500');await p.fill('[data-cm="체험.r"]','30');await p.dispatchEvent('[data-cm="체험.r"]','input');await p.waitForTimeout(100);
ok('비교열',await p.$$eval('#cm-out tr',x=>x.length-1));ok('비교_할인본전',await p.$eval('#cm-out',x=>x.innerText.split('\n').find(l=>l.startsWith('가격 할인'))||''));ok('경고신호',await p.$$eval('#cm-sig li',x=>x.length));ok('권장없음',!(await p.$eval('#tool-body',x=>x.innerText)).includes('권장'));
await p.fill('#st-b','100');await p.fill('#st-m','2');await p.fill('#st-c','10');await p.fill('#st-h','10');await p.fill('#st-s','1');await p.fill('#st-x','1');await p.fill('#st-r','150');await p.fill('#st-u','20');await p.dispatchEvent('#st-u','input');await p.waitForTimeout(80);
ok('대목인력',await p.$eval('#st-out',x=>x.innerText.replace(/\s+/g,' ').slice(0,200)));
// 달력
await tool('year');ok('달력월',await p.$$eval('#tool-body details',x=>x.length));await p.fill('#yr-n','매주 목요일 뽑기');await p.selectOption('#yr-k','매주 하는 이벤트');await p.click('#yr-add');await p.waitForTimeout(200);ok('달력계획',(await p.$eval('#tool-body',x=>x.innerText)).includes('매주 목요일 뽑기'));
// 공동구매
await tool('gb');await p.fill('#gb-nm','김장 양념');await p.fill('#gb-p','10000');await p.fill('#gb-u','3');await p.fill('#gb-bp','27000');await p.fill('#gb-c','6000');await p.fill('#gb-sm','5');await p.fill('#gb-min','10');await p.fill('#gb-o','12');await p.dispatchEvent('#gb-o','input');
ok('공동구매',await p.$eval('#gb-out',x=>x.innerText.replace(/\s+/g,' ')));await p.click('#gb-file');await p.waitForTimeout(200);
// 손님 제한·코스
await tool('lim');await p.fill('#lm-b','100');await p.fill('#lm-s','10');await p.fill('#lm-a','20000');await p.dispatchEvent('#lm-a','input');ok('손님제한',await p.$eval('#lm-out',x=>x.innerText.replace(/\s+/g,' ')));ok('보조견문구',(await p.inputValue('#lm-txt')).includes('보조견'));
await tool('course');await p.fill('[data-co="0"] [data-cf="n"]','책방');await p.fill('[data-co="1"] [data-cf="n"]','빵집');await p.click('#co-make');ok('코스',(await p.inputValue('#co-txt')).includes('2. 빵집'));await p.click('#co-file');await p.waitForTimeout(150);
// 사례 검색
await tool('find');const n0=await p.$eval('#fd-n',x=>x.innerText);await p.selectOption('#fd-m','쿠폰');await p.waitForTimeout(100);const n1=await p.$eval('#fd-n',x=>x.innerText);ok('검색즉시',n0!==n1);
await p.fill('#fd-q','원가');await p.waitForTimeout(300);ok('기능이동단추',await p.$$eval('[data-fg]',x=>x.length));
// 개선 제안
await tool('idea');await p.fill('#id-t','쿠폰 만들기');await p.click('#id-go');await p.waitForTimeout(150);ok('제안있음',(await p.$eval('#id-out',x=>x.innerText)).includes('있음'));
// 원가 날씨
await p.click('[data-tab="cost"]');await p.waitForTimeout(100);ok('날씨칸',!!(await p.$('#c-wx')));
// 백업
await tool('mine');await p.click('#mn-dl');await p.waitForTimeout(200);
ok('내려받기',DL);ok('오류',E);ok('넘침',await p.evaluate(()=>document.documentElement.scrollWidth-innerWidth));
fs.writeFileSync(path.join(__dirname,'..','reports','점검결과_판11_'+W+'.json'),JSON.stringify(o,null,1));console.log(JSON.stringify(o,null,1));await b.close()})();
