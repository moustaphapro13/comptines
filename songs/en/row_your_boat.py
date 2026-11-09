TITLE = "Row, Row, Row Your Boat"
LANG = "en"
BPM = 76
PARTS = {"v1": [
    "Row,|C row,|C row|C|2/3 your|D|1/3 boat|E",
    "gent~|E|2/3 ly|D|1/3 down|E|2/3 the|F|1/3 stream.|G|2",
    "Mer~|C5|1/3 ri~|C5|1/3 ly,|C5|1/3 mer~|G|1/3 ri~|G|1/3 ly,|G|1/3 mer~|E|1/3 ri~|E|1/3 ly,|E|1/3 mer~|C|1/3 ri~|C|1/3 ly,|C|1/3",
    "life|G|2/3 is|F|1/3 but|E|2/3 a|D|1/3|ə dream.|C|2",
]}
CHORDS = {"v1": "C C C C C C G C"}
INTRO = 4
SHORT = [("v1", "normal"), ("v1", "ensemble", "Everybody!"), ("v1", "canon", "Sing it as a round!", 4),
         ("v1", "karaoke", "Your turn to row!")]
LONG = SHORT
SCENE = dict(sky="day", ground="water", props=[
    dict(k="sun", size=150, at=(0.15, 0.22), sky=True, anim="float"),
    dict(k="tree", size=230, at=(0.08, -10)),
    dict(k="tree", size=190, at=(0.93, -20), fruit="#FF6F61"),
    dict(k="critter", kind="bear", size=150, at=(0.5, 10), anim=["bob", "sing"], z=1),
    dict(k="boat", size=300, at=(0.5, 55), anim="bob", z=2),
    dict(k="oar", size=180, at=(0.6, 25), anim="row", z=3),
    dict(k="critter", kind="duck", size=90, at=(0.78, 75), anim="bob", z=2),
    dict(k="critter", kind="frog", size=80, at=(0.25, 80), anim="hop", z=2),
], short_props=[
    dict(k="sun", size=150, at=(0.2, 0.25), sky=True, anim="float"),
    dict(k="tree", size=220, at=(0.12, -10)),
    dict(k="critter", kind="bear", size=150, at=(0.5, 80), anim=["bob", "sing"], z=1),
    dict(k="boat", size=300, at=(0.5, 130), anim="bob", z=2),
    dict(k="oar", size=170, at=(0.66, 95), anim="row", z=3),
    dict(k="critter", kind="duck", size=90, at=(0.85, 190), anim="bob", z=2),
])
