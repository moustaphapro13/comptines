from engine.compose import line
TITLE = "Plouf, plouf, dans le bain"
LANG = "fr"
BPM = 120
ORIGINAL = True
M1, M2, M3, M4 = "C5 G A:.5 A:.5 G:2 -:3", "E:.5 F:.5 G A:.5 G:.5 E C:2 -:2", "C5 G A:.5 B:.5 C5:2 -:3", "D:.5 E:.5 F D:.5 E:.5 D C:2 -:2"
L1 = line("Plouf, plouf, dans le bain,", M1)
L3 = line("plouf, plouf, je suis bien_!", M3)
V = {"v1": ("des bul-les sur tout mon nez,", "et le ca-nard fait coin coin_!"),
     "v2": ("je la-ve mes pe-tits bras,", "et mes pieds, et puis|||pɥˈi mon dos_!|||dˈo"),
     "v3": ("Ding|||dˈiŋ fait des va-gues, des vagues,", "et Dang|||dˈaŋ rit, rit aux é-clats_!"),
     "v4": ("on sort, on se sè-che bien,", "tout pro-pre et tout câ-lin_!")}
PARTS = {k: [L1, line(a, M2), L3, line(b, M4)] for k, (a, b) in V.items()}
CHORDS = {k: "C F C C C F C C C G C C G G7 C C" for k in PARTS}
INTRO = 4
SHORT = [("v1", "normal"), ("v3", "normal", "Avec Ding et Dang_!"), ("v4", "ensemble", "Tous ensemble_!")]
LONG = [("v1", "normal"), ("v2", "normal", "On se lave_!"), ("v3", "normal", "Avec Ding et Dang_!"),
        ("v4", "ensemble", "Tous ensemble_!"), ("v1", "karaoke", "À toi de chanter_!"), ("v4", "loud", "Plus fort_!")]
BUB = [(0.1, 0.3, 70), (0.22, 0.5, 45), (0.38, 0.22, 60), (0.55, 0.42, 50), (0.7, 0.25, 65), (0.86, 0.45, 55), (0.94, 0.2, 40)]
SCENE = dict(sky="day", ground="floor", props=[dict(k="balloon", size=s, col="#CDEBFF", at=(x, y), sky=True, anim="float") for x, y, s in BUB] + [
    dict(k="critter", kind="duck", size=130, at=(0.5, 100), anim="bob"),
    dict(k="hedgehog", who="ding", size=300, at=(0.28, 70), anim=["bounce", "sing"]),
    dict(k="hedgehog", who="dang", size=290, face=-1, at=(0.72, 75), anim=["hop", "sing"]),
], short_props=[dict(k="balloon", size=s, col="#CDEBFF", at=(x, y), sky=True, anim="float") for x, y, s in BUB[::2]] + [
    dict(k="critter", kind="duck", size=120, at=(0.5, 150), anim="bob"),
    dict(k="hedgehog", who="ding", size=320, at=(0.25, 110), anim=["bounce", "sing"]),
    dict(k="hedgehog", who="dang", size=310, face=-1, at=(0.75, 115), anim=["hop", "sing"]),
])
