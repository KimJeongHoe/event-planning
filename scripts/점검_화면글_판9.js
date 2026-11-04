// 판 9 화면 글 점검: 덜 만든 표시가 사장님 화면 글에 나오는지 업종·샘플·탭·도구를 돌며 찾음. 사용: node 점검_화면글_판9.js <화면 html> [폭]
const {chromium}=require('playwright');const BAD=/확인 필요|확인필요|준비 중|연결 대기|미확인|원문 미확인|예시 파일/;
(async()=>{const b=await chromium.launch();const p=await b.newPage({viewport:{width:+process.argv[3]||1100,height:900}});const E=[];p.on('pageerror',e=>E.push(e.message));p.on('dialog',d=>d.accept());
await p.goto('file://'+process.argv[2]);await p.waitForTimeout(500);const hits=[];let views=0;
const scan=async w=>{views++;const t=await p.evaluate(()=>document.body.innerText);const m=t.match(new RegExp('.{0,30}('+BAD.source+').{0,30}','g'));if(m)hits.push(w+': '+m.slice(0,2).join(' / '))};
const tabs=await p.$$eval('[data-tab]',x=>x.map(y=>y.dataset.tab));
const flows=[['sample','고깃집'],['sample','카페'],['sample','미용실'],['ind','학원·교육|학원'],['ind','병의원·약국|치과'],['ind','병의원·약국|약국'],['ind','소매|편의점'],['ind','서비스업|헬스장'],['ind','미용·뷰티|네일'],['ind','소매|편의점'],['ind','요식업|한식'],['ind','서비스업|세탁']];
for(const [k,v] of flows){if(k==='sample'){await p.click('#nav-home').catch(()=>{});await p.waitForTimeout(100);await p.click(`[data-sample="${v}"]`)}else{const [i,s]=v.split('|');await p.click('#nav-home').catch(()=>{});await p.selectOption('#in-ind',i);await p.selectOption('#in-sub',s).catch(()=>{});await p.click('#go').catch(async()=>{await p.click('button.main').catch(()=>{})})}
 await p.waitForTimeout(250);await scan(v+' 2단계');const pick=await p.$('[data-pick]');if(!pick)continue;await pick.click();await p.waitForTimeout(200);
 for(const t of tabs){await p.click(`[data-tab="${t}"]`).catch(()=>{});await p.waitForTimeout(60);await scan(v+' 탭 '+t)}
 const tools=await p.$$eval('[data-tool]',x=>x.map(y=>y.dataset.tool));for(const t of tools){await p.click(`[data-tool="${t}"]`);await p.waitForTimeout(80);await scan(v+' 도구 '+t)}}
const tools=await p.$$eval('[data-tool]',x=>x.map(y=>y.dataset.tool));
console.log(JSON.stringify({본화면:views,도구:tools,걸림:hits.length,예:hits.slice(0,8),오류:E,넘침:await p.evaluate(()=>document.documentElement.scrollWidth-innerWidth)},null,1));await b.close()})();
