"""Bibliothèque de dessins (style plat, couleurs douces) rendus en sprites anticrénelés.
Chaque fabrique renvoie (image RGBA, (ax, ay)) : le point d'ancrage (en général bas-centre)."""
import math
from PIL import Image, ImageDraw

SS = 3  # suréchantillonnage


def hexc(h, a=255):
    h = h.lstrip("#")
    return tuple(int(h[i:i + 2], 16) for i in (0, 2, 4)) + (a,)


def canvas(w, h):
    im = Image.new("RGBA", (int(w * SS), int(h * SS)), (0, 0, 0, 0))
    return im, ImageDraw.Draw(im)


def done(im, w, h, anchor):
    return im.resize((int(w), int(h)), Image.LANCZOS), anchor


class P:
    """Petit assistant : coordonnées en unités du sprite, multipliées par SS."""
    def __init__(self, d):
        self.d = d

    def e(self, x0, y0, x1, y1, c, **kw):
        if "width" in kw: kw["width"] = int(kw["width"] * SS)
        self.d.ellipse([x0 * SS, y0 * SS, x1 * SS, y1 * SS], fill=hexc(c) if isinstance(c, str) else c, **kw)

    def c(self, x, y, r, col, **kw):
        self.e(x - r, y - r, x + r, y + r, col, **kw)

    def r(self, x0, y0, x1, y1, c, rad=0):
        if rad:
            self.d.rounded_rectangle([x0 * SS, y0 * SS, x1 * SS, y1 * SS], radius=rad * SS, fill=hexc(c))
        else:
            self.d.rectangle([x0 * SS, y0 * SS, x1 * SS, y1 * SS], fill=hexc(c))

    def poly(self, pts, c):
        self.d.polygon([(x * SS, y * SS) for x, y in pts], fill=hexc(c))

    def line(self, pts, c, w):
        self.d.line([(x * SS, y * SS) for x, y in pts], fill=hexc(c), width=int(w * SS), joint="curve")

    def arc(self, x0, y0, x1, y1, a0, a1, c, w):
        self.d.arc([x0 * SS, y0 * SS, x1 * SS, y1 * SS], a0, a1, fill=hexc(c), width=int(w * SS))


def face(p, cx, cy, R, mood="happy", eye="#2B2140", cheek="#FF9FB0"):
    ex = R * 0.38
    if mood == "sleep":
        for s in (-1, 1):
            p.arc(cx + s * ex - R * .16, cy - R * .2, cx + s * ex + R * .16, cy + R * .05, 20, 160, "#5A3A2A", R * .07)
    else:
        for s in (-1, 1):
            p.e(cx + s * ex - R * .13, cy - R * .25, cx + s * ex + R * .13, cy + R * .08, eye)
            p.c(cx + s * ex + R * .04, cy - R * .14, R * .05, "#FFFFFF")
    for s in (-1, 1):
        p.e(cx + s * R * .62 - R * .14, cy + R * .1, cx + s * R * .62 + R * .14, cy + R * .26, cheek)
    if mood == "sing":
        p.e(cx - R * .14, cy + R * .2, cx + R * .14, cy + R * .48, "#C2405A")
    elif mood != "sleep":
        p.arc(cx - R * .25, cy + R * .05, cx + R * .25, cy + R * .42, 20, 160, "#7A2A3A", R * .07)


# ------------------------------------------------------------------ décor
def moon(size, face_on=True):
    w = h = size * 1.2
    im, d = canvas(w, h); p = P(d)
    c = w / 2; R = size / 2
    p.c(c, c, R * 1.15, hexc("#FFF6C8", 60))
    p.c(c, c, R, "#FFF1B0")
    p.c(c - R * .35, c + R * .3, R * .12, "#F2E08A"); p.c(c + R * .4, c - R * .35, R * .09, "#F2E08A")
    if face_on:
        face(p, c, c, R * .8, "happy")
    return done(im, w, h, (w / 2, h / 2))


def sun(size):
    w = h = size * 2
    im, d = canvas(w, h); p = P(d)
    c = w / 2; R = size / 2
    for i in range(12):
        a = i * math.pi / 6
        p.poly([(c + math.cos(a - .12) * R * .95, c + math.sin(a - .12) * R * .95),
                (c + math.cos(a) * R * 1.8, c + math.sin(a) * R * 1.8),
                (c + math.cos(a + .12) * R * .95, c + math.sin(a + .12) * R * .95)], "#FFD54A")
    p.c(c, c, R, "#FFC531")
    face(p, c, c, R * .8)
    return done(im, w, h, (w / 2, h / 2))


def star(size, face_on=True, col="#FFD84A"):
    w = h = size * 1.1
    im, d = canvas(w, h); p = P(d)
    c = w / 2; R = size / 2
    pts = []
    for i in range(10):
        a = -math.pi / 2 + i * math.pi / 5
        rr = R if i % 2 == 0 else R * .48
        pts.append((c + math.cos(a) * rr, c + math.sin(a) * rr * 1.0 + R * .06))
    p.poly(pts, col)
    if face_on:
        face(p, c, c + R * .12, R * .42)
    return done(im, w, h, (w / 2, h / 2))


def cloud(size, col="#FFFFFF"):
    w, h = size * 2.2, size * 1.1
    im, d = canvas(w, h); p = P(d)
    for x, y, r in [(.25, .62, .28), (.5, .45, .38), (.75, .62, .28), (.5, .7, .3)]:
        p.c(w * x, h * y, size * r * 1.1, col)
    return done(im, w, h, (w / 2, h / 2))


def house(size, wall="#FFE2B8", roof="#E85A4F", window=True):
    w, h = size * 1.4, size * 1.35
    im, d = canvas(w, h); p = P(d)
    x0, x1, top, base = w * .15, w * .85, h * .45, h
    p.r(x1 - w * .2, h * .12, x1 - w * .1, h * .4, "#B5544A")
    p.r(x0, top, x1, base, wall)
    p.poly([(x0 - w * .08, top + 4), (w / 2, h * .05), (x1 + w * .08, top + 4)], roof)
    p.r(x1 - w * .24, base - h * .3, x1 - w * .1, base, "#9B6A3E", rad=w * .06)
    if window:
        p.c(w * .38, h * .68, w * .12, "#FFF6DC")
        p.c(w * .38, h * .68, w * .12, hexc("#8B5A2B"), outline=hexc("#8B5A2B"), width=0)
        p.c(w * .38, h * .68, w * .1, "#FFF6DC")
    return done(im, w, h, (w / 2, h))


def tree(size, col="#5DB55A", trunk="#8B5A2B", fruit=None):
    w, h = size * 1.1, size * 1.4
    im, d = canvas(w, h); p = P(d)
    p.r(w * .44, h * .55, w * .56, h, trunk)
    for x, y, r in [(.5, .32, .32), (.3, .45, .25), (.7, .45, .25), (.5, .5, .28)]:
        p.c(w * x, h * y, w * r, col)
    if fruit:
        for x, y in [(.35, .35), (.6, .3), (.45, .52), (.7, .5), (.28, .5)]:
            p.c(w * x, h * y, w * .045, fruit)
    return done(im, w, h, (w / 2, h))


def fir(size, snow=True, deco=True):
    w, h = size * 1.0, size * 1.45
    im, d = canvas(w, h); p = P(d)
    p.r(w * .44, h * .86, w * .56, h, "#7A4A28")
    for i, (y0, y1, ww) in enumerate([(.08, .42, .32), (.25, .62, .4), (.42, .88, .48)]):
        p.poly([(w * .5, h * y0), (w * (.5 + ww), h * y1), (w * (.5 - ww), h * y1)], "#2E8B57")
        if snow:
            p.poly([(w * .5, h * y0), (w * (.5 + ww * .35), h * (y0 + (y1 - y0) * .35)),
                    (w * (.5 - ww * .35), h * (y0 + (y1 - y0) * .35))], "#F4FBFF")
    if deco:
        for x, y, c in [(.42, .35, "#FF5A5A"), (.6, .5, "#4AA8FF"), (.36, .58, "#FFD24A"), (.55, .72, "#FF5A5A"),
                        (.7, .78, "#FFD24A"), (.3, .8, "#4AA8FF"), (.5, .62, "#C77DFF")]:
            p.c(w * x, h * y, w * .04, c)
    return done(im, w, h, (w / 2, h))


def tree_star(size):
    return star(size, face_on=False, col="#FFD84A")


def barn(size):
    w, h = size * 1.5, size * 1.3
    im, d = canvas(w, h); p = P(d)
    p.r(w * .1, h * .4, w * .9, h, "#D9473F")
    p.poly([(w * .02, h * .45), (w * .5, h * .05), (w * .98, h * .45)], "#8C2F2A")
    p.r(w * .35, h * .55, w * .65, h, "#FFF4E0")
    p.r(w * .38, h * .58, w * .62, h, "#C9493F")
    p.line([(w * .38, h * .58), (w * .62, h)], "#FFF4E0", w * .02)
    p.line([(w * .62, h * .58), (w * .38, h)], "#FFF4E0", w * .02)
    p.r(w * .44, h * .22, w * .56, h * .36, "#FFF4E0")
    return done(im, w, h, (w / 2, h))


def fence(length, size):
    w, h = length, size
    im, d = canvas(w, h); p = P(d)
    p.r(0, h * .3, w, h * .42, "#FFF4E0"); p.r(0, h * .62, w, h * .74, "#FFF4E0")
    x = 6
    while x < w - 6:
        p.poly([(x - 9, h), (x - 9, h * .1), (x, 0), (x + 9, h * .1), (x + 9, h)], "#FFF4E0")
        x += 46
    return done(im, w, h, (w / 2, h))


def bridge(width, height, col="#C9B79C"):
    w, h = width, height
    im, d = canvas(w, h); p = P(d)
    p.r(0, h * .18, w, h * .32, col)
    p.r(0, 0, w, h * .06, "#A89478")
    for i in range(12):
        p.r(w * i / 12 + 4, h * .03, w * i / 12 + 14, h * .2, "#A89478")
    n = 3
    for i in range(n):
        x0 = w * i / n
        p.r(x0, h * .3, x0 + w / n, h, col)
        p.e(x0 + w / n * .15, h * .48, x0 + w / n * .85, h * 1.5, (0, 0, 0, 0))
    # arches : on « creuse » en peignant la couleur transparente
    for i in range(n):
        x0 = w * i / n
        d.ellipse([(x0 + w / n * .15) * SS, h * .48 * SS, (x0 + w / n * .85) * SS, h * 1.55 * SS], fill=(0, 0, 0, 0))
    return done(im, w, h, (w / 2, h))


def boat(size, col="#E85A4F"):
    w, h = size * 1.6, size * .7
    im, d = canvas(w, h); p = P(d)
    p.poly([(w * .02, h * .25), (w * .98, h * .25), (w * .8, h * .95), (w * .2, h * .95)], col)
    p.r(w * .02, h * .2, w * .98, h * .32, "#FFF4E0")
    return done(im, w, h, (w / 2, h * .55))


def oar(size):
    w, h = size * 1.4, size * .3
    im, d = canvas(w, h); p = P(d)
    p.line([(w * .05, h * .5), (w * .8, h * .5)], "#9B6A3E", h * .18)
    p.e(w * .72, h * .1, w * .98, h * .9, "#9B6A3E")
    return done(im, w, h, (w * .3, h * .5))


def cake(size):
    w, h = size * 1.4, size * 1.2
    im, d = canvas(w, h); p = P(d)
    p.e(w * .02, h * .86, w * .98, h, "#E0E0EA")
    p.r(w * .1, h * .55, w * .9, h * .92, "#FFB6C9", rad=w * .04)
    p.r(w * .18, h * .3, w * .82, h * .58, "#FFE3EC", rad=w * .04)
    for i in range(8):
        p.c(w * (.14 + i * .1), h * .56, w * .045, "#FFFFFF")
    for i in range(6):
        p.c(w * (.24 + i * .1), h * .32, w * .035, "#FF6F91")
    for i in range(3):
        x = w * (.35 + i * .15)
        p.r(x - w * .02, h * .1, x + w * .02, h * .31, ["#6EC6FF", "#FFD24A", "#8BE28B"][i])
    return done(im, w, h, (w / 2, h))


def flame(size):
    w, h = size * .5, size * .8
    im, d = canvas(w, h); p = P(d)
    p.e(w * .1, h * .25, w * .9, h, "#FFB020")
    p.e(w * .3, h * .5, w * .7, h * .95, "#FFF2A0")
    p.poly([(w * .5, 0), (w * .85, h * .55), (w * .15, h * .55)], "#FFB020")
    return done(im, w, h, (w / 2, h))


def balloon(size, col):
    w, h = size, size * 2.2
    im, d = canvas(w, h); p = P(d)
    p.line([(w * .5, h * .45), (w * .45, h * .7), (w * .55, h)], "#888888", 2)
    p.e(w * .08, 0, w * .92, h * .46, col)
    p.e(w * .22, h * .06, w * .38, h * .18, hexc("#FFFFFF", 120))
    p.poly([(w * .5, h * .44), (w * .42, h * .5), (w * .58, h * .5)], col)
    return done(im, w, h, (w / 2, h))


def stall(size):
    w, h = size * 1.8, size * 1.4
    im, d = canvas(w, h); p = P(d)
    p.r(w * .05, h * .55, w * .95, h, "#C98A4B")
    p.r(w * .1, h * .2, w * .14, h * .6, "#9B6A3E"); p.r(w * .86, h * .2, w * .9, h * .6, "#9B6A3E")
    for i in range(8):
        p.r(w * (.02 + i * .12), h * .08, w * (.14 + i * .12), h * .24, "#FF6F61" if i % 2 == 0 else "#FFF4E0")
        p.e(w * (.02 + i * .12), h * .17, w * (.14 + i * .12), h * .31, "#FF6F61" if i % 2 == 0 else "#FFF4E0")
    return done(im, w, h, (w / 2, h))


def bun(size):
    w, h = size, size * .8
    im, d = canvas(w, h); p = P(d)
    p.e(0, h * .1, w, h, "#D98C3A")
    p.e(w * .1, h * .15, w * .9, h * .7, "#E8A458")
    p.line([(w * .5, h * .18), (w * .5, h * .78)], "#FFF4E0", w * .08)
    p.line([(w * .15, h * .45), (w * .85, h * .45)], "#FFF4E0", w * .08)
    return done(im, w, h, (w / 2, h))


def window_frame(size):
    w = h = size
    im, d = canvas(w, h); p = P(d)
    p.c(w / 2, h / 2, w * .48, "#8B5A2B")
    d.ellipse([w * .08 * SS, h * .08 * SS, w * .92 * SS, h * .92 * SS], fill=(0, 0, 0, 0))
    return done(im, w, h, (w / 2, h / 2))


def bell(size):
    w = h = size
    im, d = canvas(w, h); p = P(d)
    c = w / 2
    p.r(c - w * .03, c - h * .05, c + w * .03, c + h * .05, "#7A5A20")
    p.e(c - w * .2, c, c + w * .2, c + h * .5, "#FFC23A")
    p.poly([(c - w * .2, c + h * .25), (c + w * .2, c + h * .25), (c + w * .3, c + h * .42), (c - w * .3, c + h * .42)], "#FFC23A")
    p.e(c - w * .3, c + h * .38, c + w * .3, c + h * .46, "#E39A16")
    p.c(c, c + h * .47, w * .06, "#B57212")
    return done(im, w, h, (w / 2, h / 2))


def tower(size):
    w, h = size * .8, size * 2.2
    im, d = canvas(w, h); p = P(d)
    p.r(w * .12, h * .25, w * .88, h, "#F2E6D0")
    p.r(w * .25, h * .3, w * .75, h * .5, "#5B4A6E")
    p.e(w * .25, h * .27, w * .75, h * .37, "#5B4A6E")
    p.poly([(w * .02, h * .26), (w * .5, h * .02), (w * .98, h * .26)], "#4F7FD9")
    p.r(w * .4, h * .85, w * .6, h, "#9B6A3E", rad=w * .1)
    return done(im, w, h, (w / 2, h))


def candy_jar(size):
    w, h = size, size * 1.2
    im, d = canvas(w, h); p = P(d)
    p.r(w * .08, h * .2, w * .92, h, hexc("#D8F1FF", 170)[:3] and "#D8F1FF", rad=w * .15)
    import random
    rnd = random.Random(4)
    for _ in range(26):
        x, y = rnd.uniform(.2, .8), rnd.uniform(.35, .92)
        p.c(w * x, h * y, w * .07, rnd.choice(["#FF6F91", "#FFD24A", "#7BD389", "#6EC6FF", "#C77DFF"]))
    p.r(w * .2, h * .08, w * .8, h * .22, "#FF6F91", rad=w * .05)
    return done(im, w, h, (w / 2, h))


def lollipop(size, col="#FF6F91"):
    w, h = size, size * 2
    im, d = canvas(w, h); p = P(d)
    p.r(w * .46, h * .45, w * .54, h, "#FFFFFF")
    p.c(w / 2, h * .25, w * .45, col)
    p.arc(w * .2, h * .05, w * .8, h * .45, 0, 300, "#FFFFFF", w * .06)
    return done(im, w, h, (w / 2, h))


def snowman(size):
    w, h = size, size * 1.6
    im, d = canvas(w, h); p = P(d)
    p.c(w * .5, h * .74, w * .38, "#FFFFFF")
    p.c(w * .5, h * .38, w * .27, "#FFFFFF")
    face(p, w * .5, h * .38, w * .2)
    p.poly([(w * .5, h * .4), (w * .75, h * .43), (w * .5, h * .45)], "#FF8C2A")
    p.r(w * .3, h * .08, w * .7, h * .18, "#2B2140"); p.r(w * .22, h * .17, w * .78, h * .2, "#2B2140")
    p.r(w * .25, h * .52, w * .75, h * .58, "#E85A4F")
    return done(im, w, h, (w / 2, h))


def clock(size):
    w, h = size * .9, size * 2.2
    im, d = canvas(w, h); p = P(d)
    p.r(w * .1, h * .3, w * .9, h, "#A0522D", rad=w * .08)
    p.poly([(w * .05, h * .32), (w * .5, h * .12), (w * .95, h * .32)], "#8B4513")
    p.c(w * .5, h * .42, w * .32, "#FFF8E8")
    p.line([(w * .5, h * .42), (w * .5, h * .33)], "#2B2140", w * .04)
    p.line([(w * .5, h * .42), (w * .62, h * .44)], "#2B2140", w * .04)
    p.r(w * .3, h * .6, w * .7, h * .92, "#5A3A2A", rad=w * .05)
    return done(im, w, h, (w / 2, h))


def pendulum(size):
    w, h = size * .3, size * .7
    im, d = canvas(w, h); p = P(d)
    p.line([(w / 2, 0), (w / 2, h * .75)], "#FFC23A", w * .1)
    p.c(w / 2, h * .82, w * .35, "#FFC23A")
    return done(im, w, h, (w / 2, 0))


# ------------------------------------------------------------------ personnages
def critter(size, kind="lamb", mood="happy", col=None):
    """Personnage mignon générique (debout, ancré au sol)."""
    w, h = size * 1.3, size * 1.6
    im, d = canvas(w, h); p = P(d)
    cx = w / 2
    body = {"lamb": "#FFFFFF", "sheep": "#3A3A44", "mouse": "#9AA5B1", "cow": "#FFFFFF", "pig": "#FFB3C6",
            "duck": "#FFD84A", "girl": "#FF8FB1", "boy": "#6EC6FF", "pierrot": "#FFFFFF", "bear": "#B07A4E",
            "cat": "#F2A65A", "wolf": "#8E9AAF", "egg": "#FFF4E0", "frog": "#7BD389"}[kind]
    if col:
        body = col
    skin = {"girl": "#FFD9BC", "boy": "#FFD9BC", "pierrot": "#FFFFFF", "lamb": "#FFE7D6", "sheep": "#5A5A66",
            "egg": "#FFF4E0"}.get(kind, body)
    R = size * .3
    hy = h * .41
    by = h * .74
    # corps / jambes
    if kind != "egg":
        p.r(cx - R * .55, h * .86, cx - R * .25, h, "#5A4A44" if kind not in ("duck",) else "#FF8C2A", rad=R * .1)
        p.r(cx + R * .25, h * .86, cx + R * .55, h, "#5A4A44" if kind not in ("duck",) else "#FF8C2A", rad=R * .1)
    if kind in ("lamb", "sheep"):
        wool = "#FFFFFF" if kind == "lamb" else "#3A3A44"
        for a in range(10):
            ang = a * math.pi / 5
            p.c(cx + math.cos(ang) * R * .75, by + math.sin(ang) * R * .45, R * .35, wool)
        p.e(cx - R * .9, by - R * .55, cx + R * .9, by + R * .5, wool)
    elif kind == "egg":
        p.e(cx - R * 1.1, h * .15, cx + R * 1.1, h, body)
    elif kind in ("girl",):
        p.poly([(cx, by - R * .7), (cx + R * .95, h * .9), (cx - R * .95, h * .9)], body)
    elif kind == "pierrot":
        p.poly([(cx, by - R * .7), (cx + R * .9, h * .9), (cx - R * .9, h * .9)], "#FFFFFF")
        for yy in (.62, .74, .86):
            p.c(cx, h * yy, R * .1, "#2B2140")
    else:
        p.e(cx - R * .95, by - R * .85, cx + R * .95, by + R * .55, body)
        if kind == "cow":
            p.c(cx - R * .3, by - R * .1, R * .25, "#2B2140"); p.c(cx + R * .4, by + R * .2, R * .18, "#2B2140")
        if kind == "duck":
            p.e(cx + R * .3, by - R * .4, cx + R * 1.1, by + R * .2, "#F5C93A")
    # oreilles / accessoires derrière la tête
    if kind == "mouse":
        p.c(cx - R * .75, hy - R * .7, R * .45, body); p.c(cx + R * .75, hy - R * .7, R * .45, body)
        p.c(cx - R * .75, hy - R * .7, R * .28, "#FFB3C6"); p.c(cx + R * .75, hy - R * .7, R * .28, "#FFB3C6")
        p.line([(cx + R * .8, by + R * .3), (cx + R * 1.5, by), (cx + R * 1.6, by - R * .5)], body, R * .1)
    if kind in ("cat", "wolf"):
        for s in (-1, 1):
            p.poly([(cx + s * R * .9, hy - R * .3), (cx + s * R * .75, hy - R * 1.25), (cx + s * R * .2, hy - R * .75)], body)
    if kind in ("bear",):
        p.c(cx - R * .75, hy - R * .7, R * .3, body); p.c(cx + R * .75, hy - R * .7, R * .3, body)
    if kind == "cow":
        for s in (-1, 1):
            p.poly([(cx + s * R * .5, hy - R * .7), (cx + s * R * .95, hy - R * 1.2), (cx + s * R * .8, hy - R * .6)], "#F2E6D0")
            p.e(cx + s * R * 1.05 - R * .3, hy - R * .45, cx + s * R * 1.05 + R * .3, hy - R * .15, body)
    if kind in ("lamb", "sheep"):
        for s in (-1, 1):
            p.e(cx + s * R * .95 - R * .35, hy - R * .25, cx + s * R * .95 + R * .35, hy + R * .1, skin)
    if kind == "pig":
        for s in (-1, 1):
            p.poly([(cx + s * R * .4, hy - R * .7), (cx + s * R * .9, hy - R * 1.05), (cx + s * R * .85, hy - R * .4)], "#FF9AB3")
    # tête
    if kind == "egg":
        face(p, cx, h * .45, R * .9, mood)
        return done(im, w, h, (w / 2, h))
    if kind in ("girl", "boy"):
        hair = "#7A4A28" if kind == "girl" else "#3A2A20"
        p.c(cx, hy, R * 1.05, hair)
        if kind == "girl":
            p.c(cx - R * 1.05, hy + R * .3, R * .38, hair); p.c(cx + R * 1.05, hy + R * .3, R * .38, hair)
    p.c(cx, hy, R, skin)
    if kind in ("lamb", "sheep"):
        for a in range(7):
            ang = math.pi + a * math.pi / 6
            p.c(cx + math.cos(ang) * R * .65, hy + math.sin(ang) * R * .75, R * .3, "#FFFFFF" if kind == "lamb" else "#3A3A44")
    if kind == "girl":
        p.e(cx - R * .95, hy - R * 1.05, cx + R * .95, hy - R * .25, hair)
        p.c(cx + R * .75, hy - R * .85, R * .25, "#FF6F91")
    if kind == "boy":
        p.e(cx - R * .95, hy - R * 1.0, cx + R * .95, hy - R * .3, hair)
    if kind == "pierrot":
        p.poly([(cx - R * .9, hy - R * .55), (cx, hy - R * 2.0), (cx + R * .9, hy - R * .55)], "#FFFFFF")
        p.c(cx, hy - R * 2.0, R * .15, "#2B2140")
        p.c(cx, hy + R * .9, R * .5, "#FFFFFF")
    face(p, cx, hy + R * .05, R * .95, mood, cheek="#FF9FB0")
    if kind == "pig":
        p.e(cx - R * .3, hy + R * .15, cx + R * .3, hy + R * .5, "#FF8FAA")
        p.c(cx - R * .12, hy + R * .32, R * .06, "#B0506A"); p.c(cx + R * .12, hy + R * .32, R * .06, "#B0506A")
    if kind == "duck":
        p.e(cx - R * .35, hy + R * .2, cx + R * .35, hy + R * .48, "#FF8C2A")
    if kind == "cow":
        p.e(cx - R * .5, hy + R * .25, cx + R * .5, hy + R * .75, "#FFC9D6")
    if kind == "pierrot":
        p.e(cx - R * .1, hy - R * .1, cx + R * .1, hy + R * .25, hexc("#2B2140", 160))
    return done(im, w, h, (w / 2, h))


FACTORIES = dict(moon=moon, sun=sun, star=star, cloud=cloud, house=house, tree=tree, fir=fir, barn=barn,
                 fence=fence, bridge=bridge, boat=boat, oar=oar, cake=cake, flame=flame, balloon=balloon,
                 stall=stall, bun=bun, window_frame=window_frame, bell=bell, tower=tower, candy_jar=candy_jar,
                 lollipop=lollipop, snowman=snowman, clock=clock, pendulum=pendulum, critter=critter)
