TITLE = "London Bridge Is Falling Down"
LANG = "en"
BPM = 104


def verse(a, b):
    """a = 'Lon~|G|1.5 don|A|0.5 Bridge|G is|F fall~|E ing|F down,|G|2' ; b = refrain (3 syllables)"""
    s1, s2, s3 = b
    return [a,
            f"{s1}|D {s2}|E {s3}|F|2 {s1}|E {s2}|F {s3}|G|2",
            a,
            "my|D|2 fair|G|2 la~|E dy.|C|3 -|-|1"]


PARTS = {
    "v1": verse("Lon~|G|1.5 don|A|0.5 Bridge|G is|F fall~|E ing|F down,|G|2", ("fall~", "ing", "down,")),
    "v2": verse("Build|G|1.5 it|A|0.5 up|G with|F i~|E ron|F bars,|G|2", ("i~", "ron", "bars,")),
    "v3": verse("I~|G|1.5 ron|A|0.5 bars|G will|F bend|E and|F break,|G|2", ("bend", "and", "break,")),
    "v4": verse("Build|G|1.5 it|A|0.5 up|G with|F stone|E so|F strong,|G|2", ("stone", "so", "strong,")),
}
CH = "C C C C G G C C C C C C G G C C"
CHORDS = {k: CH for k in PARTS}
INTRO = 4
SHORT = [("v1", "normal"), ("v2", "ensemble", "Build it up!"), ("v4", "loud", "Stone so strong!")]
LONG = [("v1", "normal"), ("v2", "ensemble"), ("v3", "soft"), ("v4", "loud", "Stone so strong!"),
        ("v1", "karaoke", "Your turn to sing!")]
SCENE = dict(sky="day", ground="water", props=[
    dict(k="sun", size=140, at=(0.12, 0.2), sky=True, anim="float"),
    dict(k="bridge", width=1500, size=330, at=(0.5, 160), z=1),
    dict(k="critter", kind="girl", size=130, at=(0.3, -165), anim=["walk", "sing"], z=2),
    dict(k="critter", kind="boy", size=130, at=(0.55, -165), anim=["walk", "sing"], z=2),
    dict(k="critter", kind="duck", size=90, at=(0.82, 210), anim="bob", z=3),
], short_props=[
    dict(k="sun", size=140, at=(0.8, 0.25), sky=True, anim="float"),
    dict(k="bridge", width=1000, size=280, at=(0.5, 150), z=1),
    dict(k="critter", kind="girl", size=120, at=(0.35, -125), anim=["walk", "sing"], z=2),
    dict(k="critter", kind="boy", size=120, at=(0.75, -125), anim=["walk", "sing"], z=2),
])
