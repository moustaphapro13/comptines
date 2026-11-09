TITLE = "Mary Had a Little Lamb"
LANG = "en"
BPM = 100
PARTS = {
    "v1": ["Ma~|E ry|D had|C a|D|1|ə lit~|E tle|E lamb,|E|2",
           "lit~|D tle|D lamb,|D|2 lit~|E tle|G lamb,|G|2",
           "Ma~|E ry|D had|C a|D|1|ə lit~|E tle|E lamb,|E its|E",
           "fleece|D was|D white|E as|D snow.|C|4"],
    "v2": ["Ev~|E ery~|D where|C that|D Ma~|E ry|E went,|E|2",
           "Ma~|D ry|D went,|D|2 Ma~|E ry|G went,|G|2",
           "Ev~|E ery~|D where|C that|D Ma~|E ry|E went,|E the|E",
           "lamb|D was|D sure|E to|D go.|C|4"],
}
CHORDS = {"v1": "C C C C G G C C C C C C G G C C", "v2": "C C C C G G C C C C C C G G C C"}
INTRO = 4
SHORT = [("v1", "normal"), ("v2", "ensemble", "Everybody!"), ("v1", "loud", "Loud and proud!")]
LONG = [("v1", "normal"), ("v2", "ensemble", "Everybody!"), ("v1", "soft", "Softly…"),
        ("v2", "normal"), ("v1", "karaoke", "Your turn to sing!"), ("v2", "loud", "Loud and proud!")]
SCENE = dict(sky="day", ground="hills", props=[
    dict(k="sun", size=140, at=(0.88, 0.2), sky=True, anim="float"),
    dict(k="house", size=300, wall="#FFE9B0", roof="#4F7FD9", at=(0.16, 40)),
    dict(k="fence", length=520, size=70, at=(0.7, 50)),
    dict(k="tree", size=230, at=(0.95, 55), fruit="#FF6F61"),
    dict(k="critter", kind="girl", size=200, at=(0.42, 80), anim=["bounce", "sing"]),
    dict(k="critter", kind="lamb", size=150, at=(0.6, 95), anim="hop"),
], short_props=[
    dict(k="sun", size=140, at=(0.8, 0.25), sky=True, anim="float"),
    dict(k="house", size=260, wall="#FFE9B0", roof="#4F7FD9", at=(0.2, 20)),
    dict(k="fence", length=420, size=60, at=(0.72, 30)),
    dict(k="critter", kind="girl", size=190, at=(0.4, 100), anim=["bounce", "sing"]),
    dict(k="critter", kind="lamb", size=140, at=(0.7, 110), anim="hop"),
])
