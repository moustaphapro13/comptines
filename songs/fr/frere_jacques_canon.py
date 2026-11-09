TITLE = "Frère Jacques en canon"
LANG = "fr"
BPM = 92
PARTS = {"v1": [
    "Frè~|C re|D Jac~|E ques,|C frè~|C re|D Jac~|E ques,|C",
    "dor~|E mez-|F vous_?|G|2 Dor~|E mez-|F vous_?|G|2",
    "Son~|G|0.5 nez|A|0.5 les|G|0.5 ma~|F|0.5 ti~|E nes,|C son~|G|0.5 nez|A|0.5 les|G|0.5 ma~|F|0.5 ti~|E nes,|C",
    "Ding,|C|1|dˈiŋ dang,|G3|1|dˈɑŋ dong_!|C|2|dˈɔŋ Ding,|C|1|dˈiŋ dang,|G3|1|dˈɑŋ dong_!|C|2|dˈɔŋ",
]}
CHORDS = {"v1": "C C C C C C C C C C C C C G C C"}
INTRO = 8
SHORT = [("v1", "normal"), ("v1", "canon", "En canon_!", 8)]
LONG = SHORT
SCENE = dict(sky="winter", ground="snow", snow=True, props=[
    dict(k="sun", size=120, at=(0.5, 0.2), sky=True, anim="float"),
    dict(k="house", size=320, wall="#FFE2B8", roof="#E85A4F", at=(0.2, 40)),
    dict(k="tower", size=260, at=(0.8, 40)),
    dict(k="bell", size=110, at=(0.8, 40 - 260 * 1.47), anim="swing", z=2),
    dict(k="fir", size=200, at=(0.06, 50)),
    dict(k="snowman", size=150, at=(0.62, 70), anim="sway"),
    dict(k="critter", kind="boy", size=160, at=(0.44, 80), anim=["bounce", "sing"]),
], short_props=[
    dict(k="house", size=280, at=(0.25, 20)),
    dict(k="tower", size=230, at=(0.78, 20)),
    dict(k="bell", size=100, at=(0.78, 20 - 230 * 1.47), anim="swing", z=2),
    dict(k="snowman", size=140, at=(0.75, 120), anim="sway"),
    dict(k="critter", kind="boy", size=160, at=(0.42, 110), anim=["bounce", "sing"]),
])
