"""Partition (texte compact), structure, paroles et mixage audio — générique pour toutes les comptines.

Format d'une ligne de paroles : jetons séparés par des espaces, « texte|note|durée|phonèmes ».
  - texte se terminant par « ~ » : la syllabe continue le mot (pas d'espace affiché) ; « _ » = espace affichée
  - note : C D E F G A B (+ # ou b) + octave optionnelle (4 par défaut), « - » = silence
  - durée en temps (1 par défaut ; « 0.5 », « 2/3 »…) ; phonèmes optionnels (sinon automatiques)
"""
import re
import wave
from fractions import Fraction
import numpy as np
from scipy.signal import fftconvolve
from . import voice as V

SR = 44100
NOTE = {"C": 0, "D": 2, "E": 4, "F": 5, "G": 7, "A": 9, "B": 11}
CHORD_IV = {"": [0, 4, 7], "m": [0, 3, 7], "7": [0, 4, 7, 10], "m7": [0, 3, 7, 10], "maj7": [0, 4, 7, 11]}


def note_midi(s):
    m = re.fullmatch(r"([A-G])([#b]?)(\d?)", s)
    n = NOTE[m.group(1)] + (1 if m.group(2) == "#" else -1 if m.group(2) == "b" else 0)
    octv = int(m.group(3)) if m.group(3) else 4
    return 12 * (octv + 1) + n


def parse_line(s):
    out = []
    for tok in s.split():
        parts = tok.split("|")
        txt = parts[0]
        note = parts[1] if len(parts) > 1 else "-"
        dur = float(Fraction(parts[2])) if len(parts) > 2 and parts[2] else 1.0
        ph = parts[3] if len(parts) > 3 else None
        cont = txt.endswith("~")
        txt = txt.rstrip("~").replace("_", " ")
        join = cont or txt.endswith("-") or txt.endswith("'")
        out.append(dict(txt=txt, midi=None if note == "-" else note_midi(note), dur=dur, ph=ph, cont=cont, join=join))
    return out


def chord_notes(sym):
    m = re.fullmatch(r"([A-G][#b]?)(m7|maj7|m|7)?", sym)
    root = note_midi(m.group(1)) % 12
    return root, CHORD_IV[m.group(2) or ""]


class Song:
    def __init__(self, mod):
        self.m = mod
        self.lang = mod.LANG
        self.bpm = mod.BPM
        self.beat = 60.0 / self.bpm
        self.parts = {k: [parse_line(l) for l in lines] for k, lines in mod.PARTS.items()}
        self.chords = {}
        for k, lines in mod.PARTS.items():
            cs = getattr(mod, "CHORDS", {}).get(k)
            self.chords[k] = cs.split() if cs else None
        self.chord_len = getattr(mod, "CHORD_LEN", 2)
        self._phon()
        allm = [s["midi"] for p in self.parts.values() for l in p for s in l if s["midi"]]
        mean = np.mean(allm)
        self.vshift = int(round((63 - mean) / 12)) * 12
        self.ishift = int(round((76 - mean) / 12)) * 12

    def _phon(self):
        """Phonèmes automatiques : regroupe les syllabes par mot et découpe."""
        for p in self.parts.values():
            for line in p:
                word = []
                for s in line + [None]:
                    if s is not None and s["midi"] is None:
                        continue
                    if s is not None:
                        word.append(s)
                    if s is None or not s["cont"]:
                        if word:
                            need = [w for w in word if not w["ph"]]
                            if need and len(need) < len(word):
                                for w in need:
                                    w["ph"] = V.syllabify(self.lang, re.sub(r"[^\w'’]", "", w["txt"]) or "a", 1)[0]
                            elif need:
                                text = "".join(re.sub(r"[^\w'’-]", "", w["txt"]) for w in word)
                                text = text.replace("-", " ")
                                sy = V.syllabify(self.lang, text, len(word))
                                for w, ph in zip(word, sy):
                                    if not w["ph"]:
                                        w["ph"] = ph
                        word = []

    def part_beats(self, k):
        return sum(s["dur"] for l in self.parts[k] for s in l)

    # ------------------------------------------------------------ structure
    def timeline(self, kind):
        m = self.m
        secs = m.LONG if kind == "long" else m.SHORT
        intro = getattr(m, "INTRO", 8 if kind == "long" else 4)
        b = intro
        sections, lines, labels = [], [], []
        tail_end = 0
        for sec in secs:
            part, mode, lab = sec[0], sec[1], sec[2] if len(sec) > 2 else None
            off = sec[3] if len(sec) > 3 else None
            L = self.part_beats(part)
            sections.append(dict(part=part, mode=mode, start=b, beats=L, canon=off))
            lb = b
            for i, line in enumerate(self.parts[part]):
                lines.append(dict(start=lb, part=part, idx=i, voice2=False))
                lb += sum(s["dur"] for s in line)
            if off:
                lb = b + off
                for i, line in enumerate(self.parts[part]):
                    if lb >= b + L:
                        lines.append(dict(start=lb, part=part, idx=i, voice2=True))
                    lb += sum(s["dur"] for s in line)
                tail_end = max(tail_end, b + L + off)
            if lab:
                labels.append((b, b + L + (off or 0), lab))
            b += L
        song_end = max(b, tail_end)
        outro = 4
        return dict(intro=intro, sections=sections, lines=lines, labels=labels,
                    song_end=song_end, end=song_end + outro, beat=self.beat)

    def notes(self, part, start):
        out, b = [], start
        for line in self.parts[part]:
            for s in line:
                if s["midi"] is not None:
                    out.append((b, s))
                b += s["dur"]
        return out

    def chord_at(self, part, rel):
        cs = self.chords.get(part)
        if not cs:
            return None
        i = int(rel // self.chord_len)
        return cs[min(i, len(cs) - 1)]


# ---------------------------------------------------------------- synthèse
def mtof(m):
    return 440.0 * 2 ** ((m - 69) / 12)


def add(buf, sig, t0, pan=0.0):
    i = int(t0 * SR)
    if i < 0:
        sig = sig[-i:]; i = 0
    j = min(len(buf), i + len(sig))
    if j <= i:
        return
    l, r = np.cos((pan + 1) * np.pi / 4), np.sin((pan + 1) * np.pi / 4)
    buf[i:j, 0] += sig[: j - i] * l
    buf[i:j, 1] += sig[: j - i] * r


def glock(f, dur):
    n = int((dur + 1.2) * SR); t = np.arange(n) / SR
    s = (np.sin(2 * np.pi * f * t) * np.exp(-t / 0.7) + 0.25 * np.sin(4 * np.pi * f * t) * np.exp(-t / 0.35)
         + 0.08 * np.sin(2 * np.pi * 5.4 * f * t) * np.exp(-t / 0.12))
    return s * np.minimum(1, t / 0.004)


def flute(f, dur, vib=5.0):
    n = int((dur + 0.15) * SR); t = np.arange(n) / SR
    ph = 2 * np.pi * f * t + 0.004 * f / vib * np.sin(2 * np.pi * vib * t) * np.minimum(1, t / 0.3) * 2 * np.pi
    s = np.sin(ph) + 0.18 * np.sin(2 * ph) + 0.06 * np.sin(3 * ph)
    return s * np.minimum(1, t / 0.035) * np.clip((dur + 0.15 - t) / 0.15, 0, 1)


def bass(f, dur):
    n = int((dur + 0.3) * SR); t = np.arange(n) / SR
    s = np.sin(2 * np.pi * f * t) + 0.3 * np.sin(4 * np.pi * f * t) * np.exp(-t / 0.1)
    return s * np.exp(-t / 0.5) * np.minimum(1, t / 0.005)


def pad(freqs, dur):
    n = int(dur * SR); t = np.arange(n) / SR
    s = sum(np.sin(2 * np.pi * f * t) + 0.2 * np.sin(4 * np.pi * f * t) for f in freqs)
    return s * np.minimum(1, t / 0.3) * np.clip((dur - t) / 0.3, 0, 1)


def pluck(f, dur):
    n = int((dur + 0.5) * SR); t = np.arange(n) / SR
    s = sum(np.sin(2 * np.pi * f * k * t) * np.exp(-t * (3 + k * 2)) / k for k in range(1, 5))
    return s * np.minimum(1, t / 0.003)


def kick():
    n = int(0.25 * SR); t = np.arange(n) / SR
    f = 50 + 90 * np.exp(-t / 0.03)
    return np.sin(2 * np.pi * np.cumsum(f) / SR) * np.exp(-t / 0.09)


def noise_hit(rng, dur, tau):
    n = int(dur * SR); t = np.arange(n) / SR
    x = np.diff(np.concatenate([[0], rng.standard_normal(n)]))
    return x * np.exp(-t / tau)


def clap(rng):
    s = 0
    for k, d in enumerate([0, 0.008, 0.017]):
        h = noise_hit(rng, 0.2, 0.012 if k < 2 else 0.06)
        s = s + np.concatenate([np.zeros(int(d * SR)), h])[: int(0.2 * SR)]
    return s


def reverb(x, rng, mix=0.18):
    n = int(1.4 * SR); t = np.arange(n) / SR
    ir = rng.standard_normal(n) * np.exp(-t / 0.35); ir[: int(0.02 * SR)] = 0
    ir /= np.sqrt((ir ** 2).sum())
    return x + mix * fftconvolve(x, ir)[: len(x)]


def voice_track(song, part, start, N, shift=0, formant=1.0, gain=1.0, breath=0.0):
    out = np.zeros(N)
    prev = None
    B = song.beat
    for b, s in song.notes(part, start):
        mm = s["midi"] + song.vshift + shift
        y, adv = V.sing(song.lang, s["ph"], mm, s["dur"] * B * 0.94, prev, formant, breath)
        i = int((b * B - adv) * SR)
        j = min(N, i + len(y))
        if i < 0:
            y = y[-i:]; i = 0
        out[i:j] += y[: j - i]
        prev = mm
    return out * gain


def render_audio(song, kind, path):
    tl = song.timeline(kind)
    B = song.beat
    N = int((tl["end"] * B + 2.5) * SR)
    buf = np.zeros((N, 2)); vox = np.zeros((N, 2))
    rng = np.random.default_rng(1)
    I = song.ishift
    first = tl["sections"][0]["part"]
    c0 = song.chord_at(first, 0) or "C"
    # intro : arpège de l'accord de départ
    root, iv = chord_notes(c0)
    for k in range(int(tl["intro"] * 2)):
        n = 60 + root + iv[k % len(iv)] + 12 * ((k // len(iv)) % 2) + I - 12
        add(buf, 0.22 * glock(mtof(n + 12), 0.5 * B), k * 0.5 * B, 0.3 if k % 2 else -0.3)
    for sec in tl["sections"]:
        part, mode, st = sec["part"], sec["mode"], sec["start"]
        ml = {"karaoke": 1.0, "soft": 0.45}.get(mode, 0.55)
        for b, s in song.notes(part, st):
            add(buf, 0.33 * ml * glock(mtof(s["midi"] + I), s["dur"] * B), b * B, -0.15)
            add(buf, 0.20 * ml * flute(mtof(s["midi"] + I), s["dur"] * B), b * B, 0.15)
        if mode != "karaoke":
            add(vox, voice_track(song, part, st, N, gain=0.55 if mode == "soft" else 1.0,
                                 breath=0.15 if mode == "soft" else 0.0), 0, -0.05)
        if mode in ("ensemble", "loud"):
            add(vox, voice_track(song, part, st, N, shift=12, formant=1.18, gain=0.33), 0, 0.35)
        if mode == "canon":
            o = st + sec["canon"]
            add(vox, voice_track(song, part, o, N, shift=12, formant=1.18, gain=0.55), 0, 0.45)
            for b, s in song.notes(part, o):
                add(buf, 0.15 * glock(mtof(s["midi"] + I - 12), s["dur"] * B), b * B, 0.5)
        # harmonie
        L = sec["beats"] + (sec["canon"] or 0)
        cl = song.chord_len
        prevc = None
        for k in range(int(np.ceil(L / cl))):
            rel = k * cl
            sym = song.chord_at(part, rel % sec["beats"]) or c0
            r, iv = chord_notes(sym)
            t0 = (st + rel) * B
            g = 0.6 if mode == "soft" else 1.0
            add(buf, 0.30 * g * bass(mtof(36 + r if r < 7 else 24 + r), cl * B), t0, 0)
            add(buf, 0.03 * g * pad([mtof(60 + r + i if r + i < 8 else 48 + r + i) for i in iv[:3]], cl * B + 0.3), t0, 0)
            if mode in ("normal", "ensemble", "loud", "canon", "karaoke") and k % 1 == 0:
                for e in range(int(cl * 2)):
                    if e % 2 == 1:
                        add(buf, 0.06 * g * pluck(mtof(60 + r + iv[e // 2 % len(iv)]), 0.5 * B), t0 + e * 0.5 * B, 0.4)
            prevc = sym
        if mode != "soft":
            for bb in range(int(L)):
                t0 = (st + bb) * B
                if bb % 2 == 0:
                    add(buf, (0.35 if bb % 4 == 0 else 0.25) * kick(), t0, 0)
                add(buf, 0.05 * noise_hit(rng, 0.05, 0.012), t0 + 0.5 * B, 0.3)
                if mode in ("loud", "canon") and bb % 2 == 1:
                    add(buf, 0.22 * clap(rng), t0, -0.1)
    se = tl["song_end"]
    r, iv = chord_notes(c0)
    add(buf, 0.06 * pad([mtof(48 + r)] + [mtof(60 + r + i) for i in iv[:3]], 4 * B + 1.5), se * B, 0)
    add(buf, 0.3 * glock(mtof(72 + r + I - 12), 3), se * B, 0)
    pk = np.abs(vox).max()
    if pk > 0:
        vox = vox / pk * 0.75
        for c in range(2):
            vox[:, c] = reverb(vox[:, c], rng)
    mix = buf / max(1e-9, np.abs(buf).max()) * 0.7 + vox
    mix = mix[: int((tl["end"] * B + 1.0) * SR)]
    fade = int(1.0 * SR)
    mix[-fade:] *= np.linspace(1, 0, fade)[:, None]
    mix = np.tanh(mix * 1.1)
    mix /= np.abs(mix).max() / 0.89
    with wave.open(path, "wb") as w:
        w.setnchannels(2); w.setsampwidth(2); w.setframerate(SR)
        w.writeframes((mix * 32767).astype(np.int16).tobytes())
    return tl["end"] * B + 1.0
