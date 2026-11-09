TITLE = "Old MacDonald Had a Farm"
LANG = "en"
BPM = 126


def verse(animal, snd):
    s = snd
    return [
        "Old|G Mac~|G Don~|G ald|D had|E a|E|1|ə farm,|D|2",
        "E-~|B i-~|B e-~|A i-~|A o!|G|3 And|D",
        f"on|G his|G farm|G he|D had|E a|E|1|ə {animal},|D|2",
        "E-~|B i-~|B e-~|A i-~|A o!|G|3 With|D|0.5 a|D|0.5|ə",
        f"{s}|G {s}|G here,|G and|D|0.5 a|D|0.5|ə {s}|G {s}|G there,|G|2",
        f"here|G|0.5 a|G|0.5|ə {s},|G there|G|0.5 a|G|0.5|ə {s},|G ev~|G|0.5 ery~|G|0.5 where|G|0.5 a|G|0.5|ə {s}|G {s}.|G",
        "Old|G Mac~|G Don~|G ald|D had|E a|E|1|ə farm,|D|2",
        "E-~|B i-~|B e-~|A i-~|A o!|G|4",
    ]


PARTS = {"cow": verse("cow", "moo"), "pig": verse("pig", "oink"), "duck": verse("duck", "quack"),
         "sheep": verse("sheep", "baa")}
CH = "G G C G D D G G G G C G D D G G G G G G G G D G G G C G D D G G"
CHORDS = {k: CH for k in PARTS}
INTRO = 4
SHORT = [("cow", "normal"), ("duck", "ensemble", "Quack quack!")]
LONG = [("cow", "normal"), ("pig", "ensemble", "Oink oink!"), ("duck", "normal", "Quack quack!"),
        ("sheep", "loud", "Baa baa!"), ("cow", "karaoke", "Your turn to sing!")]
SCENE = dict(sky="day", ground="hills", props=[
    dict(k="sun", size=140, at=(0.5, 0.18), sky=True, anim="float"),
    dict(k="barn", size=330, at=(0.2, 30)),
    dict(k="fence", length=700, size=70, at=(0.65, 30)),
    dict(k="critter", kind="cow", size=170, at=(0.45, 85), anim=["bounce", "sing"]),
    dict(k="critter", kind="pig", size=130, at=(0.6, 95), anim="hop"),
    dict(k="critter", kind="duck", size=100, at=(0.72, 100), anim="bounce"),
    dict(k="critter", kind="lamb", size=130, at=(0.85, 95), anim="sway"),
    dict(k="tree", size=220, at=(0.96, 40), fruit="#FF6F61"),
], short_props=[
    dict(k="sun", size=140, at=(0.8, 0.22), sky=True, anim="float"),
    dict(k="barn", size=300, at=(0.3, 10)),
    dict(k="fence", length=500, size=60, at=(0.72, 20)),
    dict(k="critter", kind="cow", size=160, at=(0.25, 110), anim=["bounce", "sing"]),
    dict(k="critter", kind="pig", size=120, at=(0.5, 120), anim="hop"),
    dict(k="critter", kind="duck", size=95, at=(0.7, 125), anim="bounce"),
    dict(k="critter", kind="lamb", size=120, at=(0.88, 120), anim="sway"),
])
