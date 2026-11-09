TITLE = "Twinkle, Twinkle, Little Star"
LANG = "en"
BPM = 96
PARTS = {
    "v1": [
        "Twin~|C kle,|C twin~|G kle,|G lit~|A tle|A star,|G|2",
        "How|F I|F won~|E der|E what|D you|D are!|C|2",
        "Up|G a~|G bove|F the|F world|E so|E high,|D|2",
        "Like|G a|G|1|ˈə dia~|F mond|F in|E the|E sky.|D|2",
        "Twin~|C kle,|C twin~|G kle,|G lit~|A tle|A star,|G|2",
        "How|F I|F won~|E der|E what|D you|D are!|C|2",
    ],
}
CHORDS = {"v1": "C C F C  F C G C  C F C G  C F C G  C C F C  F C G C"}
INTRO = 8
SHORT = [("v1", "normal"), ("v1", "ensemble", "Everybody!")]
LONG = [("v1", "normal"), ("v1", "ensemble", "Everybody!"), ("v1", "soft", "Softly…"),
        ("v1", "karaoke", "Your turn to sing!"), ("v1", "loud", "Loud and proud!")]
SCENE = dict(
    sky="night", ground="hills", stars=True,
    props=[
        dict(k="star", size=330, at=(0.5, 0.32), sky=True, anim=["twinkle", "float"]),
        dict(k="star", size=70, face_on=False, at=(0.18, 0.2), sky=True, anim="twinkle"),
        dict(k="star", size=55, face_on=False, at=(0.82, 0.15), sky=True, anim="twinkle"),
        dict(k="star", size=60, face_on=False, at=(0.3, 0.55), sky=True, anim="twinkle"),
        dict(k="moon", size=150, at=(0.88, 0.45), sky=True, anim="float"),
        dict(k="house", size=300, at=(0.2, 40)),
        dict(k="tree", size=220, at=(0.92, 60), col="#3E7A55"),
        dict(k="critter", kind="bear", size=170, at=(0.66, 70), anim=["bounce", "sing"]),
        dict(k="critter", kind="cat", size=130, at=(0.42, 80), anim=["sway", "sing"]),
    ],
    short_props=[
        dict(k="star", size=360, at=(0.5, 0.3), sky=True, anim=["twinkle", "float"]),
        dict(k="star", size=70, face_on=False, at=(0.15, 0.12), sky=True, anim="twinkle"),
        dict(k="star", size=55, face_on=False, at=(0.85, 0.1), sky=True, anim="twinkle"),
        dict(k="moon", size=140, at=(0.85, 0.62), sky=True, anim="float"),
        dict(k="house", size=260, at=(0.22, 30)),
        dict(k="critter", kind="bear", size=170, at=(0.7, 60), anim=["bounce", "sing"]),
        dict(k="critter", kind="cat", size=120, at=(0.47, 80), anim=["sway", "sing"]),
    ],
)
