from engine.compose import line
TITLE = "Colors with Dang"
LANG = "en"
BPM = 120
ORIGINAL = True
M1, M2, M3, M4 = "G:.5 G:.5 A:.5 A:.5 G E C5:2 -:2", "C5:.5 B:.5 A G:.5 F:.5 E D:2 -:2", "E:.5 E:.5 F:.5 F:.5 G A G:2 -:2", "A:.5 G:.5 F E:.5 D:.5 D C:2 -:2"
L1 = line("Red and yel-low, green and blue,", M1)
L3 = line("all the col-ors, me and you!", M3)
V = {"v1": ("red is like a|||ɐ straw-ber-ry,", "and the ap-ple on the tree!"),
     "v2": ("yel-low is the shin-ing sun,", "and the duck-ie hav-ing fun!"),
     "v3": ("green is like the big fir tree,", "and the frog-gy, hop with me!"),
     "v4": ("blue is like the sky so high,", "like Ding's scarf, oh my, oh my!")}
PARTS = {k: [L1, line(a, M2), L3, line(b, M4)] for k, (a, b) in V.items()}
CHORDS = {k: "C F C C F F G G C F C C F F G C" for k in PARTS}
INTRO = 4
SHORT = [("v1", "normal", "Red!"), ("v2", "normal", "Yellow!"), ("v4", "ensemble", "Blue!")]
LONG = [("v1", "normal", "Red!"), ("v2", "normal", "Yellow!"), ("v3", "normal", "Green!"), ("v4", "ensemble", "Blue!"),
        ("v1", "karaoke", "Your turn to sing!"), ("v4", "loud", "Louder!")]
COLS = ["#FF5A5F", "#FFD24A", "#6BD66B", "#4AA8FF"]
SCENE = dict(sky="day", ground="hills", props=[
    dict(k="sun", size=140, at=(0.88, 0.18), sky=True, anim="float")] + [
    dict(k="balloon", size=100, col=c, at=(0.12 + i * 0.1, 0.3 + (i % 2) * 0.12), sky=True, anim="float") for i, c in enumerate(COLS)] + [
    dict(k="tree", size=240, at=(0.88, 40)),
    dict(k="critter", kind="frog", size=110, at=(0.5, 110), anim="hop"),
    dict(k="hedgehog", who="dang", size=300, at=(0.32, 70), anim=["hop", "sing"]),
    dict(k="hedgehog", who="ding", size=300, face=-1, at=(0.68, 75), anim=["bounce", "sing"]),
], short_props=[
    dict(k="sun", size=130, at=(0.82, 0.2), sky=True, anim="float")] + [
    dict(k="balloon", size=95, col=c, at=(0.15 + i * 0.2, 0.35 + (i % 2) * 0.1), sky=True, anim="float") for i, c in enumerate(COLS)] + [
    dict(k="critter", kind="frog", size=110, at=(0.5, 160), anim="hop"),
    dict(k="hedgehog", who="dang", size=320, at=(0.25, 110), anim=["hop", "sing"]),
    dict(k="hedgehog", who="ding", size=320, face=-1, at=(0.75, 115), anim=["bounce", "sing"]),
])
