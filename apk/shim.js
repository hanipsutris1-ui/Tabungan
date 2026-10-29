(function(){
var KEY="tabungan_db_v1",A=window.Android,store=null,subs={};
function load(){var raw=null;try{raw=localStorage.getItem(KEY)}catch(e){}
 if(!raw&&A&&A.readState){try{raw=A.readState()}catch(e){}}
 try{var j=raw&&JSON.parse(raw);if(j&&j.t==="tabungan")return j.d}catch(e){}return null}
store=load();
if(!store){store={};var seed=__SEED__;for(var c in seed){store[c]={};seed[c].forEach(function(d){var x=Object.assign({},d),id=x.id;delete x.id;store[c][id]=x})}}
["anggota","setoran","tarik","periode","pribadi","pset","ptarik","dkas","dcfg"].forEach(function(c){store[c]=store[c]||{}});
function save(){var s=JSON.stringify({t:"tabungan",d:store});try{localStorage.setItem(KEY,s)}catch(e){}try{if(A&&A.persistState)A.persistState(s)}catch(e){}}
save();
function snap(c){return{docs:Object.keys(store[c]).map(function(id){return{id:id,data:function(){return JSON.parse(JSON.stringify(store[c][id]))}}})}}
function notify(c){(subs[c]||[]).forEach(function(f){f()})}
var db={collection:function(c){return{
 onSnapshot:function(n,e){var f=function(){n(snap(c))};(subs[c]=subs[c]||[]).push(f);setTimeout(f,0);return function(){subs[c]=subs[c].filter(function(x){return x!==f})}},
 doc:function(id){return{
  set:async function(d){store[c][id]=JSON.parse(JSON.stringify(d));save();notify(c)},
  delete:async function(){delete store[c][id];save();notify(c)}}}}}};
function toDataUrl(b){return new Promise(function(res,rej){var r=new FileReader();r.onload=function(){res(r.result)};r.onerror=rej;r.readAsDataURL(b)})}
var dls={save:async function(o){
 var fn=o.filename||"file",ext=(fn.split(".").pop()||"").toLowerCase();
 if(!A)throw{code:"unavailable",message:"no bridge"};
 if(ext==="json"||ext==="csv"){var t=typeof o.data==="string"?o.data:await (new Blob([o.data])).text();A.saveBackup(t,fn);return{status:"saved"}}
 if(ext==="png"){var u=await toDataUrl(o.data instanceof Blob?o.data:new Blob([o.data],{type:"image/png"}));A.saveImage(u,fn);return{status:"saved"}}
 throw{code:"rejected_extension",message:"format tidak didukung di aplikasi"}}};
var usr={can:async function(){return true},canEdit:async function(){return true}};
window.claude={use:async function(n){return n==="db"?db:n==="user"?usr:n==="downloads"?dls:null}};

/* Tombol Back: tutup panel dulu, lalu tekan 2x untuk keluar */
if(A){var armed=false,tm=null;
 function guard(){try{history.pushState({g:1},"")}catch(e){}}
 function tip(m){var d=document.createElement("div");d.textContent=m;d.style.cssText="position:fixed;left:50%;bottom:110px;transform:translateX(-50%);background:#1d1640;color:#fff;padding:10px 16px;border-radius:99px;font:600 14px sans-serif;z-index:99999";document.body.appendChild(d);setTimeout(function(){d.remove()},1800)}
 window.addEventListener("load",guard);
 window.addEventListener("popstate",function(){
  var ov=document.querySelector(".ov");
  if(ov){ov.remove();guard();return}
  armed=true;tip("Tekan sekali lagi untuk keluar");
  clearTimeout(tm);tm=setTimeout(function(){armed=false;guard()},2000);
 });
}
})();
