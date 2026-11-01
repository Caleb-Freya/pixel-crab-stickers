# SPDX-License-Identifier: MIT
# 情侣日常 · 49 张像素小螃蟹动态表情。基于 kit.py（改编自 MIT 项目 alwinecor/clawd-stickers）。
# 用法：python love.py [中文名...] [--dark]   浅色 -> ../out/，深色 -> ../out-dark/
import argparse, math, os, random
from PIL import Image, ImageDraw, ImageFont
from kit import *
import kit

PINK='#F59AA6'; HRT='#FF5C7C'; TEAR='#6CB4EE'; CREAM='#FFF3DC'; BROWN='#5A3A22'
YEL='#FFD43B'; SMK='#CFC8C0'; ARM2='#B85C3F'; PURP='#8E6BBF'; GRN='#4CAF6A'
FONT="/usr/share/fonts/truetype/wqy/wqy-zenhei.ttc"

# ---------- 粗格子小图 ----------
H3=["x.x","xxx",".x."]
H5=[".x.x.","xxxxx",".xxx.","..x.."]
H7=[".xx.xx.","xxxxxxx","xxxxxxx",".xxxxx.","..xxx.."]
STAR=["..x..","..x..","xxxxx",".xxx.",".x.x."]
SPARK=[".x.","xxx",".x."]
NOTE=["..xx","..x.","..x.",".xx.",".xx."]
ANG=["xx..xx","x....x","......","x....x","xx..xx"]
QM=[".xxx.","x...x","....x","...x.","..x..",".....","..x.."]
DROP=["x","x"]
BUB=["..xxxxxxx..",".xwwwwwwwx.","xwwwwwwwwwx","xwwwwwwwwwx","xwwwwwwwwwx",".xwwwwwwwx.","..xxxxxxx.."]
BPAL={'x':INK,'w':'#FFFFFF'}

def wave(i,T): return math.sin(TAU*i/T)
def bk(i,T=36,at=30): return (i%T) in (at,at+1)
def mk(N,f,ms=70,hd=None):
    fr=[(f(i),ms) for i in range(N)]
    if hd: hold(fr,hd)
    return fr
def sc(p,dx=0,dy=0,rot=0,sq=None,fx=None,back=None,front=None,sh=True,piv=(7.5,15)):
    return comp(shadow(max(0,-dy)) if sh else None,back,xform(p,dx,dy,rot=rot,piv=piv,**(sq or {})),fx,front)
def shut(p):
    face(p,'n'); put(p,[(4,8),(4,9),(10,8),(10,9)],BODY); put(p,[(3,9),(4,9),(10,9),(11,9)],K); return p
def blush(p): put(p,[(3,10),(11,10)],PINK); return p
def heart_eyes(p):
    face(p,'n'); put(p,[(4,8),(4,9),(10,8),(10,9)],BODY)
    p.update(spr(H3,3,7,{'x':HRT})); p.update(spr(H3,9,7,{'x':HRT})); return p
def star_eyes(p,big=True):
    face(p,'n'); put(p,[(4,8),(4,9),(10,8),(10,9)],BODY)
    pat=["..k..",".kxk.","kxwxk",".kxk.","..k.."] if big else [".....","..k..",".kwk.","..k..","....."]
    for ex in (2,8): p.update(spr(pat,ex,6,{'x':'#FFD21F','w':'#FFFFFF','k':K}))
    return p
def bubble(x,y): return spr(BUB,x,y,BPAL)
def cut(rows,x,y,col): return spr(rows,x,y,{'x':col})
def hrt(w): return {3:H3,5:H5,7:H7}[w]
def floaty(i,start,x,y0,rise=14,span=30,col=HRT,sizes=(3,5,5)):
    """从 start 帧起，一颗心从 (x,y0) 往上飘 span 帧，边飘边晃。"""
    t=(i-start)/span
    if not 0<=t<1: return {}
    w=sizes[min(len(sizes)-1,int(t*len(sizes)))]
    return cut(hrt(w),round(x+1.2*math.sin(t*7)),round(y0-t*rise),col)

# ---------- 举牌：米白底深棕边，中文大字 ----------
_FC={}
def _mask(s,w,h,fs):
    k=(s,w,h,fs)
    if k not in _FC:
        m=Image.new('L',(w,h),0); ImageDraw.Draw(m).text((w//2,h//2),s,font=ImageFont.truetype(FONT,fs),fill=255,anchor='mm')
        _FC[k]=m.point(lambda v:255 if v>110 else 0)
    return _FC[k]
def sign(s,dxp=0,dyp=0,rot=0,cols=15,rows=7,x0=0,y0=-2):
    """整块牌子贴格子画：1 格深棕边，里面米白底，字按大像素取样。牌子下沿正好压在举起的手上。"""
    lay=canvas(); d=ImageDraw.Draw(lay); X,Y=cx(x0),cy(y0)
    d.rectangle([X,Y,X+cols*S-1,Y+rows*S-1],fill=BROWN); d.rectangle([X+S,Y+S,X+(cols-1)*S-1,Y+(rows-1)*S-1],fill=CREAM)
    iw,ih=(cols-2)*S,(rows-2)*S; fs=min(ih-4,(iw-8)//len(s)); m=_mask(s,iw,ih,fs)
    lay.paste(Image.new('RGBA',(iw,ih),BROWN),(X+S,Y+S),m)
    if rot: lay=lay.rotate(rot,resample=Image.NEAREST,center=(X+cols*S//2,Y+rows*S))
    if dxp or dyp: lay=lay.transform(lay.size,Image.AFFINE,(1,0,-dxp,0,1,-dyp),resample=Image.NEAREST)
    return lay
def hold_arms(p): return arms(p,rect(0,5,1,6),rect(0,5,1,6))

# ================= 1-10 =================
def 想你():
    def f(i):
        p=base(); face(p,'n',ey=-1,blink=bk(i,30,27))
        bob=round(0.5+0.5*wave(i,24)); w=[7,7,5,5,5,5,3,3,5,5,5,5,5,5,5,5][i%16]
        fx=bubble(2,-6+bob); fx.update({(7,2):INK,(6,4):INK})
        fx.update(cut(hrt(w),7-w//2,-3+bob-(2 if w==7 else 1),HRT))
        return sc(p,rot=2*wave(i,48),fx=fx)
    return mk(48,f,70)
def 贴贴():
    def f(i):
        cs=round(kf(i,[(0,12),(8,12),(20,17),(38,17),(48,12)]))
        sx=kf(i,[(18,1),(23,1.12),(36,1.12),(41,1)]); sy=kf(i,[(18,1),(23,.82),(36,.82),(41,1)])
        p=base(); touch=22<=i<39
        if touch: shut(p); blush(p); arms(p,UP,UP)
        else: face(p,'n',blink=(i in (4,5)))
        ay=264+(cs-12)
        fx={}
        if touch:
            for k,(x,y) in enumerate([(-3,4),(17,5),(-2,-1),(16,-2),(7,-3)]):
                q=(i+k*5)%16
                if q<12: fx.update(cut(H5 if k%2 else H3,x,y-q//3,HRT))
        return comp(shadow() if cs==12 else None,render(p,cs,MIDX,ay,sx=sx,sy=sy),fx)
    return mk(52,f,70,{22:200})
def 抱抱():
    OPEN=[(1,8),(0,7),(-1,6),(-2,5),(1,7),(0,6),(-1,5),(-2,4)]
    def f(i):
        p=base(); fx={}; closed=i>=26
        hx=kf(i,[(6,19),(26,6)]) if i<28 else 6
        if i<26: face(p,'n',dx=1 if i<22 else 0,blink=bk(i,40,35))
        else: face(p,'hap')
        if i<26:
            o=2 if (i//4)%2 else 1 if i>=4 else 0
            L=[(x+(o if k>=4 else 0)*0,y) for k,(x,y) in enumerate(OPEN)]
            arms(p,[(x,y+(1 if (i//5)%2 else 0)) for x,y in OPEN],[(x,y+(1 if (i//5)%2 else 0)) for x,y in OPEN])
        else:
            arms(p,[],[]); put(p,rect(0,10,4,11)+rect(10,10,14,11),ARM2)
        if i<28: fx.update(cut(H5,round(hx),9 if i>=22 else 8,HRT))
        elif i<38: fx.update(cut(H5,5,9,HRT))
        sq=squash(kf(i,[(26,1),(29,.88),(33,1)]))
        if i>=34:
            for k,(x,y) in enumerate([(-1,2),(15,0),(7,-3)]):
                q=(i-34+k*4)%20
                if q<14: fx.update(cut(H3 if k!=2 else H5,x,y-q//2,HRT))
        return sc(p,rot=2*wave(i,40) if i<26 else 0,sq=sq,fx=fx)
    return mk(54,f,70,{27:160})
def 蹭蹭():
    PIL_={'x':'#F77FA0','h':'#FFB3C6','d':'#D95F82'}
    PIL=[".xxxx.xxxx.","xhhxxxxxxxx","xhxxxxxxxxx","xxxxxxxxxxx",".xxxxxxxxxd","..xxxxxxxdd","...xxxxxdd.","....xxxdd..",".....xdd...."][:9]
    PIL=[r[:11].ljust(11,'.') for r in PIL]
    def f(i):
        p=base(); shut(p); arms(p,UP,MID)
        dy=-1.6*(0.5-0.5*math.cos(TAU*i/24)); rot=7+2*wave(i,24)
        back=draw(canvas(),spr(PIL,7,5,PIL_))
        fx={}
        for k,(x,y) in enumerate([(14,0),(17,3)]):
            q=(i+k*9)%24
            if q<16: fx.update(cut(H3,x,y-q//4,HRT))
        return comp(shadow(),back,xform(p,-3,dy,rot=rot),fx)
    return mk(48,f,70)
def 亲亲():
    def f(i):
        p=base(); shut(p); blush(p); arms(p,MID,MID)
        t=(i%30)/30; lean=kf(i%30,[(0,0),(6,1),(10,1),(16,0)]); sq={}
        fx={}
        if 8<=i%30:
            q=(i%30-8); w=3 if q<5 else 5 if q<14 else 7
            fx=cut(hrt(w),round(13+q*0.3),round(4-q*0.45),HRT)
        return sc(p,dx=lean,rot=4*lean,fx=fx,sq=squash(1-0.05*lean))
    return mk(60,f,70)
def 哄你():
    def f(i):
        p=base(); face(p,'hap'); blush(p); hold_arms(p)
        up=kf(i,[(0,6),(8,0)]); sw=wave(i,24) if i>8 else 0
        sh=3*sw
        p2=dict(p); fx={}
        s=sign('乖乖',dxp=round(sw*12),dyp=round(up*12),rot=-sw*8)
        for k,(x,y) in enumerate([(-3,5),(17,3)]):
            q=(i+k*7)%20
            if i>10 and q<14: fx.update(cut(H3,x,y-q//2,HRT))
        return comp(shadow(),xform(p,sh/2,-up*0,rot=sw*3),s,fx)
    return mk(48,f,70)
def 吃醋():
    def f(i):
        p=base(); puff=kf(i,[(0,0),(12,0),(22,1),(34,1),(44,0)]); fx={}
        face(p,'n',dx=1 if 4<=i<40 else 0,blink=(i in (46,47))); 
        if 4<=i<40: arms(p,MID,MID)
        if 2<=i<18: fx.update(cut(H3,round(kf(i,[(2,20),(18,15)])),round(7+wave(i,10)),PINK))
        if 20<=i<42:
            for k in range(3):
                q=(i*1+k*5)%12
                fx[(4+k*3+round(math.sin(q*.9+k)),4-q)]='#9ACD32'
            fx.update(cut(ANG,11,-1,RED) if (i//3)%2 else {})
        sx=1+0.1*puff; sy=1+0.06*puff
        return sc(p,rot=-3*puff,sq=dict(sx=sx,sy=sy),fx=fx)
    return mk(48,f,70)
def 委屈():
    def f(i):
        p=base(); face(p,'n',ey=1,dx=0); arms(p,MID,MID); fx={}
        sh=kf(i,[(0,0),(10,1),(40,1),(50,0)])
        w=round(kf(i,[(0,0),(14,1),(40,2),(50,2)]))
        for x in (4,10):
            put(p,[(x,10)] if w>=1 else [],TEAR); put(p,[(x-1,10),(x+1,10)] if w>=2 else [],TEAR)
        if i>=18:
            q=(i-18)%24
            if q<16: fx[(14,4+q//2)]=TEAR; fx[(14,5+q//2)]=TEAR
        sq=dict(sx=1-0.04*sh,sy=1-0.08*sh)
        return sc(p,dx=0.25*math.sin(i*2.4)*(i>10),sq=sq,fx=fx)
    return mk(50,f,70)
def 哭():
    def f(i):
        p=base(); face(p,'x'); arms(p,MID,MID); fx={}
        for k,x in enumerate((3,11)):
            for j in range(3):
                q=(i*2+j*5+k*3)%16
                if q<5: fx[(x,10+q)]=TEAR; fx[(x,11+q)]=TEAR
        for j in range(4):
            q=(i*2+j*4)%16
            if q<6: fx[(3-q//3,10+q)]=TEAR; fx[(11+q//3,10+q)]=TEAR
        pw=round(kf(i,[(0,1),(48,6)]))
        for x in range(7-pw,8+pw): fx[(x,15)]=TEAR
        return sc(p,dx=0.4*math.sin(i*3.3),dy=-0.2*abs(wave(i,6)),sh=False,fx=fx,front=None) if False else comp(sc(p,dx=0.4*math.sin(i*3.3),sh=False),draw(canvas(),fx))
    return mk(48,f,70)
def 生气():
    def f(i):
        p=base(); face(p,'x'); fx={}
        flap(p,(i//2)%2); 
        for k in range(3):
            q=(i+k*7)%20
            if q<16:
                c=SMK; x=6+k*3+round(math.sin(q*.5+k)*1.2); y=4-q//2
                fx.update(cut(["xx","xx"],x,y,c))
        if (i//3)%2==0: fx.update(cut(ANG,12,-2,RED))
        return sc(p,dx=0.5*math.sin(i*4.1),dy=-0.5*abs(wave(i,8)),fx=fx)
    return mk(40,f,60)

# ================= 11-20 =================
SLASH=["..x",".x.","x.."]
def 害羞():
    def f(i):
        p=base(); sh=kf(i,[(0,0),(10,1),(46,1),(56,0)]); fx={}
        peek=30<=i<37
        face(p,'n',dx=1 if peek else -1,blink=(i in (44,45)))
        if i>=6: blush(p)
        arms(p,MID,MID) if (i//8)%2 else arms(p,DOWN,MID)
        if i>=12 and (i//3)%4:
            for k in range(3): fx.update(cut(SLASH,12+2*k,2,PINK))
        return sc(p,dx=-0.3*sh+0.2*wave(i,10)*sh,dy=0.3*sh,sq=squash(1-0.09*sh),fx=fx)
    return mk(56,f,70)
def 捂眼睛():
    def f(i):
        p=base(); fx={}; flinch=i>=10
        if not flinch: face(p,'n',dx=1)
        else: face(p,'x'); arms(p,MID,MID)
        if 2<=i<12: fx.update(bang(16,0))
        if flinch:
            for k in range(3):
                q=(i+k*2)%6
                fx.update(cut(["x","x","x"] if q<4 else ["x","x"],14+2*k,4+k%2*2,SMK))
        t=kf(i,[(8,0),(13,1)])
        return sc(p,dx=-1.5*t+0.35*math.sin(i*3.7)*(flinch),rot=-12*t,dy=-0.8*max(0,1-abs(i-10)/2),fx=fx)
    return mk(44,f,70)
def 星星眼():
    def f(i):
        p=base(); star_eyes(p,(i//3)%4!=3); fx={}
        t=(i%16)/16; hop=abs(math.sin(math.pi*t))*3.0
        arms(p,UP,UP) if hop>1 else arms(p,MID,MID)
        sq=squash(0.9) if t<0.08 or t>0.92 else {}
        for k,(x,y) in enumerate([(-2,3),(16,2),(0,-3),(15,-4)]):
            if (i+k*3)%8<5: fx.update(cut(SPARK,x,y,YEL))
        return sc(p,dy=-hop,sq=sq,fx=fx)
    return mk(48,f,60)
def 开心():
    def f(i):
        p=base(); face(p,'hap'); fx={}
        t=(i%14)/14; hop=abs(math.sin(math.pi*t))*3.0
        arms(p,UP,UP) if (i//2)%2 else arms(p,MID,MID)
        sq=squash(0.9) if t<0.1 else {}
        if 0.2<t<0.8:
            fx.update(cut(STAR,-3,0,YEL)); fx.update(cut(STAR,16,0,YEL)); fx.update(cut(SPARK,7,-5,YEL) if (i//2)%2 else {})
        return sc(p,dy=-hop,sq=sq,fx=fx)
    return mk(42,f,60)
SUN=["..xxx..",".xxxxx.","xxxxxxx","xxxxxxx","xxxxxxx",".xxxxx.","..xxx.."]
def 早安():
    def f(i):
        p=base(); sunY=kf(i,[(0,14),(30,-5)]); fx={}
        st=kf(i,[(10,0),(22,1),(34,1),(42,0)])
        if i<10: shut(p); arms(p,DOWN,DOWN)
        elif i<34: face(p,'x') if 14<=i<26 else shut(p); arms(p,UP,UP) if st>.5 else arms(p,MID,MID)
        else: face(p,'hap'); arms(p,UP if (i//4)%2 else MID,DOWN)
        if i>=34: pass
        sun={k:v for k,v in cut(SUN,12,round(sunY),'#FFB703').items() if k[1]<6}
        rays={}
        if i>=28:
            for (x,y) in [(15,-7),(11,-5),(19,-5),(11,-1),(19,-1),(15,3)]:
                if (i//3)%2: rays[(x,y)]='#FFB703'
        ground=cut(["x"*17],-1,15,'#D9D2CB')
        return comp(draw(canvas(),sun),draw(canvas(),rays),None,shadow(),xform(p,0,0,sx=1-0.05*st,sy=1+0.12*st))
    return mk(52,f,70,{-1:400})
def 晚安():
    BL={'x':'#B39DDB','d':'#8E7CC3','s':'#FFF3DC'}
    BLK=["xxxxxxxxxxxxx","xxsxxxxxsxxxx","xxxxxsxxxxxxx","xxxxxxxxxxxsx","dddddddddddd d"]
    BLK=[r.replace(' ','d') for r in BLK]
    MOON=["..xx.",".xx..","xx...","xx...",".xx..","..xx."]
    def f(i):
        p=base(); shut(p); arms(p,MID,MID)
        br=0.5+0.5*wave(i,40); sy=1-0.04*br
        fx=cut(MOON,-3,-5,YEL); fx.update(cut(SPARK,15,-5,YEL) if (i//6)%2 else {})
        img=canvas()
        for k in range(3):
            a=(i+k*20)%60; t=a/60
            text(img,'z',round(cx(14)+t*24),round(cy(3)-t*100),[3,4,5,6][min(3,int(t*4))],'#7C8FD9')
        blk=draw(canvas(),spr(BLK,1,10,BL)); 
        blk2=draw(canvas(),{k:v for k,v in spr(BLK,1,10,BL).items()})
        return comp(shadow(),xform(p,0,0,sy=sy),blk,draw(canvas(),fx),img)
    return mk(60,f,90)
def 熬夜():
    MOON=["..xx.",".xx..","xx...","xx...",".xx..","..xx."]
    def f(i):
        p=base(); c=i%30; fx=cut(MOON,-3,-5,YEL)
        if c<12: face(p,'n',blink=True)
        elif c<15: face(p,'n'); put(p,[(4,7),(10,7)],K)
        elif c<25: face(p,'n',blink=True)
        else: shut(p)
        put(p,[(3,10),(4,10),(5,10),(9,10),(10,10),(11,10)],PURP)
        rot=kf(c,[(0,0),(11,13),(12,0),(15,0),(24,12),(25,12),(29,0)]); dy=0.04*rot
        if 12<=c<17: fx.update(bang(16,0))
        return sc(p,rot=rot,dy=dy,fx=fx,sq=squash(1-0.01*rot))
    return mk(60,f,70)
WM=["rrrrrrrrrrr","rrkrrrrrkrr","rrrrrkrrrrr","wrrrrrrrrrw","gwwwwwwwwwg",".ggggggggg.","...ggggg..."]
WPAL={'r':'#F2536B','k':'#2B2B2B','w':'#E8F5D8','g':'#3E9B4F'}
def 吃瓜():
    BITES=[(12,10,2.9),(1,10,2.9),(7,10,3.4)]
    def f(i):
        c=i%60; k=i//60
        nb=0 if c<14 else 1 if c<30 else 2 if c<46 else 3
        p=base(); look=-1 if (c%20)<10 else 1
        chew=(14<=c<20) or (30<=c<36) or (46<=c<52)
        if chew: face(p,'hap')
        else: face(p,'n',dx=look,blink=bk(c,30,26))
        arms(p,MID,MID)
        m=spr(WM,2,10,WPAL)
        for (bx,by,r) in BITES[:nb]:
            for (x,y) in list(m):
                if (x-bx)**2+(y-by)**2<=r*r: m.pop((x,y))
        # 吃完最后一口换新
        fx={}
        if c in (14,30,46) and False: pass
        for j,s0 in enumerate((14,30,46)):
            q=c-s0-2
            if 0<=q<8: fx[(8+q,9-round(q*0.8)+round(q*q*0.12))]=K
        dy=0.5 if 11<=c<14 or 27<=c<30 or 43<=c<46 else 0
        return comp(shadow(),xform(p,0,dy+(-0.3*abs(wave(c,6)) if chew else 0)),draw(canvas(),m),draw(canvas(),fx))
    return mk(60,f,80)
def 无语():
    def f(i):
        c=i%48; p=base(); face(p,'n',blink=True) if c<40 else face(p,'n'); fx={}
        for k,s0 in enumerate((6,13,20)):
            if s0<=c<42: fx.update(cut(["xx","xx"],5+k*3,1,INK))
        if c>=10:
            q=(c-10)%20
            if c<42 and q<14: fx.update(cut(DROP,13,5+q//2,TEAR) if False else {(14,4+q//2):TEAR,(14,5+q//2):TEAR})
        return sc(p,dy=0.3*(c>=6),sq=squash(0.97 if c>=6 else 1),fx=fx)
    return mk(48,f,80)
def 疑问():
    def f(i):
        c=i%40; p=base(); fx={}
        t=kf(c,[(0,0),(4,1),(8,.9),(10,1)])
        tilt=0 if c<6 else 8*wave(c-6,28)
        face(p,'n',dx=1 if tilt>0 else -1 if c>=6 else 0,ey=-1 if c>=6 else 0)
        if c>=4:
            bounce=-round(kf(c,[(4,3),(8,-1),(11,0)]))
            fx.update(cut(QM,5,-6-bounce,'#3B82F6'))
        sq=squash(kf(c,[(0,1),(3,.92),(6,1)]))
        return sc(p,rot=tilt,sq=sq,fx=fx)
    return mk(40,f,70,{8:150})

# ================= 21-30 =================
def rise(i,pre): return kf(i,[(0,9),(pre,-1),(pre+3,0)]) if i<pre+3 else 0
def 我错了():
    def f(i):
        p=base(); hold_arms(p); face(p,'n',ey=1); fx={}
        for x in (4,10): put(p,[(x-1,10),(x,10),(x+1,10)],TEAR)
        for k,x in enumerate((3,11)):
            q=(i+k*5)%14
            if q<10 and i>8: fx[(x,11+q//2)]=TEAR; fx[(x,12+q//2)]=TEAR
        up=rise(i,8); sh=0.25*math.sin(i*2.7)*(i>8)
        return comp(shadow(),xform(p,sh,0),draw(canvas(),fx),sign('我错了',dxp=round(sh*12),dyp=round(up*12)))
    return mk(48,f,70)
def 收到():
    def f(i):
        p=base(); hold_arms(p); fx={}; up=rise(i,10); c=i-14
        face(p,'hap') if c>=0 else face(p,'n',dx=1 if i<8 else 0,ey=-1 if i<8 else 0)
        nod=max(0,math.sin(TAU*c/16))*1.2 if c>=0 and c<32 else 0
        if c>=12 and (i//3)%2:
            for (x,y) in [(-2,2),(16,3),(15,-4)]: fx.update(cut(SPARK,x,y,YEL))
        return comp(shadow(),xform(p,0,nod*0.5,sy=1-0.04*nod),sign('收到',dyp=round((up+nod*0.5)*12)),draw(canvas(),fx))
    return mk(48,f,70)
def 好哒():
    def f(i):
        p=base(); hold_arms(p); face(p,'hap'); fx={}; up=rise(i,6)
        hop=abs(math.sin(math.pi*((i-8)%12)/12))*1.6 if i>=8 else 0
        for k,(x,y) in enumerate([(-3,3),(16,3),(-1,-4),(15,-5)]):
            if i>=10 and (i+k*3)%8<5: fx.update(cut(H3 if k<2 else SPARK,x,y,HRT if k<2 else YEL))
        return comp(shadow(1),xform(p,0,-hop*0.7,sy=1-0.0*hop),sign('好哒',dyp=round((up-hop*.7)*12)),draw(canvas(),fx))
    return mk(48,f,70)
def 在吗():
    def f(i):
        p=base(); hold_arms(p); up=rise(i,6); c=i-8; fx={}
        dxs=[0,-1,-1,0,1,1,0,0][(max(c,0)//5)%8] if c>0 and c<42 else 0
        face(p,'n',dx=dxs,blink=bk(i,24,20))
        lean=kf(i,[(40,0),(46,1),(52,1),(58,0)])
        rot=3*wave(i,20)*(c>0)
        if 42<=i<54: fx.update(cut(QM,15,-6,'#3B82F6') if False else {})
        return comp(shadow(),xform(p,0,0,rot=0,sx=1+.1*lean,sy=1+.1*lean),sign('在吗',dyp=round(up*12),rot=rot))
    return mk(60,f,70)
def 等你():
    def f(i):
        p=base(); hold_arms(p); up=rise(i,6); c=i-8
        face(p,'n',dx=1 if (c//10)%2==0 else 0,ey=0,blink=bk(i,30,27))
        if c>0: run_legs(p,(c//5)%2)
        fx={}
        if c>16 and (i//4)%2: fx.update(cut(H3,16,2,PINK))
        return comp(shadow(),xform(p,0,0),sign('等你',dyp=round(up*12),rot=2*wave(i,40)),draw(canvas(),fx))
    return mk(60,f,70)
def 在忙():
    def f(i):
        p=base(); hold_arms(p); up=rise(i,6); c=i-6; fx={}
        face(p,'n',dx=[-1,0,1,0][(c//3)%4] if c>0 else 0,blink=bk(i,20,17))
        jit=0.3*math.sin(i*5) if c>0 else 0
        if c>0:
            q=(c)%16; 
            if q<12: fx[(14,3+q//2)]=TEAR; fx[(14,4+q//2)]=TEAR
            for k,(x,y) in enumerate([(-3,4),(-2,-3),(17,-4)]):
                if (i+k*2)%6<3: fx.update(cut(SPARK,x,y,SMK))
        return comp(shadow(),xform(p,jit,0),sign('在忙',dxp=round(jit*12),dyp=round(up*12)),draw(canvas(),fx))
    return mk(48,f,60)
def 陪我():
    def f(i):
        p=base(); hold_arms(p); up=rise(i,6); c=i-8; fx={}
        face(p,'n',ey=1)
        for x in (4,10): put(p,[(x,10)],TEAR)
        hop=abs(math.sin(math.pi*(c%14)/14))*1.4 if c>0 else 0
        for k,(x,y) in enumerate([(-3,5),(17,4),(16,-4)]):
            q=(i+k*6)%18
            if c>0 and q<14: fx.update(cut(H3,x,y-q//2,HRT))
        return comp(shadow(1),xform(p,0.5*wave(i,28)*(c>0),-hop*.6,sy=1),sign('陪我',dxp=round(0.5*wave(i,28)*(c>0)*12),dyp=round((up-hop*.6)*12)),draw(canvas(),fx))
    return mk(56,f,70)
def 哼():
    def f(i):
        p=base(); fx={}; c=i%40; t=kf(c,[(0,0),(6,1)])
        face(p,'n',dx=1 if t>.5 else 0,ey=0,blink=(c in (36,37))); arms(p,MID,MID)
        if t>.5: put(p,[(11,7)],K) if False else None
        for s0 in (9,22):
            q=c-s0
            if 0<=q<8:
                fx.update(cut(["xx","xx"] if q<4 else ["xxx","x.x","xxx"] if False else ["xxx","xxx"],14+q//2,10+q//4,'#FFFFFF' if False else SMK))
        return sc(p,dx=-0.8*t,rot=-9*t,fx=fx)
    return mk(40,f,70)
def 比心():
    L=rect(0,2,1,8)+[(2,1),(2,2)]
    def f(i):
        p=base(); face(p,'hap'); blush(p); arms(p,UP,UP); fx={}
        w=7 if (i%12)<4 else 5
        p.update(spr(hrt(w),7-w//2,-1 if w==7 else 0,{'x':HRT}))
        return sc(p,dy=-0.3*abs(wave(i,12)),fx=fx)
    return mk(48,f,70)
BIG=[".xxx.xxx.","xxxxxxxxx","xxxxxxxxx","xxxxxxxxx",".xxxxxxx.","..xxxxx..","...xxx...","....x...."]
def 心碎():
    CR=[4,5,4,5,4,5,4,4]
    def f(i):
        p=base(); c=i%60; fx={}
        t=kf(c,[(0,0),(14,0),(20,1),(50,1)]); fall=kf(c,[(24,0),(52,3)])
        face(p,'n',ey=1) if c>=14 else face(p,'n',dx=0,ey=-1)
        if c>=18:
            arms(p,MID,MID)
            for x in (4,10): put(p,[(x-1,10),(x,10),(x+1,10)],TEAR)
        if c<18 and c>=14: pass
        cells=spr(BIG,3,-6,{'x':HRT})
        if c>=14:
            for (x,y),v in cells.items():
                left=(x-3)<=CR[y+6]
                sgn=-1 if left else 1
                nx=x+round(sgn*t*2)+(0 if left else 0); ny=y+round(fall+ (0 if c<24 else 0)); 
                if c<18: fx[(x,y)]=v
                else:
                    fx[(nx,ny+int(left!=True)*0)]=v if ny<14 else v
        else:
            fx=dict(cells)
            if c<14 and (c//7)%2: 
                for k in range(4): fx[(7,-6+k)]='#fff'
        if c>=14 and c<18:
            for k in range(8): fx[(3+CR[k],-6+k)]='#FFFFFF'
        if c>=22:
            for k,x in enumerate((3,11)):
                q=(i+k*4)%12
                if q<8: fx[(x,11+q//2)]=TEAR; fx[(x,12+q//2)]=TEAR
        return sc(p,dy=0.2*(c>=24),sq=squash(1-.05*(c>=24)),fx=fx)
    return mk(60,f,70)

# ================= 31-40 =================
def gshadow(dx=0,col='#D9D2CB'): return {(x+dx,15):col for x in range(3,12)}
def 偷看():
    def f(i):
        c=i%48; p=base(); dx=kf(c,[(0,22),(8,8),(26,8),(32,22)]) if c<34 else 22
        dx2=kf(c,[(0,22),(10,12)]) 
        face(p,'n',dx=-1 if 12<=c<26 else 0,blink=(c in (22,23)))
        if c<=34 or True: pass
        fx={}
        if 14<=c<26 and (c//4)%2: fx.update(cut(H3,9,2,HRT))
        return comp(draw(canvas(),gshadow(round(dx))),xform(p,dx,0,rot=-6*(1-abs(dx-8)/14) if dx<22 else 0),draw(canvas(),fx))
    return mk(48,f,70,{14:140})
def 撒花():
    def f(i):
        p=base(); face(p,'hap'); t=(i%12)/12; hop=abs(math.sin(math.pi*t))*2.5
        arms(p,UP,UP) if (i//2)%2 else arms(p,MID,MID)
        fx=confetti(i,0,26,3); fx.update(confetti(i,22,20,5))
        sq=squash(.9) if t<.1 else {}
        return comp(shadow(),draw(canvas(),fx),xform(p,0,-hop,**sq))
    return mk(56,f,60)
BUB2=["..xxxxxxx..",".xwwwwwwwx.","xwwwwwwwwwx","xwwwwwwwwwx","xwwwwwwwwwx","xwwwwwwwwwx","xwwwwwwwwwx",".xwwwwwwwx.","..xxxxxxx.."]
ONI=["...o...","..owo..",".owwwo.","owwwwwo","okkkkko","okkkkko","ooooooo"]
def 饿饿():
    def f(i):
        c=i%40; p=base(); face(p,'n',ey=-1,blink=bk(c,40,37)); fx={}
        bob=round(0.5+0.5*wave(i,30))
        fx.update(spr(BUB2,2,-8+bob,BPAL)); fx.update(spr(ONI,4,-7+bob,{'o':INK,'w':'#F4F1E8','k':'#2B3A33'}))
        fx.update({(7,3):INK,(6,5):INK})
        rum=(c%20)<10
        if rum:
            for k,(x,y) in enumerate([(-1,9),(-1,11),(15,9),(15,11)]):
                if (c//2+k)%2: fx.update(cut(["x","x"],x-(k<2)*1+(k>1)*0,y,SMK))
        sq=dict(sx=1+0.05*math.sin(c*2.2)*rum,sy=1-0.05*math.sin(c*2.2)*rum)
        return sc(p,rot=1.5*math.sin(c*2.2)*rum,sq=sq,fx=fx)
    return mk(40,f,70)
FLW=[".ppp.","ppyyp".replace('yy','y'+'p') if False else "ppypp",".ppp.","..g..",".gg..","..g..","..g..","..g.."]
def 送你花():
    def f(i):
        c=i%48; p=base(); face(p,'hap'); arms(p,DOWN,UP)
        off=kf(c,[(0,0),(10,1.5),(40,1.5),(47,0)])
        pet=(c//4)%2
        rows=[r for r in FLW]
        if pet: rows[0]="pp.pp"; rows[2]="pp.pp"
        fx=spr(rows,round(11+off),1,{'p':PINK,'y':YEL,'g':GRN})
        fl=0.8*math.sin(TAU*c/12)
        for k,(x,y) in enumerate([(-3,0),(8,-5)]):
            q=(c+k*8)%24
            if c>14 and q<16: fx.update(cut(H3,x,y-q//3+3,HRT))
        return comp(shadow(),xform(p,-2+off*.2,0,rot=0),draw(canvas(),fx))
    return mk(48,f,70)
def 转圈圈():
    def f(i):
        c=i%56; p=base(); th=360*kf(c,[(4,0),(26,1),(28,1),(50,2)])/1.0
        ang=math.radians(th); sx=math.cos(ang); back=math.cos(ang)<0
        if th%360==0 or (abs(sx)>0.3 and not back): face(p,'hap')
        else: face(p,'hap'); clear(p,[(x,y) for x in range(3,12) for y in range(7,11)]); put(p,[(x,y) for x in range(3,12) for y in range(7,11)],BODY) if back else None
        hop=abs(math.sin(math.pi*((c-4)%22)/22))*1.6 if 4<=c<50 else 0
        return sc(p,dy=-hop,sq=dict(sx=max(0.12,abs(sx)),sy=1),sh=True)
    return mk(56,f,60)
CUP_O=INK
def 喝奶茶():
    def f(i):
        c=i%60; p=base(); fx={}
        lvl=round(kf(c,[(0,5),(14,5),(46,1),(60,1)])); sip=14<=c<48
        face(p,'hap' if sip or c>=48 else 'n',dx=0)
        arms(p,MID,MID)
        rows=["ooooooo"]+["o.....o"]*5+[".ooooo."]
        cup=spr(rows,4,10,{'o':CUP_O})
        for r in range(lvl):
            y=15-r
            for x in range(5,10): cup[(x,y)]='#D9B48F'
        for x in (5,7,9): cup[(x,15)]='#3B2A20' if lvl>=1 else None
        for x in (6,8): 
            if lvl>=1: cup[(x,14)]='#3B2A20' if lvl>=2 else '#D9B48F'
        cup={k:v for k,v in cup.items() if v}
        for y in (7,8,9): cup[(7,y)]='#FFFFFF' if y%2 else '#E8708A'
        cup[(7,10)]='#E8708A'
        if sip and (c%8)<4: cup[(7,9-(c%8))]='#3B2A20'
        if sip and c%12<3: cup.update(cut(SPARK,-2,5,YEL) if False else {})
        if c>=50 and (c//3)%2:
            for (x,y) in [(-2,4),(16,3)]: cup.update(cut(SPARK,x,y,YEL))
        dy=0.4*math.sin(c*1.1) if sip else 0
        return comp(shadow(),xform(p,0,dy*0.5),draw(canvas(),cup))
    return mk(60,f,80)
def 打滚():
    def f(i):
        c=i%48; p=base(); face(p,'hap'); arms(p,MID,MID); fx={}
        x=kf(c,[(0,-4),(18,6),(22,6),(40,-4)]); th=kf(c,[(0,0),(18,360),(22,360),(40,0)])
        rot=th
        if c<8 or 22<=c<28:
            for k in range(3): fx[(round(x)-2-k,14-k%2)]='#D9D2CB'
        sh={(xx+round(x),15):'#D9D2CB' for xx in range(3,12)}
        return comp(draw(canvas(),sh),xform(p,x,-0.6,rot=rot,piv=(7.5,9.5)),draw(canvas(),fx))
    return mk(48,f,60,{20:300})
PH={'x':'#2B2B2B','s':'#9ED0F2'}
def 打电话():
    def f(i):
        c=i%48; p=base(); fx={}
        talk=(c//6)%3<2
        face(p,'hap' if talk and (c//2)%2 else 'n',blink=bk(c,24,20))
        arms(p,MID,UP)
        ph=spr(["xxx","xsx","xsx","xsx","xxx","xxx"],13,3,PH)
        for k,(x,y) in enumerate([(-3,6),(-1,2),(16,-3)]):
            q=(c+k*8)%24
            if talk and q<14: fx.update(cut(H3,x,y-q//2,HRT))
        return comp(shadow(),xform(p,0,-0.3*abs(wave(c,12)) if talk else 0),draw(canvas(),ph),draw(canvas(),fx))
    return mk(48,f,70)
def 撑伞():
    ROWS=["....xxxxxxxx....","..xxxxxxxxxxxx..",".xxxxxxxxxxxxxx.","xxxxxxxxxxxxxxxx"]
    def f(i):
        p=base(); face(p,'n',ey=-1,blink=bk(i,30,27)); arms(p,UP,MID)
        u={}
        for r,row in enumerate(ROWS):
            for k,ch in enumerate(row):
                if ch=='x': u[(k,-2+r)]='#F59AA6' if (k//2)%2 else '#E8708A'
        u[(7,2)]=BROWN;u[(8,2)]=BROWN
        for y in (3,4,5): u[(7,y)]=BROWN; u[(8,y)]=BROWN
        rain={}
        for k,x in enumerate(range(-4,19,2)):
            for j in range(2):
                y=(i*2+k*5+j*8)%16-7
                top=-3 if 0<=x<=15 else 15
                if y<=top: rain[(x,y)]=TEAR; rain[(x,y+1)]=TEAR if y+1<=top else None
        rain={k:v for k,v in rain.items() if v}
        for x in (-4,-2,17): 
            if (i//2+x)%3==0: rain[(x,15)]=TEAR
        return comp(shadow(),draw(canvas(),u),xform(p,0,0,rot=1.5*wave(i,40)),draw(canvas(),rain))
    return mk(48,f,70)
CK={'f':'#FF9F1C','c':'#6CB4EE','p':'#F59AA6','s':'#F6D8A8','b':'#CFC8C0'}
CAKE=["....f....","....f....","....c....","....c....","ppppppppp","pspsspsps","sssssssss","ppppppppp","bbbbbbbbb"]
def 生日快乐():
    def f(i):
        c=i%56; p=base(); fx={}
        puff=22<=c<28; out=24<=c<34
        face(p,'hap' if c>=30 else 'n',dx=1 if c<30 else 0)
        if c>=30: arms(p,UP,UP) if (c//3)%2 else arms(p,MID,MID)
        cake=spr(CAKE,10,7,CK)
        if out:
            cake.pop((14,7)); cake.pop((14,8))
            for k in range(4):
                q=(c-24)*0.5+k
                if q<7: cake[(14+round(math.sin(q+k)),6-round(q))]=SMK
        elif c%6>=3: cake.pop((14,7))
        conf=confetti(c,32,22,7) if c>=32 else {}
        lean=0.8*puff
        return comp(shadow(),xform(p,-3+lean,-0.4*abs(wave(c,8)) if c>=30 else 0,rot=3*lean),draw(canvas(),cake),draw(canvas(),conf))
    return mk(56,f,70)

# ================= 41-50 =================
def 爱你():
    def f(i):
        p=base(); hold_arms(p); heart_eyes(p); fx={}; up=rise(i,6); c=i-8
        hop=abs(math.sin(math.pi*(c%14)/14))*1.2 if c>0 else 0
        for k,(x,y) in enumerate([(-3,5),(17,4),(-2,0),(16,0)]):
            q=(i+k*5)%22
            if c>0 and q<16: fx.update(cut(H3 if k<2 else H5,x,y-q//4,HRT if k%2 else PINK))
        return comp(shadow(1),xform(p,0,-hop*.7),sign('爱你',dyp=round((up-hop*.7)*12)),draw(canvas(),fx))
    return mk(56,f,70)
def 躺平():
    def f(i):
        c=i%52; p=base(); fx={}
        sy=kf(c,[(0,1),(6,1),(10,.8),(14,1.05),(30,.3),(52,.3)]); sx=min(1.6,1/math.sqrt(sy))
        if c<8: face(p,'n',blink=(c==4)); 
        elif c<30: shut(p) if c>=16 else face(p,'n',blink=True)
        else: shut(p) if not bk(c,12,10) else face(p,'x')
        if c>=34 and c%16<8:
            q=c%16; fx.update(cut(["xx","xx"],10+q//3,3-q//2,SMK))
        return sc(p,sq=dict(sx=sx,sy=sy),fx=fx)
    return mk(52,f,70,{0:200})
def 跳舞():
    def f(i):
        p=base(); face(p,'hap'); fx={}; ph=(i%16)/16
        arms(p,UP if ph<.5 else DOWN,DOWN if ph<.5 else UP)
        sw=wave(i,16); hop=abs(math.sin(TAU*i/16))*1.2
        for k,(x,y) in enumerate([(-3,2),(16,0),(-2,-4),(15,-5)]):
            q=(i+k*5)%20
            if q<14: fx.update(cut(NOTE,x,y-q//2,PURP if k%2 else HRT))
        return sc(p,dx=1.2*sw,dy=-hop,rot=7*sw,fx=fx)
    return mk(48,f,60)
def 冲呀():
    def f(i):
        p=base(); face(p,'n',dx=1); run_legs(p,(i//2)%2); flap(p,(i//2)%2); fx={}
        for k in range(5):
            y=3+k*2+(k%2); x=(18-(i*3+k*7)%26)
            L=3+k%3
            for j in range(L): fx[(x+j,y)]=SMK
        for k in range(3):
            q=(i+k*3)%9
            fx.update(cut(["xx","xx"] if q<5 else ["x"],-1-q//2,14-q//3,'#D9D2CB'))
        return comp(draw(canvas(),fx),xform(p,0,-0.3*(i%2),rot=9))
    return mk(36,f,50)
DK={'y':YEL,'k':'#2B2B2B','o':'#FF8C1A','Y':'#F2B705','w':'#FFFFFF'}
DUCK=["...yyy...","..yyyyy..","..ywkyyoo","y.yyyyyoo","yyyYYyy..","yyyyyyyy.",".YYYYYY.."]
def 洗澡():
    def f(i):
        p=base(); face(p,'hap',blink=False); fx={}
        arms(p,UP if (i//5)%2 else MID,MID if (i//5)%2 else UP)
        foam={(x-3,y-1):'#CDEBFA' for x,y in rect(4,4,10,5)+rect(5,3,8,3)+[(4,6),(10,6),(7,2)]}
        tub={}
        for x in range(-3,18):
            for y in range(12,17):
                tub[(x,y)]='#8EB6DC' if y==12 else '#CFE3F5'
        for x in range(-3,18): tub[(x,16)]='#8EB6DC'
        for x in (-3,17): 
            for y in range(12,17): tub[(x,y)]='#8EB6DC'
        for x in (-1,15):
            for y in (16,): pass
        bub={}
        for k in range(5):
            q=(i+k*7)%30
            x=[0,4,8,11,14][k]; y=10-q*0.5
            if y>-6: bub.update(cut(["xx","xx"] if q<20 else ["x"],x+round(math.sin(q*.5+k)),round(y),'#9ED0F2'))
        duck=spr(DUCK,10,6+round(0.6*math.sin(i*.4)),DK)
        return comp(xform(p,-3,-0.5,rot=2*wave(i,20)),draw(canvas(),foam),draw(canvas(),tub),draw(canvas(),duck),draw(canvas(),bub))
    return mk(48,f,70)
def 许愿():
    def f(i):
        c=i%56; p=base(); fx={}
        arms(p,MID,MID)
        if c<34 or c>=44: shut(p)
        else: face(p,'n',ey=-1)
        if c>=36 and c<54: pass
        for (x,y) in [(-3,-4),(15,-5),(1,-6),(17,0),(-3,2)]:
            if (c//4+x)%3: fx[(x,y)]='#F2C14E'
        t=kf(c,[(8,0),(30,1)])
        if 8<=c<=30:
            sx=round(20-t*26); sy=round(-6+t*8)
            for k in range(7): fx[(sx+k*2+0,sy-k)]=mix(YEL,'#FFFFFF',0) if False else (YEL if k<3 else '#F6D8A8')
            fx.update(cut(STAR,sx-2,sy-2,YEL))
        if 38<=c<54:
            q=c-38; fx.update(cut(H3 if q<8 else H5,7-(1 if q<8 else 2),0-q//3,HRT))
        return sc(p,rot=-4*(c<34),fx=fx,sq=squash(1-0.02*wave(c,28)))
    return mk(56,f,70)
STR=[".ggggg.","rrkrkrr","rkrrrkr","rrrkrrr",".rkrkr.","..rrr..","...r..."]
SP={'g':GRN,'r':'#F2536B','k':'#FFE08A'}
def 好吃():
    BITES=[(11,12,2.6),(3,12,2.6),(7,15,3.0)]
    def f(i):
        c=i%60; nb=0 if c<12 else 1 if c<26 else 2 if c<40 else 3
        p=base(); chew=(12<=c<18) or (26<=c<32) or (40<=c<46); fx={}
        face(p,'hap' if chew or c>=46 else 'n',ey=0)
        arms(p,MID,MID)
        m=spr(STR,4,10,SP)
        for (bx,by,r) in BITES[:nb]:
            for (x,y) in list(m):
                if (x-bx)**2+(y-by)**2<=r*r: m.pop((x,y))
        if chew or c>=46:
            for k,(x,y) in enumerate([(-2,3),(16,2),(0,-3),(15,-4)]):
                if (c+k*3)%8<5: fx.update(cut(SPARK,x,y,YEL))
        dy=0.5 if 9<=c<12 or 23<=c<26 or 37<=c<40 else -0.3*abs(wave(c,6)) if chew else 0
        return comp(shadow(),xform(p,0,dy),draw(canvas(),m),draw(canvas(),fx))
    return mk(60,f,80)
def 求抱抱():
    L=rect(0,3,1,8)
    def f(i):
        p=base(); face(p,'n',ey=1); arms(p,L,L); fx={}
        for x in (4,10): put(p,[(x-1,10),(x,10),(x+1,10)],TEAR)
        t=(i%12)/12; hop=abs(math.sin(math.pi*t))*1.5
        for k,(x,y) in enumerate([(-3,0),(17,-1),(7,-6)]):
            q=(i+k*6)%20
            if q<14: fx.update(cut(H3,x,y-q//3+5,HRT))
        return sc(p,dy=-hop,sq=squash(.92) if t<.1 else {},fx=fx)
    return mk(48,f,70)
POM=[".xx.","xxxx","xxxx",".xx."]
def 加油():
    def f(i):
        p=base(); face(p,'hap'); fx={}; ph=(i//4)%2
        arms(p,UP if ph else MID,MID if ph else UP)
        hop=abs(math.sin(TAU*i/16))*1.0
        # 彩球贴在手上，一上一下
        fx.update(cut(POM,-2,3 if ph else 5,YEL)); fx.update(cut(POM,13,5 if ph else 3,YEL))
        for (x,y) in ([(-3,3),(15,6)] if ph else [(-3,6),(15,3)]): pass
        sg=sign('加油',cols=11,rows=6,x0=2,y0=-5,dyp=-round(hop*12))
        return comp(shadow(),xform(p,0,-hop),draw(canvas(),fx),sg)
    return mk(48,f,70)
BF=["xx.k.xx","xxxkxxx",".xxkxx.","..x.x.."]; BF2=["...k...","..xkx..","..xkx..","...k..."]
def 发呆():
    def f(i):
        p=base(); c=i
        if c<42:
            th=TAU*c/28; bx=4.5+8*math.cos(th); by=1.5+3*math.sin(th)
        else:
            t=kf(c,[(42,0),(50,1)]); th=TAU*42/28; bx=lerp(4.5+8*math.cos(th),4.5,t); by=lerp(1.5+3*math.sin(th),2.5,t)
        c0=math.cos(th) if c<42 else 0
        face(p,'n',dx=1 if c0>0.35 else -1 if c0<-0.35 else 0,ey=-1 if by<3 or c>=44 else 0,blink=bk(c,28,26))
        wing=BF if (c//2)%2 else BF2
        bf=spr(wing,round(bx),round(by),{'x':'#E58BC0' if (c//10)%2 else '#C77DFF','k':K})
        return comp(shadow(),xform(p,0,0,rot=2*c0),draw(canvas(),bf))
    return mk(56,f,70)

NAMES={n:globals()[n] for n in '想你 贴贴 抱抱 蹭蹭 亲亲 哄你 吃醋 委屈 哭 生气 害羞 捂眼睛 开心 早安 晚安 熬夜 吃瓜 无语 疑问 我错了 收到 好哒 在吗 等你 在忙 陪我 哼 比心 心碎 偷看 撒花 饿饿 送你花 转圈圈 喝奶茶 打滚 打电话 撑伞 生日快乐 爱你 躺平 跳舞 冲呀 洗澡 许愿 好吃 求抱抱 加油 发呆'.split()}

if __name__=='__main__':
    ap=argparse.ArgumentParser(description='生成情侣日常像素螃蟹表情')
    ap.add_argument('names',nargs='*',metavar='中文名',help='默认全部：'+' '.join(NAMES))
    ap.add_argument('--dark',action='store_true',help='深色背景版，出到 ../out-dark/')
    a=ap.parse_args()
    bad=[n for n in a.names if n not in NAMES]
    if bad: ap.error('没有这个表情：'+', '.join(bad))
    set_dark(a.dark)
    for n in (a.names or NAMES): save(n,NAMES[n]())
