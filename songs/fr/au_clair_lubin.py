TITLE = "Au clair de la lune – l’aimable Lubin"
LANG = "fr"
BPM = 100
A1 = "Au|C clair|C de|C la|D lu~|E|2 ne,|D|2"


def couplet(l1, l2, l3, l4, l5, l6, l7, l8):
    return [l1 + " " + l2, l3 + " " + l4, l5 + " " + l6, l7 + " " + l8]


PARTS = {
    "v1": couplet(A1, "mon|C a~|E mi|D Pier~|D rot,|C|4",
                  "Prê~|C te-|C moi|C ta|D plu~|E|2 me|D|2", "pour|C é~|E crire|D un|D mot.|C|4",
                  "Ma|D chan~|D|1|ʃˈɑŋ del~|D|1|dˈɛ le_est|D|1|lˈɛ mor~|A3|2 te,|A3|2", "je|D n'ai|C plus|B3 de|A3 feu.|G3|4",
                  "Ou~|C vre-|C moi|C ta|D por~|E|2 te|D|2", "pour|C l'a~|E mour|D de|D Dieu.|C|4"),
    "v2": couplet(A1, "Pier~|C rot|E ré~|D pon~|D dit_:|C|4",
                  "«_Je|C n'ai|C pas|C de|D plu~|E|2 me,|D|2", "je|C suis|E dans|D mon|D lit.|C|4",
                  "Va|D chez|D la|D voi~|D si~|A3|2 ne,|A3|2", "je|D crois|C qu'el~|B3|1|kˈɛ le_y|A3|1|lˈi est,|G3|4|ˈɛ",
                  "car|C dans|C sa|C cui~|D|1|kɥˈi si~|E|2 ne|D|2", "on|C bat|E le|D bri~|D quet._»|C|4"),
    "v3": couplet(A1, "l'ai~|C ma~|E ble|D Lu~|D bin|C|4",
                  "frap~|C pe|C chez|C la|D bru~|E|2 ne,|D|2", "elle_ré~|C|1|ɛlʁˈe pond|E sou~|D dain_:|D|4",
                  "«_Qui|D frap|D|1|fʁˈap de|D la|D sor~|A3|2 te_?_»|A3|2", "Il|D dit|C à|B3 son|A3 tour_:|G3|4",
                  "«_Ou~|C vrez|C vo~|C tre|D por~|E|2 te|D|2", "pour|C le|E dieu|D d'A~|D mour._»|C|4"),
}
A = "C C C G C G C C"
CHORDS = {k: A + " " + A + " G G Dm Dm G G G G " + A for k in PARTS}
INTRO = 4
SHORT = [("v3", "normal")]
LONG = [("v1", "normal"), ("v2", "ensemble", "Pierrot répond…"), ("v3", "soft", "Tout doucement…"),
        ("v1", "karaoke", "À toi de chanter_!")]
SCENE = dict(sky="night", ground="hills", stars=True, props=[
    dict(k="moon", size=300, at=(0.62, 0.33), sky=True, anim="float"),
    dict(k="star", size=60, face_on=False, at=(0.2, 0.2), sky=True, anim="twinkle"),
    dict(k="star", size=50, face_on=False, at=(0.88, 0.15), sky=True, anim="twinkle"),
    dict(k="house", size=330, wall="#FFE2B8", roof="#7A5AC8", at=(0.2, 40)),
    dict(k="critter", kind="pierrot", size=200, at=(0.47, 80), anim=["sway", "sing"]),
    dict(k="tree", size=220, col="#3E7A55", at=(0.9, 50)),
], short_props=[
    dict(k="moon", size=330, at=(0.6, 0.3), sky=True, anim="float"),
    dict(k="star", size=60, face_on=False, at=(0.15, 0.15), sky=True, anim="twinkle"),
    dict(k="house", size=300, wall="#FFE2B8", roof="#7A5AC8", at=(0.25, 20)),
    dict(k="critter", kind="pierrot", size=200, at=(0.68, 110), anim=["sway", "sing"]),
])
