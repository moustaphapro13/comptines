from engine.compose import line
TITLE = "Goodnight, Ding and Dang"
LANG = "en"
BPM = 84
ORIGINAL = True
M1, M2, M3, M4 = "E G G A G E D:2", "C D E G E D C:2", "E G G C5 B A G:2", "A G E D E D C:2"
L1 = line("Good-night, the moon is shin-ing,", M1)
L3 = line("good-night to all the bird-ies,", M3)
V = {"v1": ("Ding and Dang now close their eyes,", "in their co-zy lit-tle beds."),
     "v2": ("soft-ly sings the win-ter wind,", "and the for-est falls a-sleep."),
     "v3": ("one small kiss up-on your nose,", "one big hug and off to sleep."),
     "v4": ("have sweet dreams, my lit-tle one,", "see you when the sun comes up.")}
PARTS = {k: [L1, line(a, M2), L3, line(b, M4)] for k, (a, b) in V.items()}
CHORDS = {k: "C F C G C C G C C C G G F C G C" for k in PARTS}
INTRO = 4
SHORT = [("v1", "soft"), ("v3", "soft", "One big hug…")]
LONG = [("v1", "soft"), ("v2", "soft"), ("v3", "soft", "One big hug…"), ("v4", "soft", "Sweet dreams…"), ("v1", "karaoke", "Sing it softly…")]
SCENE = dict(sky="night", ground="hills", props=[
    dict(k="moon", size=160, at=(0.82, 0.2), sky=True, anim="float"),
    dict(k="star", size=50, at=(0.15, 0.15), sky=True, anim="twinkle"),
    dict(k="star", size=40, at=(0.35, 0.1), sky=True, anim="twinkle"),
    dict(k="star", size=45, at=(0.6, 0.18), sky=True, anim="twinkle"),
    dict(k="house", size=300, wall="#F6E6C8", roof="#8E6CCF", at=(0.88, 40)),
    dict(k="hedgehog", who="ding", size=290, at=(0.32, 70), anim=["sway", "sing"]),
    dict(k="hedgehog", who="dang", size=280, face=-1, at=(0.6, 75), anim=["sway", "sing"]),
], short_props=[
    dict(k="moon", size=150, at=(0.75, 0.2), sky=True, anim="float"),
    dict(k="star", size=45, at=(0.2, 0.15), sky=True, anim="twinkle"),
    dict(k="star", size=40, at=(0.45, 0.25), sky=True, anim="twinkle"),
    dict(k="hedgehog", who="ding", size=320, at=(0.27, 110), anim=["sway", "sing"]),
    dict(k="hedgehog", who="dang", size=310, face=-1, at=(0.73, 115), anim=["sway", "sing"]),
])
