import fs from 'fs';import vm from 'vm';import {fileURLToPath} from 'url';
const root=fileURLToPath(new URL('../',import.meta.url));
// Headless AI acceptance: drive full VS COMPUTER matches on the readable source and
// confirm the AI takes turns, fires through fire(), and matches resolve without stalling.
function extract(){let h=fs.readFileSync(root+'dist/index.html','utf8'),a=h.indexOf('<script>')+8,b=h.indexOf('</script>',a);return h.slice(a,b)}
function ctx(){let x=new Proxy({},{get:(o,k)=>k=='measureText'?s=>({width:String(s).length*8}):k=='createLinearGradient'||k=='createRadialGradient'?()=>({addColorStop(){}}):()=>{},set:()=>1}),c={width:960,height:540,getContext:()=>x,addEventListener(){},getBoundingClientRect:()=>({left:0,top:0,width:960,height:540})},q={document:{querySelector:()=>c,body:{classList:{add(){},remove(){}}}},addEventListener(){},requestAnimationFrame(){},setTimeout,clearTimeout,console,AudioContext:function(){return new Proxy({currentTime:0,destination:{}},{get:(o,k)=>k in o?o[k]:()=>new Proxy({frequency:{},gain:{},type:''},{get:(a,b)=>b in a?a[b]:()=>{},set:()=>1})})},WebSocket:function(){return{}}};q.webkitAudioContext=q.AudioContext;vm.createContext(q);return q}
let q=ctx();
let test=`;(()=>{let orig=fire,fired=0;fire=(...a)=>{fired++;return orig(...a)};
let games=[];for(let g=0;g<6;g++){aiMode=1;fired=0;init();started=1;let aiCharge=0,tk=0,maxRound=0,nar=0;
for(;tk<220000&&!over;tk++){update();if(round>maxRound)maxRound=round;if(narAwake)nar=1;if(charging&&P[active]&&P[active].team==1)aiCharge++}
games.push({over,fired,aiCharge:aiCharge>0,maxRound,nar,ticks:tk,aAlive:teamAlive(0),bAlive:teamAlive(1)})}
__result=games})()`;
vm.runInContext(extract()+test,q);
let games=q.__result;
let ok=games.every(g=>g.over&&g.fired>0&&g.aiCharge);
let summary={version:'0.19-ai',passed:ok,games};
fs.writeFileSync(root+'evidence/AI_RECEIPT.json',JSON.stringify(summary,null,2)+'\n');
console.log(JSON.stringify(summary,null,2));
if(!ok)process.exit(1)
