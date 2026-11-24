from engine.compose import line
TITLE = "Bonne nuit, Ding et Dang"
LANG = "fr"
BPM = 84
ORIGINAL = True
M1, M2, M3, M4 = "E G G A G E D:2", "C D E G E D C:2", "E G G C5 B A G:2", "A G E D E D C:2"
L1 = line("Bon-ne nuit, la lu-ne brille,", M1)
L3 = line("bon-ne nuit, tous les oi-seaux,", M3)
V = {"v1": ("Ding|||dˈiŋ et Dang|||dˈaŋ fer-ment les yeux,", "dans leur pe-tit lit tout doux."),
     "v2": ("le vent chan-te tout, tout bas,", "la fo-rêt s'en-dort aus-si."),
     "v3": ("un bi-sou sur le mu-seau,", "un câ-lin, et puis|||pɥˈi do-do."),
     "v4": ("fais de beaux rê-ves, mon cœur,", "de-main, le so-leil vien-dra.")}
PARTS = {k: [L1, line(a, M2), L3, line(b, M4)] for k, (a, b) in V.items()}
CHORDS = {k: "C F C G C C G C C C G G F C G C" for k in PARTS}
INTRO = 4
SHORT = [("v1", "soft"), ("v3", "soft", "Un câlin…")]
LONG = [("v1", "soft"), ("v2", "soft"), ("v3", "soft", "Un câlin…"), ("v4", "soft", "Fais de beaux rêves…"), ("v1", "karaoke", "Chante tout doucement…")]
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
