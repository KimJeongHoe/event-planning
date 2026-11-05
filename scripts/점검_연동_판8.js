// 판 8 연결 파일 점검: 예시 3개와 틀린 파일 1개를 불러와 연결 확인. 사용: node 점검_연동_판8.js <화면 html> <예시 폴더> <틀린 파일>
// 주의: 시험 도구가 한글 파일 이름을 못 넘기므로 예시 파일은 copy.json·deliv.json·open.json 영문 이름으로 복사해 폴더를 넘김
const {chromium}=require('playwright');
(async()=>{const b=await chromium.launch();const p=await b.newPage({viewport:{width:1100,height:900}});const errs=[];p.on('pageerror',e=>errs.push(e.message));p.on('dialog',d=>d.accept());
await p.goto((process.argv[2].startsWith('http')?process.argv[2]:'file://'+process.argv[2]));await p.waitForTimeout(500);const r={};
await p.click('[data-sample="고깃집"]');await p.waitForTimeout(200);await p.click('#plan-0 [data-pick]');await p.waitForTimeout(200);
await p.click('[data-tool="link"]');r.대기=await p.$eval('#tool-body',x=>(x.innerText.match(/연결 대기/g)||[]).length);
await p.setInputFiles('[data-lk="deliv"]',process.argv[4]);await p.waitForTimeout(200);r.틀린파일=await p.$eval('#lk-msg',x=>x.innerText.replace(/\s+/g,' ').slice(0,300));
for(const [k,f] of [["copy","문구기준"],["deliv","배달요금표"],["open","개업순서표"]]){await p.setInputFiles(`[data-lk="${k}"]`,process.argv[3]+'/'+k+'.json');await p.waitForTimeout(200)}
r.연결=await p.$eval('#tool-body',x=>(x.innerText.match(/연결됨/g)||[]).length);
await p.click('[data-tool="deliv"]');await p.waitForTimeout(150);await p.selectOption('#dv-pick','0');await p.waitForTimeout(100);r.배달=await p.evaluate(()=>[dvr=document.querySelector('#dv-r').value,document.querySelector('#dv-vat').value,document.querySelector('#dv-pick-src').innerText]);
await p.click('[data-tool="open"]');await p.waitForTimeout(150);r.개업=await p.$eval('#op-t',x=>(x.innerText.match(/순서표 파일/g)||[]).length);
await p.click('[data-tab="notice"]').catch(()=>{});await p.fill('#nt-insta','100% 만족 보장 무조건 드려요');await p.dispatchEvent('#nt-insta','input');await p.waitForTimeout(150);
r.검사=await p.$eval('#nt-check',x=>x.innerText.replace(/\s+/g,' ').slice(0,400));
await p.reload();await p.waitForTimeout(500);await p.click('[data-sample="고깃집"]');await p.click('#plan-0 [data-pick]');await p.click('[data-tool="link"]');r.새로고침후연결=await p.$eval('#tool-body',x=>(x.innerText.match(/연결됨/g)||[]).length);
r.오류=errs;console.log(JSON.stringify(r,null,1));await b.close()})();
