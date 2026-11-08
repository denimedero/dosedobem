// Uso: node render.js data.json outdir [--video]
const {chromium}=require('playwright');const fs=require('fs');const path=require('path');
(async()=>{const [dataF,out]=process.argv.slice(2);const video=process.argv.includes('--video');
const DATA=JSON.parse(fs.readFileSync(dataF,'utf8'));fs.mkdirSync(out,{recursive:true});
const url='file://'+path.join(__dirname,'templates.html');const b=await chromium.launch();
async function pg(fmt,h){const p=await b.newPage({viewport:{width:1080,height:h}});
 await p.addInitScript(d=>{window.DATA=d},DATA);await p.goto(url+'?fmt='+fmt);await p.waitForTimeout(200);return p;}
const feed=await pg('feed',1350);const n=await feed.evaluate(()=>NS);
for(let k=0;k<n;k++){await feed.evaluate(k=>still(k),k);await feed.screenshot({path:`${out}/carrossel-${k+1}.png`});}
const st=await pg('story',1920);
for(let k=0;k<n;k++){await st.evaluate(k=>still(k),k);await st.screenshot({path:`${out}/story-${k+1}.png`});}
const r=await pg('reel',1920);await r.evaluate(()=>frame(2.6));await r.screenshot({path:`${out}/reel-capa.png`});
if(video){const fd=path.join(out,'.frames');fs.mkdirSync(fd,{recursive:true});const D=await r.evaluate(()=>DUR),fps=30;
 for(let k=0;k<Math.round(D*fps);k++){await r.evaluate(t=>frame(t),k/fps);await r.screenshot({path:`${fd}/${String(k).padStart(4,'0')}.png`,type:'png'});}}
await b.close();})();
