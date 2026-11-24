TITLE = "Brosse, brosse les dents"
LANG = "fr"
ORIGINAL = True
BPM = 116
# Comptine inédite (paroles et mélodie originales, Ding Dang comptines).
L1 = "Bros~|G|0.5 se,|E|0.5 bros~|G|0.5 se,|E|0.5 bros~|G|1 se|E|0.5 les|F|0.5 dents,|D|2 |-|2"
L3 = "Bros~|G|0.5 se,|E|0.5 bros~|G|0.5 se,|E|0.5 bros~|G|1 se|E|0.5 les|F|0.5 dents,|G|2 |-|2"
L4 = "des|C5|0.5 dents|B|1 tou~|A|0.5 tes|G|0.5 pro~|F|0.5 pres,|E|0.5 c'est|D|1 ga~|D|0.5 gné_!|C|2 |-|1"
R = "|F|0.5 |A|1 |F|0.5 |D|1 |E|0.5 |F|0.5 |G|0.5 |A|0.5 |G|2 |-|1".split()


def line2(words):
    toks = []
    for w, r in zip(words, R):
        toks.append(w + r)
    return " ".join(toks + R[len(words):])


V = {"v1": ["en", "haut,", "en", "bas,", "et", "sur", "les", "cô~", "tés_!"],
     "v2": ["on", "fait", "des", "p'tits|||pti", "ronds", "tout", "doux,", "tout", "doux_!"],
     "v3": ["un", "ver~", "re", "d'eau", "et", "un", "grand", "sou~", "rire_!"],
     "v4": ["et", "Ding|||dˈiŋ", "et", "Dang|||dˈaŋ", "ont", "des", "dents", "qui", "brillent_!"]}


def l2(words):
    out = []
    for w, r in zip(words, R):
        if "|||" in w:
            t, ph = w.split("|||")
            out.append(t + r + "|" + ph)
        else:
            out.append(w + r)
    return " ".join(out + R[len(words):])


PARTS = {k: [L1, l2(w), L3, L4] for k, w in V.items()}
CHORDS = {k: "C C G G F F G G C C G G F G C C" for k in PARTS}
INTRO = 4
SHORT = [("v1", "normal"), ("v2", "normal", "Tout doux, tout doux…"), ("v4", "ensemble", "Avec Ding et Dang_!")]
LONG = [("v1", "normal"), ("v2", "normal", "Tout doux, tout doux…"), ("v3", "normal", "On rince_!"),
        ("v4", "ensemble", "Avec Ding et Dang_!"), ("v1", "karaoke", "À toi de chanter_!"), ("v4", "loud", "Plus fort_!")]
SCENE = dict(sky="day", ground="floor", props=[
    dict(k="balloon", size=70, col="#CDEBFF", at=(0.12, 0.3), sky=True, anim="float"),
    dict(k="balloon", size=50, col="#CDEBFF", at=(0.25, 0.5), sky=True, anim="float"),
    dict(k="balloon", size=60, col="#CDEBFF", at=(0.45, 0.25), sky=True, anim="float"),
    dict(k="balloon", size=45, col="#CDEBFF", at=(0.62, 0.45), sky=True, anim="float"),
    dict(k="balloon", size=75, col="#CDEBFF", at=(0.8, 0.3), sky=True, anim="float"),
    dict(k="balloon", size=50, col="#CDEBFF", at=(0.9, 0.55), sky=True, anim="float"),
    dict(k="hedgehog", who="ding", size=300, at=(0.33, 70), anim=["bounce", "sing"]),
    dict(k="hedgehog", who="dang", size=290, face=-1, at=(0.67, 75), anim=["hop", "sing"]),
], short_props=[
    dict(k="balloon", size=70, col="#CDEBFF", at=(0.15, 0.3), sky=True, anim="float"),
    dict(k="balloon", size=50, col="#CDEBFF", at=(0.4, 0.45), sky=True, anim="float"),
    dict(k="balloon", size=65, col="#CDEBFF", at=(0.7, 0.28), sky=True, anim="float"),
    dict(k="balloon", size=45, col="#CDEBFF", at=(0.85, 0.5), sky=True, anim="float"),
    dict(k="hedgehog", who="ding", size=330, at=(0.28, 110), anim=["bounce", "sing"]),
    dict(k="hedgehog", who="dang", size=320, face=-1, at=(0.72, 115), anim=["hop", "sing"]),
])
