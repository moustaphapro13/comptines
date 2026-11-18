"""Décors (vectoriels, avec profondeur pour la parallaxe)."""
import math, random
import cairo
from .draw import hexc, ellipse, blob, fill_stroke, fir, oak_house, INK, LW

W, H = 1920, 1080
GROUND = 900


def cam_apply(c, cam, p=1.0):
    cx, cy, z = cam
    zl = 1 + (z - 1) * p
    c.translate(W / 2, H / 2); c.scale(zl, zl)
    c.translate(-(W / 2 + (cx - W / 2) * p), -(H / 2 + (cy - H / 2) * p))


def sky(c, top, bot):
    g = cairo.LinearGradient(0, 0, 0, H)
    g.add_color_stop_rgb(0, *hexc(top)[:3]); g.add_color_stop_rgb(1, *hexc(bot)[:3])
    c.set_source(g); c.paint()


def hills(c, y, amp, col, seed, edge=None, width=W * 1.6):
    rnd = random.Random(seed)
    ph = [rnd.random() * 6 for _ in range(3)]
    x0 = -width * 0.3
    c.move_to(x0, H + 400)
    n = 60
    for i in range(n + 1):
        x = x0 + width * i / n
        yy = y - amp * (0.5 * math.sin(x / 260 + ph[0]) + 0.3 * math.sin(x / 140 + ph[1]) + 0.2 * math.sin(x / 75 + ph[2]))
        c.line_to(x, yy)
    c.line_to(x0 + width, H + 400); c.close_path()
    c.set_source_rgba(*hexc(col)); c.fill_preserve()
    if edge:
        c.set_source_rgba(*hexc(edge)); c.set_line_width(4); c.stroke()
    else:
        c.new_path()


class Scene:
    """Décor dessiné à chaque image selon la caméra. layers: liste de (profondeur, fonction(c, t, props))."""
    def __init__(self, name):
        self.name = name

    def draw_back(self, c, cam, t, props):
        getattr(self, "_" + self.name)(c, cam, t, props)

    # ---------------------------------------------------------- clairière enneigée
    def _clairiere(self, c, cam, t, props, dusk=False, mode=None):
        mode = mode or ("dusk" if dusk else "day")
        night = mode in ("night", "fete")
        dusk = mode in ("dusk", "night", "fete")
        if mode == "dusk":
            sky(c, "#3B3A7A", "#F2A27A")
        elif night:
            sky(c, "#0E1638", "#3A4D8F")
        elif mode == "storm":
            sky(c, "#7C8796", "#C9D2DC")
        else:
            sky(c, "#9CCBF2", "#EAF4FF")
        # soleil / lune
        c.save(); cam_apply(c, cam, 0.05)
        if mode == "storm":
            pass
        elif dusk:
            ellipse(c, 1500, 260, 70, 70); c.set_source_rgba(1, 0.95, 0.8, 1); c.fill()
            if night:
                g = cairo.RadialGradient(1500, 260, 60, 1500, 260, 260)
                g.add_color_stop_rgba(0, 1, 1, 0.85, 0.35); g.add_color_stop_rgba(1, 1, 1, 0.85, 0); c.set_source(g); c.paint()
            rnd = random.Random(3)
            for k in range(40):
                x, y = rnd.random() * W * 1.2 - 100, rnd.random() * 420
                tw = 0.5 + 0.5 * math.sin(t * 2 + k)
                ellipse(c, x, y, 2.5, 2.5); c.set_source_rgba(1, 1, 0.9, 0.4 + 0.5 * tw); c.fill()
        else:
            g = cairo.RadialGradient(1550, 200, 10, 1550, 200, 260)
            g.add_color_stop_rgba(0, 1, 1, 0.9, 0.95); g.add_color_stop_rgba(1, 1, 1, 0.9, 0)
            c.set_source(g); c.paint()
        c.restore()
        c.save(); cam_apply(c, cam, 0.15)
        hills(c, 640, 90, "#C9DCF0" if not dusk else ("#2E3A6B" if night else "#8E8BB8"), 1)
        c.restore()
        c.save(); cam_apply(c, cam, 0.35)
        hills(c, 720, 60, "#DDEAF7" if not dusk else ("#4A5A8E" if night else "#B7A9C9"), 2)
        rnd = random.Random(7)
        for k in range(16):
            x = -300 + k * 170 + rnd.random() * 60
            fir(c, x, 745 + rnd.random() * 20, 150 + rnd.random() * 70, col="#4E8C78" if not dusk else "#3F5F66")
        c.restore()
        c.save(); cam_apply(c, cam, 0.7)
        hills(c, 815, 25, "#EEF5FD" if not dusk else ("#7484B8" if night else "#D8CCE0"), 3)
        rnd = random.Random(11)
        for x in (-200, 120, 330, 1650, 1880, 2150):
            fir(c, x, 830 + rnd.random() * 15, 260 + rnd.random() * 80, col="#2F7D5B" if not dusk else "#2D5450")
        c.restore()
        c.save(); cam_apply(c, cam, 1.0)
        oak_house(c, props.get("house_x", 1620), GROUND + 5, 520, light=1.0 if dusk else 0.3)
        # sol
        c.move_to(-800, GROUND - 10)
        c.curve_to(300, GROUND - 40, 1200, GROUND + 10, 2800, GROUND - 20)
        c.line_to(2800, H + 600); c.line_to(-800, H + 600); c.close_path()
        g = cairo.LinearGradient(0, GROUND - 40, 0, H)
        g.add_color_stop_rgb(0, *(hexc("#FFFFFF")[:3] if not dusk else hexc("#9FB0DD" if night else "#F0E4EE")[:3]))
        g.add_color_stop_rgb(1, *(hexc("#DCE9F7")[:3] if not dusk else hexc("#6D7FB5" if night else "#C7B8D6")[:3]))
        c.set_source(g); c.fill()
        rnd = random.Random(5)
        for k in range(26):  # petites ombres / bosses de neige
            x, y = rnd.random() * 2600 - 400, GROUND + 30 + rnd.random() * 150
            c.save(); c.translate(x, y); c.scale(1, 0.18); ellipse(c, 0, 0, 40 + rnd.random() * 60, 40)
            c.set_source_rgba(0.55, 0.65, 0.85, 0.12); c.fill(); c.restore()
        c.restore()

    def _soir(self, c, cam, t, props):
        self._clairiere(c, cam, t, props, mode="dusk")

    def _nuit(self, c, cam, t, props):
        self._clairiere(c, cam, t, props, mode="night")

    def _tempete(self, c, cam, t, props):
        self._clairiere(c, cam, t, props, mode="storm")

    def _fete(self, c, cam, t, props):
        self._clairiere(c, cam, t, props, mode="fete")

    def _cuisine(self, c, cam, t, props):
        p = dict(props); p["kitchen"] = True
        self._interieur(c, cam, t, p)

    # ---------------------------------------------------------- intérieur du terrier
    def _interieur(self, c, cam, t, props):
        c.set_source_rgb(*hexc("#5A3B26")[:3]); c.paint()
        c.save(); cam_apply(c, cam, 1.0)
        # mur arrondi (intérieur du tronc)
        g = cairo.RadialGradient(960, 520, 100, 960, 520, 1300)
        g.add_color_stop_rgb(0, *hexc("#F7D9A8")[:3]); g.add_color_stop_rgb(1, *hexc("#D9A86C")[:3])
        c.move_to(-400, H + 200); c.line_to(-400, 120); c.curve_to(300, -120, 1620, -120, 2320, 120)
        c.line_to(2320, H + 200); c.close_path(); c.set_source(g); c.fill()
        # veinure du bois
        c.set_line_width(3)
        for k in range(14):
            x = -200 + k * 170
            c.move_to(x, 60); c.curve_to(x + 30, 300, x - 30, 600, x + 10, 880)
            c.set_source_rgba(0.6, 0.4, 0.2, 0.18); c.stroke()
        # fenêtre ronde avec la neige dehors
        wx, wy, wr = 1180, 400, 170
        c.save(); ellipse(c, wx, wy, wr, wr); c.clip()
        g2 = cairo.LinearGradient(0, wy - wr, 0, wy + wr)
        g2.add_color_stop_rgb(0, *hexc("#A9CFF0")[:3]); g2.add_color_stop_rgb(1, *hexc("#E9F3FF")[:3]); c.set_source(g2); c.paint()
        hills(c, wy + 90, 25, "#FFFFFF", 9)
        fir(c, wx - 90, wy + 110, 140); fir(c, wx + 70, wy + 120, 110)
        rnd = random.Random(4)
        if props.get("snowing", True):
            for k in range(70):
                x0, sp, r = rnd.random() * 2 * wr + wx - wr, 40 + rnd.random() * 60, 2 + rnd.random() * 4
                y = (rnd.random() * 400 + t * sp) % (2 * wr + 20) + wy - wr - 10
                x = x0 + 12 * math.sin(t * 1.3 + k)
                ellipse(c, x, y, r, r); c.set_source_rgba(1, 1, 1, 0.95); c.fill()
        c.restore()
        ellipse(c, wx, wy, wr, wr); c.set_line_width(26); c.set_source_rgb(*hexc("#8A5E3B")[:3]); c.stroke_preserve()
        c.set_line_width(4); c.set_source_rgb(*INK); c.stroke()
        ellipse(c, wx, wy, wr + 13, wr + 13); c.stroke()
        c.set_line_width(12); c.set_source_rgb(*hexc("#8A5E3B")[:3])
        c.move_to(wx - wr, wy); c.line_to(wx + wr, wy); c.move_to(wx, wy - wr); c.line_to(wx, wy + wr); c.stroke()
        # rideaux
        for sd in (-1, 1):
            blob(c, [(wx + sd * (wr + 10), wy - wr - 30), (wx + sd * (wr + 70), wy - wr - 30), (wx + sd * (wr + 60), wy + wr * 0.4),
                     (wx + sd * (wr + 90), wy + wr + 40), (wx + sd * (wr + 20), wy + wr + 30), (wx + sd * (wr - 10), wy)])
            fill_stroke(c, hexc("#E86A6A"), 4)
        c.rectangle(wx - wr - 100, wy - wr - 45, 2 * wr + 200, 22); fill_stroke(c, hexc("#8A5E3B"), 4)
        # étagère avec pots
        c.rectangle(260, 330, 380, 20); fill_stroke(c, hexc("#8A5E3B"), 4)
        for k, col in enumerate(["#F2C94C", "#E86A6A", "#6FCF97", "#56CCF2"]):
            x = 290 + k * 90
            c.rectangle(x, 255, 55, 75); fill_stroke(c, hexc(col, 0.9), 4)
            c.rectangle(x - 4, 245, 63, 16); fill_stroke(c, hexc("#C9A27A"), 4)
        # lampe
        c.move_to(560, 120); c.line_to(560, 200); c.set_line_width(4); c.set_source_rgb(*INK); c.stroke()
        c.move_to(500, 260); c.line_to(620, 260); c.line_to(590, 200); c.line_to(530, 200); c.close_path()
        fill_stroke(c, hexc("#F2994A"), 4)
        g3 = cairo.RadialGradient(560, 280, 5, 560, 280, 380)
        g3.add_color_stop_rgba(0, 1, 0.9, 0.6, 0.35); g3.add_color_stop_rgba(1, 1, 0.9, 0.6, 0)
        c.set_source(g3); c.paint()
        # plancher
        c.rectangle(-400, GROUND - 40, 2800, 600)
        g4 = cairo.LinearGradient(0, GROUND - 40, 0, H)
        g4.add_color_stop_rgb(0, *hexc("#B07A4A")[:3]); g4.add_color_stop_rgb(1, *hexc("#8A5E3B")[:3]); c.set_source(g4); c.fill()
        c.set_line_width(3)
        for k in range(-3, 18):
            c.move_to(k * 160, GROUND - 40); c.line_to(k * 220 - 200, H + 100); c.set_source_rgba(0.35, 0.22, 0.12, 0.35); c.stroke()
        # tapis
        c.save(); c.translate(820, GROUND + 40); c.scale(1, 0.22); ellipse(c, 0, 0, 420, 300)
        c.set_source_rgb(*hexc("#5B8DEF")[:3]); c.fill_preserve(); c.set_line_width(10); c.set_source_rgb(*hexc("#F2C94C")[:3]); c.stroke(); c.restore()
        if props.get("kitchen"):
            # four en pierre
            c.rectangle(1500, GROUND - 330, 330, 300); fill_stroke(c, hexc("#B9A48A"), 4)
            c.arc(1665, GROUND - 160, 90, math.pi, 0); c.line_to(1755, GROUND - 90); c.line_to(1575, GROUND - 90); c.close_path()
            fill_stroke(c, hexc("#3B2A1E"), 4)
            g5 = cairo.RadialGradient(1665, GROUND - 120, 5, 1665, GROUND - 120, 90)
            g5.add_color_stop_rgba(0, 1, 0.6, 0.2, 0.9 if props.get("oven", 1) else 0); g5.add_color_stop_rgba(1, 1, 0.4, 0.1, 0)
            c.set_source(g5); c.arc(1665, GROUND - 120, 90, 0, 2 * math.pi); c.fill()
            c.rectangle(1480, GROUND - 350, 370, 30); fill_stroke(c, hexc("#8A5E3B"), 4)
        beds = [] if props.get("kitchen") else ((180, "#3D8BEB"), (1640, "#FF6F91"))
        # deux petits lits
        for bx, col in beds:
            c.rectangle(bx - 150, GROUND - 120, 300, 90); fill_stroke(c, hexc("#C98B55"), 4)
            blob(c, [(bx - 145, GROUND - 120), (bx + 145, GROUND - 120), (bx + 150, GROUND - 60), (bx - 150, GROUND - 60)])
            fill_stroke(c, hexc(col), 4)
            ellipse(c, bx - 100, GROUND - 135, 50, 25); fill_stroke(c, hexc("#FFFFFF"), 4)
            c.rectangle(bx - 160, GROUND - 200, 24, 190); fill_stroke(c, hexc("#A86F44"), 4)
        c.restore()

    # ---------------------------------------------------------- carte titre
    def _titre(self, c, cam, t, props):
        sky(c, "#8EC5FF", "#E7F2FF")
        c.save(); cam_apply(c, cam, 0.3)
        hills(c, 760, 70, "#DDEAF7", 2)
        for k in range(12):
            fir(c, -200 + k * 210, 790, 200, col="#4E8C78")
        c.restore()
        c.save(); cam_apply(c, cam, 1.0)
        hills(c, 880, 30, "#FFFFFF", 3)
        c.restore()
