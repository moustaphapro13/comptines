"""Rendu vidéo de Frère Jacques (16:9 ou 9:16). Usage :
python3 render.py long|short [t1 t2 ...]   -> PNG de contrôle aux instants donnés
python3 render.py long|short full          -> vidéo complète
"""
import sys, math, subprocess, os
import numpy as np
from PIL import Image, ImageDraw, ImageFont, ImageFilter
from song import PHRASES, BEAT, timeline, render_audio

FONT = "/usr/share/fonts/truetype/google-fonts/Poppins-Bold.ttf"
FPS = 30

LAYOUTS = {
    "long": dict(W=1920, H=1080, ground=760, hx=520, tx=1450, k=1.0, sunx=960, th=470,
                 py=955, pw=1720, ph=170, fs=84, rows=1, ty=150, tfs=120),
    "short": dict(W=1080, H=1920, ground=1150, hx=330, tx=820, k=0.92, sunx=560, th=560,
                  py=1450, pw=1000, ph=330, fs=82, rows=2, ty=230, tfs=118),
}

def font(sz):
    return ImageFont.truetype(FONT, sz)

def ease(x):
    x = min(1, max(0, x)); return x * x * (3 - 2 * x)

def hexc(h, a=255):
    h = h.lstrip("#"); return tuple(int(h[i:i+2], 16) for i in (0, 2, 4)) + (a,)

def ss_draw(w, h, fn, scale=2):
    """Dessin suréchantillonné (anticrénelage) -> RGBA w x h."""
    im = Image.new("RGBA", (w * scale, h * scale), (0, 0, 0, 0))
    fn(ImageDraw.Draw(im), scale)
    return im.resize((w, h), Image.LANCZOS)


# ---------------------------------------------------------------- calques fixes
def sky(L, night):
    W, H = L["W"], L["H"]
    top, bot = ((14, 27, 68), (52, 64, 122)) if night else ((110, 196, 242), (214, 242, 255))
    y = np.linspace(0, 1, H)[:, None, None]
    arr = (np.array(top) * (1 - y) + np.array(bot) * y) * np.ones((1, W, 1))
    img = Image.fromarray(arr.astype(np.uint8), "RGB")
    d = ImageDraw.Draw(img)
    if night:
        rng = np.random.default_rng(3)
        for _ in range(int(W * H / 9000)):
            x, yy = rng.integers(0, W), rng.integers(0, int(L["ground"] * 0.85))
            r = rng.choice([1, 1, 2, 2, 3])
            d.ellipse([x - r, yy - r, x + r, yy + r], fill=(255, 250, 220))
        # lune
        mx, my = int(W * 0.12), int(L["ground"] * 0.22)
        d.ellipse([mx - 55, my - 55, mx + 55, my + 55], fill=(255, 244, 200))
        d.ellipse([mx - 25, my - 70, mx + 85, my + 40], fill=tuple(int(c) for c in arr[my, mx]))
    # nuages (gris-bleu la nuit)
    if True:
        ccol = (58, 70, 120) if night else (255, 255, 255)
        for cx, cy, s in [(0.33, 0.16, 1.0), (0.62, 0.10, 0.8), (0.88, 0.3, 0.9)]:
            cx, cy = W * cx, L["ground"] * cy
            for dx, dy, r in [(-60, 10, 45), (0, -10, 60), (60, 10, 45), (0, 20, 50)]:
                r *= s
                d.ellipse([cx + dx * s - r, cy + dy * s - r, cx + dx * s + r, cy + dy * s + r], fill=ccol)
    return np.asarray(img).astype(np.float32)


def foreground(L, night):
    W, H, G, k = L["W"], L["H"], L["ground"], L["k"]
    hx, tx = L["hx"], L["tx"]

    def fn(d, s):
        S = lambda v: v * s
        def C(day, nt): return hexc(nt if night else day)
        # collines
        d.ellipse([S(-0.4 * W), S(G - 120), S(0.9 * W), S(G + 500)], fill=C("#8FD47A", "#2F5560"))
        d.ellipse([S(0.45 * W), S(G - 80), S(1.5 * W), S(G + 500)], fill=C("#7CC96B", "#2A4E58"))
        d.rectangle([0, S(G + 60), S(W), S(H)], fill=C("#68B95C", "#24464F"))
        # chemin
        d.polygon([(S(hx + 60 * k), S(G + 40)), (S(hx + 120 * k), S(G + 40)),
                   (S(hx + 260 * k), S(H)), (S(hx - 80 * k), S(H))], fill=C("#E9D3A0", "#4E5468"))
        # fleurs
        rng = np.random.default_rng(7)
        for _ in range(int(W / 25)):
            x, y = rng.uniform(0, W), rng.uniform(G + 80, H)
            col = ["#FF8FB1", "#FFE066", "#FFFFFF", "#B9A6FF"][rng.integers(4)]
            r = rng.uniform(5, 9)
            d.ellipse([S(x - r), S(y - r), S(x + r), S(y + r)], fill=C(col, "#5A6A88"))
        # --- maison
        base = G + 40
        w, h = 440 * k, 320 * k
        x0, x1, top = hx - w / 2, hx + w / 2, base - h
        d.rectangle([S(x1 - 110 * k), S(top - 150 * k), S(x1 - 60 * k), S(top - 40 * k)], fill=C("#B5544A", "#4A3040"))
        d.rectangle([S(x0), S(top), S(x1), S(base)], fill=C("#FFE2B8", "#5E5878"))
        d.polygon([(S(x0 - 40 * k), S(top + 5)), (S(hx), S(top - 200 * k)), (S(x1 + 40 * k), S(top + 5))],
                  fill=C("#E85A4F", "#6A3448"))
        d.rounded_rectangle([S(x1 - 130 * k), S(base - 170 * k), S(x1 - 50 * k), S(base)], radius=S(36 * k),
                            fill=C("#9B6A3E", "#3E3248"))
        d.ellipse([S(x1 - 75 * k), S(base - 90 * k), S(x1 - 63 * k), S(base - 78 * k)], fill=C("#FFD24A", "#8A7A50"))
        wx, wy, wr = hx - 70 * k, base - 175 * k, 100 * k
        d.ellipse([S(wx - wr), S(wy - wr), S(wx + wr), S(wy + wr)], fill=C("#FFF6DC", "#3B355C"))
        # --- clocher
        tb = G + 30
        tw, tt = 210 * k, tb - L["th"] * k
        d.rectangle([S(tx - tw / 2), S(tt), S(tx + tw / 2), S(tb)], fill=C("#F2E6D0", "#58587A"))
        for i in range(6):  # pierres
            yy = tt + 240 * k + i * 50 * k
            if yy > tb - 15: break
            d.line([S(tx - tw / 2), S(yy), S(tx + tw / 2), S(yy)], fill=C("#E0D0B4", "#4C4C6C"), width=S(3))
        d.rounded_rectangle([S(tx - 30 * k), S(tb - 120 * k), S(tx + 30 * k), S(tb)], radius=S(28 * k),
                            fill=C("#9B6A3E", "#3E3248"))
        aw, at, ab = 75 * k, tt + 30 * k, tt + 215 * k
        d.rectangle([S(tx - aw), S(at + aw), S(tx + aw), S(ab)], fill=C("#5B4A6E", "#23203A"))
        d.ellipse([S(tx - aw), S(at), S(tx + aw), S(at + 2 * aw)], fill=C("#5B4A6E", "#23203A"))
        d.rectangle([S(tx - tw / 2 - 12 * k), S(ab), S(tx + tw / 2 + 12 * k), S(ab + 22 * k)], fill=C("#D8C7A8", "#4A4A6A"))
        d.polygon([(S(tx - tw / 2 - 25 * k), S(tt + 2)), (S(tx), S(tt - 230 * k)), (S(tx + tw / 2 + 25 * k), S(tt + 2))],
                  fill=C("#4F7FD9", "#33406E"))
        d.line([S(tx), S(tt - 230 * k), S(tx), S(tt - 300 * k)], fill=C("#555555", "#333344"), width=S(6))
        d.polygon([(S(tx), S(tt - 300 * k)), (S(tx + 70 * k), S(tt - 280 * k)), (S(tx), S(tt - 258 * k))],
                  fill=C("#FFC93C", "#7A6A40"))
    return np.asarray(ss_draw(W, H, fn)).astype(np.float32)


def sun_sprite(r):
    def fn(d, s):
        c = (r * 2) * s
        for i in range(12):
            a = i * math.pi / 6
            d.polygon([(c + math.cos(a - .12) * r * .95 * s, c + math.sin(a - .12) * r * .95 * s),
                       (c + math.cos(a) * r * 1.9 * s, c + math.sin(a) * r * 1.9 * s),
                       (c + math.cos(a + .12) * r * .95 * s, c + math.sin(a + .12) * r * .95 * s)], fill=hexc("#FFD54A"))
        d.ellipse([c - r * s, c - r * s, c + r * s, c + r * s], fill=hexc("#FFC531"))
        d.arc([c - r * .5 * s, c - r * .3 * s, c + r * .5 * s, c + r * .45 * s], 20, 160, fill=hexc("#E0702C"), width=int(6 * s))
        for ex in (-.35, .35):
            d.ellipse([c + (ex * r - 7) * s, c - r * .28 * s, c + (ex * r + 7) * s, c - r * .05 * s], fill=hexc("#7A3A1A"))
    return ss_draw(r * 4, r * 4, fn)


def friar_sprite(R, awake):
    def fn(d, s):
        c = R * s
        d.ellipse([c - R * s, c - R * s, c + R * s, c + R * s], fill=hexc("#8C5A33"))
        fr = R * 0.7
        fy = c + R * 0.12 * s
        d.ellipse([c - fr * s, fy - fr * s, c + fr * s, fy + fr * s], fill=hexc("#FFD9BC"))
        for ex in (-.32, .32):
            ex_ = c + ex * R * s
            ey = fy - R * 0.08 * s
            if awake:
                d.ellipse([ex_ - 13 * s, ey - 17 * s, ex_ + 13 * s, ey + 17 * s], fill=hexc("#FFFFFF"))
                d.ellipse([ex_ - 7 * s, ey - 6 * s, ex_ + 7 * s, ey + 10 * s], fill=hexc("#2B2140"))
                d.arc([ex_ - 16 * s, ey - 36 * s, ex_ + 16 * s, ey - 14 * s], 200, 340, fill=hexc("#6B4026"), width=int(5 * s))
            else:
                d.arc([ex_ - 14 * s, ey - 12 * s, ex_ + 14 * s, ey + 10 * s], 20, 160, fill=hexc("#5A3A2A"), width=int(5 * s))
            d.ellipse([ex_ - 13 * s, fy + R * .12 * s, ex_ + 13 * s, fy + R * .26 * s], fill=hexc("#FFA8A8"))
        my = fy + R * 0.32 * s
        if awake:
            d.chord([c - 24 * s, my - 18 * s, c + 24 * s, my + 22 * s], 0, 180, fill=hexc("#C2405A"))
        else:
            d.ellipse([c - 7 * s, my - 4 * s, c + 7 * s, my + 10 * s], fill=hexc("#B0506A"))
    return ss_draw(2 * R, 2 * R, fn)


def ring_sprite(R, k):
    def fn(d, s):
        c = (R + 14 * k) * s
        d.ellipse([c - (R + 10 * k) * s, c - (R + 10 * k) * s, c + (R + 10 * k) * s, c + (R + 10 * k) * s],
                  outline=hexc("#8B5A2B"), width=int(16 * k * s))
    n = int(2 * (R + 14 * k))
    return ss_draw(n, n, fn)


def bell_sprite(k):
    n = int(220 * k)
    def fn(d, s):
        c = n / 2 * s
        bw, bh = 62 * k * s, 92 * k * s
        d.rectangle([c - 6 * k * s, c - 4 * k * s, c + 6 * k * s, c + 14 * k * s], fill=hexc("#7A5A20"))
        d.chord([c - bw * .7, c + 6 * k * s, c + bw * .7, c + 6 * k * s + bh * 1.0], 180, 360, fill=hexc("#FFC23A"))
        d.polygon([(c - bw * .7, c + 6 * k * s + bh * .5), (c + bw * .7, c + 6 * k * s + bh * .5),
                   (c + bw, c + 6 * k * s + bh), (c - bw, c + 6 * k * s + bh)], fill=hexc("#FFC23A"))
        d.ellipse([c - bw, c + 6 * k * s + bh - 12 * k * s, c + bw, c + 6 * k * s + bh + 12 * k * s], fill=hexc("#E39A16"))
        d.ellipse([c - 14 * k * s, c + bh + 6 * k * s, c + 14 * k * s, c + bh + 34 * k * s], fill=hexc("#B57212"))
    return ss_draw(n, n, fn)


def panel_sprite(w, h):
    def fn(d, s):
        d.rounded_rectangle([6 * s, 12 * s, (w - 6) * s, (h - 2) * s], radius=40 * s, fill=(60, 40, 90, 70))
        d.rounded_rectangle([0, 0, (w - 6) * s, (h - 12) * s], radius=40 * s, fill=(255, 255, 255, 248))
    return ss_draw(w, h, fn)


# ---------------------------------------------------------------- paroles
def layout_lyrics(L):
    """Pour chaque phrase : liste de syllabes (x, y, texte, début, durée, taille)."""
    out = []
    W, pw = L["W"], L["pw"]
    for ph in PHRASES:
        syl, b = [], 0
        for txt, _, dur in ph:
            syl.append([txt, b, dur]); b += dur
        if L["rows"] == 1:
            rows = [syl]
        else:
            cut = next(i for i, s_ in enumerate(syl) if s_[1] >= 4)
            rows = [syl[:cut], syl[cut:]]
        fs = L["fs"]
        while max(font(fs).getlength("".join(s_[0] for s_ in r).rstrip()) for r in rows) > pw - 90:
            fs -= 2
        f = font(fs)
        lh = fs * 1.35
        y0 = L["py"] - lh * len(rows) / 2 + lh * 0.12
        items = []
        for ri, r in enumerate(rows):
            tw = f.getlength("".join(s_[0] for s_ in r).rstrip())
            x = W / 2 - tw / 2
            for txt, st, dur in r:
                wd = f.getlength(txt.rstrip())
                items.append(dict(x=x, y=y0 + ri * lh, t=txt, st=st, dur=dur, cx=x + wd / 2, fs=fs))
                x += f.getlength(txt)
        out.append(items)
    return out


# ---------------------------------------------------------------- moteur
class Scene:
    def __init__(self, kind):
        self.kind = kind
        L = self.L = LAYOUTS[kind]
        self.tl = timeline(kind)
        k = L["k"]
        self.sky_n, self.sky_d = sky(L, True), sky(L, False)
        fn_, fd = foreground(L, True), foreground(L, False)
        self.fg_n, self.fg_d, self.fg_a = fn_[..., :3], fd[..., :3], fd[..., 3:4] / 255.0
        self.sun = sun_sprite(int(80 * k))
        self.friarR = int(88 * k)
        self.friar = {False: friar_sprite(self.friarR, False), True: friar_sprite(self.friarR, True)}
        self.wr = 100 * k
        self.ring = ring_sprite(int(self.wr), k)
        self.bell = bell_sprite(k)
        self.panel = panel_sprite(L["pw"], L["ph"])
        self.lyr = layout_lyrics(L)
        self.fonts = {}
        zf = font(int(54 * k))
        self.z = Image.new("RGBA", (int(70 * k), int(80 * k)), (0, 0, 0, 0))
        ImageDraw.Draw(self.z).text((4, -6), "z", font=zf, fill=(255, 255, 255, 255), stroke_width=3, stroke_fill=(90, 80, 160, 255))
        glow = Image.new("L", (int(self.wr * 3), int(self.wr * 3)), 0)
        ImageDraw.Draw(glow).ellipse([self.wr * .5, self.wr * .5, self.wr * 2.5, self.wr * 2.5], fill=200)
        self.glow = glow.filter(ImageFilter.GaussianBlur(self.wr * 0.35))

    def f(self, sz):
        if sz not in self.fonts: self.fonts[sz] = font(sz)
        return self.fonts[sz]

    def daylight(self, beat):
        keys = self.tl["day"]
        if beat <= keys[0][0]: return keys[0][1]
        for (b0, d0), (b1, d1) in zip(keys, keys[1:]):
            if b0 <= beat < b1:
                return d0 + (d1 - d0) * ease((beat - b0) / (b1 - b0))
        return keys[-1][1]

    def bell_angle(self, t):
        a = 0.0
        for i, (b, _) in enumerate(self.tl["bells"]):
            dt = t - b * BEAT
            if 0 <= dt < 4:
                a += (1 if i % 2 == 0 else -1) * 22 * math.exp(-dt / 0.9) * math.sin(math.pi * min(1, dt / 0.35) / 2) ** 2
        return max(-35, min(35, a))

    def frame(self, t):
        L, tl, k = self.L, self.tl, self.L["k"]
        W, H, G = L["W"], L["H"], L["ground"]
        beat = t / BEAT
        d = self.daylight(beat)
        rgb = self.sky_n * (1 - d) + self.sky_d * d
        img = Image.fromarray(rgb.astype(np.uint8), "RGB")
        # soleil
        sr = self.sun.size[0] // 2
        sy = G + 140 * k - (G + 140 * k - G * 0.3) * ease((d - 0.05) / 0.95)
        img.paste(self.sun, (int(L["sunx"] - sr), int(sy - sr)), self.sun)
        rgb = np.asarray(img).astype(np.float32)
        fg = self.fg_n * (1 - d) + self.fg_d * d
        rgb = rgb * (1 - self.fg_a) + fg * self.fg_a
        img = Image.fromarray(rgb.astype(np.uint8), "RGB")

        # fenêtre + frère Jacques
        base = G + 40
        wx, wy = L["hx"] - 70 * k, base - 175 * k
        if d < 0.6:
            gl = self.glow.point(lambda v: int(v * (1 - d / 0.6)))
            col = Image.new("RGB", gl.size, (255, 200, 110))
            img.paste(col, (int(wx - self.glow.size[0] / 2), int(wy - self.glow.size[1] / 2)), gl)
        awake = not any(a <= beat < b for a, b in tl["sleep"])
        bob = 0
        if awake:
            bob = -abs(math.sin(math.pi * beat)) * 10 * k
            past = [w for w in tl["wakes"] if w <= beat]
            jump = beat - past[-1] if past else 99
            if jump < 1.5:
                bob -= math.sin(math.pi * jump / 1.5) * 30 * k
        else:
            bob = math.sin(t * 2.2) * 4 * k
        fr = self.friar[awake]
        # masque circulaire de la fenêtre
        mask = Image.new("L", fr.size, 0)
        cx_, cy_ = self.friarR, self.friarR - bob - 18 * k
        ImageDraw.Draw(mask).ellipse([cx_ - self.wr + 2, cy_ - self.wr + 2, cx_ + self.wr - 2, cy_ + self.wr - 2], fill=255)
        from PIL import ImageChops
        m = ImageChops.multiply(fr.getchannel("A"), mask)
        img.paste(fr, (int(wx - self.friarR), int(wy - self.friarR + 18 * k + bob)), m)
        rs = self.ring.size[0] // 2
        img.paste(self.ring, (int(wx - rs), int(wy - rs)), self.ring)
        if not awake:
            for i in range(3):
                p = ((t / 2.4) + i / 3) % 1
                a = math.sin(math.pi * p)
                sc = 0.6 + 0.7 * p
                z = self.z.resize((max(1, int(self.z.size[0] * sc)), max(1, int(self.z.size[1] * sc))), Image.BILINEAR)
                zm = z.getchannel("A").point(lambda v, a=a: int(v * a))
                img.paste(z, (int(wx + 70 * k + p * 90 * k), int(wy - 110 * k - p * 170 * k)), zm)

        # cloche
        tt = G + 30 - L["th"] * k
        piv = (L["tx"], tt + 72 * k)
        b = self.bell.rotate(self.bell_angle(t), resample=Image.BICUBIC)
        bs = b.size[0] / 2
        img.paste(b, (int(piv[0] - bs), int(piv[1] - bs)), b)

        dr = ImageDraw.Draw(img)
        # panneau
        P = self.panel
        img.paste(P, (int(W / 2 - P.size[0] / 2), int(L["py"] - P.size[1] / 2)), P)
        line = None
        for st, idx in tl["lines"]:
            if st <= beat < st + 8:
                line = (st, idx)
        if line:
            st, idx = line
            lb = beat - st
            items = self.lyr[idx]
            f = self.f(items[0]["fs"])
            cur = None
            for i, it in enumerate(items):
                if it["st"] <= lb < it["st"] + it["dur"]:
                    cur = i
                col = (59, 59, 109) if lb < it["st"] else (255, 122, 47)
                if cur == i: col = (240, 60, 110)
                dr.text((it["x"], it["y"]), it["t"].rstrip(), font=f, fill=col)
            if cur is not None:
                it = items[cur]
                fr_ = (lb - it["st"]) / it["dur"]
                nx = items[cur + 1] if cur + 1 < len(items) and items[cur + 1]["y"] == it["y"] else None
                x = it["cx"] + ((nx["cx"] - it["cx"]) * fr_ if nx else 0)
                hgt = 55 * min(1, it["dur"] * 0.9 + 0.2)
                y = it["y"] + f.getbbox("D")[1] - 22 - math.sin(math.pi * fr_) * hgt
                r = 13
                dr.ellipse([x - r, y - r, x + r, y + r], fill=(255, 200, 40), outline=(230, 120, 20), width=3)
        else:
            f = self.f(int(L["fs"] * 1.1))
            txt = "Chante avec moi !"
            sc = 1 + 0.04 * abs(math.sin(math.pi * beat))
            f = self.f(int(L["fs"] * 1.1 * sc))
            tw = f.getlength(txt)
            dr.text((W / 2 - tw / 2, L["py"] - L["fs"] * 0.62 * sc - 6), txt, font=f, fill=(240, 60, 110))
        # étiquette de section
        for a, b_, lab in tl["labels"]:
            if a - 1 <= beat < b_:
                vis_l = ease((beat - a + 1) / 0.6) * (1 - ease((beat - b_ + 0.6) / 0.6))
                if vis_l > 0.01:
                    lf = self.f(int(L["fs"] * 0.62))
                    tw = lf.getlength(lab)
                    bx0 = W / 2 - tw / 2 - 34
                    by1 = L["py"] - L["ph"] / 2 + 14
                    by0 = by1 - L["fs"] * 0.62 - 34
                    pop = 1 - 0.0
                    ov = Image.new("RGBA", (int(tw + 68), int(by1 - by0)), (0, 0, 0, 0))
                    od = ImageDraw.Draw(ov)
                    od.rounded_rectangle([0, 0, ov.size[0] - 1, ov.size[1] - 1], radius=ov.size[1] // 2, fill=(240, 60, 110, 255))
                    od.text((34, 6), lab, font=lf, fill=(255, 255, 255, 255))
                    m_ = ov.getchannel("A").point(lambda v: int(v * vis_l))
                    img.paste(ov, (int(bx0), int(by0 - 10)), m_)
        # titre en haut (intro / outro)
        vis = max(1 - ease((beat - tl["intro"] + 1) / 1.5), ease((beat - tl["song_end"]) / 1.5))
        if vis > 0.01:
            over = Image.new("RGBA", img.size, (0, 0, 0, 0))
            od = ImageDraw.Draw(over)
            tf = self.f(L["tfs"])
            for j, (txt, fy, col) in enumerate([("Frère Jacques", 0, (255, 255, 255))]):
                tw = tf.getlength(txt)
                y = L["ty"] - L["tfs"] / 2 + math.sin(t * 3) * 6
                od.text((W / 2 - tw / 2, y), txt, font=tf, fill=col + (int(255 * vis),),
                        stroke_width=10, stroke_fill=(240, 60, 110, int(255 * vis)))
            img.paste(over, (0, 0), over)
        return img


def main():
    kind = sys.argv[1]
    sc = Scene(kind)
    if sys.argv[2] != "full":
        for ts in sys.argv[2:]:
            sc.frame(float(ts)).save(f"check_{kind}_{ts}.png")
        return
    dur = render_audio(kind, f"audio_{kind}.wav")
    L = sc.L
    tmp = f"frere_jacques_{kind}.tmp.mp4"
    cmd = ["ffmpeg", "-y", "-loglevel", "error", "-f", "rawvideo", "-pix_fmt", "rgb24",
           "-s", f"{L['W']}x{L['H']}", "-r", str(FPS), "-i", "-", "-i", f"audio_{kind}.wav",
           "-c:v", "libx264", "-preset", "veryfast", "-crf", "20", "-pix_fmt", "yuv420p",
           "-c:a", "aac", "-b:a", "192k", "-shortest", "-movflags", "+faststart", tmp]
    p = subprocess.Popen(cmd, stdin=subprocess.PIPE)
    n = int(dur * FPS)
    for i in range(n):
        p.stdin.write(sc.frame(i / FPS).tobytes())
    p.stdin.close()
    if p.wait() == 0:
        os.rename(tmp, f"frere_jacques_{kind}.mp4")
        print("ok", n)


if __name__ == "__main__":
    main()
