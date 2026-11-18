"""Dessin vectoriel (cairo) des personnages et décors de « Ding et Dang »."""
import math
import cairo

INK = (0.24, 0.16, 0.12)          # contour brun foncé, style dessin animé
LW = 0.022                         # épaisseur du contour (en unités de taille)


def hexc(h, a=1.0):
    h = h.lstrip("#")
    return tuple(int(h[i:i + 2], 16) / 255 for i in (0, 2, 4)) + (a,)


def fill_stroke(c, col, lw=None, ink=INK):
    c.set_source_rgba(*col)
    c.fill_preserve()
    c.set_source_rgb(*ink)
    if lw:
        c.set_line_width(lw)
    c.stroke()


def ellipse(c, x, y, rx, ry):
    c.save(); c.translate(x, y); c.scale(max(abs(rx), 1e-4), max(abs(ry), 1e-4)); c.arc(0, 0, 1, 0, 2 * math.pi); c.restore()


def blob(c, pts):
    """Courbe fermée lissée passant par les points (Catmull-Rom)."""
    n = len(pts)
    c.move_to(*pts[0])
    for i in range(n):
        p0, p1, p2, p3 = pts[i - 1], pts[i], pts[(i + 1) % n], pts[(i + 2) % n]
        c.curve_to(p1[0] + (p2[0] - p0[0]) / 6, p1[1] + (p2[1] - p0[1]) / 6,
                   p2[0] - (p3[0] - p1[0]) / 6, p2[1] - (p3[1] - p1[1]) / 6, p2[0], p2[1])
    c.close_path()


# ------------------------------------------------------------------ personnages
PAL = {
    "ding": dict(spike="#7A5233", spike2="#9C6B43", face="#F6DDB8", belly="#EFCB98", scarf="#3D8BEB",
                 scarf2="#7FB8FF", size=1.0),
    "dang": dict(spike="#8A5A3A", spike2="#B07A52", face="#FAE3C4", belly="#F3D2A6", scarf="#FF6F91",
                 scarf2="#FFB3C6", bow="#FF4F7B", size=0.86),
    "maman": dict(spike="#6E4A30", spike2="#8E6440", face="#F4D8B0", belly="#ECC793", scarf="#4CB08A",
                  scarf2="#8ED8B8", size=1.28, flower="#FFD84A"),
    "papa": dict(spike="#5E3F28", spike2="#7A553A", face="#F0D2A6", belly="#E6BF8A", scarf="#E8A33D",
                 scarf2="#F6CF83", size=1.35, glasses=True),
}

EMO_BROW = {"neutral": (0, 0), "happy": (0.02, -0.05), "excited": (0.04, -0.12), "surprised": (0.06, -0.15),
            "sad": (-0.02, 0.3), "angry": (-0.02, -0.35), "sleepy": (-0.03, 0.0), "proud": (0.02, -0.08),
            "worried": (0.0, 0.3)}


def hedgehog(c, who, x, y, s, st):
    """Hérisson debout, pieds en (x, y), taille s (px pour 1 unité ≈ hauteur totale).
    st : facing(-1/1), mouth(0..1), blink(0..1), emo, armL, armR (radians, 0 = bas), squash, tilt, look, step."""
    P = PAL[who]
    s = s * P["size"]
    f = st.get("facing", 1)
    c.save()
    c.translate(x, y)
    sq = st.get("squash", 0.0)
    c.scale(s * (1 + sq * 0.5), s * (1 - sq))
    c.set_line_join(cairo.LINE_JOIN_ROUND); c.set_line_cap(cairo.LINE_CAP_ROUND)
    c.set_line_width(LW)
    step = st.get("step", 0.0)
    # ombre portée
    c.save(); c.scale(1, 0.25); ellipse(c, 0, 0.05, 0.36, 0.14)
    c.set_source_rgba(0, 0, 0, 0.16); c.fill(); c.restore()
    # pieds
    for sd in (-1, 1):
        lift = max(0, math.sin(step * math.pi * 2 + (0 if sd < 0 else math.pi))) * 0.05 if step else 0
        ellipse(c, sd * 0.13 + f * 0.03, -0.035 - lift, 0.1, 0.05)
        fill_stroke(c, hexc("#5A3B26"))
    c.rotate(st.get("tilt", 0.0))
    # piquants (dos + tête), derrière le corps
    pts = []
    n = 26
    cx, cy, rx, ry = -f * 0.04, -0.52, 0.46, 0.5
    for i in range(n + 1):
        a = math.pi * (0.92 + 1.16 * i / n)       # de bas-gauche à bas-droite par le haut
        r = 1.0 if i % 2 else 1.22
        pts.append((cx + math.cos(a) * rx * r, cy + math.sin(a) * ry * r))
    c.move_to(*pts[0])
    for p in pts[1:]:
        c.line_to(*p)
    c.curve_to(cx + rx * 0.9, cy + 0.35, cx - rx * 0.9, cy + 0.35, *pts[0])
    c.close_path()
    g = cairo.LinearGradient(0, -1.1, 0, -0.1)
    g.add_color_stop_rgb(0, *hexc(P["spike2"])[:3]); g.add_color_stop_rgb(1, *hexc(P["spike"])[:3])
    c.set_source(g); c.fill_preserve(); c.set_source_rgb(*INK); c.stroke()
    # quelques traits de piquants
    c.set_line_width(LW * 0.7); c.set_source_rgba(*INK[:3], 0.5)
    for i in range(1, n, 3):
        a = math.pi * (0.92 + 1.16 * i / n)
        c.move_to(cx + math.cos(a) * rx * 0.75, cy + math.sin(a) * ry * 0.75)
        c.line_to(cx + math.cos(a) * rx * 1.05, cy + math.sin(a) * ry * 1.05)
        c.stroke()
    c.set_line_width(LW)
    # bras arrière
    def arm(sd, ang):
        bx, by = sd * 0.25, -0.42
        L = 0.22
        ex, ey = bx + math.sin(ang) * L * sd, by + math.cos(ang) * L
        c.set_line_width(0.085); c.set_source_rgb(*INK); c.move_to(bx, by); c.line_to(ex, ey); c.stroke()
        c.set_line_width(0.055); c.set_source_rgb(*hexc(P["face"])[:3]); c.move_to(bx, by); c.line_to(ex, ey); c.stroke()
        c.set_line_width(LW)
        ellipse(c, ex, ey, 0.05, 0.05); fill_stroke(c, hexc(P["face"]))
    # corps / ventre
    blob(c, [(0, -0.62), (0.27, -0.5), (0.31, -0.22), (0.2, -0.05), (0, -0.02), (-0.2, -0.05), (-0.31, -0.22), (-0.27, -0.5)])
    fill_stroke(c, hexc(P["belly"]))
    ellipse(c, f * 0.02, -0.25, 0.16, 0.17); c.set_source_rgba(1, 1, 1, 0.25); c.fill()
    arm(-1, st.get("armL", 0.25)); arm(1, st.get("armR", 0.25))
    # écharpe
    sc = hexc(P["scarf"]); sc2 = hexc(P["scarf2"])
    blob(c, [(-0.27, -0.55), (0, -0.5), (0.27, -0.55), (0.25, -0.47), (0, -0.42), (-0.25, -0.47)])
    fill_stroke(c, sc)
    c.save(); c.translate(-f * 0.12, -0.47); c.rotate(-f * 0.12 + st.get("wind", 0) * 0.25)
    blob(c, [(-0.035, 0), (0.035, 0), (0.045, 0.14), (0.0, 0.16), (-0.045, 0.14)]); fill_stroke(c, sc)
    c.set_line_width(LW * 0.8); c.set_source_rgba(*sc2)
    for k in range(2):
        c.move_to(-0.035, 0.045 + k * 0.045); c.line_to(0.035, 0.045 + k * 0.045); c.stroke()
    c.set_line_width(LW)
    c.restore()
    # tête
    hx, hy = f * 0.05, -0.74
    hx += st.get("look", 0) * 0.02
    # oreilles
    for sd in (-1, 1):
        ellipse(c, hx + sd * 0.2 - f * 0.03, hy - 0.2, 0.065, 0.065); fill_stroke(c, hexc(P["face"]))
        ellipse(c, hx + sd * 0.2 - f * 0.03, hy - 0.2, 0.035, 0.035); c.set_source_rgba(*hexc("#F4A3A8")); c.fill()
    blob(c, [(hx - 0.25, hy - 0.05), (hx - 0.18, hy - 0.2), (hx, hy - 0.25), (hx + 0.18, hy - 0.2),
             (hx + 0.25, hy - 0.05), (hx + f * 0.3, hy + 0.08), (hx + f * 0.1, hy + 0.2), (hx - f * 0.15, hy + 0.18)])
    fill_stroke(c, hexc(P["face"]))
    # mèche de piquants sur le front
    c.move_to(hx - 0.2, hy - 0.16)
    for k in range(5):
        c.line_to(hx - 0.16 + k * 0.08, hy - 0.3 + (0.06 if k % 2 else 0))
    c.line_to(hx + 0.2, hy - 0.16); c.curve_to(hx + 0.08, hy - 0.2, hx - 0.08, hy - 0.2, hx - 0.2, hy - 0.16)
    fill_stroke(c, hexc(P["spike2"]))
    if "flower" in P:
        c.save(); c.translate(hx + f * 0.17, hy - 0.26)
        for k in range(5):
            a = k * 2 * math.pi / 5
            ellipse(c, math.cos(a) * 0.045, math.sin(a) * 0.045, 0.04, 0.04); fill_stroke(c, hexc(P["flower"]))
        ellipse(c, 0, 0, 0.03, 0.03); fill_stroke(c, hexc("#F2994A"))
        c.restore()
    if "bow" in P:
        c.save(); c.translate(hx + f * 0.16, hy - 0.27); c.rotate(f * 0.3)
        for sd in (-1, 1):
            c.move_to(0, 0); c.curve_to(sd * 0.12, -0.09, sd * 0.14, 0.08, 0, 0); fill_stroke(c, hexc(P["bow"]))
        ellipse(c, 0, 0, 0.03, 0.03); fill_stroke(c, hexc(P["bow"]))
        c.restore()
    # museau
    mx, my = hx + f * 0.2, hy + 0.06
    blob(c, [(mx - f * 0.14, my - 0.06), (mx, my - 0.06), (mx + f * 0.1, my - 0.01), (mx, my + 0.05), (mx - f * 0.14, my + 0.07)])
    fill_stroke(c, hexc(P["face"]))
    ellipse(c, mx + f * 0.1, my - 0.02, 0.045, 0.038); fill_stroke(c, hexc("#2B1D16"))
    ellipse(c, mx + f * 0.09, my - 0.035, 0.013, 0.01); c.set_source_rgba(1, 1, 1, 0.8); c.fill()
    # joues
    ellipse(c, hx + f * 0.02, hy + 0.08, 0.06, 0.035); c.set_source_rgba(*hexc("#FF8FA3", 0.45)); c.fill()
    # yeux
    emo = st.get("emo", "neutral")
    bl = st.get("blink", 0.0)
    if emo == "sleepy":
        bl = max(bl, 0.6)
    look = st.get("look", 0)
    by_, bt = EMO_BROW.get(emo, (0, 0))
    for k, ex in enumerate((hx - f * 0.02, hx + f * 0.12)):
        ey = hy - 0.05
        er = 0.055 if k == 0 else 0.05
        if bl > 0.85 or emo == "happy_closed":
            c.set_line_width(LW * 1.3); c.set_source_rgb(*INK)
            c.arc(ex, ey + 0.01, er * 0.8, math.pi * 1.1, math.pi * 1.9); c.stroke(); c.set_line_width(LW)
        else:
            ellipse(c, ex, ey, er, er * 1.15 * (1 - bl)); fill_stroke(c, (1, 1, 1, 1), LW * 0.8)
            px = ex + (look * 0.02 + f * 0.012)
            ellipse(c, px, ey + 0.005, er * 0.62, er * 0.75 * (1 - bl)); c.set_source_rgb(*hexc("#2B1D16")[:3]); c.fill()
            ellipse(c, px - 0.012, ey - 0.018 * (1 - bl), er * 0.22, er * 0.22 * (1 - bl)); c.set_source_rgb(1, 1, 1); c.fill()
            if bl > 0:
                c.set_source_rgba(*hexc(P["face"])); c.rectangle(ex - er * 1.1, ey - er * 1.3, er * 2.2, er * 1.3 * bl * 1.6); c.fill()
            if P.get("lashes"):
                c.set_line_width(LW * 0.8); c.set_source_rgb(*INK)
                for j in range(3):
                    a = math.pi * (1.25 + 0.2 * j)
                    c.move_to(ex + math.cos(a) * er, ey + math.sin(a) * er * 1.15)
                    c.line_to(ex + math.cos(a) * er * 1.4, ey + math.sin(a) * er * 1.5); c.stroke()
                c.set_line_width(LW)
        # sourcils
        c.set_line_width(LW * 1.1); c.set_source_rgb(*INK)
        sy = ey - er * 1.5 - by_
        tilt = bt * (1 if k == 0 else -1) * f
        c.move_to(ex - 0.035, sy + tilt * 0.06); c.line_to(ex + 0.035, sy - tilt * 0.06); c.stroke()
        c.set_line_width(LW)
    if P.get("glasses"):
        c.set_line_width(LW * 0.9); c.set_source_rgb(*INK)
        for ex in (hx - f * 0.02, hx + f * 0.12):
            ellipse(c, ex, hy - 0.05, 0.07, 0.07); c.stroke()
        c.move_to(hx + f * 0.03, hy - 0.05); c.line_to(hx + f * 0.07, hy - 0.05); c.stroke()
        c.set_line_width(LW)
    # bouche
    mo = st.get("mouth", 0.0)
    ox, oy = hx + f * 0.14, hy + 0.13
    if mo > 0.08:
        h = 0.015 + 0.06 * mo
        w = 0.045 + 0.015 * mo
        blob(c, [(ox - w, oy - h * 0.3), (ox, oy - h * 0.45), (ox + w, oy - h * 0.3), (ox + w * 0.6, oy + h * 0.6), (ox, oy + h), (ox - w * 0.6, oy + h * 0.6)])
        fill_stroke(c, hexc("#7A2E2E"), LW * 0.9)
        ellipse(c, ox, oy + h * 0.55, w * 0.55, h * 0.35); c.set_source_rgba(*hexc("#FF8A8A")); c.fill()
    else:
        c.set_line_width(LW * 1.1); c.set_source_rgb(*INK)
        if emo in ("sad", "worried"):
            c.arc_negative(ox, oy + 0.04, 0.04, -0.4, -math.pi + 0.4)
        elif emo == "angry":
            c.move_to(ox - 0.035, oy + 0.01); c.line_to(ox + 0.035, oy + 0.01)
        elif emo == "surprised":
            ellipse(c, ox, oy + 0.01, 0.018, 0.022)
        else:
            c.arc(ox, oy - 0.02, 0.045, 0.35, math.pi - 0.35)
        c.stroke(); c.set_line_width(LW)
    c.restore()


def owl(c, x, y, s, st):
    """Papy Hibou (narrateur), perché ; pieds en (x, y)."""
    c.save(); c.translate(x, y); c.scale(s, s)
    c.set_line_join(cairo.LINE_JOIN_ROUND); c.set_line_width(LW)
    blob(c, [(0, -1.0), (0.3, -0.9), (0.38, -0.5), (0.3, -0.1), (0, 0), (-0.3, -0.1), (-0.38, -0.5), (-0.3, -0.9)])
    fill_stroke(c, hexc("#9B7B5B"))
    blob(c, [(0, -0.62), (0.22, -0.5), (0.2, -0.15), (0, -0.06), (-0.2, -0.15), (-0.22, -0.5)])
    fill_stroke(c, hexc("#E8D6B8"))
    for sd in (-1, 1):
        c.move_to(sd * 0.18, -0.9); c.line_to(sd * 0.3, -1.08); c.line_to(sd * 0.32, -0.85); fill_stroke(c, hexc("#9B7B5B"))
        bl = st.get("blink", 0)
        ellipse(c, sd * 0.14, -0.75, 0.12, 0.12); fill_stroke(c, (1, 1, 1, 1))
        ellipse(c, sd * 0.14, -0.74, 0.06, 0.07 * (1 - bl)); c.set_source_rgb(0.15, 0.1, 0.08); c.fill()
        c.set_line_width(LW * 0.9); ellipse(c, sd * 0.14, -0.75, 0.14, 0.14); c.set_source_rgb(*INK); c.stroke(); c.set_line_width(LW)
    c.move_to(-0.03, -0.66); c.line_to(0.03, -0.66); c.line_to(0, -0.56 + 0.04 * st.get("mouth", 0)); fill_stroke(c, hexc("#F2B23A"))
    for sd in (-1, 1):
        blob(c, [(sd * 0.3, -0.7), (sd * 0.42, -0.45), (sd * 0.36, -0.15), (sd * 0.26, -0.35)]); fill_stroke(c, hexc("#7E6046"))
    c.restore()


# ------------------------------------------------------------------ accessoires
def snowman(c, x, y, s, stage, scarf="#E84A4A"):
    """Bonhomme de neige construit en étapes (1 = boule du bas, 2 = + tête, 3 = + visage, 4 = + écharpe)."""
    if stage <= 0:
        return
    c.save(); c.translate(x, y); c.scale(s, s); c.set_line_width(LW); c.set_line_join(cairo.LINE_JOIN_ROUND)
    c.save(); c.scale(1, 0.22); ellipse(c, 0, 0.1, 0.5, 0.2); c.set_source_rgba(0.3, 0.4, 0.6, 0.18); c.fill(); c.restore()
    ellipse(c, 0, -0.32, 0.36, 0.32); fill_stroke(c, hexc("#FFFFFF"), ink=(0.42, 0.5, 0.62))
    ellipse(c, -0.1, -0.42, 0.12, 0.08); c.set_source_rgba(0.85, 0.92, 1, 1); c.fill()
    if stage >= 2:
        ellipse(c, 0, -0.82, 0.24, 0.22); fill_stroke(c, hexc("#FFFFFF"), ink=(0.42, 0.5, 0.62))
        ellipse(c, -0.07, -0.9, 0.08, 0.05); c.set_source_rgba(0.85, 0.92, 1, 1); c.fill()
    if stage >= 3:
        for sd in (-1, 1):
            ellipse(c, sd * 0.08, -0.88, 0.03, 0.035); c.set_source_rgb(0.15, 0.12, 0.12); c.fill()
        c.move_to(0, -0.82); c.line_to(0.2, -0.79); c.line_to(0, -0.77); fill_stroke(c, hexc("#FF8A2A"))
        for k in range(5):
            a = math.pi * (0.25 + k * 0.125)
            ellipse(c, math.cos(a) * 0.12, -0.78 + math.sin(a) * 0.08, 0.015, 0.015); c.set_source_rgb(0.15, 0.12, 0.12); c.fill()
        for k in range(3):
            ellipse(c, 0, -0.45 + k * 0.12, 0.025, 0.025); c.set_source_rgb(0.15, 0.12, 0.12); c.fill()
        for sd in (-1, 1):
            c.set_line_width(0.03); c.set_source_rgb(*hexc("#6B4A2E")[:3])
            c.move_to(sd * 0.3, -0.45); c.line_to(sd * 0.55, -0.62); c.move_to(sd * 0.47, -0.56); c.line_to(sd * 0.52, -0.7); c.stroke()
        c.set_line_width(LW)
    if stage >= 4:
        blob(c, [(-0.22, -0.64), (0, -0.6), (0.22, -0.64), (0.2, -0.56), (0, -0.53), (-0.2, -0.56)]); fill_stroke(c, hexc(scarf))
        c.rectangle(0.08, -0.6, 0.08, 0.22); fill_stroke(c, hexc(scarf))
        # chapeau (un vieux seau)
        c.move_to(-0.16, -0.98); c.line_to(0.16, -0.98); c.line_to(0.12, -1.18); c.line_to(-0.12, -1.18); c.close_path()
        fill_stroke(c, hexc("#4A78C0"))
    c.restore()


def snowball(c, x, y, r):
    ellipse(c, x, y, r, r); fill_stroke(c, hexc("#FFFFFF"), r * 0.15, ink=(0.42, 0.5, 0.62))


def fir(c, x, y, s, snow=True, col="#2F7D5B"):
    c.save(); c.translate(x, y); c.scale(s, s); c.set_line_width(LW * 0.8); c.set_line_join(cairo.LINE_JOIN_ROUND)
    c.rectangle(-0.06, -0.15, 0.12, 0.15); fill_stroke(c, hexc("#6B4A2E"))
    for k in range(3):
        w = 0.42 - k * 0.1; yb = -0.12 - k * 0.27; ht = 0.45
        c.move_to(-w, yb); c.curve_to(-w * 0.5, yb + 0.04, w * 0.5, yb + 0.04, w, yb); c.line_to(0, yb - ht); c.close_path()
        fill_stroke(c, hexc(col))
        if snow:
            c.move_to(-w * 0.62, yb - ht * 0.38); c.line_to(0, yb - ht); c.line_to(w * 0.62, yb - ht * 0.38)
            c.curve_to(w * 0.3, yb - ht * 0.28, w * 0.15, yb - ht * 0.45, 0, yb - ht * 0.36)
            c.curve_to(-w * 0.15, yb - ht * 0.45, -w * 0.3, yb - ht * 0.28, -w * 0.62, yb - ht * 0.38)
            c.close_path(); c.set_source_rgb(1, 1, 1); c.fill()
    c.restore()


def oak_house(c, x, y, s, light=0.0, snow=True):
    """Maison des hérissons : gros chêne creux avec porte ronde et fenêtre."""
    c.save(); c.translate(x, y); c.scale(s, s); c.set_line_width(LW * 0.7); c.set_line_join(cairo.LINE_JOIN_ROUND)
    blob(c, [(-0.45, 0), (-0.32, -0.3), (-0.3, -0.9), (-0.4, -1.05), (0.4, -1.05), (0.3, -0.9), (0.32, -0.3), (0.45, 0)])
    fill_stroke(c, hexc("#8A5E3B"))
    for k in range(5):
        xx = -0.22 + k * 0.11
        c.move_to(xx, -0.05); c.curve_to(xx + 0.03, -0.4, xx - 0.03, -0.6, xx + 0.01, -0.95); c.set_source_rgba(*INK, ) if False else c.set_source_rgba(0.35, 0.22, 0.14, 0.45); c.stroke()
    # couronne
    for (cx, cy, r) in [(-0.35, -1.15, 0.3), (0.0, -1.3, 0.38), (0.36, -1.12, 0.3), (-0.15, -1.05, 0.25), (0.2, -1.02, 0.25)]:
        ellipse(c, cx, cy, r, r * 0.8); fill_stroke(c, hexc("#3E8A5E"))
    if snow:
        for (cx, cy, r) in [(-0.35, -1.32, 0.22), (0.0, -1.53, 0.3), (0.36, -1.29, 0.22)]:
            ellipse(c, cx, cy, r, r * 0.35); c.set_source_rgb(1, 1, 1); c.fill()
    # porte ronde
    c.arc(0.02, -0.18, 0.15, math.pi, 0); c.line_to(0.17, 0); c.line_to(-0.13, 0); c.close_path(); fill_stroke(c, hexc("#C0392B"))
    ellipse(c, 0.11, -0.12, 0.018, 0.018); c.set_source_rgb(*hexc("#F2C94C")[:3]); c.fill()
    # fenêtre
    ellipse(c, -0.12, -0.6, 0.1, 0.1)
    g = cairo.RadialGradient(-0.12, -0.6, 0.01, -0.12, -0.6, 0.12)
    g.add_color_stop_rgb(0, 1, 0.9 * (0.5 + light * 0.5) + 0.05, 0.5 + 0.3 * light)
    g.add_color_stop_rgb(1, 0.95, 0.65 + light * 0.2, 0.25)
    c.set_source(g); c.fill_preserve(); c.set_source_rgb(*INK); c.stroke()
    c.move_to(-0.22, -0.6); c.line_to(-0.02, -0.6); c.move_to(-0.12, -0.7); c.line_to(-0.12, -0.5); c.stroke()
    c.restore()
