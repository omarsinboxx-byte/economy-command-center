(()=>{
'use strict';
const STORAGE='finance-command-center-v1';
const files=['economy','futures','rates','calendar','status'];
const num=v=>Number(String(v??'').replace(/[$,%\s,]/g,''))||0;
const rateId=name=>{const x=String(name||'').toLowerCase();if(x.includes('high-yield')||x.includes('high yield')||x==='savings')return'savings';if(x==='cd')return'cd';if(x.includes('3-month'))return't3m';if(x.includes('1-year'))return't1y';if(x.includes('2-year'))return't2y';if(x.includes('credit card'))return'card';if(x.includes('auto'))return'auto';if(x.includes('mortgage'))return'mortgage';if(x.includes('heloc'))return'heloc';return''};
const evKey=e=>e.uid||`${e.date||''}|${e.start||''}|${e.title||''}`;
const normalizeType=v=>{const x=String(v||'').toLowerCase();if(x.includes('econ'))return'economic';if(x.includes('earning'))return'earnings';if(x.includes('call')||x.includes('conference'))return'call';if(x.includes('split'))return'split';if(x.includes('dividend'))return'dividend';if(x.includes('ipo')||x.includes('listing'))return'ipo';return'other'};
function status(text,cls,time){const a=document.getElementById('publicDataStatus'),b=document.getElementById('publicDataTime');if(a){a.textContent=text;a.className='mini '+(cls||'')}if(b)b.textContent='Last public refresh: '+(time?new Date(time).toLocaleString():'—')}
function readState(){try{return JSON.parse(localStorage.getItem(STORAGE)||'{}')}catch{return{}}}
function mergePayload(payload,mode){
  const state=window.__FCC_STATE||readState();
  state.eco=state.eco||{};state.history=state.history||{};state.futures=state.futures||{};state.futureHistory=state.futureHistory||{};state.rates=state.rates||{};
  Object.entries(payload?.economy?.series||{}).forEach(([id,v])=>{if(v?.latest==null)return;state.eco[id]={...(state.eco[id]||{}),latest:num(v.latest),previous:v.previous==null?state.eco[id]?.previous:num(v.previous),date:v.date||state.eco[id]?.date};if(Array.isArray(v.history)&&v.history.length)state.history[id]=v.history.map(x=>({date:x.date,value:num(x.value)}))});
  Object.entries(payload?.futures?.contracts||{}).forEach(([sym,v])=>{if(v?.latest==null)return;state.futures[sym]={...(state.futures[sym]||{}),latest:num(v.latest),previous:v.previous==null?state.futures[sym]?.previous:num(v.previous),open:v.open??'',high:v.high??'',low:v.low??'',volume:v.volume??'',date:v.date||state.futures[sym]?.date};if(Array.isArray(v.history)&&v.history.length)state.futureHistory[sym]=v.history.map(x=>({date:x.date,latest:num(x.latest??x.value),value:num(x.latest??x.value)}))});
  Object.values(payload?.rates?.rates||{}).forEach(v=>{const id=rateId(v?.name);if(id&&v?.rate!=null)state.rates[id]={...(state.rates[id]||{}),rate:num(v.rate),date:v.date||'',status:v.status||'current'}});
  if(Array.isArray(payload?.calendar?.events)){const priv=(state.calendarEvents||[]).filter(e=>e.publicSource!=='github'),seen=new Set(priv.map(evKey)),remote=[];payload.calendar.events.forEach((e,i)=>{if(!e?.date||!e?.title)return;const o={id:e.id||`public-${i}`,uid:e.uid||'',date:e.date,start:e.start||'',end:e.end||'',type:normalizeType(e.type||'economic'),importance:e.importance||'Medium',ticker:e.ticker||'',title:e.title,location:e.location||'',notes:e.notes||'',publicSource:'github'};const k=evKey(o);if(!seen.has(k)){seen.add(k);remote.push(o)}});state.calendarEvents=[...priv,...remote]}
  const updated=payload?.status?.completedAt||payload?.status?.updated||payload?.economy?.updated||payload?.futures?.updated||null;
  state._publicMeta={mode,status:payload?.status?.overall||'ok',updated};
  localStorage.setItem(STORAGE,JSON.stringify(state));
  const label=mode==='offline'?'Public data: OFFLINE SNAPSHOT':state._publicMeta.status==='ok'?'Public data: ONLINE • healthy':'Public data: ONLINE • partial';
  status(label,mode==='offline'?'public-offline':state._publicMeta.status==='ok'?'public-ok':'public-warn',updated);
  const token=(updated||'none')+'|'+mode;
  if(sessionStorage.getItem('fcc-public-token')!==token){sessionStorage.setItem('fcc-public-token',token);location.reload()}
}
async function run(){
  try{
    const embedded=document.getElementById('offline-public-data');
    if(embedded){mergePayload(JSON.parse(embedded.textContent||'{}'),'offline');return}
    if(location.protocol!=='http:'&&location.protocol!=='https:'){const m=readState()._publicMeta;status('Public data: local/offline fallback','public-warn',m?.updated);return}
    const entries=await Promise.all(files.map(async n=>{const r=await fetch(`data/${n}.json?v=${Date.now()}`,{cache:'no-store'});if(!r.ok)throw new Error(`${n}:${r.status}`);return[n,await r.json()]}));
    mergePayload(Object.fromEntries(entries),'online');
  }catch(e){console.warn('Automatic public data refresh failed',e);const m=readState()._publicMeta;status('Public data: saved fallback','public-warn',m?.updated)}
}
run();
})();