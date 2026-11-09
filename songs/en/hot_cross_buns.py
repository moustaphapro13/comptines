TITLE = "Hot Cross Buns"
LANG = "en"
BPM = 100
PARTS = {
    "v1": ["Hot|E cross|D buns!|C|2 Hot|E cross|D buns!|C|2",
           "One|C|0.5 a|C|0.5|ə pen~|C|0.5 ny,|C|0.5 two|D|0.5 a|D|0.5|ə pen~|D|0.5 ny,|D|0.5 Hot|E cross|D buns!|C|2"],
    "v2": ["Hot|E cross|D buns!|C|2 Hot|E cross|D buns!|C|2",
           "If|C|0.5 you|C|0.5 have|C|0.5 no|C|0.5 daugh~|D|0.5 ters,|D|0.5 give|D|0.5 them|D|0.5 to|E your|D sons!|C|2"],
}
CHORDS = {"v1": "C C C C C G C C", "v2": "C C C C C G C C"}
INTRO = 4
SHORT = [("v1", "normal"), ("v1", "ensemble", "Everybody!"), ("v2", "normal", "Verse 2"),
         ("v1", "loud", "Loud and proud!"), ("v1", "karaoke", "Your turn to sing!")]
LONG = SHORT
SCENE = dict(sky="day", ground="hills", props=[
    dict(k="sun", size=140, at=(0.85, 0.2), sky=True, anim="float"),
    dict(k="stall", size=360, at=(0.5, 50)),
    dict(k="bun", size=80, at=(0.42, -60), anim="bounce"),
    dict(k="bun", size=80, at=(0.5, -60), anim="hop"),
    dict(k="bun", size=80, at=(0.58, -60), anim="bounce"),
    dict(k="critter", kind="bear", size=190, at=(0.24, 70), anim=["bounce", "sing"]),
    dict(k="critter", kind="cat", size=140, at=(0.78, 80), anim=["sway", "sing"]),
    dict(k="tree", size=240, at=(0.06, 60)),
], short_props=[
    dict(k="sun", size=140, at=(0.8, 0.25), sky=True, anim="float"),
    dict(k="stall", size=330, at=(0.5, 0)),
    dict(k="bun", size=75, at=(0.38, -110), anim="bounce"),
    dict(k="bun", size=75, at=(0.5, -110), anim="hop"),
    dict(k="bun", size=75, at=(0.62, -110), anim="bounce"),
    dict(k="critter", kind="bear", size=170, at=(0.25, 90), anim=["bounce", "sing"]),
    dict(k="critter", kind="cat", size=130, at=(0.77, 95), anim=["sway", "sing"]),
])
