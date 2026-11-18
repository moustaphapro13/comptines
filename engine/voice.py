"""Voix chantée multilingue : Piper (phonèmes) + recalage hauteur/durée WORLD."""
import json
import numpy as np
import pyworld as pw
import parselmouth
from parselmouth.praat import call
from scipy.signal import resample_poly
from piper import PiperVoice, SynthesisConfig

VOICES = {
    "fr": "/home/claude/voice/sherpa/vits-piper-fr_FR-siwis-medium/fr_FR-siwis-medium.onnx",
    "en": "/home/claude/voice/en-us-lessac-medium.onnx",
    "es": "/home/claude/voice/es-mls_10246-low.onnx",
}
FP = 5.0
VOWELS = set("aeiouyæɑɒɔəɛɜɚɝɪʊʌøœɐɨɘɵ")
LIQ = set("ʁlɹrjwɥ")
_v, _cache, _sr = {}, {}, {}


def voice(lang):
    if lang not in _v:
        _v[lang] = PiperVoice.load(VOICES[lang])
        cfg = json.load(open(VOICES[lang] + ".json"))
        _sr[lang] = cfg["audio"]["sample_rate"]
        _v[lang]._idmap = cfg["phoneme_id_map"]
    return _v[lang]


def _clean(lang, ph):
    v = voice(lang)
    out = []
    for p in ph:
        if p in "ˈˌ -,.;:!?'\"«»()‿":
            continue
        if p == "̃":            # voyelle nasale : marqueur interne Ñ (devient ŋ si la voix ignore le tilde)
            out.append("̃" if "̃" in v._idmap else "Ñ")
            continue
        if p in v._idmap:
            out.append(p)
    return out


def syllabify(lang, word, n, overrides=None):
    """Découpe les phonèmes d'un mot en n syllabes chantées."""
    v = voice(lang)
    ph = [p for sent in v.phonemize(word) for p in sent]
    ph = _clean(lang, ph)
    nuc = []                     # groupes de voyelles [start, end)
    i = 0
    while i < len(ph):
        if ph[i] in VOWELS:
            j = i + 1
            while j < len(ph) and (ph[j] in "ːÑ\u0303"):
                j += 1
            nuc.append([i, j])
            i = j
        else:
            i += 1
    # trop de noyaux : fusionner ceux qui se touchent (diphtongues) puis les plus proches
    while len(nuc) > n and len(nuc) > 1:
        gaps = [nuc[k + 1][0] - nuc[k][1] for k in range(len(nuc) - 1)]
        k = int(np.argmin(gaps))
        nuc[k] = [nuc[k][0], nuc[k + 1][1]]
        del nuc[k + 1]
    sylls = []
    if not nuc:
        return ["".join(ph)] + ["ə"] * (n - 1)
    start = 0
    for k, (a, b) in enumerate(nuc):
        if k + 1 < len(nuc):
            na = nuc[k + 1][0]
            cons = na - b
            cut = b if cons <= 1 else b + 1
            if cons >= 3:
                cut = b + 1
            if cons == 2 and ph[b + 1] in LIQ and ph[b] not in LIQ:
                cut = b
            sylls.append(ph[start:a] + ["ˈ"] + ph[a:cut])
            start = cut
        else:
            sylls.append(ph[start:a] + ["ˈ"] + ph[a:])
    # pas assez : e muet français / syllabe finale chantée
    while len(sylls) < n:
        last = sylls[-1]
        vi = max(i for i, p in enumerate(last) if p in VOWELS or p == "ˈ")
        coda = [p for p in last[vi + 1:] if p not in VOWELS and p not in "ːÑ\u0303"]
        if coda:
            mv = 2 if len(coda) >= 2 and coda[-1] in LIQ and coda[-2] not in LIQ else 1
            sylls[-1] = last[: len(last) - mv]
            sylls.append(coda[-mv:] + ["ˈ", "ə"])
        else:
            sylls.append(["ˈ", "ə"])
    return ["".join(s).replace("Ñ", "ŋ") for s in sylls]


def raw(lang, phon):
    key = (lang, phon)
    if key in _cache:
        return _cache[key]
    v = voice(lang)
    sr = _sr[lang]
    ids = v.phonemes_to_ids(list(phon))
    cfg = SynthesisConfig(length_scale=1.5, noise_scale=0.4, noise_w_scale=0.5)
    a = v.phoneme_ids_to_audio(ids, cfg).astype(np.float64)
    env = np.abs(a)
    idx = np.where(env > env.max() * 0.03)[0]
    a = a[max(0, idx[0] - 50): idx[-1] + 200]
    f0, t = pw.harvest(a, sr, f0_floor=90, f0_ceil=500, frame_period=FP)
    if (f0 > 0).sum() < 3:                      # sécurité : syllabe sans voisement détecté
        f0, t = pw.dio(a, sr, f0_floor=80, f0_ceil=600, frame_period=FP)
        f0 = pw.stonemask(a, f0, t, sr)
    if (f0 > 0).sum() < 3:
        f0[:] = 0; f0[len(f0) // 3: 2 * len(f0) // 3] = 200
    sp = pw.cheaptrick(a, f0, t, sr)
    ap = pw.d4c(a, f0, t, sr)
    _cache[key] = (f0, sp, ap, sr)
    return _cache[key]


def warp(sp, ratio):
    n = sp.shape[1]
    src = np.arange(n) / ratio
    out = np.empty_like(sp)
    for i in range(sp.shape[0]):
        out[i] = np.interp(src, np.arange(n), sp[i])
    return out


_rawpsola = {}


def _syll_audio(lang, phon):
    key = (lang, phon)
    if key not in _rawpsola:
        v = voice(lang); sr = _sr[lang]
        ids = v.phonemes_to_ids(list(phon))
        a = v.phoneme_ids_to_audio(ids, SynthesisConfig(length_scale=1.4, noise_scale=0.5, noise_w_scale=0.5)).astype(np.float64)
        env = np.abs(a); idx = np.where(env > env.max() * 0.03)[0]
        a = a[max(0, idx[0] - 50): idx[-1] + 300]
        snd = parselmouth.Sound(a, sr)
        pt = snd.to_pitch_ac(0.005, 90, 600)
        f = pt.selected_array["frequency"]; ts = pt.xs()
        vi = np.where(f > 0)[0]
        if len(vi) >= 3:
            v0, v1 = ts[vi[0]], ts[vi[-1]]
        else:
            v0, v1 = len(a) / sr * 0.3, len(a) / sr * 0.7
        _rawpsola[key] = (a, sr, v0, v1)
    return _rawpsola[key]


def sing(lang, phon, midi, dur, prev=None, formant=1.0, breath=0.0, out_sr=44100):
    """Chant naturel : synthèse Piper puis PSOLA (Praat) pour la hauteur et la durée (pas de vocodeur)."""
    a, sr, v0, v1 = _syll_audio(lang, phon)
    T = len(a) / sr
    vlen = max(0.04, v1 - v0)
    onset, coda = v0, T - v1
    k = max(0.25, (dur - coda - onset * 0.0) / vlen) if dur > onset + coda else max(0.25, (dur * 0.6) / vlen)
    snd = parselmouth.Sound(a, sr)
    man = call(snd, "To Manipulation", 0.01, 75, 600)
    dt = call("Create DurationTier", "d", 0, T)
    call(dt, "Add point", max(0.0, v0 - 0.005), 1.0); call(dt, "Add point", v0 + 0.005, k)
    call(dt, "Add point", v1 - 0.005, k); call(dt, "Add point", min(T, v1 + 0.005), 1.0)
    call([man, dt], "Replace duration tier")
    target = 440.0 * 2 ** ((midi - 69) / 12)
    ptier = call("Create PitchTier", "p", 0, T)
    n = 40
    for i in range(n + 1):
        u = i / n
        to = u * vlen * k                       # temps de sortie depuis le début de la voyelle
        ti = v0 + u * vlen                      # temps d'origine correspondant
        semis = 0.0
        if prev is not None and prev != midi:
            g = min(1.0, to / 0.06); semis += (prev - midi) * (1 - g * g * (3 - 2 * g))
        semis += 0.22 * np.sin(2 * np.pi * 5.2 * to) * min(1.0, max(0.0, (to - 0.25) / 0.2))
        semis += 0.04 * np.sin(2 * np.pi * 1.3 * to + midi)
        call(ptier, "Add point", ti, target * 2 ** (semis / 12))
    call(ptier, "Add point", max(0, v0 - 0.02), target * 2 ** (((prev - midi) if prev is not None else 0) / 12))
    call(ptier, "Add point", min(T, v1 + 0.02), target)
    call([man, ptier], "Replace pitch tier")
    out = call(man, "Get resynthesis (overlap-add)")
    if formant != 1.0:
        out = call(out, "Change gender", 75, 600, formant, 0, 1, 1)
    y = out.values[0].astype(np.float64)
    if breath:
        y = y + breath * 0.02 * np.random.default_rng(len(y)).standard_normal(len(y)) * (np.abs(y) > 0.01)
    rel = int(0.04 * out.sampling_frequency)
    if len(y) > rel:
        y[-rel:] *= np.linspace(1, 0, rel)
    from math import gcd
    sr2 = int(out.sampling_frequency)
    g = gcd(out_sr, sr2)
    y = resample_poly(y, out_sr // g, sr2 // g)
    return y, onset
