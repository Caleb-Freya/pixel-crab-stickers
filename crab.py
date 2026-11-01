#!/usr/bin/env python3
"""Pixel Crab Stickers / 像素小螃蟹表情包 —— unofficial fan work 非官方粉丝二创.
纯标准库逐帧画像素，ffmpeg 出透明 GIF。Pure-stdlib pixel drawing, frame by frame; ffmpeg writes transparent GIFs.
用法 Usage: python3 crab.py [名字 name ...]   不带名字=全部 / no args = all; 输出 output: out/<名字>.gif（浅色底 light）+ out-dark/<名字>.gif（深色底 dark）"""
import math, os, subprocess, sys

S, SCALE, FPS, N = 64, 3, 12, 12        # 画布 64×64 小像素，放大 3 倍 = 192px；12 帧一圈
C = 5                                    # 一格 = 5 小像素
ORANGE, DARK, PINK, BLUE, YEL, WHITE = "#DA7756", "#2A1A14", "#F59AA6", "#6EB6FF", "#FFD23F", "#FFFFFF"
SHADE, RED, PAPER, SHADOW = "#BF6143", "#E8456B", "#FFF6E8", "#E6DDD3"
OUT = os.path.join(os.path.dirname(os.path.abspath(__file__)), "out")

# 身体网格（10 列）：1=身体 2=眼睛格。顶上平的扁长方形、两边短臂、底下 4 条腿
STAND = [".11111111.", ".12111121.", "1111111111", ".11111111.", ".1.1..1.1.", ".1.1..1.1."]
WAVE = [".11111111.", "1121111211", ".11111111.", ".11111111.", ".1.1..1.1.", ".1.1..1.1."]   # 手抬到两边挥
RAISE = ["1........1", "1111111111", ".12111121.", ".11111111.", ".11111111.", ".1.1..1.1.", ".1.1..1.1."]
EYES = {  # 5×5 画在眼睛格里（w=高光）；左右眼按 MIRROR 决定右眼要不要左右翻
    "normal": [".##..", "#w##.", "####.", "####.", ".##.."],
    "happy": [".....", ".###.", "#...#", ".....", "....."],
    "line": [".....", ".....", "#...#", ".###.", "....."],
    "cry": ["##...", ".##..", "..##.", ".##..", "##..."],
    "side": ["####.", "..##.", "..##.", "..##.", "....."],
    "wet": [".##..", "#w##.", "####.", "####.", ".bb.."],
    "angry": ["#....", ".##..", ".###.", ".###.", "....."],
    "tired": [".....", "####.", "####.", ".....", "ssss."],
    "flat": [".....", ".....", "####.", ".....", "....."],
}
MIRROR = {"normal", "cry", "wet", "angry", "tired", "flat"}
MOUTH = ["#.#.#", ".#.#."]   # 小 ω


def rgb(h):
    return bytes(int(h[i:i + 2], 16) for i in (1, 3, 5)) + b"\xff"


class Frame:
    def __init__(self):
        self.p = [[None] * S for _ in range(S)]

    def dot(self, x, y, c):
        if 0 <= x < S and 0 <= y < S:
            self.p[y][x] = c

    def get(self, x, y):
        return self.p[y][x] if 0 <= x < S and 0 <= y < S else None

    def box(self, x, y, w, h, c):
        for yy in range(y, y + h):
            for xx in range(x, x + w):
                self.dot(xx, yy, c)

    def pat(self, x, y, rows, c, mirror=False, z=1):
        for r, row in enumerate(rows):
            for k, ch in enumerate(row[::-1] if mirror else row):
                if ch != ".":
                    self.box(x + k * z, y + r * z, z, z, {"w": WHITE, "r": RED, "b": BLUE, "s": SHADE, "y": YEL, "g": "#5DAA4A", "p": PINK, "k": DARK}.get(ch, c))

    def raw(self):
        return b"".join(rgb(c) if c else b"\0\0\0\0" for row in self.p for c in row)


def crab(f, grid=STAND, dx=0, dy=0, eyes="normal", blush=False, mouth=False, sx=1.0, sy=1.0, mouth_pat=None, shadow=True):
    """先在临时画布画好，再以脚底中点为锚压扁/拉长贴到 f 上。返回两只眼睛格（贴图后）的左上角。"""
    if shadow:                              # 地上的影子：跳得越高越小
        w = max(12, round(40 * sx) + 2 * min(0, dy))
        f.box(32 + dx - w // 2, S - 2, w, 2, SHADOW)
    t = Frame()
    ox, oy = (S - 10 * C) // 2, S - 2 - len(grid) * C
    pos = []
    for r, row in enumerate(grid):
        for k, ch in enumerate(row):
            if ch != ".":
                t.box(ox + k * C, oy + r * C, C, C, ORANGE)
            if ch == "2":
                pos.append((ox + k * C, oy + r * C))
    body = {(x, y) for y in range(S) for x in range(S) if t.p[y][x]}
    for x, y in body:                      # 磨圆凸角 + 底边阴影
        up, dn, lf, rt = (x, y - 1) in body, (x, y + 1) in body, (x - 1, y) in body, (x + 1, y) in body
        if (not up or not dn) and (not lf or not rt):
            t.p[y][x] = None
        elif not dn:
            t.p[y][x] = SHADE
    for i, (x, y) in enumerate(pos):
        if eyes in EYES:
            t.pat(x + (1 if i else 0), y, EYES[eyes], DARK, mirror=(i == 1 and eyes in MIRROR))
        if blush:
            t.box(x + (-4 if i == 0 else 5), y + C + 1, 4, 2, PINK)
    if (mouth or mouth_pat) and len(pos) == 2:
        mp = mouth_pat or MOUTH
        t.pat((pos[0][0] + pos[1][0]) // 2 + 2 - len(mp[0]) // 2, pos[0][1] + C + 1, mp, DARK)
    ax, ay = S / 2, S - 2                   # 锚点：脚底中间
    for y in range(S):
        for x in range(S):
            u, v = int(ax + (x + 0.5 - ax) / sx), int(ay + (y + 0.5 - ay) / sy)
            c = t.get(u, v)
            if c:
                f.dot(x + dx, y + dy, c)
    return [(round(ax + (x - ax) * sx) + dx, round(ay + (y - ay) * sy) + dy) for x, y in pos]


def hop(t, h=4):
    """一跳：返回 (dy, sx, sy)，起跳拉长、落地压扁。"""
    ph = t / N
    if ph < 0.15:
        return 0, 1.08, 0.9                          # 蓄力压扁
    if ph < 0.65:
        k = (ph - 0.15) / 0.5
        return -round(h * 4 * k * (1 - k)), 0.95, 1.07  # 空中拉长
    if ph < 0.8:
        return 0, 1.1, 0.88                          # 落地压扁
    return 0, 1, 1


HEART = [".##.##.", "#######", "#######", ".#####.", "..###..", "...#..."]
HEART_S = [".#.#.", "#####", ".###.", "..#.."]
STAR = ["..#..", ".###.", "#####", ".###.", ".#.#."]
PLUS = ["..#..", "..#..", "#####", "..#..", "..#.."]
Z = ["####", "..#.", ".#..", "####"]
ANGER = ["##.##", "#...#", ".....", "#...#", "##.##"]
SPARK = [".#.", "###", ".#."]


def bob(t, amp=1):
    return -round(amp * (0.5 - 0.5 * math.cos(2 * math.pi * t / N)))


# ---------------- 每个表情 = 一个 fn(帧号) -> Frame ----------------
def 想你(t):
    f = Frame()
    d = [0, 0, 1, 1, 1, 0, 0, 0, -1, -1, -1, 0][t]       # 慢慢晃
    pos = crab(f, dx=d, eyes=None, blush=True)
    for i, (x, y) in enumerate(pos):                   # 眼睛往上望
        f.pat(x + (1 if i else 0), y - 1, [".##..", "#w##.", "####.", ".##.."], DARK, mirror=(i == 1))
    f.box(44 + d, 26, 2, 2, "#CCCCCC"); f.box(47 + d, 21, 3, 3, "#CCCCCC")     # 想念泡泡
    f.box(33, 1, 28, 18, "#CCCCCC"); f.box(34, 0, 26, 20, "#CCCCCC"); f.box(35, 1, 24, 18, WHITE)
    big = t % 6 < 3
    f.pat(40, 3, HEART, RED, z=2) if big else f.pat(42, 5, HEART_S, RED, z=2)
    return f


def 吃醋(t):
    f = Frame()
    puff = 1 + 0.06 * (0.5 - 0.5 * math.cos(2 * math.pi * t / N))    # 气鼓鼓：一胀一胀
    crab(f, dx=(1 if t % 2 else -1) if t < 4 else 0, eyes="side", blush=True, sx=puff, sy=2 - puff)
    if t % 6 < 4:
        f.pat(50, 12, ANGER, RED)
    for k in range(3):                               # 冒酸气：三缕往上
        y = 30 - ((t * 2 + k * 6) % 18)
        f.box(22 + k * 8, y, 2, 2, "#9BC46B")
    return f


def 晚安(t):
    f = Frame()
    br = 0.5 - 0.5 * math.cos(2 * math.pi * t / N)               # 慢慢呼吸
    crab(f, eyes="line", blush=True, sx=1 + 0.04 * br, sy=1 - 0.04 * br)
    for k in range(2):
        y = 28 - ((t * 2 + k * 12) % 24)
        f.pat(44 + k * 8, y, Z, BLUE)
    return f


def 哭(t):
    f = Frame()
    pos = crab(f, dx=(1 if t % 2 else 0), eyes="cry", sx=1.04, sy=0.95)
    for x, y in pos:                                 # 两行眼泪往下流
        for k in range(3):
            yy = y + C + ((t * 2 + k * 6) % 18)
            f.box(x + 1, yy, 2, 3, BLUE)
    return f


def 星星眼(t):
    f = Frame()
    dy, sx, sy = hop(t, 6)
    pos = crab(f, WAVE if t % 4 < 2 else STAND, dy=dy, eyes=None, blush=True, mouth=True, sx=sx, sy=sy)
    for x, y in pos:
        f.pat(x, y, STAR if t % 4 < 2 else PLUS, YEL)
    for k, (px, py) in enumerate([(4, 14), (54, 8), (30, 3), (12, 2)]):
        if (t + k) % 3 != 0:
            f.pat(px, py, SPARK, YEL)
    return f


def _text_mask(txt, w, h, size, th=0.42):
    """用正黑把字渲成 w×h 的 0/1 网格：先放大 4 倍渲，再按 4×4 块取平均，笔画更干净（ffmpeg drawtext，免装 PIL）。"""
    font, Z = "/usr/share/fonts/truetype/wqy/wqy-zenhei.ttc", 4
    vf = (f"drawtext=fontfile={font}:fontcolor=white:fontsize={size * Z}:text='{txt}':"
          f"x=(w-text_w)/2:y=(h-text_h)/2")
    out = subprocess.run(["ffmpeg", "-loglevel", "error", "-f", "lavfi", "-i", f"color=black:s={w * Z}x{h * Z}",
                          "-vf", vf, "-frames:v", "1", "-f", "rawvideo", "-pix_fmt", "gray", "-"],
                         capture_output=True, check=True).stdout
    W = w * Z
    return [[sum(out[(y * Z + j) * W + x * Z + i] for j in range(Z) for i in range(Z)) / (Z * Z * 255) > th
             for x in range(w)] for y in range(h)]


_SIGN = {}


def 我错了(t):
    f = Frame()
    up = 1 if t % 6 < 3 else 0
    crab(f, WAVE, dy=-up, eyes="wet", blush=True, mouth_pat=[".#.#.", "#.#.#"])
    words(f, "我错了", 5, 3 - up, 54)
    f.box(8, 3 - up + 19, 2, 15, "#8A5A3C"); f.box(54, 3 - up + 19, 2, 15, "#8A5A3C")
    return f


def words(f, txt, x0, y0, w, h=18, color=RED, bg=PAPER, size=16):
    """一块带边框的字牌/气泡。"""
    key = (txt, w, h, size)
    mask = _SIGN.get(key) or _SIGN.setdefault(key, _text_mask(txt, w, h, size))
    f.box(x0 - 1, y0 - 1, w + 2, h + 2, DARK); f.box(x0, y0, w, h, bg)
    for y, row in enumerate(mask):
        for x, on in enumerate(row):
            if on:
                f.dot(x0 + x, y0 + y, color)


def sign(txt):
    def fn(t):
        f = Frame()
        up = 1 if t % 6 < 3 else 0
        crab(f, WAVE, dy=-up, eyes="happy", blush=True, mouth=True)
        words(f, txt, 5, 3 - up, 54)
        f.box(8, 3 - up + 19, 2, 15, "#8A5A3C"); f.box(54, 3 - up + 19, 2, 15, "#8A5A3C")
        return f
    return fn


收到, 好哒 = sign("收到"), sign("好哒")


def 贴贴(t):
    f = Frame()
    k = [0, .3, .7, 1, 1, 1, 1, 1, .7, .3, 0, 0][t]      # 凑到屏幕上贴住，脸压扁
    crab(f, eyes="line" if k == 1 else "happy", blush=True, mouth=True, sx=1 + 0.3 * k, sy=1 + 0.18 * k, dy=0)
    if k == 1:                                         # 贴在玻璃上的反光
        for x, y in ((4, 6), (52, 4)):
            for j in range(4):
                f.dot(x + j, y + 3 - j, WHITE); f.dot(x + j + 1, y + 3 - j, WHITE)
        f.pat(28, 4 - (t - 3), HEART_S, RED)
    return f


def 抱抱(t):
    f = Frame()
    L = [10, 10, 9, 7, 4, 2, 2, 4, 7, 9, 10, 10][t]       # 手张得开开的，再合起来
    pos = crab(f, eyes="happy", blush=True, mouth=True)
    ox = (S - 10 * C) // 2
    y = pos[0][1] + C                                  # 手臂那一排
    for side in (-1, 1):
        x0 = ox + C if side < 0 else ox + 9 * C
        for j in range(L + C):
            xx = x0 - 1 - j if side < 0 else x0 + j
            f.box(xx, y - (j // 4 if L > 6 else 0), 1, C, ORANGE)
    if t % 6 < 3:
        f.pat(28, 14, HEART_S, RED)
    return f


def 蹭蹭(t):
    f = Frame()
    d = [0, -2, -4, -2, 0, -2, -4, -2, 0, -2, -4, -2][t]   # 靠在抱枕上一上一下蹭
    for r, row in enumerate(HEART):                    # 右边一颗大爱心抱枕
        for k, ch in enumerate(row):
            if ch == "#":
                f.box(36 + k * 4, 26 + r * 4 - (1 if d < -2 else 0), 4, 4, "#F7A8B8")
    crab(f, dx=-8, dy=d // 2, eyes="happy", blush=True, mouth=True, sx=0.9, sy=0.9 + (0.03 if d else 0))
    for k in range(3):
        f.box(46, 18 - k * 3 + (t % 3), 3 - k % 2, 1, PINK)
    return f


def 委屈(t):
    f = Frame()
    shake = 1 if t % 4 == 0 else 0
    crab(f, dx=shake, eyes="wet", blush=True, sx=1.05, sy=0.92, mouth_pat=[".#.#.", "#.#.#"])
    if t % 6 < 4:
        f.box(54, 26, 2, 3, BLUE); f.box(53, 29, 4, 2, BLUE)        # 一滴汗
    return f


def 哄你(t):
    f = Frame()
    d = [0, 1, 2, 1, 0, -1, -2, -1, 0, 1, 2, 1][t]
    crab(f, WAVE if t % 4 < 2 else STAND, dx=d, eyes="happy", blush=True, mouth=True)
    words(f, "乖乖", 16, 3, 32, color=DARK, bg="#FFE3EA")
    return f


def 亲亲(t):
    f = Frame()
    crab(f, eyes="line", blush=True, mouth_pat=[".##.", "#..#", ".##."], sx=1 - 0.03 * (t % 6 < 3), sy=1 + 0.04 * (t % 6 < 3))
    for k in range(2):                                 # 小心从嘴边往右上飘
        ph = (t + k * 6) % N
        f.pat(36 + ph * 2, 34 - ph * 2, HEART_S, RED if k == 0 else PINK)
    return f


def 害羞(t):
    f = Frame()
    sh = 0.5 - 0.5 * math.cos(2 * math.pi * t / N)                # 缩一缩
    crab(f, eyes="happy", blush=True, sx=1 - 0.05 * sh, sy=1 - 0.08 * sh)
    if t % 4 < 3:                                      # 脸上 ///
        for x0 in (14, 46):
            for k in range(3):
                f.box(x0 + k * 2, 42 - k, 1, 3, RED)
    return f


def 生气(t):
    f = Frame()
    crab(f, dx=(1 if t % 2 else -1), eyes="angry", mouth_pat=["#####", "....."], sx=1.04, sy=0.97)
    f.pat(50, 12, ANGER, RED)
    for k in range(2):                                 # 头顶冒烟
        y = 28 - ((t * 2 + k * 9) % 18)
        f.box(20 + k * 22, y, 3, 3, "#BBBBBB")
    return f


def disc(f, cx, cy, r, c):
    for y in range(cy - r, cy + r + 1):
        for x in range(cx - r, cx + r + 1):
            if (x - cx) ** 2 + (y - cy) ** 2 <= r * r + r:
                f.dot(x, y, c)


def 捂眼睛(t):
    f = Frame()
    pos = crab(f, dx=(1 if t % 2 else -1), eyes=None, blush=True)
    for i, (x, y) in enumerate(pos):                   # 脸扭向一边：眼睛挤到右边、紧紧闭上
        f.pat(x + 4, y, EYES["cry"], DARK, mirror=(i == 1))
    for k in range(3):                                 # 旁边三道"不看不看"
        f.box(4, 28 + k * 4, 3 - k % 2, 1, DARK)
    return f


def 无语(t):
    f = Frame()
    crab(f, eyes="flat", mouth_pat=["####"])
    for k in range(min(3, t // 3 + 1)):                # 三个点一个个冒出来
        f.box(22 + k * 8, 14, 4, 4, DARK)
    f.box(54, 26, 2, 3, BLUE); f.box(53, 29, 4, 3, BLUE)            # 一滴汗
    return f


def 吃瓜(t):
    f = Frame()
    crab(f, eyes="side", blush=True)
    bite = t % 6 < 3
    cx, cy, r = 32, 40 + (1 if bite else 0), 12    # 半圆：平的瓜瓤边朝上，瓜皮弧在下
    for y in range(cy, cy + r + 1):
        for x in range(cx - r, cx + r + 1):
            d = ((x - cx) ** 2 + (y - cy) ** 2) ** 0.5
            if d <= r and not (bite and (x - (cx + 3)) ** 2 + (y - cy) ** 2 <= 12):   # 上沿咬掉一口
                f.dot(x, y, "#2E7D32" if d > r - 2 else "#B5E08A" if d > r - 3 else "#F0566A")
    for x, y in ((26, cy + 3), (32, cy + 5), (38, cy + 3), (29, cy + 7), (35, cy + 7)):
        f.box(x, y, 1, 2, DARK)
    return f


def 熬夜(t):
    f = Frame()
    pos = crab(f, eyes="flat" if t % 6 == 5 else "normal", sx=1.02, sy=0.97 + 0.02 * (t % 6 < 3))
    for x, y in pos:                                   # 眼睛下面一排淤青
        f.box(x - 1, y + 5, 7, 2, "#8E6FB0")
    return f


def 早安(t):
    f = Frame()
    dy, sx, sy = hop(t, 4)
    crab(f, WAVE if t % 4 < 2 else STAND, dy=dy, eyes="happy", blush=True, mouth=True, sx=sx, sy=sy)
    cx, cy = 52, 9                                     # 太阳+转动的光
    f.box(cx - 3, cy - 3, 7, 7, YEL); f.box(cx - 4, cy - 2, 9, 5, YEL); f.box(cx - 2, cy - 4, 5, 9, YEL)
    for a in range(8):
        ang = a * math.pi / 4 + t * math.pi / 24
        f.dot(cx + round(7 * math.cos(ang)), cy + round(7 * math.sin(ang)), "#FFB000")
    return f


def 开心(t):
    f = Frame()
    dy, sx, sy = hop(t, 8)
    crab(f, WAVE if t % 4 < 2 else STAND, dy=dy, eyes="happy", blush=True, mouth=True, sx=sx, sy=sy)
    for k, (px, py) in enumerate([(6, 12), (52, 8), (30, 2)]):
        if (t + k) % 3:
            f.pat(px, py, SPARK, YEL)
    return f


def 疑问(t):
    f = Frame()
    d = 2 if t % 12 < 6 else -2
    crab(f, dx=d, eyes="normal", mouth_pat=[".##."])
    words(f, "？", 26 + d, 6 - (t % 6 < 3), 12, h=14, color=DARK, bg="#FFFFFF")
    return f


在吗, 等你, 在忙 = sign("在吗"), sign("等你"), sign("在忙")


def 哼(t):
    f = Frame()
    pos = crab(f, eyes=None, blush=True, sx=1.05, sy=0.97, mouth_pat=[".#", "#."])
    for i, (x, y) in enumerate(pos):                   # 扭头不看你
        f.pat(x + 3, y, EYES["flat"], DARK)
    if t % 6 < 4:                                      # 鼻子喷气
        k = t % 6
        f.box(6 - k, 44, 3, 2, "#C8C8C8"); f.box(3 - k, 41, 2, 2, "#C8C8C8")
    return f


def 比心(t):
    f = Frame()
    pos = crab(f, WAVE if t % 4 < 2 else STAND, eyes=None, blush=True, mouth=True)
    f.pat(pos[0][0], pos[0][1], EYES["happy"], DARK); f.pat(pos[1][0] + 1, pos[1][1], EYES["normal"], DARK, mirror=True)
    big = t % 6 < 3
    f.pat(25 - big * 0, 6 - big * 2, HEART, RED, z=2 if big else 1) if big else f.pat(28, 10, HEART, RED)
    if big:
        for x, y in ((14, 8), (48, 6)):
            f.pat(x, y, SPARK, YEL)
    return f


def 心碎(t):
    f = Frame()
    crab(f, eyes="wet", sx=1.04, sy=0.94, mouth_pat=[".#.#.", "#.#.#"])
    gap = min(t, 6) // 2                               # 心裂开、两半慢慢分开
    for r, row in enumerate(HEART):
        for k, ch in enumerate(row):
            if ch == "#":
                left = k < 3 or (k == 3 and r % 2 == 0)
                f.box(18 + k * 4 + (-gap if left else gap), 6 + r * 4 + (gap if left else 0), 4, 4, RED if left else "#C83A5A")
    return f


def 偷看(t):
    f = Frame()
    x = [34, 30, 26, 24, 24, 24, 24, 24, 26, 30, 34, 36][t]   # 从右边探出半个身子
    pos = crab(f, dx=x, eyes=None, blush=True)
    look = -1 if t in (4, 5, 6) else 0
    for i, (ex, ey) in enumerate(pos):
        f.pat(ex + look, ey, EYES["normal"], DARK)
    return f


CONF = ["#E8456B", "#FFD23F", "#6EB6FF", "#7BC96F", "#B48AE0"]


def 撒花(t):
    f = Frame()
    dy, sx, sy = hop(t, 5)
    crab(f, WAVE if t % 4 < 2 else STAND, dy=dy, eyes="happy", blush=True, mouth=True, sx=sx, sy=sy)
    for k in range(14):                                # 彩纸往下飘
        x = (k * 23 + k * k * 7) % 58 + 3
        y = (k * 29 + k * k * 3 + t * 3) % 34
        f.box(x + (1 if (t + k) % 4 < 2 else 0), y, 2 if k % 2 else 3, 2, CONF[k % 5])
    return f


RICE = ["...kk...", "..kwwk..", ".kwwwwk.", "kwwwwwwk", "kwkkkkwk", "kkkkkkkk"]


def 饿饿(t):
    f = Frame()
    rumble = t % 4 < 2
    crab(f, dx=(1 if rumble and t % 2 else 0), eyes="flat", sx=1.04, sy=0.94, mouth_pat=[".##.", "#..#"])
    f.box(16, 12, 2, 2, "#DDDDDD"); f.box(20, 8, 3, 3, "#DDDDDD")      # 想吃的泡泡
    f.box(25, 0, 22, 18, "#DDDDDD"); f.box(26, 1, 20, 16, WHITE)
    for r, row in enumerate(RICE):
        for k, ch in enumerate(row):
            if ch != ".":
                f.box(28 + k * 2, 3 + r * 2 - (1 if rumble else 0), 2, 2, DARK if ch == "k" else WHITE if ch == "w" else ch)
    return f


# ---------------- 第二批（11-01）：带小道具和小故事的 ----------------
NOTE = ["..##", "..#.", "..#.", "###.", "###."]
HEART_EYE = [".r.r.", "rrrrr", ".rrr.", "..r.."]
GREEN, PINK2 = "#5DAA4A", "#E8456B"
STAND_RUN = STAND[:-2] + [".11....11.", ".11....11."]


def line(f, x0, y0, x1, y1, c, w=1):
    n = max(abs(x1 - x0), abs(y1 - y0), 1)
    for i in range(n + 1):
        f.box(round(x0 + (x1 - x0) * i / n), round(y0 + (y1 - y0) * i / n), w, w, c)


def 送你花(t):
    f = Frame()
    crab(f, WAVE, dy=bob(t), eyes="happy", blush=True, mouth=True)
    sw = [0, 0, 1, 1, 1, 0, 0, 0, -1, -1, -1, 0][t]          # 花轻轻摇
    line(f, 54, 38, 55 + sw * 2, 16, GREEN, 2)
    f.box(50, 27, 4, 2, GREEN)
    cx, cy = 56 + sw * 2, 11
    for ox, oy in ((0, -4), (4, -1), (3, 4), (-3, 4), (-4, -1)):
        disc(f, cx + ox, cy + oy, 2, PINK)
    disc(f, cx, cy, 2, YEL)
    if t % 6 < 3:
        f.pat(6, 12, HEART_S, RED)
    return f


def 转圈圈(t):
    f = Frame()
    c = math.cos(2 * math.pi * t / N)                       # 原地转一圈：转到背面就看不见脸
    front = c > 0
    crab(f, eyes="happy" if front else None, blush=front, mouth=front, sx=max(0.18, abs(c)))
    for k in range(4):
        a = 2 * math.pi * (t / N + k / 4)
        if (t + k) % 2:
            f.pat(30 + round(26 * math.cos(a)), 20 + round(8 * math.sin(a)), SPARK, YEL)
    return f


def 喝奶茶(t):
    f = Frame()
    crab(f, dx=-6, sx=0.92, eyes="happy" if t % 8 < 6 else "line", blush=True, mouth_pat=[".#."])
    x0, y0, w, h = 46, 30, 14, 26                           # 一杯珍珠奶茶，越喝越少
    f.box(x0 - 1, y0 - 1, w + 2, h + 2, "#B89A7A"); f.box(x0, y0, w, h, PAPER)
    lv = y0 + 3 + t // 2
    f.box(x0, lv, w, y0 + h - lv, "#D9A066")
    for x, y in ((2, 4), (6, 3), (10, 4), (4, 7), (9, 7)):
        f.box(x0 + x, y0 + h - y, 2, 2, "#3B2416")
    f.box(x0 - 2, y0 - 3, w + 4, 3, PINK)
    line(f, x0 + 8, y0 - 3, x0 + 3, y0 - 15, PINK2, 2)
    if t % 4 < 2:
        disc(f, x0 + 1, y0 - 19 - t % 4, 1, "#C8C8C8")
    return f


def 打滚(t):
    f = Frame()
    tmp = Frame()
    crab(tmp, eyes="happy", blush=True, mouth=True, shadow=False)
    k, cx, cy = t // 3, 32, 47                              # 每 3 帧翻 90 度
    pts = []
    for y in range(S):
        for x in range(S):
            c = tmp.p[y][x]
            if c:
                u, v = x, y
                for _ in range(k):
                    u, v = cx - (v - cy), cy + (u - cx)
                pts.append((u, v, c))
    bx = (min(p[0] for p in pts) + max(p[0] for p in pts)) // 2
    by = max(p[1] for p in pts)
    f.box(14, S - 2, 36, 2, SHADOW)
    for x, y, c in pts:
        f.dot(x - bx + 32, y - by + S - 3, c)
    if t % 3 == 0:                                          # 每翻一下扬起一点灰
        for d in (-1, 1):
            disc(f, 32 + d * 26, S - 6, 2, "#DDDDDD")
    return f


def 打电话(t):
    f = Frame()
    crab(f, WAVE, dx=-4, eyes="happy", blush=True, mouth_pat=MOUTH if t % 4 < 2 else [".##.", "#..#", ".##."])
    f.box(47, 22, 9, 16, DARK); f.box(48, 24, 7, 11, BLUE); f.box(50, 36, 3, 1, "#888888")
    for k in range(2):
        ph = (t + k * 6) % N
        f.pat(52 + ph // 3, 18 - ph * 2, HEART_S, RED if k else PINK)
    return f


def 撑伞(t):
    f = Frame()
    crab(f, dy=bob(t), eyes="happy", blush=True, mouth=True)
    cx, cy, r = 32, 22, 20                                  # 一把粉红条纹伞
    for y in range(cy - r, cy + 1):
        for x in range(cx - r, cx + r + 1):
            if (x - cx) ** 2 + (y - cy) ** 2 <= r * r:
                f.dot(x, y, PINK if (x - cx + 40) // 7 % 2 else PINK2)
    f.box(31, 0, 2, 3, "#8A5A3C"); f.box(31, cy, 2, 12, "#8A5A3C")
    for k in range(8):                                      # 伞外面在下雨
        x = (2, 6, 9, 55, 58, 62, 4, 60)[k]
        y = (t * 5 + k * 11) % 58
        f.box(x, y, 1, 3, BLUE)
    return f


def 生日快乐(t):
    f = Frame()
    crab(f, WAVE, dx=-12, sx=0.8, sy=0.9, eyes="happy", blush=True, mouth=True)
    f.box(36, 47, 24, 14, PAPER); f.box(35, 46, 26, 1, "#D8C0A0"); f.box(35, 61, 26, 1, "#D8C0A0")
    f.box(36, 46, 24, 4, PINK)
    for x in (38, 44, 50, 56):
        f.box(x, 50, 2, 2 + x % 3, PINK)
        f.box(x, 44, 2, 2, RED)
    f.box(47, 36, 2, 9, BLUE)
    big = t % 4 < 2
    f.box(47, 31 if big else 32, 2, 5 if big else 4, YEL); f.box(47, 34, 2, 2, "#FF8C2A")
    for k in range(6):
        x, y = (k * 17 + 5) % 60, (k * 13 + t * 3) % 30
        f.box(x, y, 2, 2, CONF[k % 5])
    return f


def 爱你(t):
    f = Frame()
    up = 1 if t % 6 < 3 else 0
    pos = crab(f, WAVE, dy=-up, eyes=None, blush=True, mouth=True)
    for i, (x, y) in enumerate(pos):                        # 爱心眼，一跳一跳
        f.pat(x - (0 if up else 0), y, HEART_EYE, RED)
    words(f, "爱你", 14, 3 - up, 36, color=RED, bg="#FFE3EA")
    for k in range(2):
        ph = (t + k * 6) % N
        f.pat(4 + k * 50, 30 - ph * 2, HEART_S, PINK)
    return f


def 躺平(t):
    f = Frame()
    k = min(t, 6) / 6                                       # 慢慢化成一摊
    crab(f, eyes="flat", sx=1 + 0.3 * k, sy=1 - 0.45 * k, mouth_pat=["###"] if k == 1 else None)
    if k == 1 and t % 4 < 3:
        for i in range(t - 6):
            f.box(46 + i * 5, 34 - i * 3, 4 - i % 2, 1, BLUE)
    return f


def 跳舞(t):
    f = Frame()
    up = t // 3 % 2
    dy, sx, sy = hop(t * 2 % N, 3)
    crab(f, RAISE if up else WAVE, dx=3 if up else -3, dy=dy, eyes="happy", blush=True, mouth=True, sx=sx, sy=sy)
    for k in range(3):
        ph = (t + k * 4) % N
        f.pat((6, 52, 28)[k] + (1 if ph % 4 < 2 else -1), 26 - ph * 2, NOTE, (BLUE, PINK2, "#B48AE0")[k])
    return f


def 冲呀(t):
    f = Frame()
    step = t % 4 < 2
    crab(f, STAND_RUN if step else STAND, dx=4, dy=-(1 if step else 0), eyes="angry", mouth_pat=["####", "#..#"], sx=1.04)
    for k, y in enumerate((34, 42, 50)):                    # 速度线 + 脚后跟的灰
        f.box(0 + (t + k) % 3, y, 6 - k, 1, "#BBBBBB")
    for k in range(2):
        ph = (t + k * 3) % 6
        disc(f, 8 - ph * 2, S - 4 - ph // 2, 2 - ph // 3, "#DDDDDD")
    return f


def 洗澡(t):
    f = Frame()
    crab(f, dy=2 + (1 if t % 6 < 3 else 0), sx=0.8, eyes="happy", blush=True, mouth=True, shadow=False)
    f.box(3, 49, 58, 13, "#9FC9E8"); f.box(4, 50, 56, 11, WHITE); f.box(4, 50, 56, 3, "#BFE3FF")
    f.box(8, 62, 4, 2, "#9FC9E8"); f.box(52, 62, 4, 2, "#9FC9E8")
    d = 1 if t % 6 < 3 else 0                               # 小黄鸭跟着水晃
    f.box(52, 44 + d, 9, 6, YEL); f.box(55, 38 + d, 6, 6, YEL); f.box(61, 41 + d, 2, 2, "#FF8C2A"); f.dot(58, 40 + d, DARK)
    for k in range(5):
        ph = (t + k * 5) % N
        x, y = (6, 14, 50, 40, 24)[k] + (1 if ph % 4 < 2 else 0), 34 - ph * 3
        disc(f, x, y, 3 - k % 2, "#BFE3FF"); disc(f, x, y, 2 - k % 2, WHITE)
    return f


def 许愿(t):
    f = Frame()
    crab(f, eyes="line", blush=True, mouth=True, dy=bob(t))
    x, y = 62 - t * 5, 2 + t * 2                            # 流星划过去
    for i in range(1, 6):
        f.box(x + i * 3, y - i, 2, 1, "#FFE9A0" if i > 2 else YEL)
    f.pat(x - 2, y - 2, STAR, YEL)
    for k, (px, py) in enumerate([(8, 6), (20, 14), (50, 22)]):
        if (t + k) % 3:
            f.pat(px, py, SPARK, "#FFE9A0")
    return f


def 好吃(t):
    f = Frame()
    chew = t % 4 < 2
    crab(f, dx=-4, eyes="happy", blush=True, sx=1.06 if chew else 1.0, mouth_pat=[".##.", "#..#"] if chew else ["####"])
    disc(f, 53, 40, 6, PINK2)                               # 一颗草莓，咬一口少一块
    if t % 6 >= 3:
        disc(f, 47, 38, 3, None)
    for x, y in ((51, 38), (55, 40), (52, 43), (56, 36)):
        if f.get(x, y):
            f.dot(x, y, YEL)
    f.box(50, 32, 7, 2, GREEN); f.box(52, 30, 3, 2, GREEN)
    for k, (px, py) in enumerate([(6, 14), (30, 4), (58, 18)]):
        if (t + k) % 3:
            f.pat(px, py, SPARK, YEL)
    return f


def 求抱抱(t):
    f = Frame()
    dy, sx, sy = hop(t, 3)
    crab(f, RAISE, dy=dy, eyes="wet", blush=True, mouth_pat=[".##.", "#..#"], sx=sx, sy=sy)
    for k in range(2):
        ph = (t + k * 6) % N
        f.pat((20, 38)[k], 22 - ph * 2, HEART_S, PINK)
    return f


def 加油(t):
    f = Frame()
    up = t % 4 < 2
    crab(f, RAISE, eyes="normal", blush=True, mouth_pat=[".##.", "#..#", ".##."])
    for x, d in ((9, up), (54, not up)):                    # 两团彩球一上一下
        cy = 24 - (3 if d else 0)
        disc(f, x, cy, 5, YEL); disc(f, x - 1, cy - 1, 2, "#FFE9A0")
        for i in range(3):
            f.dot(x - 4 + i * 4, cy + 5, PINK2)
    words(f, "加油", 20, 2, 24, h=16, color=PINK2, bg=PAPER, size=14)
    return f


def 发呆(t):
    f = Frame()
    a = 2 * math.pi * t / N                                 # 一只小蝴蝶绕着飞，眼睛跟着转
    bx, by = 32 + round(22 * math.cos(a)), 16 + round(7 * math.sin(a))
    pos = crab(f, eyes=None, mouth_pat=[".#."])
    look = (bx - 32) // 10
    for i, (x, y) in enumerate(pos):
        f.pat(x + look + (1 if i else 0), y, EYES["normal"], DARK, mirror=(i == 1))
    flap = t % 2
    f.box(bx - 3, by - 2 + flap, 3, 3 - flap, "#B48AE0"); f.box(bx + 1, by - 2 + flap, 3, 3 - flap, "#B48AE0")
    f.box(bx - 2, by + 1, 2, 2, PINK); f.box(bx + 1, by + 1, 2, 2, PINK); f.box(bx, by - 2, 1, 5, DARK)
    return f


陪我 = sign("陪我")


ALL = {k: v for k, v in list(globals().items()) if callable(v) and not k.isascii()}


def dark(f):
    """深色版：去掉地上的影子，外面描一圈白边，贴在黑底上也看得清。"""
    for row in f.p:
        for x, c in enumerate(row):
            if c == SHADOW:
                row[x] = None
    on = {(x, y) for y in range(S) for x in range(S) if f.p[y][x]}
    for x, y in on:
        for dx, dy in ((1, 0), (-1, 0), (0, 1), (0, -1)):
            if (x + dx, y + dy) not in on:
                f.dot(x + dx, y + dy, WHITE)
    return f


def render(name, is_dark=False):
    out = OUT + ("-dark" if is_dark else "")
    os.makedirs(out, exist_ok=True)
    raw = b"".join((dark if is_dark else (lambda f: f))(ALL[name](t)).raw() for t in range(N))
    vf = (f"scale={S * SCALE}:{S * SCALE}:flags=neighbor,split[a][b];[a]palettegen=reserve_transparent=1"
          f":max_colors=24[p];[b][p]paletteuse=dither=none:alpha_threshold=128")
    path = os.path.join(out, f"{name}.gif")
    subprocess.run(["ffmpeg", "-loglevel", "error", "-y", "-f", "rawvideo", "-pix_fmt", "rgba", "-s", f"{S}x{S}",
                    "-r", str(FPS), "-i", "-", "-filter_complex", vf, "-loop", "0", path], input=raw, check=True)
    print(name, "dark" if is_dark else "", os.path.getsize(path) // 1024, "KB")


if __name__ == "__main__":
    for n in sys.argv[1:] or ALL:
        render(n)
        render(n, True)
