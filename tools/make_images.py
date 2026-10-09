"""Draws every picture in ../images as an original SVG food illustration.
Run:  python3 tools/make_images.py   (reads js/data.js, so new dishes get pictures too)"""
import json, math, os, random
H = os.path.dirname(os.path.abspath(__file__)); OUT = os.path.join(H, "..", "images")
def C(x,y,r,f,o=""): return f'<circle cx="{x:.1f}" cy="{y:.1f}" r="{r:.1f}" fill="{f}" {o}/>'
def E(x,y,a,b,f,o=""): return f'<ellipse cx="{x:.1f}" cy="{y:.1f}" rx="{a:.1f}" ry="{b:.1f}" fill="{f}" {o}/>'
def Rc(x,y,w,h,f,rx=0,o=""): return f'<rect x="{x:.1f}" y="{y:.1f}" width="{w:.1f}" height="{h:.1f}" rx="{rx:.1f}" fill="{f}" {o}/>'
def P(g,x,y,a,b):
    t=g.random()*6.283; d=g.random()**.5; return x+a*d*math.cos(t), y+b*d*math.sin(t)
def rot(g,px,py,lo=0,hi=180): return f'transform="rotate({g.randint(lo,hi)} {px:.1f} {py:.1f})"'
def plate(x,y,s,col="#fff"): return E(x+6*s,y+14*s,155*s,148*s,"#0004")+C(x,y,150*s,col)+C(x,y,128*s,"#f0efec")
def leaf(g,px,py,s,col="#2e7d32"): return E(px,py,12*s,6*s,col,rot(g,px,py))
def biryani(g,x,y,s):
    o=plate(x,y,s)+E(x,y+5*s,105*s,78*s,"#e3a02e")
    for _ in range(110):
        px,py=P(g,x,y+5*s,100*s,74*s); o+=C(px,py,g.uniform(2.5,6)*s,g.choice(["#fff2c4","#c5731d","#7a3a12","#3f8f3a","#e24b2b","#f6c85f"]))
    for dx in(-70,70): o+=E(x+dx*s,y+58*s,26*s,20*s,"#fff")+C(x+dx*s,y+58*s,10*s,"#f5b82e")
    for _ in range(5): o+=leaf(g,*P(g,x,y-20*s,70*s,40*s),s)
    return o
def dosa(g,x,y,s):
    o=plate(x,y,s)+f'<g transform="rotate(-18 {x} {y})">'+E(x,y,135*s,52*s,"#e1a23c")+E(x,y-8*s,128*s,40*s,"#ebb653")
    for _ in range(40): px,py=P(g,x,y,125*s,44*s); o+=C(px,py,g.uniform(2,5)*s,"#b9701f",'opacity=".6"')
    return o+"</g>"+C(x-95*s,y+88*s,28*s,"#fff")+C(x-95*s,y+88*s,20*s,"#cfe8b5")+C(x+95*s,y+92*s,28*s,"#fff")+C(x+95*s,y+92*s,20*s,"#d9532f")
def pizza(g,x,y,s):
    o=E(x+6*s,y+12*s,160*s,154*s,"#0004")+C(x,y,152*s,"#a9783f")+C(x,y,142*s,"#d9a45b")+C(x,y,124*s,"#c53b26")+C(x,y,118*s,"#f4c744")
    for _ in range(16): px,py=P(g,x,y,108*s,108*s); o+=C(px,py,g.uniform(8,12)*s,"#ffe58a",'opacity=".7"')
    for a in range(9):
        t=a*.698+.3; k=1 if a%2 else .75; px,py=x+68*s*k*math.cos(t),y+68*s*k*math.sin(t); o+=C(px,py,19*s,"#a82020")+C(px,py,13*s,"#c93a2f")
    for _ in range(8): o+=leaf(g,*P(g,x,y,95*s,95*s),s)
    for a in range(4):
        t=a*.785; c,n=142*s*math.cos(t),142*s*math.sin(t); o+=f'<line x1="{x-c:.1f}" y1="{y-n:.1f}" x2="{x+c:.1f}" y2="{y+n:.1f}" stroke="#fff" stroke-opacity=".35" stroke-width="2"/>'
    return o
def burger(g,x,y,s):
    o=E(x,y+82*s,125*s,18*s,"#0004")+Rc(x-100*s,y+42*s,200*s,36*s,"#d58b2c",18*s)+Rc(x-104*s,y+14*s,208*s,34*s,"#4e2713",16*s)
    o+=f'<polygon points="{x-100*s:.1f},{y+10*s:.1f} {x+100*s:.1f},{y+10*s:.1f} {x+60*s:.1f},{y+34*s:.1f} {x-60*s:.1f},{y+34*s:.1f}" fill="#f6c343"/>'+Rc(x-106*s,y-8*s,212*s,16*s,"#d93a2b",8*s)
    for i in range(9): o+=E(x-96*s+i*24*s,y-6*s,16*s,10*s,"#5aa83a")
    o+=f'<path d="M{x-104*s:.1f},{y-12*s:.1f} Q{x:.1f},{y-135*s:.1f} {x+104*s:.1f},{y-12*s:.1f} Z" fill="#e1963a"/>'
    for _ in range(18): px,py=P(g,x,y-60*s,70*s,28*s); o+=E(px,py,5*s,2.6*s,"#fff1c9",rot(g,px,py,-40,40))
    return o
def noodles(g,x,y,s):
    o=plate(x,y,s,"#fafaf8")+C(x,y,112*s,"#e0b05a")
    for _ in range(26):
        px,py=P(g,x,y,100*s,100*s); a=g.uniform(0,6.28); L=g.uniform(30,60)*s
        o+=f'<path d="M{px:.1f},{py:.1f} q{L*.5*math.cos(a):.1f},{-L*.6:.1f} {L*math.cos(a):.1f},{L*.2*math.sin(a):.1f}" stroke="#f4cf7d" stroke-width="{5*s:.1f}" fill="none" stroke-linecap="round"/>'
    for _ in range(50): px,py=P(g,x,y,104*s,104*s); o+=C(px,py,g.uniform(3,6)*s,g.choice(["#e8702a","#3f9a3a","#c62828","#5a2d17","#fff3c4"]))
    return o
def dessert(g,x,y,s):
    o=plate(x,y,s,"#f6efe2")+C(x,y,95*s,"#fff")+C(x,y,80*s,"#e9a53a",'opacity=".85"')
    for px,py in((-32,-22),(30,-26),(-4,24),(-46,28),(44,20)): o+=C(x+px*s,y+py*s,27*s,"#6b2a12")+C(x+(px-8)*s,y+(py-8)*s,8*s,"#a85a2c",'opacity=".7"')
    for _ in range(16): px,py=P(g,x,y,70*s,70*s); o+=C(px,py,3*s,g.choice(["#7cb342","#f6e27a"]))
    return o
def salad(g,x,y,s):
    o=plate(x,y,s)+C(x,y,118*s,"#7fb83f")
    for _ in range(55): px,py=P(g,x,y,108*s,108*s); o+=E(px,py,16*s,7*s,g.choice(["#5f9e2f","#8cc152","#a5d36a","#3f8a2a"]),rot(g,px,py))
    for _ in range(7): px,py=P(g,x,y,80*s,80*s); o+=C(px,py,14*s,"#e53935")+C(px-4*s,py-4*s,4*s,"#ff8a80")
    for _ in range(6): px,py=P(g,x,y,80*s,80*s); o+=C(px,py,15*s,"#c5e1a5")+C(px,py,10*s,"#e8f5e9")
    for _ in range(4): px,py=P(g,x,y,70*s,70*s); o+=E(px,py,20*s,11*s,"#cddc39")
    return o
def sushi(g,x,y,s):
    o=Rc(x-165*s,y-110*s,330*s,220*s,"#b8834d",18*s)+Rc(x-155*s,y-100*s,310*s,200*s,"#c99760",12*s)
    for i in range(6):
        cx=x+(i%3-1)*95*s; cy=y+(i//3-.5)*95*s-8*s
        o+=C(cx+3*s,cy+5*s,40*s,"#0003")+C(cx,cy,38*s,"#17212b")+C(cx,cy,31*s,"#fffdf5")+C(cx,cy,17*s,g.choice(["#ff7a45","#f06292","#7cb342","#ffb300"]))+C(cx,cy,7*s,"#fff",'opacity=".5"')
    return o+E(x+120*s,y+78*s,18*s,12*s,"#8bc34a")+E(x+85*s,y+86*s,22*s,10*s,"#f8a5b8")
def fries(g,x,y,s):
    o=E(x,y+96*s,100*s,14*s,"#0004")
    for i in range(22):
        px=x-70*s+i*6.5*s+g.uniform(-4,4)*s; h=g.uniform(70,110)*s
        o+=Rc(px,y-60*s-h*.5,12*s,h,g.choice(["#f3c43a","#f7d35a","#e6b02a"]),3*s,f'transform="rotate({g.uniform(-14,14):.1f} {px:.1f} {y:.1f})"')
    return o+f'<polygon points="{x-80*s:.1f},{y-10*s:.1f} {x+80*s:.1f},{y-10*s:.1f} {x+62*s:.1f},{y+95*s:.1f} {x-62*s:.1f},{y+95*s:.1f}" fill="#d62f2f"/>'+Rc(x-70*s,y+30*s,140*s,22*s,"#fff",0,'opacity=".9"')
def drink(g,x,y,s):
    col=g.choice(["#6b3f26","#f5a623","#9ccc65","#f48fb1","#ffe082"])
    o=E(x,y+100*s,70*s,12*s,"#0004")+f'<path d="M{x-60*s:.1f},{y-90*s:.1f} L{x+60*s:.1f},{y-90*s:.1f} L{x+44*s:.1f},{y+96*s:.1f} L{x-44*s:.1f},{y+96*s:.1f} Z" fill="#fff" fill-opacity=".35" stroke="#fff" stroke-opacity=".7" stroke-width="3"/>'
    o+=f'<path d="M{x-55*s:.1f},{y-60*s:.1f} L{x+55*s:.1f},{y-60*s:.1f} L{x+42*s:.1f},{y+92*s:.1f} L{x-42*s:.1f},{y+92*s:.1f} Z" fill="{col}"/>'
    o+=E(x,y-62*s,55*s,10*s,"#fff",'opacity=".85"')+Rc(x+10*s,y-150*s,10*s,110*s,"#e53935",4*s,f'transform="rotate(12 {x} {y})"')
    for _ in range(4): px,py=P(g,x,y,30*s,50*s); o+=Rc(px-10*s,py-10*s,20*s,20*s,"#fff",4*s,'opacity=".35"')
    return o
K=dict(biryani=biryani,dosa=dosa,pizza=pizza,burger=burger,noodles=noodles,dessert=dessert,salad=salad,sushi=sushi,fries=fries,drink=drink)
BG=[("#33463f","#1b2a25"),("#5a3a28","#2d1c12"),("#2b3d5c","#141f33"),("#6a2f2f","#331616"),("#e8e0cf","#cdbf9f"),("#d6e6dc","#a9c3b3"),("#4a2f5c","#22132e"),("#3f4a2b","#1d2412")]
def scene(kinds,pos,seed):
    g=random.Random(seed); a,b=BG[seed%8]
    o=f'<svg xmlns="http://www.w3.org/2000/svg" viewBox="0 0 600 400" width="600" height="400"><defs><radialGradient id="b" cx=".5" cy=".45" r=".75"><stop offset="0" stop-color="{a}"/><stop offset="1" stop-color="{b}"/></radialGradient></defs><rect width="600" height="400" fill="url(#b)"/>'
    for k,(x,y,s) in zip(kinds,pos): o+=K[k](g,x,y,s)
    return o+"</svg>"
def save(name,svg): open(os.path.join(OUT,name),"w").write(svg)
os.makedirs(OUT,exist_ok=True)
src=open(os.path.join(H,"..","js","data.js")).read(); R=json.loads(src[src.index("["):src.rindex("]")+1])
for r in R:
    save(f"r{r['id']}.svg",scene([r["k"]]+r["k2"],[(250,205,1.0),(478,125,.5),(488,292,.5)],r["id"]))
    for i,m in enumerate(r["m"]): save(f"{r['id']}-{i}.svg",scene([m[3]],[(300,200,1.25)],r["id"]*10+i))
for i,k in enumerate(["biryani","pizza","burger"],1): save(f"hero{i}.svg",scene([k],[(300,200,1.2)],i*3))
print("images:",len(os.listdir(OUT)))
