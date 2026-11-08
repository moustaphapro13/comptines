"""Frère Jacques — partition, structure, synthèse audio avec voix chantée."""
import numpy as np
import wave
from sing import sing_note, key_of

BPM = 92
BEAT = 60.0 / BPM
SR = 44100

# (syllabe affichée, note midi, durée en temps)
PHRASES = [
    [("Frè", 72, 1), ("re ", 74, 1), ("Jac", 76, 1), ("ques, ", 72, 1),
     ("Frè", 72, 1), ("re ", 74, 1), ("Jac", 76, 1), ("ques,", 72, 1)],
    [("Dor", 76, 1), ("mez-", 77, 1), ("vous ? ", 79, 2),
     ("Dor", 76, 1), ("mez-", 77, 1), ("vous ?", 79, 2)],
    [("Son", 79, .5), ("nez ", 81, .5), ("les ", 79, .5), ("ma", 77, .5), ("ti", 76, 1), ("nes, ", 72, 1),
     ("son", 79, .5), ("nez ", 81, .5), ("les ", 79, .5), ("ma", 77, .5), ("ti", 76, 1), ("nes,", 72, 1)],
    [("Ding, ", 72, 1), ("dang, ", 67, 1), ("dong ! ", 72, 2),
     ("Ding, ", 72, 1), ("dang, ", 67, 1), ("dong !", 72, 2)],
]

# Sections : (début en temps, mode, étiquette affichée)
STRUCT = {
    "long": dict(
        intro=8,
        sections=[(8, "normal", None), (40, "ensemble", "Tous ensemble !"),
                  (72, "soft", "Tout doucement…"), (104, "loud", "Plus fort !"),
                  (136, "karaoke", "À toi de chanter !"), (168, "canon", "En canon !")],
        canon2=176,
        day=[(0, 0), (8, 0), (32, .18), (38, 1), (72, 1), (80, 0), (96, .06), (102, 1)],
        sleep=[(0, 32), (79, 96)],
        outro=8),
    "short": dict(
        intro=4,
        sections=[(4, "normal", None)],
        canon2=None,
        day=[(0, 0), (4, 0), (28, .18), (34, 1)],
        sleep=[(0, 28)],
        outro=4),
}


def timeline(kind):
    S = STRUCT[kind]
    secs = S["sections"]
    last = secs[-1][0] + 32
    if S["canon2"]:
        last = S["canon2"] + 32
    song_end = last
    end = song_end + S["outro"]
    lines = []
    for st, mode, lab in secs:
        for i in range(4):
            lines.append((st + 8 * i, i))
    if S["canon2"]:
        lines.append((S["canon2"] + 24, 3))
    bells = []
    for k in range(S["intro"] // 4):
        bells += [(4 * k, 72), (4 * k + 1, 67), (4 * k + 2, 72)]
    starts = [s for s, _, _ in secs] + ([S["canon2"]] if S["canon2"] else [])
    for s in starts:
        for r in range(2):
            b = s + 24 + 4 * r
            bells += [(b, 72), (b + 1, 67), (b + 2, 72)]
    labels = [(st, st + 32, lab) for st, _, lab in secs if lab]
    if S["canon2"]:
        labels[-1] = (labels[-1][0], song_end, labels[-1][2])
    return dict(intro=S["intro"], sections=secs, canon=S["canon2"], end=end, lines=lines,
                bells=sorted(set(bells)), song_end=song_end, day=S["day"], sleep=S["sleep"],
                wakes=[e for _, e in S["sleep"]], labels=labels)


def notes_from(start):
    out, b = [], start
    for ph in PHRASES:
        for syl, m, d in ph:
            out.append((b, m, d, syl))
            b += d
    return out


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
    n = int((dur + 1.2) * SR)
    t = np.arange(n) / SR
    s = (np.sin(2 * np.pi * f * t) * np.exp(-t / 0.7)
         + 0.25 * np.sin(2 * np.pi * 2 * f * t) * np.exp(-t / 0.35)
         + 0.08 * np.sin(2 * np.pi * 5.4 * f * t) * np.exp(-t / 0.12))
    return s * np.minimum(1, t / 0.004)


def flute(f, dur, vib=5.0):
    n = int((dur + 0.15) * SR)
    t = np.arange(n) / SR
    ph = 2 * np.pi * f * t + 0.004 * f / vib * np.sin(2 * np.pi * vib * t) * np.minimum(1, t / 0.3) * 2 * np.pi
    s = np.sin(ph) + 0.18 * np.sin(2 * ph) + 0.06 * np.sin(3 * ph)
    env = np.minimum(1, t / 0.035) * np.clip((dur + 0.15 - t) / 0.15, 0, 1)
    return s * env


def bass(f):
    n = int(1.4 * SR)
    t = np.arange(n) / SR
    s = np.sin(2 * np.pi * f * t) + 0.3 * np.sin(4 * np.pi * f * t) * np.exp(-t / 0.1)
    return s * np.exp(-t / 0.45) * np.minimum(1, t / 0.005)


def pad(freqs, dur):
    n = int(dur * SR)
    t = np.arange(n) / SR
    s = sum(np.sin(2 * np.pi * f * t) + 0.2 * np.sin(4 * np.pi * f * t) for f in freqs)
    env = np.minimum(1, t / 0.4) * np.clip((dur - t) / 0.4, 0, 1)
    return s * env


def bell(f):
    n = int(3.0 * SR)
    t = np.arange(n) / SR
    s = 0
    for r, a, tau in [(0.5, .6, 2.0), (1, 1, 1.4), (1.19, .5, 1.0), (1.5, .4, .8),
                      (2, .35, .6), (2.52, .2, .4), (3.01, .15, .3)]:
        s = s + a * np.sin(2 * np.pi * f * r * t) * np.exp(-t / tau)
    return s * np.minimum(1, t / 0.003)


def kick():
    n = int(0.25 * SR)
    t = np.arange(n) / SR
    f = 50 + 90 * np.exp(-t / 0.03)
    return np.sin(2 * np.pi * np.cumsum(f) / SR) * np.exp(-t / 0.09)


def noise_hit(rng, dur, tau, hp=True):
    n = int(dur * SR)
    t = np.arange(n) / SR
    x = rng.standard_normal(n)
    if hp:
        x = np.diff(np.concatenate([[0], x]))
    return x * np.exp(-t / tau)


def clap(rng):
    s = 0
    for k, d in enumerate([0, 0.008, 0.017]):
        h = noise_hit(rng, 0.2, 0.012 if k < 2 else 0.06)
        s = s + np.concatenate([np.zeros(int(d * SR)), h])[: int(0.2 * SR)]
    return s


def reverb(x, rng, secs=1.4, mix=0.18):
    n = int(secs * SR)
    t = np.arange(n) / SR
    ir = rng.standard_normal(n) * np.exp(-t / 0.35)
    ir[: int(0.02 * SR)] = 0
    ir /= np.sqrt((ir ** 2).sum())
    from scipy.signal import fftconvolve
    wet = fftconvolve(x, ir)[: len(x)]
    return x + mix * wet


def voice_track(start, n_samples, shift=0, formant=1.0, gain=1.0, breath=0.0):
    out = np.zeros(n_samples)
    prev = None
    for b, m, d, syl in notes_from(start):
        mm = m - 12 + shift
        y, adv = sing_note(key_of(syl), mm, d * BEAT * 0.94, prev, formant, breath)
        i = int((b * BEAT - adv) * SR)
        j = min(n_samples, i + len(y))
        out[i:j] += y[: j - i]
        prev = mm
    return out * gain


def render_audio(kind, path):
    tl = timeline(kind)
    total = tl["end"] * BEAT + 2.0
    N = int(total * SR)
    buf = np.zeros((N, 2))
    vox = np.zeros((N, 2))
    rng = np.random.default_rng(1)
    drums_on = []
    for st, mode, _ in tl["sections"]:
        soft = mode == "soft"
        ml = {"karaoke": 1.0, "soft": 0.45}.get(mode, 0.55)
        for b, m, d, _ in notes_from(st):
            add(buf, 0.33 * ml * glock(mtof(m), d * BEAT), b * BEAT, -0.15)
            add(buf, 0.22 * ml * flute(mtof(m), d * BEAT), b * BEAT, 0.15)
        if mode != "karaoke":
            g = 0.55 if soft else 1.0
            v = voice_track(st, N, gain=g, breath=0.15 if soft else 0.0)
            add(vox, v, 0, -0.05)
        if mode in ("ensemble", "loud"):
            v = voice_track(st, N, shift=12, formant=1.18, gain=0.33)
            add(vox, v, 0, 0.35)
        if mode == "canon":
            v = voice_track(tl["canon"], N, shift=12, formant=1.18, gain=0.55)
            add(vox, v, 0, 0.45)
            for b, m, d, _ in notes_from(tl["canon"]):
                add(buf, 0.15 * glock(mtof(m - 12), d * BEAT), b * BEAT, 0.5)
        end = st + 32 if mode != "canon" else tl["song_end"]
        drums_on.append((st, end, mode))
    for b, m in tl["bells"]:
        add(buf, 0.14 * bell(mtof(m - 12)), b * BEAT, 0.35)
    for bar in range(int(tl["song_end"] // 4)):
        b = bar * 4
        mode = next((md for s, e, md in drums_on if s <= b < e), None)
        soft = mode == "soft"
        bg = 0.6 if soft else 1.0
        add(buf, 0.30 * bg * bass(mtof(48)), b * BEAT, 0)
        add(buf, 0.26 * bg * bass(mtof(43)), (b + 2) * BEAT, 0)
        add(buf, 0.035 * pad([mtof(60), mtof(64), mtof(67)], 4 * BEAT + 0.4), b * BEAT, 0)
        if mode and not soft:
            add(buf, 0.35 * kick(), b * BEAT, 0)
            add(buf, 0.25 * kick(), (b + 2) * BEAT, 0)
            for e in range(8):
                add(buf, 0.05 * noise_hit(rng, 0.05, 0.012), (b + e * 0.5 + 0.5) * BEAT, 0.3 if e % 2 else -0.3)
            if mode in ("loud", "canon"):
                add(buf, 0.22 * clap(rng), (b + 1) * BEAT, -0.1)
                add(buf, 0.22 * clap(rng), (b + 3) * BEAT, 0.1)
    se = tl["song_end"]
    add(buf, 0.06 * pad([mtof(48), mtof(60), mtof(64), mtof(67)], 4 * BEAT + 1.5), se * BEAT, 0)
    add(buf, 0.3 * glock(mtof(72), 3), se * BEAT, 0)
    add(buf, 0.2 * bell(mtof(60)), se * BEAT, 0.35)
    # voix : niveau + réverb
    pk = np.abs(vox).max()
    if pk > 0:
        vox = vox / pk * 0.75
        for c in range(2):
            vox[:, c] = reverb(vox[:, c], rng)
    mix = buf / max(1e-9, np.abs(buf).max()) * 0.7 + vox
    mix = mix[: int((tl["end"] * BEAT + 1.0) * SR)]
    fade = int(1.0 * SR)
    mix[-fade:] *= np.linspace(1, 0, fade)[:, None]
    mix = np.tanh(mix * 1.1)
    mix /= np.abs(mix).max() / 0.89
    pcm = (mix * 32767).astype(np.int16)
    with wave.open(path, "wb") as w:
        w.setnchannels(2); w.setsampwidth(2); w.setframerate(SR)
        w.writeframes(pcm.tobytes())
    return tl["end"] * BEAT + 1.0


if __name__ == "__main__":
    import sys
    for k in sys.argv[1:] or ("long", "short"):
        print(k, render_audio(k, f"audio_{k}.wav"))
