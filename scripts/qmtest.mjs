import fs from 'fs';import vm from 'vm';import {fileURLToPath} from 'url';
const root=fileURLToPath(new URL('../',import.meta.url));
// Quick-match acceptance on the readable source with a mock js13k relay hub.
// Covers: same-window pairing, simultaneous-host tie-break (jitter collapsed to 0),
// and room-full auto-retry leaving the live match untouched.
function src(){let h=fs.readFileSync(root+'dist/index.html','utf8'),a=h.indexOf('<script>')+8,b=h.indexOf('</script>',a);return h.slice(a,b)}
function hub(){
  let rooms={},nid=0;
  return{
    WebSocket:function(url){let sock=this;sock.readyState=1;let m=String(url).match(/parties\/[^/]+\/(.+)$/);sock.room=m?m[1]:'?';
      sock.send=msg=>{for(let o of rooms[sock.room]||[])if(o!==sock&&o.readyState==1&&o.onmessage)o.onmessage({data:msg})};
      sock.close=()=>{if(sock.readyState!=1)return;sock.readyState=3;rooms[sock.room]=(rooms[sock.room]||[]).filter(o=>o!==sock);for(let o of rooms[sock.room]||[])if(o.onmessage)o.onmessage({data:'-'+sock.id})};
      setTimeout(()=>{rooms[sock.room]=rooms[sock.room]||[];sock.id='p'+(++nid);rooms[sock.room].push(sock);sock.onmessage({data:'@'+sock.id});for(let o of rooms[sock.room])if(o!==sock&&o.onmessage){o.onmessage({data:'+'+sock.id});sock.onmessage({data:'+'+o.id})}sock.onopen&&sock.onopen()},0)}
  }
}
function page(net){
  let x=new Proxy({},{get:(o,k)=>k=='measureText'?s=>({width:String(s).length*8}):k=='createLinearGradient'||k=='createRadialGradient'?()=>({addColorStop(){}}):()=>{},set:()=>1});
  let c={width:960,height:540,getContext:()=>x,addEventListener(){},getBoundingClientRect:()=>({left:0,top:0,width:960,height:540})};
  let q={document:{querySelector:()=>c,body:{classList:{add(){},remove(){}}}},addEventListener(){},requestAnimationFrame(){},setTimeout,clearTimeout,console,Date,Math,WebSocket:net.WebSocket};
  q.AudioContext=function(){return new Proxy({currentTime:0,destination:{}},{get:(o,k)=>k in o?o[k]:()=>new Proxy({frequency:{},gain:{},type:''},{get:(a,b)=>b in a?a[b]:()=>{},set:()=>1})})};
  q.webkitAudioContext=q.AudioContext;vm.createContext(q);return q;
}
const sleep=ms=>new Promise(r=>setTimeout(r,ms));
let net=hub(),A=page(net),B=page(net),C=page(net);
vm.runInContext(src(),A);vm.runInContext(src(),B);vm.runInContext(src(),C);
const ev=(q,code)=>vm.runInContext('('+code+')()',q);
let results={},pass=true;
function check(name,v,want=true){v=!!v;results[name]=v===want?'ok':'FAIL('+v+')';if(v!==want)pass=false}
// 1: same-window quick match pairs deterministically
await ev(A,()=>quickMatch());await ev(B,()=>quickMatch());
let t0=Date.now();
while(Date.now()-t0<6000){if(await ev(A,()=>started)&&await ev(B,()=>started))break;await sleep(100)}
check('paired',await ev(A,()=>started)&&await ev(B,()=>started));
check('sameSeed',await ev(A,()=>seed)===await ev(B,()=>seed));
check('distinctTeams',await ev(A,()=>myTeam)!==await ev(B,()=>myTeam));
check('sameTerrain',await ev(A,()=>ghash())===await ev(B,()=>ghash()));
// 2: third quick-matcher hits the live room -> auto-retries next window, match untouched
await ev(C,()=>{Math.random=()=>0;quickMatch()});
await sleep(2500);
check('matchUnaffected',await ev(A,()=>started)&&await ev(B,()=>started)&&await ev(A,()=>over)===0);
check('thirdRetrying',await ev(C,()=>!started&&(netUI=='host'||netUI=='qwait'||netUI=='conn')));
// 3: simultaneous-host tie-break (both jitter to 0 -> both claim host in a fresh window)
let net2=hub(),D=page(net2),E=page(net2);
vm.runInContext(src(),D);vm.runInContext(src(),E);
await ev(D,()=>{Math.random=()=>0;quickMatch()});await ev(E,()=>{Math.random=()=>0;quickMatch()});
let t1=Date.now();while(Date.now()-t1<8000){if(await ev(D,()=>started)&&await ev(E,()=>started))break;await sleep(100)}
check('tiebreakPaired',await ev(D,()=>started)&&await ev(E,()=>started));
check('tiebreakSameSeed',await ev(D,()=>seed)===await ev(E,()=>seed));
check('tiebreakTeams',await ev(D,()=>myTeam)!==await ev(E,()=>myTeam));
let out={version:'0.19-qm',pass,results};
fs.writeFileSync(root+'evidence/QM_RECEIPT.json',JSON.stringify(out,null,2)+'\n');
console.log(JSON.stringify(out,null,2));if(!pass)process.exit(1)
