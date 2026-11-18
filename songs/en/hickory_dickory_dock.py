TITLE = "Hickory Dickory Dock"
LANG = "en"
BPM = 126
# Traditional melody (6/8), C major. Quarter = 1 beat.
WORD = {1: "one", 2: "two", 3: "three", 4: "four", 5: "five"}


def verse(n):
    return ["Hick~|E|0.5 o~|F|0.5 ry|G|0.5 dick~|G|0.5 o~|A|0.5 ry|B|0.5 dock,|C5|2.5 |-|0.5",
            "the|E|0.5 mouse|F|0.5 ran|G|1 up|A|0.5 the|B|0.5 clock.|C5|2.5",
            f"The|G|0.5 clock|C5|1 struck|C5|0.5 {WORD[n]},|B|1 the|B|0.5 mouse|A|1 ran|A|0.5 down,|G|1.5",
            "hick~|G|0.5 o~|A|0.5 ry|G|0.5 dick~|F|0.5 o~|E|0.5 ry|D|0.5 dock.|C|3"]


PARTS = {f"v{n}": verse(n) for n in WORD}
CHORD_LEN = 1.5
CH = "C C C G7 C C C C C G G C C G7 C C"
CHORDS = {k: CH for k in PARTS}
INTRO = 6
SHORT = [("v1", "normal"), ("v2", "normal", "Two o'clock!"), ("v3", "ensemble", "Three o'clock!"),
         ("v4", "soft", "Tiptoe, little mouse…"), ("v5", "loud", "Five o'clock!")]
LONG = [("v1", "normal"), ("v2", "normal", "Two o'clock!"), ("v3", "ensemble", "Three o'clock!"),
        ("v4", "soft", "Tiptoe, little mouse…"), ("v5", "loud", "Five o'clock!"),
        ("v1", "ensemble", "All together!"), ("v2", "normal", "Two o'clock!"), ("v3", "soft", "Very quietly…"),
        ("v4", "karaoke", "Your turn to sing!"), ("v5", "loud", "Louder!")]
SCENE = dict(sky="night", ground="hills", props=[
    dict(k="moon", size=150, at=(0.85, 0.2), sky=True, anim="float"),
    dict(k="star", size=50, at=(0.1, 0.15), sky=True, anim="twinkle"),
    dict(k="star", size=40, at=(0.3, 0.1), sky=True, anim="twinkle"),
    dict(k="clock", size=300, at=(0.45, 60)),
    dict(k="critter", kind="mouse", size=130, at=(0.62, 90), anim=["hop", "sing"]),
    dict(k="critter", kind="cat", size=160, at=(0.85, 95), anim="sway"),
    dict(k="fir", size=200, snow=False, deco=False, at=(0.12, 50)),
], short_props=[
    dict(k="moon", size=140, at=(0.8, 0.2), sky=True, anim="float"),
    dict(k="star", size=45, at=(0.15, 0.15), sky=True, anim="twinkle"),
    dict(k="clock", size=280, at=(0.4, 60)),
    dict(k="critter", kind="mouse", size=130, at=(0.75, 110), anim=["hop", "sing"]),
])
