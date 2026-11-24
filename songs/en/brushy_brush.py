from engine.compose import line
TITLE = "Brushy Brush Your Teeth"
LANG = "en"
BPM = 116
ORIGINAL = True
M1 = "G:.5 E:.5 G:.5 E:.5 G E:.5 F:.5 D:2 -:2"
M2 = "F:.5 A F:.5 D E:.5 F:.5 G:.5 A:.5 G:2 -:1"
M3 = "G:.5 E:.5 G:.5 E:.5 G E:.5 F:.5 G:2 -:2"
M4 = "C5:.5 B A:.5 G:.5 F:.5 E:.5 D D:.5 C:2 -:1"
L1 = line("Brush-y, brush-y, brush, brush your teeth,", M1)
L3 = line("brush-y, brush-y, brush, brush your teeth,", M3)
L4 = line("shi-ny, clean and spark-ly, hip hoo-ray!", M4)
V = {"v1": "up and down and round and round we go,",
     "v2": "gen-tle lit-tle cir-cles, nice and slow,",
     "v3": "rinse and spit, and give a|||ɐ great big smile,",
     "v4": "Ding and Dang have teeth that shine so bright!"}
PARTS = {k: [L1, line(a, M2), L3, L4] for k, a in V.items()}
CHORDS = {k: "C C G G F F G G C C G G F G C C" for k in PARTS}
INTRO = 4
SHORT = [("v1", "normal"), ("v2", "normal", "Nice and slow…"), ("v4", "ensemble", "With Ding and Dang!")]
LONG = [("v1", "normal"), ("v2", "normal", "Nice and slow…"), ("v3", "normal", "Rinse and spit!"),
        ("v4", "ensemble", "With Ding and Dang!"), ("v1", "karaoke", "Your turn to sing!"), ("v4", "loud", "Louder!")]
BUB = [(0.12, 0.3, 70), (0.25, 0.5, 50), (0.45, 0.25, 60), (0.62, 0.45, 45), (0.8, 0.3, 75), (0.9, 0.55, 50)]
SCENE = dict(sky="day", ground="floor", props=[dict(k="balloon", size=s, col="#CDEBFF", at=(x, y), sky=True, anim="float") for x, y, s in BUB] + [
    dict(k="hedgehog", who="ding", size=300, at=(0.33, 70), anim=["bounce", "sing"]),
    dict(k="hedgehog", who="dang", size=290, face=-1, at=(0.67, 75), anim=["hop", "sing"]),
], short_props=[dict(k="balloon", size=s, col="#CDEBFF", at=(x, y), sky=True, anim="float") for x, y, s in BUB[::2]] + [
    dict(k="hedgehog", who="ding", size=330, at=(0.28, 110), anim=["bounce", "sing"]),
    dict(k="hedgehog", who="dang", size=320, face=-1, at=(0.72, 115), anim=["hop", "sing"]),
])
