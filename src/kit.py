# SPDX-License-Identifier: MIT
# Pixel drawing kit. Adapted (MIT) from alwinecor/clawd-stickers dev-life/src/clawd_dev.py
#   https://github.com/alwinecor/clawd-stickers  — Copyright (c) 2026 alwinecor and contributors
#   which in turn adapts portions of Qisi3344/clawd-moji — Copyright (c) Qisi3344
# See LICENSE-THIRD-PARTY.md. 像素画工具：改编自上面两个 MIT 项目，原版权声明保留。

"""Crab: 15x16 body grid, colour #D77757, 1x2 black square eyes."""
import argparse, math, os, random
from PIL import Image, ImageDraw
S=12; W,H=23,24; OX,OY=4,7
BODY='#D77757'; K='#1a1a1a'; WH='#FFFFFF'; RED='#E5484D'; GOLD='#F2C14E'; INK='#3A3A44'
HERE=os.path.dirname(os.path.abspath(__file__))
DARK_MODE=False   # change it with set_dark(): a star import only copies the value
# Dark-background theme: colours that vanish or glare on a dark chat are swapped at draw time.
DARK={'#3A3A44':'#E6E1DA',   # text / outlines
      '#D9D2CB':'#3A3A42',   # ground shadow, dust
      '#CFC8C0':'#8F8A84',   # speed lines, smoke
      '#3A3A48':'#6A6A7A'}   # terminal frame
def tc(c): return DARK.get(c.upper(),c) if DARK_MODE and isinstance(c,str) else c
def set_dark(on):
    global DARK_MODE; DARK_MODE=on

# ---------- shared helpers, adapted from Qisi3344/clawd-moji 01-movie-night ----------
def rect(x0,y0,x1,y1): return [(x,y) for x in range(x0,x1+1) for y in range(y0,y1+1)]
def put(p,pts,c,dy=0):
    for x,y in pts: p[(x,y+dy)]=c
def clear(p,pts,dy=0):
    for x,y in pts: p.pop((x,y+dy),None)
UP=rect(0,7,1,8); MID=rect(0,8,1,9); DOWN=rect(0,9,1,10)
def mirror(pts): return [(14-x,y) for x,y in pts]
def base(arms_=True):
    p={}
    for x in range(2,13):
        for y in range(6,13): p[(x,y)]=BODY
    if arms_: put(p,DOWN+mirror(DOWN),BODY)
    for x in (3,5,9,11):
        for y in (13,14): p[(x,y)]=BODY
    for x in (4,10):
        for y in (8,9): p[(x,y)]=K
    return p
def arms(p,left=DOWN,right=DOWN):
    clear(p,rect(0,7,1,10)+rect(13,7,14,10))
    put(p,left,BODY); put(p,mirror(right),BODY); return p
def flap(p,f): return arms(p,UP if f else MID,MID if f else UP)
TAU=2*math.pi; M=6
def clamp(x,a=0,b=1): return max(a,min(b,x))
def ease(t): t=clamp(t); return 0.5-0.5*math.cos(math.pi*t)
def lerp(a,b,t): return a+(b-a)*t
def kf(i,keys):
    if i<=keys[0][0]: return keys[0][1]
    for (a,va),(b,vb) in zip(keys,keys[1:]):
        if a<=i<=b: return va+(vb-va)*ease((i-a)/(b-a))
    return keys[-1][1]
def face(p,mode='n',dx=0,ey=0,blink=False):
    for x in range(2,13):
        for y in range(6,12):
            if p.get((x,y))==K: p[(x,y)]=BODY
    if mode=='n':
        for x in (4,10):
            for y in ((9,) if blink else (8,9)): p[(x+dx,y+ey)]=K
    elif mode=='hap':
        for ex in (4,10): put(p,[(ex-1+dx,9+ey),(ex+dx,8+ey),(ex+1+dx,9+ey)],K)
    else:  # '> <'
        put(p,[(3,7),(4,8),(3,9),(11,7),(10,8),(11,9)],K)
    return p
def canvas(pad=0): return Image.new('RGBA',((W+2*pad)*S,(H+2*pad)*S),(0,0,0,0))
def draw(img,p,pad=0):
    d=ImageDraw.Draw(img)
    for (x,y),c in p.items():
        X,Y=x+OX+pad,y+OY+pad
        if 0<=X<W+2*pad and 0<=Y<H+2*pad: d.rectangle([X*S,Y*S,(X+1)*S-1,(Y+1)*S-1],fill=tc(c))
    return img
def xform(p,dx=0,dy=0,sx=1,sy=1,rot=0,piv=(7.5,15)):
    img=draw(canvas(M),p,M)
    Px,Py=(piv[0]+OX+M)*S,(piv[1]+OY+M)*S; Tx,Ty=dx*S,dy*S
    a=math.radians(rot); c,s=math.cos(a),math.sin(a)
    co=(c/sx,-s/sx,Px-(c*(Px+Tx)-s*(Py+Ty))/sx, s/sy,c/sy,Py-(s*(Px+Tx)+c*(Py+Ty))/sy)
    out=img.transform(img.size,Image.AFFINE,co,resample=Image.NEAREST)
    return out.crop((M*S,M*S,(M+W)*S,(M+H)*S))
def squash(v): return dict(sy=v,sx=1/math.sqrt(v))
def hold(fr,ms):
    """Change how long frames stay on screen: {frame index: ms}."""
    for k,d in ms.items(): fr[k]=(fr[k][0],d)
def render(p,cs,ax,ay,rot=0,sx=1,sy=1):
    """Draw at any cell size cs; (ax,ay) in px is where the feet centre (7.5,15) lands."""
    img=canvas(); d=ImageDraw.Draw(img)
    for (x,y),c in p.items():
        X=math.floor(ax+(x-7.5)*cs+0.5); Y=math.floor(ay+(y-15)*cs+0.5)
        d.rectangle([X,Y,X+cs-1,Y+cs-1],fill=tc(c))
    if rot or sx!=1 or sy!=1:
        a=math.radians(rot); c,s_=math.cos(a),math.sin(a)
        co=(c/sx,-s_/sx,ax-(c*ax-s_*ay)/sx, s_/sy,c/sy,ay-(s_*ax+c*ay)/sy)
        img=img.transform(img.size,Image.AFFINE,co,resample=Image.NEAREST)
    return img
def shadow(h=0,y=15,col='#D9D2CB'):
    w=9-4*clamp(h/3.5); x0=round(7.5-w/2); x1=round(7.5+w/2)-1
    return {(x,y):col for x in range(x0,x1+1)}
def comp(*layers):
    out=canvas()
    for L in layers:
        if L is None: continue
        if isinstance(L,dict): L=draw(canvas(),L)
        out.alpha_composite(L)
    return out
def bang(x,y): return {(x,y):RED,(x,y+1):RED,(x,y+2):RED,(x,y+4):RED}
QMARK=[(6,-2),(7,-3),(8,-3),(9,-2),(9,-1),(8,0),(8,1),(8,3)]
def cx(x): return (x+OX)*S   # scene cell -> px
def cy(y): return (y+OY)*S
MIDX,FOOT=W*S//2,cy(15)   # px: horizontal centre, ground under the feet

# ---------- tiny pixel font (3x5, row 5 = descender) ----------
GL={
 'a':["...","xx.","..x",".xx","xxx"], 'c':["...",".xx","x..","x..",".xx"],
 'e':["...",".x.","xxx","x..",".xx"], 'f':["..x",".x.","xxx",".x.",".x."],
 'g':["...",".xx","x.x",".xx","..x","xx."], 'i':["x",".","x","x","x"],
 'l':["x.","x.","x.","x.",".x"], 'm':[".....","xx.x.","x.x.x","x.x.x","x.x.x"],
 'n':["...","xx.","x.x","x.x","x.x"], 'o':["...",".x.","x.x","x.x",".x."],
 'p':["...","xx.","x.x","x.x","xx.","x.."], 'r':["...",".xx","x..","x..","x.."],
 't':[".x.","xxx",".x.",".x.","..x"], '-':["...","...","xxx","...","..."],
 '/':["..x","..x",".x.","x..","x.."], '>':["x..",".x.","..x",".x.","x.."],
 '<':["..x",".x.","x..",".x.","..x"], '=':["...","xxx","...","xxx","..."],
 '_':["...","...","...","...","xxx"], ' ':["..",".."],
 'b':["x..","xx.","x.x","x.x","xx."], 'd':["..x",".xx","x.x","x.x",".xx"],
 'h':["x..","xx.","x.x","x.x","x.x"], 'k':["x..","x.x","xx.","xx.","x.x"],
 's':["...",".xx","x..","..x","xx."], 'u':["...","x.x","x.x","x.x",".xx"],
 'w':[".....","x...x","x.x.x","x.x.x",".x.x."], 'y':["...","x.x","x.x",".xx","..x","xx."],
 'z':["...","xxx","..x",".x.","xxx"], ',':[".",".",".","x","x"],
 '(':[".x","x.","x.","x.",".x"], ')':["x.",".x",".x",".x","x."],
 ':':[".","x",".","x","."], '!':["x","x","x",".","x"],
 'E':["xxx","x..","xx.","x..","xxx"], 'L':["x..","x..","x..","x..","xxx"],
 'G':[".xx","x..","x.x","x.x",".xx"], 'T':["xxx",".x.",".x.",".x.",".x."],
 'M':["x...x","xx.xx","x.x.x","x...x","x...x"],
 '0':["xxx","x.x","x.x","x.x","xxx"], '1':[".x.","xx.",".x.",".x.","xxx"],
 '2':["xx.","..x",".x.","x..","xxx"], '3':["xx.","..x",".x.","..x","xx."],
 '4':["x.x","x.x","xxx","..x","..x"], '5':["xxx","x..","xx.","..x","xx."],
 '6':[".xx","x..","xx.","x.x",".x."], '7':["xxx","..x",".x.",".x.",".x."],
 '8':["xxx","x.x","xxx","x.x","xxx"], '9':["xxx","x.x","xxx","..x","xx."],
 '.':[".",".",".",".","x"], '?':["xx.","..x",".x.","...",".x."], "'":["x","x",".",".","."],
 'B':["xx.","x.x","xx.","x.x","xx."],
 'H':["x.x","x.x","xxx","x.x","x.x"], 'R':["xx.","x.x","xx.","x.x","x.x"], 'v':["...","x.x","x.x","x.x",".x."], 'A':[".x.","x.x","xxx","x.x","x.x"],
 'N':["x..x","xx.x","x.xx","x..x","x..x"], 'D':["xx.","x.x","x.x","x.x","xx."],
 'Y':["x.x","x.x",".x.",".x.",".x."], 'x':["...","x.x",".x.",".x.","x.x"],
}
def mix(c1,c2,t):
    a=[int(c1[k:k+2],16) for k in (1,3,5)]; b=[int(c2[k:k+2],16) for k in (1,3,5)]
    return '#'+''.join(f'{round(x+(y-x)*t):02X}' for x,y in zip(a,b))
def run_legs(p,f):
    """Alternate leg pairs for a running cycle; f is 0 or 1."""
    clear(p,rect(3,13,11,14))
    for x in ((3,9) if f else (5,11)): put(p,[(x,13)],BODY)
    for x in ((5,11) if f else (3,9)): put(p,[(x,13),(x,14)],BODY)
    return p
def term(img,x0,y0,x1,y1):
    box(img,x0,y0,x1,y1,'#3A3A48'); box(img,x0+4,y0+4,x1-4,y1-4,'#1E1E26')
def textc(img,s,mid,y,px,col): return text(img,s,round(mid-text_w(s)*px/2),y,px,col)
def spr(rows,x0,y0,pal):
    """Cell sprite from strings; chars not in pal are transparent."""
    return {(x0+k,y0+r):pal[ch] for r,row in enumerate(rows) for k,ch in enumerate(row) if ch in pal}
def confetti(i,start,n=16,seed=3):
    rng=random.Random(seed); fx={}; cols=[GOLD,RED,'#3B82F6','#2FB15A','#C77DFF']
    for k in range(n):
        x0=rng.uniform(-4,18); v=rng.uniform(0.5,0.9); ph=rng.uniform(0,6); c=cols[k%5]
        t=i-start-rng.uniform(0,8)
        if t<0: continue
        y=-7+t*v
        if y<16: fx[(round(x0+math.sin(t*0.5+ph)),round(y))]=c
    return fx
def text_w(s): return sum(len(GL[c][0])+1 for c in s)-1
def text(img,s,x,y,px,col):
    """Draw s with its top-left at (x,y) px, each font pixel px wide."""
    d=ImageDraw.Draw(img); col=tc(col)
    for c in s:
        g=GL[c]
        for r,row in enumerate(g):
            for k,ch in enumerate(row):
                if ch=='x': d.rectangle([x+k*px,y+r*px,x+(k+1)*px-1,y+(r+1)*px-1],fill=col)
        x+=(len(g[0])+1)*px
    return x
def box(img,x0,y0,x1,y1,col):
    if round(x1)<=round(x0) or round(y1)<=round(y0): return
    ImageDraw.Draw(img).rectangle([round(x0),round(y0),round(x1)-1,round(y1)-1],fill=tc(col))

def to_gif(frames,path):
    gf=[]
    for im,_ in frames:
        a=im.split()[3]; pal=im.convert('RGB').convert('P',palette=Image.ADAPTIVE,colors=255)
        pal.paste(255,a.point(lambda v:255 if v<128 else 0)); gf.append(pal)
    gf[0].save(path,save_all=True,append_images=gf[1:],duration=[d for _,d in frames],loop=0,transparency=255,disposal=2)
    return os.path.getsize(path)
def square(frames):
    """Pad the 276x288 drawing canvas to 288x288, centered horizontally."""
    sq=[]
    for im,d in frames:
        c=Image.new('RGBA',(H*S,H*S),(0,0,0,0)); c.paste(im,((H*S-W*S)//2,0)); sq.append((c,d))
    return sq
def save(nm,fr):
    out=os.path.join(HERE,'..','out-dark' if DARK_MODE else 'out')
    os.makedirs(out,exist_ok=True)
    fr=square(fr)
    n=to_gif(fr,os.path.join(out,nm+'.gif'))
    print(f'{nm}: {len(fr)} frames, {n//1024}KB')
