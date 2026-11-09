TITLE = "Joyeux anniversaire"
LANG = "fr"
BPM = 104
CHORD_LEN = 1
L1 = "Jo~|G|0.75 yeux|G|0.25 an~|A ni~|G ver~|C5 saire,|B|2"
PARTS = {"v1": [
    L1,
    "Jo~|G|0.75 yeux|G|0.25 an~|A ni~|G ver~|D5 saire,|C5|2",
    "Jo~|G|0.75 yeux|G|0.25 an~|G5 ni~|E5 ver~|C5 sai~|B re,|A|2",
    "Jo~|F5|0.75 yeux|F5|0.25 an~|E5 ni~|C5 ver~|D5 saire_!|C5|2",
]}
CHORDS = {"v1": "C C C G7 G7 G7  G7 G7 G7 G7 C C  C C C C F F F  F C C G7 C C"}
INTRO = 4
SHORT = [("v1", "normal"), ("v1", "ensemble", "Tous ensemble_!"), ("v1", "loud", "Plus fort_!")]
LONG = [("v1", "normal"), ("v1", "ensemble", "Tous ensemble_!"), ("v1", "soft", "Tout doucement…"),
        ("v1", "loud", "Plus fort_!"), ("v1", "karaoke", "À toi de chanter_!")]
SCENE = dict(sky="party", ground="floor", clouds=False, props=[
    dict(k="balloon", size=110, col="#FF6F91", at=(0.12, 0.35), sky=True, anim="float"),
    dict(k="balloon", size=100, col="#6EC6FF", at=(0.2, 0.42), sky=True, anim="float"),
    dict(k="balloon", size=105, col="#FFD24A", at=(0.82, 0.36), sky=True, anim="float"),
    dict(k="balloon", size=95, col="#8BE28B", at=(0.9, 0.45), sky=True, anim="float"),
    dict(k="cake", size=280, at=(0.5, 20)),
    dict(k="flame", size=40, at=(0.5 - 0.21 * 280 / 1920 * 1.4 * 0.5, 20 - 280 * 1.08), anim="flicker", z=2),
    dict(k="flame", size=40, at=(0.5, 20 - 280 * 1.08), anim="flicker", z=2),
    dict(k="flame", size=40, at=(0.5 + 0.21 * 280 / 1920 * 1.4 * 0.5, 20 - 280 * 1.08), anim="flicker", z=2),
    dict(k="critter", kind="bear", size=170, at=(0.28, 60), anim=["bounce", "sing"]),
    dict(k="critter", kind="mouse", size=120, at=(0.7, 70), anim=["hop", "sing"]),
    dict(k="critter", kind="cat", size=130, at=(0.8, 70), anim="sway"),
], short_props=[
    dict(k="balloon", size=110, col="#FF6F91", at=(0.15, 0.4), sky=True, anim="float"),
    dict(k="balloon", size=100, col="#6EC6FF", at=(0.85, 0.42), sky=True, anim="float"),
    dict(k="balloon", size=100, col="#FFD24A", at=(0.3, 0.55), sky=True, anim="float"),
    dict(k="cake", size=280, at=(0.5, 20)),
    dict(k="flame", size=40, at=(0.5 - 0.21 * 280 / 1080 * 0.92 * 0.5 * 1.4, 20 - 280 * 1.08), anim="flicker", z=2),
    dict(k="flame", size=40, at=(0.5, 20 - 280 * 1.08), anim="flicker", z=2),
    dict(k="flame", size=40, at=(0.5 + 0.21 * 280 / 1080 * 0.92 * 0.5 * 1.4, 20 - 280 * 1.08), anim="flicker", z=2),
    dict(k="critter", kind="bear", size=160, at=(0.2, 110), anim=["bounce", "sing"]),
    dict(k="critter", kind="mouse", size=120, at=(0.8, 115), anim=["hop", "sing"]),
])
