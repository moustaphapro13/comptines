TITLE = "Are You Sleeping, Brother John?"
LANG = "en"
BPM = 92
PARTS = {"v1": [
    "Are|C you|D sleep~|E ing,|C are|C you|D sleep~|E ing,|C",
    "Bro~|E ther|F John?|G|2 Bro~|E ther|F John?|G|2",
    "Morn~|G|0.5 ing|A|0.5 bells|G|0.5 are|F|0.5 ring~|E ing,|C morn~|G|0.5 ing|A|0.5 bells|G|0.5 are|F|0.5 ring~|E ing,|C",
    "Ding,|C dang,|G3 dong!|C|2 Ding,|C dang,|G3 dong!|C|2",
]}
CHORDS = {"v1": "C C C C C C C C C C C C C G C C"}
INTRO = 8
SHORT = [("v1", "normal"), ("v1", "canon", "Sing it as a round!", 8)]
LONG = [("v1", "normal"), ("v1", "ensemble", "Everybody!"), ("v1", "soft", "Softly…"),
        ("v1", "loud", "Loud and proud!"), ("v1", "canon", "Sing it as a round!", 8)]
SCENE = dict(sky="day", ground="hills", props=[
    dict(k="sun", size=150, at=(0.55, 0.3), sky=True, anim="float"),
    dict(k="house", size=320, wall="#FFE2B8", roof="#E85A4F", at=(0.22, 40)),
    dict(k="tower", size=260, at=(0.8, 40)),
    dict(k="bell", size=110, at=(0.8, 40 - 260 * 1.47), anim="swing", z=2),
    dict(k="critter", kind="bear", size=150, at=(0.48, 80), anim=["bounce", "sing"]),
    dict(k="critter", kind="boy", size=140, at=(0.6, 85), anim=["sway", "sing"]),
], short_props=[
    dict(k="sun", size=150, at=(0.5, 0.3), sky=True, anim="float"),
    dict(k="house", size=280, at=(0.25, 20)),
    dict(k="tower", size=230, at=(0.78, 20)),
    dict(k="bell", size=100, at=(0.78, 20 - 230 * 1.47), anim="swing", z=2),
    dict(k="critter", kind="bear", size=140, at=(0.5, 110), anim=["bounce", "sing"]),
])
