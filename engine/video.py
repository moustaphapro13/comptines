"""Scène animée + karaoké, générique (16:9 « long » ou 9:16 « short »)."""
import math, os, subprocess
import numpy as np
from PIL import Image, ImageDraw, ImageFont, ImageChops
from . import sprites as S

FONT = "/usr/share/fonts/truetype/google-fonts/Poppins-Bold.ttf"
FPS = 30
LAYOUTS = {
    "long": dict(W=1920, H=1080, ground=760, k=1.0, py=955, pw=1720, ph=170, fs=84, rows=1, ty=150, tfs=120),
    "short": dict(W=1080, H=1920, ground=1150, k=0.92, py=1450, pw=1000, ph=330, fs=82, rows=2, ty=230, tfs=118),
}
SING = {"fr": "Chante avec moi !", "en": "Sing along!", "es": "¡Canta conmigo!"}
SKIES = {
    "night": ((14, 27, 68), (52, 64, 122)),
    "day": ((110, 196, 242), (214, 242, 255)),
    "dusk": ((60, 60, 140), (255, 170, 140)),
    "winter": ((150, 190, 230), (235, 245, 255)),
    "party": ((255, 214, 230), (255, 244, 220)),
}
GROUNDS = {
    "hills": ("#8FD47A", "#7CC96B", "#68B95C"),
    "snow": ("#FFFFFF", "#F1F7FF", "#E6F0FA"),
    "water": ("#8FD47A", "#7CC96B", "#4FA3E0"),
    "floor": ("#F7D9A8", "#F2CC92", "#E8BC7E"),
}


def font(sz, _c={}):
    if sz not in _c:
        _c[sz] = ImageFont.truetype(FONT, sz)
    return _c[sz]


def ease(x):
    x = min(1, max(0, x)); return x * x * (3 - 2 * x)


class Video:
    def __init__(self, song, kind):
        self.song, self.kind = song, kind
        self.L = L = LAYOUTS[kind]
        self.tl = song.timeline(kind)
        self.B = song.beat
        sc = song.m.SCENE
        self.sc = sc
        props = sc.get("short_props") if kind == "short" and sc.get("short_props") else sc["props"]
        self.night = sc.get("sky") == "night"
        W, H, G, k = L["W"], L["H"], L["ground"], L["k"]
        # ---- couche ciel
        top, bot = SKIES[sc.get("sky", "day")]
        y = np.linspace(0, 1, H)[:, None, None]
        sky = (np.array(top) * (1 - y) + np.array(bot) * y) * np.ones((1, W, 1))
        skyimg = Image.fromarray(sky.astype(np.uint8), "RGB").convert("RGBA")
        d = ImageDraw.Draw(skyimg)
        if sc.get("stars"):
            rng = np.random.default_rng(3)
            for _ in range(int(W * H / 9000)):
                xx, yy = rng.integers(0, W), rng.integers(0, int(G * .85))
                r = rng.choice([1, 1, 2, 2, 3])
                d.ellipse([xx - r, yy - r, xx + r, yy + r], fill=(255, 250, 220))
        if sc.get("clouds", sc.get("sky") in ("day", "winter", "party")):
            for cx, cy, s in [(.15, .18, 1.0), (.62, .1, .8), (.88, .3, .9)]:
                im, (ax, ay) = S.cloud(110 * s * k, "#FFFFFF" if not self.night else "#3A4577")
                skyimg.alpha_composite(im, (int(W * cx - ax), int(G * cy - ay)))
        # ---- sol
        fg = Image.new("RGBA", (W, H), (0, 0, 0, 0))
        im, d2 = S.canvas(W, H); p = S.P(d2)
        g = GROUNDS[sc.get("ground", "hills")]
        if self.night:
            g = ("#2F5560", "#2A4E58", "#24464F") if sc.get("ground") != "water" else ("#2F5560", "#2A4E58", "#1E3F66")
        if sc.get("ground") == "floor":
            p.r(0, G - 40, W, H, g[0])
            for i in range(0, W, 120):
                p.r(i, G - 40, i + 4, H, g[2])
        else:
            p.e(-0.4 * W, G - 120, 0.9 * W, G + 500, g[0])
            p.e(0.45 * W, G - 80, 1.5 * W, G + 500, g[1])
            p.r(0, G + 60, W, H, g[2])
            if sc.get("ground") == "water":
                p.r(0, G + 10, W, H, g[2])
        if sc.get("ground") in ("hills", None) and not self.night:
            rng = np.random.default_rng(7)
            for _ in range(int(W / 25)):
                xx, yy = rng.uniform(0, W), rng.uniform(G + 80, H)
                r = rng.uniform(5, 9)
                p.c(xx, yy, r, ["#FF8FB1", "#FFE066", "#FFFFFF", "#B9A6FF"][rng.integers(4)])
        im = im.resize((W, H), Image.LANCZOS)
        fg.alpha_composite(im)
        # ---- accessoires
        self.anim_sky, self.anim_front = [], []
        for pr in sorted(props, key=lambda q: q.get("z", 0)):
            pr = dict(pr)
            kind_ = pr.pop("k")
            at = pr.pop("at"); size = pr.pop("size", 200) * k
            anim = pr.pop("anim", None); is_sky = pr.pop("sky", False); pr.pop("z", None)
            x = W * at[0]
            y = G * at[1] if is_sky else G + at[1] * k
            fac = S.FACTORIES[kind_]
            if kind_ in ("fence",):
                img = fac(pr.pop("length", 400) * k, size)
            elif kind_ == "bridge":
                img = fac(pr.pop("width", 900) * k, size)
            else:
                img = fac(size, **pr)
            item = dict(img=img, x=x, y=y, anim=anim, size=size, kind=kind_, opts=pr)
            if anim and "sing" in (anim if isinstance(anim, (list, tuple)) else [anim]):
                o = dict(pr); o["mood"] = "sing"
                item["img_sing"] = fac(size, **o)
            target = None
            if anim:
                (self.anim_sky if is_sky else self.anim_front).append(item)
            else:
                spr, (ax, ay) = img
                (skyimg if is_sky else fg).alpha_composite(spr, (int(x - ax), int(y - ay)))
        self.sky = np.asarray(skyimg.convert("RGB")).astype(np.float32)
        fga = np.asarray(fg).astype(np.float32)
        self.fg_rgb, self.fg_a = fga[..., :3], fga[..., 3:4] / 255.0
        base = self.sky * (1 - self.fg_a) + self.fg_rgb * self.fg_a
        self.base = Image.fromarray(base.astype(np.uint8), "RGB")
        self.inv = Image.fromarray((255 * (1 - self.fg_a[..., 0])).astype(np.uint8), "L")
        self.panel = self._panel(L["pw"], L["ph"])
        self.lyr = {}
        self.notes_on = self._voice_onsets()

    def _panel(self, w, h):
        im, d = S.canvas(w, h)
        s = S.SS
        d.rounded_rectangle([6 * s, 12 * s, (w - 6) * s, (h - 2) * s], radius=40 * s, fill=(60, 40, 90, 70))
        d.rounded_rectangle([0, 0, (w - 6) * s, (h - 12) * s], radius=40 * s, fill=(255, 255, 255, 248))
        return im.resize((w, h), Image.LANCZOS)

    def _voice_onsets(self):
        """Intervalles (en temps) où une voix chante : pour faire « chanter » les personnages."""
        iv = []
        for sec in self.tl["sections"]:
            if sec["mode"] == "karaoke":
                continue
            for b, s in self.song.notes(sec["part"], sec["start"]):
                iv.append((b, b + s["dur"] * 0.85))
        return iv

    def singing(self, beat):
        for a, b in self.notes_on:
            if a <= beat < b:
                return True
            if a > beat:
                break
        return False

    # ------------------------------------------------------------ paroles
    def layout(self, part, idx):
        key = (part, idx)
        if key in self.lyr:
            return self.lyr[key]
        L = self.L
        line = self.song.parts[part][idx]
        syl, b = [], 0
        for s in line:
            if s["txt"]:
                syl.append([s["txt"] + ("" if s["join"] else " "), b, s["dur"]])
            b += s["dur"]
        total = b
        fs = L["fs"]
        rows = [syl]
        if L["rows"] == 2 and font(fs).getlength("".join(x[0] for x in syl).strip()) > L["pw"] - 90:
            half = total / 2
            cut = min(range(1, len(syl)), key=lambda i: abs(syl[i][1] - half)) if len(syl) > 1 else 1
            while cut > 1 and syl[cut - 1][0].endswith(" ") is False:
                cut -= 1
            rows = [syl[:cut], syl[cut:]]
        while max(font(fs).getlength("".join(x[0] for x in r).strip()) for r in rows) > L["pw"] - 90:
            fs -= 2
        f = font(fs)
        lh = fs * 1.35
        y0 = L["py"] - lh * len(rows) / 2 + lh * 0.12
        items = []
        for ri, r in enumerate(rows):
            tw = f.getlength("".join(x[0] for x in r).strip())
            x = L["W"] / 2 - tw / 2
            for txt, st, dur in r:
                wd = f.getlength(txt.rstrip())
                items.append(dict(x=x, y=y0 + ri * lh, t=txt.rstrip(), st=st, dur=dur, cx=x + wd / 2, fs=fs, row=ri))
                x += f.getlength(txt)
        self.lyr[key] = (items, total)
        return self.lyr[key]

    def current_line(self, beat):
        cur = None
        for ln in self.tl["lines"]:
            items, total = self.layout(ln["part"], ln["idx"])
            if ln["start"] <= beat < ln["start"] + total:
                if ln["voice2"] and cur is not None:
                    continue
                cur = (ln, items, total)
        return cur

    # ------------------------------------------------------------ image
    def paste_anim(self, img, item, t, beat, behind=False):
        spr, (ax, ay) = item["img"]
        anims = item["anim"] if isinstance(item["anim"], (list, tuple)) else [item["anim"]]
        if "sing" in anims and self.singing(beat):
            spr, (ax, ay) = item["img_sing"]
        dx = dy = 0.0; rot = 0.0; sc = 1.0; alpha = 1.0
        s = item["size"]
        for a in anims:
            if a == "bounce":
                dy -= abs(math.sin(math.pi * beat)) * s * 0.06
            elif a == "hop":
                dy -= abs(math.sin(math.pi * beat / 2)) * s * 0.12
            elif a == "sway":
                rot += 5 * math.sin(math.pi * beat / 2)
            elif a == "float":
                dy += math.sin(t * 0.9 + item["x"] * 0.01) * s * 0.06
            elif a == "drift":
                dx += math.sin(t * 0.3 + item["x"]) * s * 0.15
            elif a == "twinkle":
                sc = 1 + 0.08 * math.sin(t * 4 + item["x"])
            elif a == "swing":
                rot += 22 * math.sin(math.pi * beat)
            elif a == "pendulum":
                rot += 20 * math.sin(math.pi * beat)
            elif a == "bob":
                dy += math.sin(math.pi * beat / 2) * s * 0.05; rot += 3 * math.sin(math.pi * beat / 2 + 1)
            elif a == "row":
                rot += 25 * math.sin(math.pi * beat)
            elif a == "flicker":
                sc = 1 + 0.12 * math.sin(t * 17 + item["x"]) * math.sin(t * 7)
            elif a == "pulse":
                alpha = 0.55 + 0.45 * (0.5 + 0.5 * math.sin(t * 3 + item["x"] * 0.05))
            elif a == "walk":
                span = self.L["W"] * 1.2
                dx = ((t * 60 + item["x"]) % span) - item["x"] - self.L["W"] * 0.1
                dy -= abs(math.sin(math.pi * beat)) * s * 0.05
        if rot or sc != 1:
            w0, h0 = spr.size
            if sc != 1:
                spr = spr.resize((max(1, int(w0 * sc)), max(1, int(h0 * sc))), Image.BILINEAR)
                ax, ay = ax * sc, ay * sc
            if rot:
                # rotation autour du point d'ancrage
                big = Image.new("RGBA", (spr.size[0] * 2, spr.size[1] * 2), (0, 0, 0, 0))
                ox, oy = int(big.size[0] / 2 - ax), int(big.size[1] / 2 - ay)
                big.paste(spr, (ox, oy))
                spr = big.rotate(rot, resample=Image.BICUBIC, center=(big.size[0] / 2, big.size[1] / 2))
                ax, ay = big.size[0] / 2, big.size[1] / 2
        m = spr.getchannel("A")
        if alpha < 1:
            m = m.point(lambda v, a=alpha: int(v * a))
        pos = (int(item["x"] + dx - ax), int(item["y"] + dy - ay))
        if behind:
            # derrière le décor : masque = alpha du sprite × zones non couvertes par le premier plan
            box = (pos[0], pos[1], pos[0] + spr.size[0], pos[1] + spr.size[1])
            m = ImageChops.multiply(m, self.inv.crop(box))
        img.paste(spr, pos, m)

    def frame(self, t):
        L, tl = self.L, self.tl
        W, H, G = L["W"], L["H"], L["ground"]
        beat = t / self.B
        img = self.base.copy()
        for it in self.anim_sky:
            self.paste_anim(img, it, t, beat, behind=True)
        dr = ImageDraw.Draw(img)
        if self.sc.get("ground") == "water":
            for row in range(4):
                yy = G + 70 + row * 55 * L["k"]
                pts = [(x, yy + 8 * math.sin(x / 60 + t * 2 + row)) for x in range(0, W + 20, 20)]
                dr.line(pts, fill=(220, 240, 255), width=4)
        for it in self.anim_front:
            self.paste_anim(img, it, t, beat)
        if self.sc.get("snow"):
            rng = np.random.default_rng(11)
            n = 70
            xs = rng.uniform(0, W, n); sp = rng.uniform(40, 110, n); ph = rng.uniform(0, H, n); rs = rng.uniform(3, 7, n)
            for i in range(n):
                yy = (ph[i] + t * sp[i]) % H
                xx = xs[i] + 20 * math.sin(t + i)
                dr.ellipse([xx - rs[i], yy - rs[i], xx + rs[i], yy + rs[i]], fill=(255, 255, 255))
        # panneau + paroles
        P = self.panel
        img.paste(P, (int(W / 2 - P.size[0] / 2), int(L["py"] - P.size[1] / 2)), P)
        cur = self.current_line(beat)
        if cur:
            ln, items, total = cur
            lb = beat - ln["start"]
            f = font(items[0]["fs"])
            ci = None
            for i, it in enumerate(items):
                if it["st"] <= lb < it["st"] + it["dur"]:
                    ci = i
                col = (59, 59, 109) if lb < it["st"] else (255, 122, 47)
                if ci == i:
                    col = (240, 60, 110)
                dr.text((it["x"], it["y"]), it["t"], font=f, fill=col)
            if ci is not None:
                it = items[ci]
                fr = (lb - it["st"]) / it["dur"]
                nx = items[ci + 1] if ci + 1 < len(items) and items[ci + 1]["row"] == it["row"] else None
                x = it["cx"] + ((nx["cx"] - it["cx"]) * fr if nx else 0)
                hgt = 55 * min(1, it["dur"] * 0.9 + 0.2)
                y = it["y"] + f.getbbox("D")[1] - 22 - math.sin(math.pi * fr) * hgt
                dr.ellipse([x - 13, y - 13, x + 13, y + 13], fill=(255, 200, 40), outline=(230, 120, 20), width=3)
        else:
            txt = SING[self.song.lang]
            sc = 1 + 0.04 * abs(math.sin(math.pi * beat))
            f = font(int(L["fs"] * 1.1 * sc))
            while f.getlength(txt) > L["pw"] - 80:
                f = font(f.size - 4)
            dr.text((W / 2 - f.getlength(txt) / 2, L["py"] - f.size * 0.62 - 6), txt, font=f, fill=(240, 60, 110))
        # étiquette de section
        for a, b_, lab in tl["labels"]:
            if a - 1 <= beat < b_:
                v = ease((beat - a + 1) / 0.6) * (1 - ease((beat - b_ + 0.6) / 0.6))
                if v > 0.01:
                    lf = font(int(L["fs"] * 0.62))
                    tw = lf.getlength(lab)
                    hh = int(L["fs"] * 0.62 + 34)
                    ov = Image.new("RGBA", (int(tw + 68), hh), (0, 0, 0, 0))
                    od = ImageDraw.Draw(ov)
                    od.rounded_rectangle([0, 0, ov.size[0] - 1, hh - 1], radius=hh // 2, fill=(240, 60, 110, 255))
                    od.text((34, 6), lab, font=lf, fill=(255, 255, 255, 255))
                    m = ov.getchannel("A").point(lambda q: int(q * v))
                    img.paste(ov, (int(W / 2 - ov.size[0] / 2), int(L["py"] - L["ph"] / 2 + 14 - hh - 10)), m)
        # titre (intro / fin)
        vis = max(1 - ease((beat - tl["intro"] + 1) / 1.5), ease((beat - tl["song_end"]) / 1.5))
        if vis > 0.01:
            title = self.song.m.TITLE
            tf = font(L["tfs"])
            while tf.getlength(title) > W - 120:
                tf = font(tf.size - 4)
            over = Image.new("RGBA", img.size, (0, 0, 0, 0))
            od = ImageDraw.Draw(over)
            tw = tf.getlength(title)
            yy = L["ty"] - tf.size / 2 + math.sin(t * 3) * 6
            od.text((W / 2 - tw / 2, yy), title, font=tf, fill=(255, 255, 255, int(255 * vis)),
                    stroke_width=10, stroke_fill=(240, 60, 110, int(255 * vis)))
            img.paste(over, (0, 0), over)
        return img


def render(song, kind, out_path, audio_path, dur):
    v = Video(song, kind)
    L = v.L
    tmp = out_path[:-4] + ".tmp.mp4"
    cmd = ["ffmpeg", "-y", "-loglevel", "error", "-f", "rawvideo", "-pix_fmt", "rgb24",
           "-s", f"{L['W']}x{L['H']}", "-r", str(FPS), "-i", "-", "-i", audio_path,
           "-c:v", "libx264", "-preset", "veryfast", "-crf", "20", "-pix_fmt", "yuv420p",
           "-c:a", "aac", "-b:a", "192k", "-shortest", "-movflags", "+faststart", tmp]
    p = subprocess.Popen(cmd, stdin=subprocess.PIPE)
    for i in range(int(dur * FPS)):
        p.stdin.write(v.frame(i / FPS).tobytes())
    p.stdin.close()
    if p.wait() == 0:
        os.replace(tmp, out_path)
        return True
    return False
