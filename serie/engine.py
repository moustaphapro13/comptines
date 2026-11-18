"""Moteur de la série : script -> chronologie -> images (cairo) + son -> mp4."""
import math, random, subprocess, os, hashlib
import numpy as np
import cairo
import soundfile as sf
from scipy.signal import fftconvolve, butter, sosfilt
from . import draw as D
from .scenes import Scene, cam_apply, W, H, GROUND
from .speech import say, SR

FPS = 25
NAMES = {"ding": ("Ding", "#3D8BEB"), "dang": ("Dang", "#FF4F7B"), "maman": ("Maman", "#2E9E73"),
         "noisette": ("Noisette", "#D9772B"), "pompon": ("Pompon", "#C9A400"),
         "papa": ("Papa", "#D88A1E"), "narr": ("Papy Hibou", "#8A6A4A")}
SIZE = 330          # taille d'un hérisson (enfant) en px monde


def ease(u):
    u = min(1, max(0, u)); return u * u * (3 - 2 * u)


# ================================================================= chronologie
class Ep:
    def __init__(self, script):
        self.s = script
        self.t = 0.0
        self.scenes = []          # dict(start, end, bg, props)
        self.lines = []           # dict(t0, t1, who[list], text, audio)
        self.chars = {}           # nom -> dict(pos=[(t0,t1,x0,x1)], emo=[(t,emo)], act=[(t0,t1,act)], face=[(t,f)], vis=[(t,bool)])
        self.sfx = []             # (t, name)
        self.sets = []            # (t, key, val)
        self.cams = []            # (t, target, dur)
        self.fx = []              # (t0, kind, data)
        self.music = []           # (t0, t1, mood)
        self.build()

    def ch(self, n):
        return self.chars.setdefault(n, dict(pos=[], emo=[], act=[], face=[], vis=[]))

    def xat(self, n, t):
        x = None
        for (a, b, x0, x1) in self.ch(n)["pos"]:
            if t >= a:
                x = x0 + (x1 - x0) * ease((t - a) / max(1e-6, b - a))
        return x

    def build(self):
        for sc in self.s["scenes"]:
            st = self.t
            for n, c in sc.get("cast", {}).items():
                C = self.ch(n)
                C["vis"].append((st, True)); C["pos"].append((st, st, c["x"], c["x"]))
                C["emo"].append((st, c.get("emo", "neutral"))); C["face"].append((st, c.get("face", 1)))
            for n in self.chars:
                if n not in sc.get("cast", {}):
                    self.ch(n)["vis"].append((st, False))
            self.cams.append((st, sc.get("cam", "wide"), 0.0))
            self.music.append([st, None, sc.get("music", "cozy")])
            self.t += sc.get("lead", 0.8)
            for b in sc["beats"]:
                self.beat(b)
            self.t += sc.get("tail", 1.0)
            self.scenes.append(dict(start=st, end=self.t, bg=sc["bg"], props=dict(sc.get("props", {})),
                                    iris=sc.get("iris", True)))
            self.music[-1][1] = self.t
        self.end = self.t

    def _opts(self, who, o, t0, t1):
        for n in (who if isinstance(who, list) else [who]):
            if n == "narr":
                continue
            C = self.ch(n)
            if "emo" in o:
                C["emo"].append((t0, o["emo"]))
            if "face" in o:
                C["face"].append((t0, o["face"]))
            if "act" in o:
                C["act"].append((t0, t1 if o.get("hold", True) else t0 + 1.0, o["act"]))
            if "to" in o:
                x = self.xat(n, t0)
                C["pos"].append((t0, t0 + o.get("walk", t1 - t0), x, o["to"]))
                C["act"].append((t0, t0 + o.get("walk", t1 - t0), "walk"))
        if "cam" in o:
            self.cams.append((t0, o["cam"], o.get("camdur", 0.9)))
        if "sfx" in o:
            self.sfx.append((t0 + o.get("sfx_at", 0), o["sfx"]))
        if "set" in o:
            k, v = o["set"]; self.sets.append((t0 + o.get("set_at", 0), k, v))

    def beat(self, b):
        kind = b[0]
        if kind in ("say", "narr", "both"):
            if kind == "narr":
                who, text, o = ["narr"], b[1], (b[2] if len(b) > 2 else {})
            elif kind == "say":
                who, text, o = [b[1]], b[2], (b[3] if len(b) > 3 else {})
            else:
                who, text, o = b[1], b[2], (b[3] if len(b) > 3 else {})
            emo = o.get("voice", o.get("emo", "neutral"))
            auds = [say(w, text, emo) for w in who]
            n = max(len(a) for a in auds)
            mix = np.zeros(n)
            for a in auds:
                mix[: len(a)] += a / len(auds) * (1.3 if len(auds) > 1 else 1)
            t0 = self.t + o.get("delay", 0)
            t1 = t0 + n / SR
            self.lines.append(dict(t0=t0, t1=t1, who=who, text=text, audio=mix, env=self.env(mix)))
            self._opts(who, o, t0, t1)
            self.t = t1 + o.get("gap", 0.5)
        elif kind == "walk":
            _, n, x, dur = b[:4]; o = b[4] if len(b) > 4 else {}
            x0 = self.xat(n, self.t)
            C = self.ch(n)
            C["pos"].append((self.t, self.t + dur, x0, x))
            C["act"].append((self.t, self.t + dur, "walk"))
            C["face"].append((self.t, 1 if x > x0 else -1))
            self._opts(n, o, self.t, self.t + dur)
            if o.get("wait", True):
                self.t += dur
        elif kind == "act":
            _, n, a, dur = b[:4]; o = b[4] if len(b) > 4 else {}
            for nn in (n if isinstance(n, list) else [n]):
                self.ch(nn)["act"].append((self.t, self.t + dur, a))
            self._opts(n, o, self.t, self.t + dur)
            if o.get("wait", True):
                self.t += dur
        elif kind == "set":
            self.sets.append((self.t, b[1], b[2]))
        elif kind == "sfx":
            self.sfx.append((self.t, b[1]))
        elif kind == "wait":
            self.t += b[1]
        elif kind == "cam":
            self.cams.append((self.t, b[1], b[2] if len(b) > 2 else 0.9))
        elif kind == "fx":
            self.fx.append((self.t, b[1], b[2] if len(b) > 2 else {}))
            if b[1] == "throw":
                self.sfx.append((self.t, "whoosh")); self.sfx.append((self.t + 0.6, "pouf"))
                self.ch(b[2]["by"])["act"].append((self.t - 0.25, self.t + 0.2, "throw"))
                self.ch(b[2]["to"])["act"].append((self.t + 0.6, self.t + 1.2, "hit"))
            if b[1] == "sparkle":
                self.sfx.append((self.t, "sparkle"))
        elif kind == "emo":
            self.ch(b[1])["emo"].append((self.t, b[2]))
        elif kind == "face":
            self.ch(b[1])["face"].append((self.t, b[2]))

    @staticmethod
    def env(a):
        hop = SR // FPS
        n = len(a) // hop + 1
        e = np.array([np.sqrt(np.mean(a[i * hop:(i + 1) * hop] ** 2)) if a[i * hop:(i + 1) * hop].size else 0 for i in range(n)])
        e = e / (e.max() + 1e-9)
        e = np.convolve(e, [0.25, 0.5, 0.25], "same")
        return np.clip((e - 0.08) * 1.6, 0, 1)

    # ------------------------------------------------------------- état à l'instant t
    def last(self, lst, t, default):
        v = default
        for (tt, val) in lst:
            if tt <= t:
                v = val
        return v

    def state(self, n, t):
        C = self.chars[n]
        if not self.last(C["vis"], t, False):
            return None
        x = self.xat(n, t)
        st = dict(facing=self.last(C["face"], t, 1), emo=self.last(C["emo"], t, "neutral"))
        y = GROUND
        acts = [(a, b, k) for (a, b, k) in C["act"] if a <= t < b]
        seed = int(hashlib.md5(n.encode()).hexdigest()[:6], 16)
        # respiration / bras au repos
        st["armL"] = 0.3 + 0.05 * math.sin(t * 2 + seed)
        st["armR"] = 0.3 + 0.05 * math.sin(t * 2.2 + seed)
        st["squash"] = 0.012 * math.sin(t * 2.4 + seed)
        # clignement
        ph = (t + (seed % 100) / 37) % 3.7
        st["blink"] = max(0, 1 - abs(ph - 0.1) / 0.08) if ph < 0.2 else 0
        # parole
        mo = 0
        for L in self.lines:
            if n in L["who"] and L["t0"] <= t < L["t1"]:
                i = int((t - L["t0"]) * FPS)
                mo = L["env"][min(i, len(L["env"]) - 1)]
                st["tilt"] = 0.03 * math.sin((t - L["t0"]) * 5)
                st["squash"] += 0.02 * mo
        st["mouth"] = mo
        for (a, b, k) in acts:
            u = (t - a) / max(1e-6, b - a)
            if k == "walk":
                st["step"] = (t - a) * 1.7
                y -= abs(math.sin((t - a) * math.pi * 1.7)) * 12
                st["armL"] = 0.3 + 0.35 * math.sin((t - a) * math.pi * 1.7)
                st["armR"] = 0.3 - 0.35 * math.sin((t - a) * math.pi * 1.7)
            elif k == "jump":
                cyc = (t - a) % 0.7 / 0.7
                y -= math.sin(cyc * math.pi) * 110
                st["squash"] = -0.1 * math.sin(cyc * math.pi) + (0.12 if cyc < 0.08 or cyc > 0.92 else 0)
                st["armL"] = st["armR"] = 2.4
            elif k == "cheer":
                st["armL"] = st["armR"] = 2.7 + 0.2 * math.sin(t * 12)
                y -= abs(math.sin(t * 7)) * 25
            elif k == "wave":
                st["armR"] = 2.5 + 0.45 * math.sin(t * 11)
            elif k == "point":
                st["armR"] = 1.65
            elif k == "yawn":
                st["armL"] = st["armR"] = 2.8; st["mouth"] = max(st["mouth"], 0.9 * math.sin(min(1, u * 1.3) * math.pi))
                st["emo"] = "sleepy"
            elif k == "shake":
                st["tilt"] = 0.12 * math.sin(t * 14)
            elif k == "push":
                st["tilt"] = st["facing"] * 0.18; st["armL"] = st["armR"] = 1.5
                y -= abs(math.sin(t * 9)) * 4
            elif k == "carry":
                st["armL"] = st["armR"] = 2.95
            elif k == "twirl":
                st["facing"] = 1 if math.sin(t * 9) > 0 else -1
                y -= abs(math.sin(t * 9)) * 20; st["armL"] = st["armR"] = 2.2
            elif k == "throw":
                st["armR"] = 3.0 - 1.8 * u
            elif k == "hit":
                st["squash"] = 0.12 * (1 - u); st["tilt"] = -st["facing"] * 0.2 * (1 - u); st["emo"] = "surprised"
            elif k == "nod":
                st["tilt"] = 0.0; y -= abs(math.sin(t * 10)) * 8
            elif k == "catch":
                st["armL"] = st["armR"] = 2.2 + 0.3 * math.sin(t * 6); st["look"] = -0.5
            elif k == "hide":
                st["armL"] = st["armR"] = 2.95; st["emo"] = "happy_closed"
        return x, y, st


# ================================================================= rendu image
class Renderer:
    def __init__(self, ep):
        self.ep = ep
        self.scn = {s["bg"]: Scene(s["bg"]) for s in ep.scenes}
        rnd = random.Random(2)
        self.flakes = [(rnd.random() * W, rnd.random() * H, 0.3 + rnd.random() ** 2 * 1.7, rnd.random() * 6) for _ in range(220)]

    def cam_at(self, t):
        ep = self.ep
        cams = [c for c in ep.cams if c[0] <= t]
        def resolve(tg, tt):
            if tg == "wide":
                return (W / 2, H / 2, 1.0)
            if isinstance(tg, tuple) and tg[0] == "close":
                x = ep.xat(tg[1], tt) or W / 2
                return (x, GROUND - SIZE * 0.62, 1.45)
            if isinstance(tg, tuple) and tg[0] == "two":
                xs = [ep.xat(n, tt) or W / 2 for n in tg[1:]]
                span = max(xs) - min(xs)
                z = min(1.55, max(1.1, W * 0.62 / (span + 500)))
                return ((max(xs) + min(xs)) / 2, GROUND - SIZE * 0.6, z)
            if isinstance(tg, tuple) and tg[0] == "at":
                return (tg[1], tg[2], tg[3])
            return (W / 2, H / 2, 1.0)
        if not cams:
            return (W / 2, H / 2, 1.0)
        cur = resolve(cams[-1][1], t)
        t0, dur = cams[-1][0], cams[-1][2]
        if len(cams) > 1 and dur > 0 and t < t0 + dur:
            prev = resolve(cams[-2][1], t)
            u = ease((t - t0) / dur)
            cur = tuple(p + (q - p) * u for p, q in zip(prev, cur))
        # léger travelling permanent
        cx, cy, z = cur
        z *= 1 + 0.015 * math.sin(t * 0.25)
        # bornes : ne jamais sortir du décor
        hw, hh = W / 2 / z, H / 2 / z
        cx = min(max(cx, hw), W - hw); cy = min(max(cy, hh), H - hh)
        return (cx, cy, z)

    def props_at(self, sc, t):
        p = dict(sc["props"])
        for (tt, k, v) in self.ep.sets:
            if sc["start"] <= tt <= t:
                p[k] = v
        return p

    def frame(self, t, surf):
        ep = self.ep
        c = cairo.Context(surf)
        sc = next((s for s in ep.scenes if s["start"] <= t < s["end"]), ep.scenes[-1])
        props = self.props_at(sc, t)
        cam = self.cam_at(t)
        self.scn[sc["bg"]].draw_back(c, cam, t, props)
        c.save(); cam_apply(c, cam, 1.0)
        # accessoires de décor au sol
        if props.get("fir"):
            D.deco_fir(c, props["fir"][0], GROUND + 10, props["fir"][1], props.get("fir_stage", 1), t)
        if props.get("garlands"):
            D.garland(c, -100, 700, 120, 90, t); D.garland(c, 650, 1400, 140, 80, t + 1); D.garland(c, 1350, 2050, 110, 90, t + 2)
        for k, lx in enumerate(props.get("lanterns", [])):
            c.set_line_width(8); c.set_source_rgb(0.42, 0.28, 0.16)
            c.move_to(lx, GROUND + 30); c.line_to(lx, GROUND - 330); c.line_to(lx + 60, GROUND - 330); c.stroke()
            D.item(c, "lantern", lx + 60, GROUND - 330, 110, 1.0 if k < props.get("lanterns_lit", 0) else 0.0)
        if props.get("table"):
            tx = props["table"]
            c.rectangle(tx - 260, GROUND - 230, 520, 34); D.fill_stroke(c, D.hexc("#A86F44"), 4)
            for sd in (-1, 1):
                c.rectangle(tx + sd * 220 - 15, GROUND - 200, 30, 220); D.fill_stroke(c, D.hexc("#8A5E3B"), 4)
        if props.get("cake"):
            cx_, cy_, cs_ = props["cake"]
            D.cake(c, cx_, cy_, cs_, props.get("candles", 0))
        for (kind, ix, iy, isz) in props.get("items", []):
            D.item(c, kind, ix, iy, isz)
        if props.get("snowman", 0):
            D.snowman(c, props.get("snowman_x", 960), GROUND + 20, 380, props["snowman"])
        for (k, (bx, r)) in [("ball1", props.get("ball1", (0, 0))), ("ball2", props.get("ball2", (0, 0)))]:
            if r:
                D.snowball(c, bx, GROUND + 20 - r, r)
        if props.get("owl"):
            D.owl(c, props["owl"][0], props["owl"][1], 170, dict(blink=1 if (t % 4) < 0.12 else 0,
                  mouth=max([L["env"][min(int((t - L["t0"]) * FPS), len(L["env"]) - 1)] for L in ep.lines
                             if "narr" in L["who"] and L["t0"] <= t < L["t1"]] or [0])))
        chars = []
        for n in ep.chars:
            s = ep.state(n, t)
            if s:
                chars.append((s[0], n, s))
        for (_, n, (x, y, st)) in sorted(chars, key=lambda q: 0 if q[1] in ("maman", "papa") else 1):
            st["wind"] = math.sin(t * 2 + x) * (1 + 3 * props.get("storm", 0))
            if props.get("hat_" + n):
                st["hat"] = props["hat_" + n]
            if props.get("hold_" + n):
                st["hold"] = props["hold_" + n]
                if st.get("armR", 0) < 0.9:
                    st["armR"] = 0.9
            D.hedgehog(c, n, x, y, SIZE, st)
        # effets
        for (t0, kind, d) in ep.fx:
            if kind == "throw" and t0 <= t < t0 + 1.4:
                u = (t - t0) / 0.6
                xa = ep.xat(d["by"], t0) + 60 * (1 if ep.last(ep.chars[d["by"]]["face"], t0, 1) > 0 else -1)
                xb = ep.xat(d["to"], t0)
                ya, yb = GROUND - SIZE * 0.55, GROUND - SIZE * 0.75 * D.PAL[d["to"]]["size"]
                if u < 1:
                    x = xa + (xb - xa) * u; y = ya + (yb - ya) * u - math.sin(u * math.pi) * 160
                    D.snowball(c, x, y, 22)
                else:
                    v = (t - t0 - 0.6) / 0.8
                    rnd = random.Random(int(t0 * 10))
                    for k in range(14):
                        a = rnd.random() * 2 * math.pi; sp = 60 + rnd.random() * 110
                        D.ellipse(c, xb + math.cos(a) * sp * v, yb + math.sin(a) * sp * v + 80 * v * v, 9 * (1 - v) + 2, 9 * (1 - v) + 2)
                        c.set_source_rgba(1, 1, 1, 1 - v); c.fill()
            if kind == "sparkle" and t0 <= t < t0 + 1.6:
                v = (t - t0) / 1.6
                x0, y0 = d.get("x", 960), d.get("y", GROUND - 200)
                rnd = random.Random(int(t0 * 7))
                for k in range(12):
                    a = rnd.random() * 2 * math.pi; r = 60 + 160 * v * (0.5 + rnd.random())
                    self.star(c, x0 + math.cos(a) * r, y0 + math.sin(a) * r * 0.8, 14 * math.sin(v * math.pi) + 2, a + t * 3,
                              (1, 0.85 + 0.15 * rnd.random(), 0.3, math.sin(v * math.pi)))
        c.restore()
        # neige qui tombe (plein écran, parallaxe)
        if props.get("snow", False):
            storm = props.get("storm", 0)
            for (x0, y0, d, ph) in self.flakes:
                y = (y0 + t * 40 * d * (1 + 3 * storm)) % (H + 40) - 20
                x = (x0 + 25 * math.sin(t * 0.8 + ph) - t * 260 * d * storm - (cam[0] - W / 2) * d * 0.3) % (W + 40) - 20
                r = 2 + 3.2 * d
                D.ellipse(c, x, y, r, r); c.set_source_rgba(1, 1, 1, 0.55 + 0.25 * min(1, d)); c.fill()
        # titre / générique
        if props.get("title"):
            self.title(c, t - sc["start"], props)
        # sous-titres
        for L in ep.lines:
            if L["t0"] - 0.1 <= t < L["t1"] + 0.2 and not props.get("nosub"):
                self.subtitle(c, L)
                break
        # transition en iris
        if sc.get("iris", True):
            u_in = (t - sc["start"]) / 0.7; u_out = (sc["end"] - t) / 0.7
            u = min(u_in, u_out)
            if u < 1:
                r = max(0, ease(u)) * 1150
                c.rectangle(0, 0, W, H); c.arc_negative(W / 2, H / 2 - 60, r, 2 * math.pi, 0)
                c.set_fill_rule(cairo.FILL_RULE_EVEN_ODD); c.set_source_rgb(0.1, 0.07, 0.06); c.fill()
                c.set_fill_rule(cairo.FILL_RULE_WINDING)
        # vignette douce
        g = cairo.RadialGradient(W / 2, H / 2, H * 0.55, W / 2, H / 2, H * 1.05)
        g.add_color_stop_rgba(0, 0, 0, 0, 0); g.add_color_stop_rgba(1, 0.1, 0.05, 0.02, 0.28)
        c.set_source(g); c.paint()

    @staticmethod
    def star(c, x, y, r, a, col):
        c.save(); c.translate(x, y); c.rotate(a); c.move_to(0, -r)
        for k in range(1, 10):
            rr = r if k % 2 == 0 else r * 0.45
            c.line_to(math.sin(k * math.pi / 5) * rr, -math.cos(k * math.pi / 5) * rr)
        c.close_path(); c.set_source_rgba(*col); c.fill(); c.restore()

    def text(self, c, s, x, y, size, col, outline=(0.24, 0.16, 0.12), ow=10, align=0.5):
        c.select_font_face("Poppins", cairo.FONT_SLANT_NORMAL, cairo.FONT_WEIGHT_BOLD)
        c.set_font_size(size)
        e = c.text_extents(s)
        x0 = x - e.x_advance * align
        c.move_to(x0, y); c.text_path(s)
        c.set_line_join(cairo.LINE_JOIN_ROUND)
        if ow:
            c.set_source_rgb(*outline); c.set_line_width(ow); c.stroke_preserve()
        c.set_source_rgb(*col); c.fill()
        return e.x_advance

    def subtitle(self, c, L):
        names = [NAMES[w] for w in L["who"]]
        label = " et ".join(n for n, _ in names)
        col = D.hexc(names[0][1])
        c.select_font_face("Poppins", cairo.FONT_SLANT_NORMAL, cairo.FONT_WEIGHT_BOLD)
        fs = 40
        c.set_font_size(fs)
        words, rows, cur = L["text"].replace(" ?", "\u00a0?").replace(" !", "\u00a0!").replace(" :", "\u00a0:").split(" "), [], ""
        for w in words:
            if c.text_extents(cur + " " + w).x_advance > 1350 and cur:
                rows.append(cur); cur = w
            else:
                cur = (cur + " " + w).strip()
        rows.append(cur)
        bw = max(c.text_extents(r).x_advance for r in rows) + 80
        bh = 40 + 52 * len(rows) + 10
        x0, y0 = W / 2 - bw / 2, H - 40 - bh
        r = 28
        c.new_sub_path(); c.arc(x0 + bw - r, y0 + r, r, -math.pi / 2, 0); c.arc(x0 + bw - r, y0 + bh - r, r, 0, math.pi / 2)
        c.arc(x0 + r, y0 + bh - r, r, math.pi / 2, math.pi); c.arc(x0 + r, y0 + r, r, math.pi, 3 * math.pi / 2); c.close_path()
        c.set_source_rgba(1, 1, 1, 0.92); c.fill_preserve(); c.set_source_rgba(*col[:3], 1); c.set_line_width(5); c.stroke()
        # étiquette du personnage
        c.set_font_size(30); lw = c.text_extents(label).x_advance + 40
        lx, ly = x0 + 30, y0 - 26
        c.new_sub_path(); c.arc(lx + 22, ly + 22, 22, math.pi / 2, 3 * math.pi / 2); c.arc(lx + lw - 22, ly + 22, 22, -math.pi / 2, math.pi / 2); c.close_path()
        c.set_source_rgba(*col); c.fill()
        c.move_to(lx + 20, ly + 33); c.set_source_rgb(1, 1, 1); c.show_text(label)
        c.set_font_size(fs)
        for i, row in enumerate(rows):
            c.move_to(W / 2 - c.text_extents(row).x_advance / 2, y0 + 62 + i * 52)
            c.set_source_rgb(0.2, 0.14, 0.12); c.show_text(row)

    def title(self, c, tt, props):
        k = ease(tt / 1.2)
        y = 330 - (1 - k) * 400
        bounce = abs(math.sin(tt * math.pi * 2)) * 12   # au tempo du générique (120 bpm)
        c.save(); c.translate(W / 2, y - bounce); c.rotate(0.03 * math.sin(tt * 2))
        self.text(c, "Ding et Dang", 0, 0, 170, (1, 0.83, 0.25), ow=26)
        c.restore()
        if tt > 1.5:
            a = min(1, (tt - 1.5) / 0.6)
            c.push_group()
            self.text(c, props.get("subtitle", ""), W / 2, 450, 62, (1, 1, 1), ow=14)
            c.pop_group_to_source(); c.paint_with_alpha(a)

    def render(self, out, wav):
        ep = self.ep
        N = int(ep.end * FPS)
        p = subprocess.Popen(["ffmpeg", "-y", "-loglevel", "error", "-f", "rawvideo", "-pix_fmt", "bgra", "-s", f"{W}x{H}",
                              "-r", str(FPS), "-i", "-", "-i", wav, "-c:v", "libx264", "-preset", "veryfast", "-crf", "19",
                              "-pix_fmt", "yuv420p", "-c:a", "aac", "-b:a", "192k", "-shortest", "-movflags", "+faststart", out],
                             stdin=subprocess.PIPE)
        surf = cairo.ImageSurface(cairo.FORMAT_ARGB32, W, H)
        for i in range(N):
            self.frame(i / FPS, surf)
            surf.flush()
            p.stdin.write(bytes(surf.get_data()))
        p.stdin.close(); p.wait()
        return p.returncode == 0


# ================================================================= son
def lp(x, fc, order=2):
    return sosfilt(butter(order, fc / (SR / 2), "low", output="sos"), x)


def bp(x, f1, f2):
    return sosfilt(butter(2, [f1 / (SR / 2), f2 / (SR / 2)], "band", output="sos"), x)


def sfx(name, rng):
    t = lambda d: np.arange(int(d * SR)) / SR
    if name == "crunch":
        n = rng.standard_normal(int(0.16 * SR)) * (rng.random(int(0.16 * SR)) > 0.6)
        return bp(n, 1500, 6000) * np.exp(-t(0.16) / 0.05) * 0.8
    if name == "pouf":
        n = rng.standard_normal(int(0.4 * SR))
        return (lp(n, 1200) * np.exp(-t(0.4) / 0.08) * 1.6 + np.sin(2 * np.pi * 90 * t(0.4)) * np.exp(-t(0.4) / 0.06))
    if name == "whoosh":
        n = rng.standard_normal(int(0.45 * SR)); tt = t(0.45)
        return bp(n, 600, 3000) * np.sin(np.pi * tt / 0.45) ** 2 * 0.7
    if name == "sparkle":
        from engine.music import glock, mtof
        out = np.zeros(int(1.6 * SR))
        for k, m in enumerate([84, 88, 91, 96, 100]):
            g = glock(mtof(m), 0.4); i = int(k * 0.07 * SR); out[i:i + len(g)] += g[: len(out) - i] * 0.35
        return out
    if name == "boing":
        tt = t(0.35); f = 220 + 500 * tt
        return np.sin(2 * np.pi * np.cumsum(f) / SR) * np.exp(-tt / 0.15) * 0.5
    if name == "pop":
        tt = t(0.15); f = 900 - 3000 * tt
        return np.sin(2 * np.pi * np.cumsum(f) / SR) * np.exp(-tt / 0.04) * 0.6
    if name == "heave":
        tt = t(0.5)
        return lp(rng.standard_normal(len(tt)), 300) * np.exp(-tt / 0.2) * 1.2
    return np.zeros(10)


def music_bed(mood, dur, rng):
    from engine.music import glock, pad, bass, pluck, flute, mtof
    out = np.zeros(int((dur + 2) * SR))
    prog = {"cozy": (["C", "Am", "F", "G"], 84), "play": (["C", "F", "G", "C"], 112),
            "calm": (["F", "C", "Dm", "G"], 72), "magic": (["C", "Em", "F", "G"], 90)}[mood]
    roots = {"C": (0, [0, 4, 7]), "Am": (9, [0, 3, 7]), "F": (5, [0, 4, 7]), "G": (7, [0, 4, 7]), "Dm": (2, [0, 3, 7]), "Em": (4, [0, 3, 7])}
    B = 60 / prog[1]
    bar = 4 * B
    k = 0
    while k * bar < dur + bar:
        sym = prog[0][k % 4]; r, iv = roots[sym]; t0 = k * bar
        def put(sig, tt, g):
            i = int(tt * SR); j = min(len(out), i + len(sig))
            if i < len(out):
                out[i:j] += sig[: j - i] * g
        put(pad([mtof(60 + r + i) for i in iv], bar + 0.4), t0, 0.035)
        put(bass(mtof(36 + r), 2 * B), t0, 0.22 if mood == "play" else 0.15)
        if mood == "play":
            put(bass(mtof(43 + r if r < 5 else 31 + r), 2 * B), t0 + 2 * B, 0.18)
        for e in range(8):
            n = 72 + r + iv[(e * 2 + k) % 3] + (12 if e % 4 == 3 else 0)
            if mood == "play" or e % 2 == 0:
                put((pluck if mood == "play" else glock)(mtof(n), B / 2), t0 + e * B / 2, 0.07 if mood == "play" else 0.08)
        k += 1
    return out[: int(dur * SR)]


def render_audio(ep, path, jingle=None):
    rng = np.random.default_rng(3)
    N = int((ep.end + 1) * SR)
    dia = np.zeros(N); mus = np.zeros(N); fx = np.zeros(N)
    for L in ep.lines:
        i = int(L["t0"] * SR); a = L["audio"]
        dia[i:i + len(a)] += a[: N - i] * 0.85
    for (t, name) in ep.sfx:
        s = sfx(name, rng); i = int(t * SR); fx[i:i + len(s)] += s[: N - i] * 0.5
    for c in ep.chars.values():       # pas dans la neige
        for (a, b, k) in c["act"]:
            if k == "walk":
                tt = a
                while tt < b:
                    s = sfx("crunch", rng); i = int(tt * SR); fx[i:i + len(s)] += s[: N - i] * 0.25; tt += 0.3
    for (t0, t1, mood) in ep.music:
        if mood in ("jingle", "jingle_end") and jingle is not None:
            j, _ = sf.read(jingle[mood])
            j = j.mean(axis=1) if j.ndim > 1 else j
            j = j[: int((t1 - t0 + 0.5) * SR)].copy()
            f = int(1.2 * SR)
            if len(j) >= int((t1 - t0) * SR):
                j[-f:] *= np.linspace(1, 0, f)
            i = int(t0 * SR); mus[i:i + len(j)] += j[: N - i] * 0.9
            continue
        if mood in (None, "none"):
            continue
        m = music_bed(mood, t1 - t0, rng)
        f = int(0.8 * SR); m[:f] *= np.linspace(0, 1, f); m[-f:] *= np.linspace(1, 0, f)
        i = int(t0 * SR); mus[i:i + len(m)] += m[: N - i]
    # vent léger dans la neige
    wind = lp(rng.standard_normal(N), 500) * (0.5 + 0.5 * np.sin(np.arange(N) / SR * 0.4)) * 0.05
    for sc in ep.scenes:
        if sc["props"].get("snow"):
            i, j = int(sc["start"] * SR), int(sc["end"] * SR)
            mus[i:j] += wind[i:j]
    # réverbération courte sur les voix, ducking de la musique
    ir = rng.standard_normal(int(0.5 * SR)) * np.exp(-np.arange(int(0.5 * SR)) / SR / 0.12)
    ir /= np.sqrt((ir ** 2).sum())
    dia = dia + 0.08 * fftconvolve(dia, ir)[:N]
    env = lp(np.abs(dia), 4)
    duck = 1 - 0.55 * np.clip(env / (env.max() + 1e-9) * 4, 0, 1)
    mix = dia + mus * duck + fx
    mix = np.tanh(mix * 1.2) / np.tanh(1.2)
    mix = mix / (np.abs(mix).max() + 1e-9) * 0.9
    st = np.stack([mix, mix], 1)
    sf.write(path, st, SR, subtype="PCM_16")
