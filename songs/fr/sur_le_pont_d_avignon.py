TITLE = "Sur le pont d'Avignon"
LANG = "fr"
BPM = 104
CHORD_LEN = 1
# Mélodie traditionnelle (2/4), transposée en do. Noire = 1 temps.
PONT = "Sur|C|0.5 le|C|0.5 pont|C|1 d'A~|D|0.5 vi~|D|0.5 gnon,|D|1"
L2 = "l'on~|E|0.75|lˈɔŋ y|F|0.25|ni dan~|G|0.5 se,|C|0.5 l'on~|B3|0.75|lˈɔŋ y|C|0.25|ni dan~|D|0.5 se,|G3|0.5"
L4 = "l'on~|E|0.75|lˈɔŋ y|F|0.25|ni dan~|G|0.5 se|C|0.5 tous|D|0.5 en|B3|0.5|tɑŋ rond.|C|0.5 |-|0.5"
REFRAIN = [PONT, L2, PONT, L4]
CH_R = "C C G G C C G G C C G G C C G C"


def couplet(qui):
    return [f"{qui} font|C|0.5 comm'|D|2|kˈɔm ça,|C|1 |-|1",
            "et|C|0.75 puis|C|0.25|pɥˈi en~|C|0.5|ɑŋ cor'|C|0.5|kˈɔʁ comm'|D|2|kˈɔm ça._|C|1 |-|1"] + REFRAIN


QUI = {"messieurs": "Les|C|0.5 beaux|C|0.25 mes~|C|0.25 sieurs|C|0.5",
       "dames": "Les|C|0.5 bel~|C|0.25 les|C|0.25 dames|C|0.5|dˈam",
       "soldats": "Les|C|0.5 sol~|C|0.5 dats|C|0.5",
       "musiciens": "Les|C|0.5 mu~|C|0.25 si~|C|0.25 ciens|C|0.5",
       "enfants": "Les|C|0.5 p'tits|C|0.25|ptˈi en~|C|0.25|zɑŋ fants|C|0.5|fˈɑŋ"}
PARTS = {"refrain": REFRAIN}
CHORDS = {"refrain": CH_R}
for k, q in QUI.items():
    PARTS[k] = couplet(q)
    n = 2 if k != "soldats" else 2
    CHORDS[k] = "C C G G C C C C G G C C " + CH_R
INTRO = 4
SHORT = [("refrain", "normal"), ("messieurs", "normal", "Les beaux messieurs"), ("dames", "normal", "Les belles dames"),
         ("refrain", "ensemble", "Tous ensemble_!")]
LONG = [("refrain", "normal"), ("messieurs", "normal", "Les beaux messieurs"), ("dames", "normal", "Les belles dames"),
        ("soldats", "loud", "Les soldats"), ("musiciens", "normal", "Les musiciens"),
        ("enfants", "ensemble", "Les petits enfants"), ("refrain", "soft", "Tout doucement…"),
        ("refrain", "karaoke", "À toi de chanter_!"), ("refrain", "loud", "Plus fort_!")]
SCENE = dict(sky="dusk", ground="water", props=[
    dict(k="sun", size=150, at=(0.85, 0.22), sky=True, anim="float"),
    dict(k="cloud", size=170, at=(0.2, 0.15), sky=True, anim="drift"),
    dict(k="bridge", width=1500, size=330, at=(0.5, 160), z=1),
    dict(k="critter", kind="girl", size=130, at=(0.3, -165), anim=["hop", "sing"], z=2),
    dict(k="critter", kind="boy", size=130, at=(0.45, -165), anim=["bounce", "sing"], z=2),
    dict(k="critter", kind="pierrot", size=120, at=(0.6, -165), anim="hop", z=2),
    dict(k="critter", kind="cat", size=110, at=(0.74, -165), anim="bounce", z=2),
    dict(k="boat", size=150, at=(0.85, 220), anim="bob", z=3),
], short_props=[
    dict(k="sun", size=140, at=(0.8, 0.25), sky=True, anim="float"),
    dict(k="bridge", width=1000, size=280, at=(0.5, 150), z=1),
    dict(k="critter", kind="girl", size=120, at=(0.3, -125), anim=["hop", "sing"], z=2),
    dict(k="critter", kind="boy", size=120, at=(0.55, -125), anim=["bounce", "sing"], z=2),
    dict(k="critter", kind="cat", size=100, at=(0.78, -125), anim="bounce", z=2),
])
