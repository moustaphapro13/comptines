"""Voix parlées de la série (Piper + transformation WORLD pour les voix d'enfants)."""
import json, hashlib, os
import numpy as np, pyworld as pw, soundfile as sf
from scipy.signal import resample_poly
from piper import PiperVoice, SynthesisConfig

V = "/home/claude/voice/"
MODELS = {"siwis": V + "fr-siwis-medium.onnx", "siwis_low": V + "dl/voice-fr-siwis-low/fr-siwis-low.onnx",
          "gilles": V + "dl/voice-fr-gilles-low/fr-gilles-low.onnx",
          "mls": V + "dl/voice-fr-mls_1840-low/fr-mls_1840-low.onnx"}
# personnage -> (modèle, facteur f0, facteur formants, vitesse (length_scale), expressivité)
CAST = {
    "narr":  ("gilles", 1.0, 1.0, 1.08, 1.15),
    "maman": ("siwis", 1.06, 1.02, 0.98, 1.25),
    "papa":  ("mls", 1.0, 1.0, 0.62, 1.2),
    "ding":  ("siwis_low", 1.32, 1.12, 0.92, 1.35),
    "dang":  ("siwis", 1.55, 1.2, 0.9, 1.45),
}
SR = 44100
_m = {}
CACHE = "/tmp/serie_tts"; os.makedirs(CACHE, exist_ok=True)


def _voice(k):
    if k not in _m:
        v = PiperVoice.load(MODELS[k])
        v._idmap = json.load(open(MODELS[k] + ".json"))["phoneme_id_map"]
        v._sr = v.config.sample_rate
        _m[k] = v
    return _m[k]


def _phon(v, text):
    out = []
    for sent in v.phonemize(text):
        ph = []
        for p in sent:
            if p == "̃":            # nasale : la voix n'a pas le tilde -> ŋ
                ph.append("ŋ")
            elif p in v._idmap:
                ph.append(p)
        out.append(ph)
    return out


def _tts(k, text, ls):
    v = _voice(k)
    parts = []
    for ph in _phon(v, text):
        ids = v.phonemes_to_ids(ph)
        a = v.phoneme_ids_to_audio(ids, SynthesisConfig(length_scale=ls, noise_scale=0.6, noise_w_scale=0.8))
        parts.append(np.asarray(a, dtype=np.float64))
        parts.append(np.zeros(int(0.18 * v._sr)))
    return np.concatenate(parts[:-1]), v._sr


def say(who, text, emo="neutral"):
    """Renvoie l'audio (44.1 kHz mono float) d'une réplique."""
    k, fk, fm, ls, expr = CAST[who]
    if emo in ("excited", "surprised"):
        fk *= 1.08; expr *= 1.25; ls *= 0.93
    elif emo in ("sad", "sleepy"):
        fk *= 0.94; expr *= 0.7; ls *= 1.12
    elif emo == "whisper":
        expr *= 0.6
    key = hashlib.md5(f"{who}|{text}|{emo}|{fk}|{fm}|{ls}|{expr}|v3".encode()).hexdigest()
    fn = f"{CACHE}/{key}.wav"
    if os.path.exists(fn):
        return sf.read(fn)[0]
    a, sr = _tts(k, text, ls)
    if fk != 1.0 or fm != 1.0 or expr != 1.0:
        f0, t = pw.harvest(a, sr, f0_floor=60, f0_ceil=500, frame_period=5.0)
        sp = pw.cheaptrick(a, f0, t, sr); ap = pw.d4c(a, f0, t, sr)
        v = f0 > 0
        if v.any():
            lf = np.log(f0[v]); m = np.median(lf)
            f0[v] = np.exp(m + (lf - m) * expr) * fk
        if fm != 1.0:
            nb = sp.shape[1]; idx = np.arange(nb)
            src = np.clip(idx / fm, 0, nb - 1)
            sp = np.array([np.interp(src, idx, row) for row in sp])
        a = pw.synthesize(f0, sp, ap, sr, 5.0)
    y = resample_poly(a, SR, sr)
    y = y / (np.abs(y).max() + 1e-9) * 0.9
    sf.write(fn, y, SR)
    return y
