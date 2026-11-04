// 판 8 저장 점검: 가짜 계정 저장소를 끼워 다섯 경우를 돌림. 사용: node 점검_저장_판8.js <화면 html 절대경로>
const {chromium}=require('playwright');
const MOCK=(mode)=>`(()=>{const MODE=${JSON.stringify(mode)};
 const KEY="__mockdb";const load=()=>{try{return JSON.parse(sessionStorage.getItem(KEY)||"{}")}catch(e){return {}}};const save=o=>sessionStorage.setItem(KEY,JSON.stringify(o));
 const seg=/^[A-Za-z0-9_\\-.~:@+]{1,200}$/;const chk=p=>{for(const s of p.split("/"))if(!seg.test(s))throw new TypeError("경로 규칙 위반: "+s)};
 const err=c=>Object.assign(new Error(c),{code:c});
 const col=path=>{chk(path);return {limit:()=>({get:async()=>{if(MODE==="readfail")throw err("unavailable");const o=load();return {docs:Object.keys(o).filter(k=>k.startsWith(path+"/")).map(k=>({id:k.slice(path.length+1),data:()=>o[k]}))}}}),
  doc:id=>{chk(path+"/"+id);return {set:async d=>{if(MODE==="reject")throw err("invalid_argument");const o=load();o[path+"/"+id]=d;save(o)},delete:async()=>{const o=load();delete o[path+"/"+id];save(o)}}}}};
 const db={collection:col};const user={id:async()=>"u_test",can:async()=>MODE==="ro"?false:true};
 window.claude={use:async n=>{if(MODE==="none")return null;return n==="db"?db:n==="user"?user:null}};})();`;
(async()=>{const b=await chromium.launch();const out={};
for(const mode of (process.argv[3]?process.argv[3].split(","):["ok","ro","reject","readfail","none","nostorage"])){
 const ctx=await b.newContext();const p=await ctx.newPage({viewport:{width:1100,height:900}});const errs=[];const alerts=[];
 p.on('pageerror',e=>errs.push(e.message));p.on('dialog',async d=>{alerts.push(d.message().slice(0,60));await d.accept()});
 if(mode!=="none"&&mode!=="nostorage")await p.addInitScript(MOCK(mode));
 if(mode==="nostorage")await p.addInitScript(()=>{Object.defineProperty(window,"localStorage",{get(){throw new Error("막힘")}})});
 await p.goto('file://'+process.argv[2]);await p.waitForTimeout(600);
 await p.click('[data-sample="고깃집"]');await p.waitForTimeout(200);await p.click('#plan-0 [data-pick]');await p.waitForTimeout(200);
 await p.click('[data-tool="result"]');await p.fill('#rs-name','저장 점검');await p.fill('#rs-c0','100');await p.fill('#rs-c1','130');await p.click('#rs-save');await p.waitForTimeout(300);
 await p.click('[data-tool="coupon"]');await p.fill('#cp-ben','사이드 1접시 증정');await p.click('#cp-save');await p.waitForTimeout(300);
 const before=await p.$eval('#store-mode',x=>x.textContent);
 const db=await p.evaluate(()=>{try{return Object.keys(JSON.parse(sessionStorage.getItem("__mockdb")||"{}"))}catch(e){return []}});
 await p.reload();await p.waitForTimeout(600);
 const after=await p.$eval('#store-mode',x=>x.textContent);
 await p.click('[data-sample="고깃집"]');await p.waitForTimeout(200);await p.click('#plan-0 [data-pick]');await p.waitForTimeout(200);await p.click('[data-tool="mine"]');await p.waitForTimeout(200);
 const mine=await p.$eval('#tool-body',x=>x.innerText.replace(/\s+/g,' ').slice(0,260));
 out[mode]={저장소키:db,저장후:before,새로고침후:after,경고:alerts,오류:errs,내기록:mine};await ctx.close()}
console.log(JSON.stringify(out,null,1));await b.close()})();
