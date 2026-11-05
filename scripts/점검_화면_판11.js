// 판 11 화면 점검(판정만, 결과는 reports/점검결과_화면_판11.json): 개발 낱말·글자 잘림·누르는 곳 크기·대비·Tab 포커스·반응 없는 단추·새 창 링크·처음으로/이전 단계.
// 사용: node 점검_화면_판11.js <화면 주소> — 폭 360·768·1280
const {chromium}=require('playwright');const fs=require('fs'),path=require('path');
const DEV="\\bundefined\\b|\\bNaN\\b|\\[object |\\bnull\\b|function ?\\(|=>|TODO|FIXME|scratchpad|D\\.cases";
(async()=>{const b=await chromium.launch();const R={};
for(const W of (process.argv[3]?process.argv[3].split(',').map(Number):[360,768,1280])){const ctx=await b.newContext({viewport:{width:W,height:860},acceptDownloads:true});const p=await ctx.newPage();const E=[];let dlg=0,dl=0;
 p.on('pageerror',e=>E.push(e.message));p.on('dialog',async d=>{dlg++;await d.accept()});p.on('download',()=>dl++);await p.addInitScript(()=>{window.print=()=>{}});
 await p.goto(process.argv[2]);await p.waitForTimeout(700);const r={dev:[],clip:new Set(),small:new Set(),noReact:[],views:0};
 const scan=async w=>{r.views++;const x=await p.evaluate(DS=>{const t=document.body.innerText;const m=t.match(new RegExp(DS));
   const vis=e=>{const s=getComputedStyle(e);const q=e.getBoundingClientRect();return s.visibility!=="hidden"&&s.display!=="none"&&q.width>0&&q.height>0};
   const clip=[...document.querySelectorAll("button,label,h2,h3,.badge,th,td,summary")].filter(e=>vis(e)&&e.scrollWidth>e.clientWidth+2&&getComputedStyle(e).overflowX!=="auto").map(e=>e.tagName+":"+e.innerText.slice(0,20));
   const small=[...document.querySelectorAll("button,select,input:not([type=checkbox]):not([type=file])")].filter(e=>vis(e)&&e.getBoundingClientRect().height<32).map(e=>e.tagName+":"+(e.innerText||e.id||"").slice(0,16));
   return {m:m?t.slice(Math.max(0,m.index-25),m.index+25):"",clip,small,ov:document.documentElement.scrollWidth-innerWidth}},DEV);
   if(x.ov>0)(r.ov=r.ov||[]).push(w+": "+x.ov);
   if(x.m)r.dev.push(w+": "+x.m.replace(/\s+/g," "));x.clip.forEach(c=>r.clip.add(c));x.small.forEach(c=>r.small.add(c))};
 const tryBtns=async w=>{const n=await p.$$eval('#tool-body button',x=>x.length);for(let i=0;i<Math.min(n,12);i++){const bs=await p.$$('#tool-body button');const bt=bs[i];if(!bt||!(await bt.isVisible()))continue;
   const before=await p.evaluate(()=>document.body.innerHTML.length+"|"+document.body.innerText.length);const d0=dlg,l0=dl;const label=(await bt.innerText()).slice(0,20);
   await bt.click({timeout:2000}).catch(()=>{});await p.waitForTimeout(120);const after=await p.evaluate(()=>document.body.innerHTML.length+"|"+document.body.innerText.length);
   if(after===before&&dlg===d0&&dl===l0)r.noReact.push(w+": "+label);if(!(await p.$('#tool-body')))break}};
 await scan('처음');await p.click('[data-sample="고깃집"]');await p.waitForTimeout(250);await scan('2단계');await p.click('#plan-0 [data-pick]');await p.waitForTimeout(200);
 for(const t of await p.$$eval('[data-tab]',x=>x.map(y=>y.dataset.tab))){await p.click(`[data-tab="${t}"]`);await p.waitForTimeout(80);await scan('탭 '+t)}
 await p.click('#mbox summary');await p.waitForTimeout(100);await scan('방식');
 for(const t of await p.$$eval('[data-tool]',x=>x.map(y=>y.dataset.tool))){await p.click(`[data-tool="${t}"]`);await p.waitForTimeout(120);await scan('도구 '+t);await tryBtns('도구 '+t)}
 await p.click('#nav-back').catch(()=>{});await p.waitForTimeout(100);const back=await p.$eval('#nav-where',x=>x.innerText);await p.click('#nav-home');await p.waitForTimeout(100);const home=await p.$eval('#nav-where',x=>x.innerText);
 let focusOk=0;await p.evaluate(()=>window.scrollTo(0,0));for(let i=0;i<12;i++){await p.keyboard.press('Tab');const f=await p.evaluate(()=>{const e=document.activeElement;if(!e||e===document.body)return null;const s=getComputedStyle(e);return (s.outlineStyle!=="none"&&s.outlineWidth!=="0px")||s.boxShadow!=="none"});if(f)focusOk++}
 const contrast=await p.evaluate(()=>{const L=c=>{const m=c.match(/\d+(\.\d+)?/g).map(Number).slice(0,3).map(v=>{v/=255;return v<=.03928?v/12.92:Math.pow((v+.055)/1.055,2.4)});return .2126*m[0]+.7152*m[1]+.0722*m[2]};
   const bg=e=>{while(e){const c=getComputedStyle(e).backgroundColor;if(c&&!/rgba\(0, 0, 0, 0\)|transparent/.test(c))return c;e=e.parentElement}return "rgb(255, 255, 255)"};
   let min=99,at="";for(const e of document.querySelectorAll("p,span,label,button,h2,h3,td,b,li")){if(!e.innerText||!e.offsetParent)continue;const a=L(getComputedStyle(e).color),c=L(bg(e));const q=(Math.max(a,c)+.05)/(Math.min(a,c)+.05);if(q<min){min=q;at=e.tagName+":"+e.innerText.slice(0,15)}}return {min:+min.toFixed(2),at}});
 const unsafe=await p.$$eval('a[target=_blank]',x=>x.filter(a=>!/noopener/.test(a.rel)).length);
 R[W]={넘친화면:(r.ov||[]).slice(0,6),화면수:r.views,개발낱말:r.dev.slice(0,5),잘림수:r.clip.size,잘림:[...r.clip].slice(0,8),작은곳수:r.small.size,작은곳:[...r.small].slice(0,6),반응없는단추:r.noReact.slice(0,10),이전단계:back,처음으로:home,Tab포커스보임:`${focusOk}/12`,최저대비:contrast,안전하지않은새창:unsafe,오류:E.slice(0,3),넘침:await p.evaluate(()=>document.documentElement.scrollWidth-innerWidth)};await ctx.close()}
fs.writeFileSync(path.join(__dirname,'..','reports','점검결과_화면_판11.json'),JSON.stringify(R,null,1));console.log(JSON.stringify(R,null,1));await b.close()})();
