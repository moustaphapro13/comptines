TITLE = "Ah ! Vous dirai-je, maman"
LANG = "fr"
BPM = 96
PARTS = {"v1": [
    "Ah_!|C vous|C di~|G rai-~|G je,|A ma~|A man,|G|2",
    "ce|F qui|F cau~|E se|E mon|D tour~|D ment_?|C|2",
    "Pa~|G pa|G veut|F que|F je|E rai~|E sonne|D|2",
    "comm'|G|1|kˈɔm u~|G ne|F gran~|F de|E per~|E sonne.|D|2",
    "Moi,|C je|C dis|G que|G les|A bon~|A bons|G|2",
    "va~|F lent|F mieux|E que|E la|D rai~|D son_!|C|2",
]}
CHORDS = {"v1": "C C F C  F C G C  C F C G  C F C G  C C F C  F C G C"}
INTRO = 4
SHORT = [("v1", "normal"), ("v1", "ensemble", "Tous ensemble_!")]
LONG = [("v1", "normal"), ("v1", "ensemble", "Tous ensemble_!"), ("v1", "soft", "Tout doucement…"),
        ("v1", "karaoke", "À toi de chanter_!"), ("v1", "loud", "Plus fort_!")]
SCENE = dict(sky="day", ground="hills", props=[
    dict(k="sun", size=140, at=(0.12, 0.22), sky=True, anim="float"),
    dict(k="house", size=320, wall="#FFE9F0", roof="#FF6F91", at=(0.18, 40)),
    dict(k="candy_jar", size=170, at=(0.72, 60), anim="bounce"),
    dict(k="lollipop", size=70, col="#FF6F91", at=(0.84, 70), anim="sway"),
    dict(k="lollipop", size=60, col="#6EC6FF", at=(0.9, 75), anim="sway"),
    dict(k="critter", kind="girl", size=200, at=(0.45, 80), anim=["bounce", "sing"]),
    dict(k="critter", kind="bear", size=200, at=(0.58, 75), anim="sway"),
], short_props=[
    dict(k="sun", size=140, at=(0.8, 0.25), sky=True, anim="float"),
    dict(k="house", size=280, wall="#FFE9F0", roof="#FF6F91", at=(0.25, 20)),
    dict(k="candy_jar", size=150, at=(0.8, 70), anim="bounce"),
    dict(k="critter", kind="girl", size=190, at=(0.35, 110), anim=["bounce", "sing"]),
    dict(k="critter", kind="bear", size=180, at=(0.58, 105), anim="sway"),
])
