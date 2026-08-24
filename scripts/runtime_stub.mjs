import fs from 'fs';import vm from 'vm';import {fileURLToPath} from 'url';
const root=fileURLToPath(new URL('../',import.meta.url));
// Extract the <script> body. For the packed release, run the roadroller decoder (eval(...))
// which returns the decompressed source string.
function extract(file,packed){let h=fs.readFileSync(file,'utf8'),a=h.indexOf('<script>')+8,b=h.indexOf('</script>',a),s=h.slice(a,b);if(packed){let out='',q={eval:x=>out=x,Function,console};vm.createContext(q);vm.runInContext(s,q);s=out}return s}
function ctx(){let x=new Proxy({},{get:(o,k)=>k=='measureText'?s=>({width:String(s).length*8}):k=='createLinearGradient'||k=='createRadialGradient'?()=>({addColorStop(){}}):()=>{},set:()=>1}),c={width:960,height:540,getContext:()=>x,addEventListener(){},getBoundingClientRect:()=>({left:0,top:0,width:960,height:540})},q={document:{querySelector:()=>c,body:{classList:{add(){},remove(){}}}},addEventListener(){},requestAnimationFrame(){},setTimeout,clearTimeout,console,AudioContext:function(){return new Proxy({currentTime:0,destination:{}},{get:(o,k)=>k in o?o[k]:()=>new Proxy({frequency:{},gain:{},type:''},{get:(a,b)=>b in a?a[b]:()=>{},set:()=>1})})},WebSocket:function(){return{}}};q.webkitAudioContext=q.AudioContext;vm.createContext(q);return q}
// Authoritative behavioral test on the READABLE source (real function names).
function readableTest(){let q=ctx();
let test=`;(()=>{init();started=1;let z=620,t=h[z],n=holes.length,cc=ch(z),g=ground(z,cc),a=solid(z,cc),f=solid(z,cc+50),spread=new Set;for(let x=180;x<1620;x+=120)spread.add(Math.round(ch(x)-h[x]));boom(z,t+18,20,0,1);let damage=holes.length-n,dry=0;for(let x=180;x<1620;x+=120)dry+=ground(x,ch(x))<water;proj=[{x:z,y:-50,dx:0,dy:0,life:10,r:3,d:1,g:.1,c:'#fff'}];phase=1;let life=proj[0].life;update();phase=0;let p=P[active];p.y=h[p.x|0]+120;weapon=11;targetX=900;let want=ground(targetX,ch(targetX))-13;fire();__result={world:[W,H,water],holesAtInit:n,caveAir:a,caveFloor:f,ground:Math.round(g-cc),caveOffsets:spread.size,damageHole:damage,dryCaveSamples:dry,labels:[WN[3],WN[11]],highArc:[life,proj[0]?.life],blink:[p.x,Math.round(p.y),Math.round(want)],snap:(()=>{let s=JSON.parse(snap());return[s.u,s.v,s.d,s.x].every(v=>v!==undefined)})()}})()`;
vm.runInContext(extract(root+'dist/index.html',0)+test,q);return q.__result}
// Name-agnostic smoke on the PACKED release: confirm it decodes and executes without throwing.
function packedRuns(){try{let q=ctx();vm.runInContext(extract(root+'dist/release.html',1)+';__ok=1',q);return q.__ok===1}catch(e){return 'THREW: '+e.message}}
let readable=readableTest();
let packed=packedRuns();
let ok=packed===true&&readable.holesAtInit==0&&readable.caveAir==0&&readable.caveFloor==1&&readable.ground>=46&&readable.ground<=50&&readable.caveOffsets>=4&&readable.damageHole==1&&readable.dryCaveSamples>=10&&readable.highArc[1]==10&&readable.blink[0]==900&&readable.blink[1]==readable.blink[2]&&readable.snap;
let out={version:'0.20',passed:ok,readable,packedDecodesAndRuns:packed,note:'Readable VM test is behavioral authority; readable==packed rendering equivalence is proven byte-identical by scripts/agree.mjs.'};
fs.writeFileSync(root+'evidence/RUNTIME_RECEIPT.json',JSON.stringify(out,null,2)+'\n');console.log(JSON.stringify(out,null,2));if(!ok)process.exit(1)
