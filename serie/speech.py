"""Voix parlées de la série.
Voix neuronales naturelles (Kokoro « ff_siwis », Piper « tom » et « upmc »), sans vocodeur WORLD.
Voix d'enfants : synthèse un peu plus lente puis lecture accélérée (hauteur + timbre plus aigus,
débit normal) — le procédé des dessins animés, sans artefact robotique."""
import hashlib, os
from math import gcd
import numpy as np, soundfile as sf, onnxruntime as ort
from scipy.signal import resample_poly
from piper import PiperVoice, SynthesisConfig

B = "/home/claude/voice/sherpa/"
KOK = B + "kokoro-multi-lang-v1_0/"
PIPER = {"tom": B + "vits-piper-fr_FR-tom-medium/fr_FR-tom-medium.onnx",
         "upmc": B + "vits-piper-fr_FR-upmc-medium/fr_FR-upmc-medium.onnx",
         "siwis": B + "vits-piper-fr_FR-siwis-medium/fr_FR-siwis-medium.onnx"}
# personnage -> (moteur, locuteur, vitesse de synthèse, accélération de lecture)
CAST = {
    "narr":  ("upmc", 1, 0.92, 0.97),
    "maman": ("upmc", 0, 0.98, 1.0),
    "papa":  ("tom", None, 0.95, 0.97),
    "ding":  ("tom", None, 0.85, 1.3),
    "dang":  ("siwis", None, 0.9, 1.18),
}
SR = 44100
CACHE = "/tmp/serie_tts2"; os.makedirs(CACHE, exist_ok=True)
_p, _k = {}, {}


def _piper(n):
    if n not in _p:
        _p[n] = PiperVoice.load(PIPER[n])
    return _p[n]


def _kokoro():
    if not _k:
        tok = {}
        for l in open(KOK + "tokens.txt", encoding="utf-8"):
            l = l.rstrip("\n")
            if l:
                s, i = l.rsplit(" ", 1); tok[s if s else " "] = int(i)
        _k["tok"] = tok
        _k["V"] = np.fromfile(KOK + "voices.bin", dtype=np.float32).reshape(-1, 510, 256)
        _k["s"] = ort.InferenceSession(KOK + "model.onnx")
    return _k


FIX = [("dˈɪŋ", "dˈiŋ"), ("dɪŋ", "diŋ"), ("dˈɑ̃ɡ", "dˈaŋ"), ("dɑ̃ɡ", "daŋ")]   # Ding [diŋ], Dang [daŋ]


def _phon(text):
    out = []
    for sent in _piper("siwis").phonemize(text):
        ph = "".join(sent)
        for a, b in FIX:
            ph = ph.replace(a, b)
        out.append(ph)
    return out


def _gen(eng, sid, speed, text):
    sents = _phon(text)
    if eng == "kokoro":
        k = _kokoro()
        groups = []                     # phrases courtes regroupées : Kokoro les prononce mal isolées
        for ph in sents:
            if groups and (len(groups[-1]) < 28 or len(ph) < 18):
                groups[-1] += " " + ph
            else:
                groups.append(ph)
        out = []
        for ph in groups:
            ids = [k["tok"][c] for c in ph if c in k["tok"]]
            st = k["V"][sid, min(len(ids), 509)][None]
            a = k["s"].run(None, {"tokens": np.array([[0] + ids + [0]], dtype=np.int64), "style": st,
                                   "speed": np.array([speed], dtype=np.float32)})[0]
            out += [a, np.zeros(int(0.15 * 24000), dtype=np.float32)]
        return np.concatenate(out[:-1]).astype(np.float64), 24000
    v = _piper(eng)
    cfg = SynthesisConfig(speaker_id=sid, length_scale=1.0 / speed, noise_scale=0.667, noise_w_scale=0.8)
    parts = []
    for ph in sents:
        ids = v.phonemes_to_ids(list(ph))
        parts += [np.asarray(v.phoneme_ids_to_audio(ids, cfg), dtype=np.float64), np.zeros(int(0.2 * v.config.sample_rate))]
    return np.concatenate(parts[:-1]), v.config.sample_rate


def say(who, text, emo="neutral"):
    """Audio (44,1 kHz mono) d'une réplique."""
    eng, sid, speed, play = CAST[who]
    if emo in ("excited", "surprised"):
        speed *= 1.07
    elif emo in ("sad", "sleepy"):
        speed *= 0.9
    key = hashlib.md5(f"{who}|{text}|{emo}|{CAST[who]}|v6".encode()).hexdigest()
    fn = f"{CACHE}/{key}.wav"
    if os.path.exists(fn):
        return sf.read(fn)[0]
    tts = text.replace("…", ",").replace("?!", "?").replace(" ,", ",").replace(",,", ",")
    a, sr = _gen(eng, sid, speed, tts)
    src = int(round(sr * play))          # lecture accélérée = rééchantillonnage depuis sr*play
    g = gcd(SR, src)
    y = resample_poly(a, SR // g, src // g)
    i = np.flatnonzero(np.abs(y) > 0.02 * np.abs(y).max())
    if i.size:
        y = y[max(0, i[0] - 1500): i[-1] + 8000]
    y = y / (np.abs(y).max() + 1e-9) * 0.9
    sf.write(fn, y, SR)
    return y
