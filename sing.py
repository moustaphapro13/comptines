"""Voix chantée : synthèse vocale (Piper, voix française siwis, CC-BY 4.0)
puis recalage hauteur/durée note par note avec le vocodeur WORLD."""
import numpy as np
import pyworld as pw
from scipy.signal import resample_poly
from piper import PiperVoice, SynthesisConfig

VOICE = "/home/claude/voice/fr-siwis-medium.onnx"
VSR = 22050
FP = 5.0  # ms par trame WORLD

# syllabe chantée -> phonèmes
PHON = {
    "Frè": "fʁˈɛ", "re": "ʁˈə", "Jac": "ʒˈa", "ques": "kˈə",
    "Dor": "dˈɔʁ", "mez": "mˈe", "vous": "vˈu",
    "Son": "sˈɔ", "son": "sˈɔ", "nez": "nˈe", "les": "lˈe", "ma": "mˈa", "ti": "tˈi", "nes": "nˈə",
    "Ding": "dˈiŋ", "dang": "dˈɑŋ", "dong": "dˈɔŋ",
}

_voice = None
_cache = {}


def key_of(txt):
    t = txt.strip(" ,?!-").strip()
    return t


def raw_syllable(syl):
    global _voice
    if syl in _cache:
        return _cache[syl]
    if _voice is None:
        _voice = PiperVoice.load(VOICE)
    ph = list(PHON[syl])
    ids = _voice.phonemes_to_ids(ph)
    cfg = SynthesisConfig(length_scale=1.5, noise_scale=0.4, noise_w_scale=0.5)
    a = _voice.phoneme_ids_to_audio(ids, cfg).astype(np.float64)
    # coupe le silence
    env = np.abs(a)
    thr = env.max() * 0.03
    idx = np.where(env > thr)[0]
    a = a[max(0, idx[0] - 50): idx[-1] + 200]
    f0, t = pw.harvest(a, VSR, f0_floor=120, f0_ceil=500, frame_period=FP)
    sp = pw.cheaptrick(a, f0, t, VSR)
    ap = pw.d4c(a, f0, t, VSR)
    _cache[syl] = (f0, sp, ap)
    return _cache[syl]


def warp_formants(sp, ratio):
    n = sp.shape[1]
    src = np.arange(n) / ratio
    out = np.empty_like(sp)
    for i in range(sp.shape[0]):
        out[i] = np.interp(src, np.arange(n), sp[i])
    return out


def sing_note(syl, midi, dur, prev_midi=None, formant=1.0, breath=0.0):
    """Renvoie (audio 44.1 kHz, avance de l'attaque en s)."""
    f0, sp, ap = raw_syllable(syl)
    voiced = np.where(f0 > 0)[0]
    v0, v1 = voiced[0], voiced[-1] + 1
    onset, mid, coda = slice(0, v0), slice(v0, v1), slice(v1, len(f0))
    n_on, n_co = v0, len(f0) - v1
    total = int(dur * 1000 / FP)
    n_mid = max(8, total - n_co)
    # étirement de la partie voisée
    src = np.linspace(v0, v1 - 1, n_mid)
    lo = np.floor(src).astype(int); fr = (src - lo)[:, None]
    hi = np.minimum(lo + 1, v1 - 1)
    sp_m = np.exp(np.log(sp[lo] + 1e-12) * (1 - fr) + np.log(sp[hi] + 1e-12) * fr)
    ap_m = ap[lo] * (1 - fr) + ap[hi] * fr
    sp2 = np.vstack([sp[onset], sp_m, sp[coda]])
    ap2 = np.vstack([ap[onset], ap_m, ap[coda]])
    # courbe de hauteur
    target = 440.0 * 2 ** ((midi - 69) / 12)
    tt = np.arange(n_mid) * FP / 1000
    semis = np.zeros(n_mid)
    if prev_midi is not None and prev_midi != midi:
        g = np.clip(tt / 0.05, 0, 1)
        semis += (prev_midi - midi) * (1 - g * g * (3 - 2 * g))
    vib = 0.28 * np.sin(2 * np.pi * 5.3 * tt) * np.clip((tt - 0.22) / 0.2, 0, 1)
    semis += vib
    f0_m = target * 2 ** (semis / 12)
    f0_on = np.zeros(n_on); f0_co = np.zeros(n_co)
    f0_2 = np.concatenate([f0_on, f0_m, f0_co])
    # consonnes voisées hors zone : garder sourd
    if formant != 1.0:
        sp2 = warp_formants(sp2, formant)
    if breath:
        ap2 = np.clip(ap2 + breath, 0, 1)
    y = pw.synthesize(np.ascontiguousarray(f0_2), np.ascontiguousarray(sp2), np.ascontiguousarray(ap2), VSR, FP)
    # enveloppe douce en fin de note
    rel = int(0.04 * VSR)
    if len(y) > rel:
        y[-rel:] *= np.linspace(1, 0, rel)
    y = resample_poly(y, 2, 1)
    return y, n_on * FP / 1000
