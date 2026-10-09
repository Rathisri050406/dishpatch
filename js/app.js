const img=n=>(window.IMG&&IMG[n])||"images/"+n+".svg";
const $=s=>document.querySelector(s),$$=s=>document.querySelectorAll(s);
const STEPS={delivery:["Order placed","Being prepared","Out for delivery","Delivered"],pickup:["Order placed","Being prepared","Ready for pickup","Picked up"]};
const CATS=[["All","🏠"],["Trending","🔥"],["South Indian","🍛"],["Biryani","🍗"],["Pizza","🍕"],["Burgers","🍔"],["Chinese","🥡"],["Sushi","🍣"],["Desserts","🍰"],["Healthy","🥗"],["Snacks","🍟"]];
const PILLS=[["off","Offers"],["top","Over 4.3 ★"],["fast","Under 30 min"],["free","Free delivery"],["veg","Pure veg"]];
const S={cat:"All",veg:0,off:0,top:0,fast:0,free:0,sort:"rating",mode:"delivery",cart:{},cur:null,track:null,step:0,f:{}};let timer;
const find=id=>R.find(r=>r.id==id),fee=r=>S.mode=="pickup"?0:r.fee,promo=r=>r.p?`${r.p[0]}% off up to ₹${r.p[1]} on ₹${r.p[2]}+`:"";
const info=k=>{const[a,b]=k.split("|"),r=find(a);return{r,d:r.m[b]}};
function bill(){const ks=Object.keys(S.cart);if(!ks.length)return null;const r=info(ks[0]).r,sub=ks.reduce((s,k)=>s+info(k).d[1]*S.cart[k],0);
 const disc=r.p&&sub>=r.p[2]?Math.min(r.p[1],Math.round(sub*r.p[0]/100)):0,tax=Math.round((sub-disc)*.05),f=fee(r);return{ks,r,sub,disc,tax,f,total:sub-disc+tax+f}}
const toast=t=>{const e=$("#toast");e.textContent=t;e.style.display="block";clearTimeout(toast.t);toast.t=setTimeout(()=>e.style.display="none",2800)};
const card=r=>`<button class="card" data-r="${r.id}"><div class="ph"><img src="${img("r"+r.id)}" alt="${r.n}" loading="lazy">${r.p?`<span class="tagp">${r.p[0]}% OFF</span>`:""}</div><div class="ci"><div class="row"><b>${r.n}</b><span class="rate">${r.r} ★</span></div><div class="meta">${fee(r)?"₹"+fee(r)+" delivery":"₹0 delivery fee"} · ${r.km} km · ${r.t} min</div><div class="meta">${r.c} · ${r.rv}+ ratings${r.veg?' · <span class="vt">Pure veg</span>':""}</div></div></button>`;
function list(){const q=$("#q").value.trim().toLowerCase(),low=r=>Math.min(...r.m.map(m=>m[1]));
 const a=R.filter(r=>(S.cat=="All"||(S.cat=="Trending"?r.r>=4.4:r.c==S.cat))&&(!S.veg||r.veg)&&(!S.off||r.p)&&(!S.top||r.r>=4.3)&&(!S.fast||r.t<30)&&(!S.free||fee(r)==0)&&(!q||(r.n+r.c+r.m.map(x=>x[0]).join()).toLowerCase().includes(q)))
  .sort((x,y)=>S.sort=="time"?x.t-y.t:S.sort=="price"?low(x)-low(y):y.r-x.r);
 $("#count").textContent=a.length+(a.length==1?" restaurant":" restaurants");
 $("#grid").innerHTML=a.map(card).join("")||`<p class="empty">No restaurants match. <button class="pill" data-reset>Reset filters</button></p>`}
function ui(){$("#cats").innerHTML=CATS.map(([c,e])=>`<button class="cat" data-c="${c}" aria-pressed="${S.cat==c}"><span>${e}</span>${c=="South Indian"?"South":c}</button>`).join("");
 $("#pills").innerHTML=PILLS.map(([k,l])=>`<button class="pill" data-f="${k}" aria-pressed="${!!S[k]}">${l}</button>`).join("")+`<select id="so" aria-label="Sort"><option value="rating">Top rated</option><option value="time">Fastest</option><option value="price">Lowest price</option></select>`;
 $("#so").value=S.sort;$$(".side [data-n]").forEach(b=>b.setAttribute("aria-pressed",!!S[b.dataset.n]));
 $$(".mode button").forEach(b=>b.setAttribute("aria-pressed",b.dataset.m==S.mode));list()}
function reset(){Object.assign(S,{cat:"All",veg:0,off:0,top:0,fast:0,free:0,sort:"rating"});$("#q").value="";ui()}
function openRest(id){const r=S.cur=find(id);$("#menu").innerHTML=`<div class="hd"><b>${r.n}</b><button class="x" data-close="menu" aria-label="Close menu">✕</button></div><div class="bd"><img class="cov" src="${img("r"+r.id)}" alt=""><h2>${r.n}</h2><div class="meta">${r.c} · ${r.r} ★ (${r.rv}+) · ${r.t} min · ${r.km} km</div>${r.p?`<div class="promo">${promo(r)}</div>`:""}${r.m.map((d,i)=>`<div class="item"><img src="${img(r.id+"-"+i)}" alt="${d[0]}" loading="lazy"><div class="nm"><span class="veg ${d[2]?"":"n"}"></span>${d[0]}<div class="meta">₹${d[1]}</div></div><button class="add" data-add="${i}">Add</button></div>`).join("")}</div>`;$("#menu").classList.add("open")}
function add(i){const k=S.cur.id+"|"+i;if(Object.keys(S.cart).some(x=>x.split("|")[0]!=S.cur.id)){S.cart={};toast("Cart cleared: one restaurant per order")}S.cart[k]=(S.cart[k]||0)+1;upd();toast(S.cur.m[i][0]+" added")}
function upd(){$("#cc").textContent=Object.values(S.cart).reduce((a,b)=>a+b,0);cartUI()}
function cartUI(){const c=$("#cart"),t=S.track,hd=x=>`<div class="hd"><b>${x}</b><button class="x" data-close="cart" aria-label="Close cart">✕</button></div>`;
 if(t){c.innerHTML=hd("Order "+t.id)+`<div class="bd"><p class="meta">${t.restaurant} · ₹${t.total} · ${t.mode=="pickup"?"Pickup":"Delivery"}</p><ul class="steps">${STEPS[t.mode].map((s,i)=>`<li class="${i<=S.step?"on":""}">${s}</li>`).join("")}</ul><button class="pill" data-new>Start a new order</button></div>`;return}
 const b=bill(),f=S.f,pk=S.mode=="pickup";
 c.innerHTML=hd("Your cart")+`<div class="bd">${b?`<div class="meta">From ${b.r.n} · ${pk?"Pickup":"Delivery"}</div>`+b.ks.map(k=>`<div class="item"><div class="nm">${info(k).d[0]}<div class="meta">₹${info(k).d[1]}</div></div><div class="qty"><button data-q="${k}" data-s="-1" aria-label="Fewer">−</button>${S.cart[k]}<button data-q="${k}" data-s="1" aria-label="More">+</button></div></div>`).join(""):"<p>Your cart is empty. Pick a restaurant and add a dish.</p>"}</div>`+
 `<div class="ft">${b?`<div class="row"><span>Items</span><span>₹${b.sub}</span></div>${b.disc?`<div class="row ok"><span>Offer</span><span>−₹${b.disc}</span></div>`:b.r.p?`<div class="row meta"><span>${promo(b.r)}</span></div>`:""}<div class="row"><span>${pk?"Pickup":"Delivery"}</span><span>₹${b.f}</span></div><div class="row"><span>GST (5%)</span><span>₹${b.tax}</span></div><div class="row"><b>To pay</b><b>₹${b.total}</b></div><br>
 <input id="nm" placeholder="Your name" autocomplete="name" value="${f.nm||""}"><input id="ph" placeholder="Phone (10 digits)" inputmode="tel" autocomplete="tel" value="${f.ph||""}">${pk?"":`<input id="ad" placeholder="Delivery address" autocomplete="street-address" value="${f.ad??$("#loc").value}">`}
 <select id="py"><option value="Online"${f.py=="Online"?" selected":""}>Pay online</option><option value="Cash"${f.py=="Cash"?" selected":""}>${pk?"Pay at pickup":"Cash on delivery"}</option></select><button class="pay" id="pay">Place order · ₹${b.total}</button>`:""}</div>`}
async function place(){const b=bill(),nm=$("#nm").value.trim(),ph=$("#ph").value.trim(),ad=S.mode=="pickup"?"Pickup":($("#ad").value||"").trim();
 if(!nm||!/^\d{10}$/.test(ph)||!ad)return toast("Enter your name, a 10-digit phone number"+(S.mode=="pickup"?"":" and an address"));
 const o={restaurant:b.r.n,mode:S.mode,payment:$("#py").value,items:b.ks.map(k=>({name:info(k).d[0],price:info(k).d[1],qty:S.cart[k]})),discount:b.disc,total:b.total,customer:{name:nm,phone:ph,address:ad}};
 $("#pay").disabled=true;let id="DP"+Date.now().toString().slice(-6);
 try{if(API_URL){const r=await fetch(API_URL+"/orders",{method:"POST",headers:{"Content-Type":"application/json"},body:JSON.stringify(o)});if(!r.ok)throw 0;id=(await r.json()).orderId}
  S.track={id,restaurant:o.restaurant,total:o.total,mode:S.mode,at:Date.now()};S.step=0;S.cart={};S.f={};upd();clearInterval(timer);timer=setInterval(poll,4000)}
 catch(e){toast("Could not place the order. Check your connection and try again.");$("#pay").disabled=false}}
async function poll(){const t=S.track;if(!t)return;try{S.step=API_URL?(await(await fetch(API_URL+"/orders/"+t.id)).json()).step:Math.min(3,Math.floor((Date.now()-t.at)/25000))}catch(e){}cartUI();if(S.step>=3)clearInterval(timer)}
function nav(n){if(n=="home")reset();else if(n=="order"){cartUI();$("#cart").classList.add("open")}else{S[n]=S[n]?0:1;ui()}}
document.addEventListener("click",e=>{const t=e.target.closest("button");if(!t)return;const d=t.dataset;
 if(d.c){S.cat=d.c;ui()}else if(d.f){S[d.f]=S[d.f]?0:1;ui()}else if(d.n)nav(d.n);else if(d.m){S.mode=d.m;ui();cartUI()}
 else if("reset" in d)reset();else if(d.r)openRest(d.r);else if(d.add)add(+d.add);else if(d.close)$("#"+d.close).classList.remove("open");
 else if(d.q){S.cart[d.q]+=+d.s;if(S.cart[d.q]<1)delete S.cart[d.q];upd()}else if("new" in d){S.track=null;cartUI()}
 else if(t.id=="cartbtn"){cartUI();$("#cart").classList.add("open")}else if(t.id=="pay")place()});
document.addEventListener("change",e=>{if(e.target.id=="so"){S.sort=e.target.value;list()}});
document.addEventListener("input",e=>{const k={nm:"nm",ph:"ph",ad:"ad",py:"py"}[e.target.id];if(k)S.f[k]=e.target.value;if(e.target.id=="q")list()});
ui();cartUI();
