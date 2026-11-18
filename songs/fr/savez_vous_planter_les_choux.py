TITLE = "Savez-vous planter les choux ?"
LANG = "fr"
BPM = 138
CHORD_LEN = 1.5
# Mélodie traditionnelle (6/8), transposée en do. Noire = 1 temps.
MODE = "à|B3|1 la|C|0.5 mo~|D|1 de,|D|0.5 à|C|1 la|D|0.5 mo~|E|1 de,|C|0.5"
FIN = "à|B3|1 la|C|0.5 mo~|D|1 de|F|0.5 de|E|1 chez|D|0.5 nous.|C|1.5"


def couplet(l1):
    return [l1, MODE, l1, FIN]


def avec(mot, ph=None):
    m = f"{mot}|C|1.5" + (f"|{ph}" if ph else "")
    return f"On|C|1 les|E|0.5 plan~|G|1 t'a~|C5|0.5 vec|G|1 le|E|0.5 {m}"


REFRAIN = "Sa~|C|1 vez-~|E|0.5 vous|G|1 plan~|C5|0.5 ter|G|1 les|E|0.5 choux_?|C|1.5"
PARTS = {"refrain": couplet(REFRAIN), "doigt": couplet(avec("doigt,")), "pied": couplet(avec("pied,")),
         "genou": couplet(avec("g'nou,", "ʒnˈu")), "coude": couplet(avec("coude,", "kˈud")),
         "nez": couplet(avec("nez,"))}
CH = "C C C C G G7 G7 C C C C C G G7 G7 C"
CHORDS = {k: CH for k in PARTS}
INTRO = 6
SHORT = [("refrain", "normal"), ("doigt", "normal", "Avec le doigt_!"), ("pied", "normal", "Avec le pied_!"),
         ("genou", "normal", "Avec le genou_!"), ("refrain", "ensemble", "Tous ensemble_!")]
LONG = [("refrain", "normal"), ("doigt", "normal", "Avec le doigt_!"), ("pied", "normal", "Avec le pied_!"),
        ("genou", "normal", "Avec le genou_!"), ("coude", "ensemble", "Avec le coude_!"),
        ("nez", "normal", "Avec le nez_!"), ("refrain", "ensemble", "Tous ensemble_!"),
        ("doigt", "soft", "Tout doucement…"), ("pied", "karaoke", "À toi de chanter_!"),
        ("refrain", "loud", "Plus fort_!")]
SCENE = dict(sky="day", ground="hills", props=[
    dict(k="sun", size=140, at=(0.88, 0.2), sky=True, anim="float"),
    dict(k="cloud", size=180, at=(0.25, 0.16), sky=True, anim="drift"),
    dict(k="house", size=300, wall="#FFF1D6", roof="#5DB55A", at=(0.1, 40)),
    dict(k="fence", length=600, size=60, at=(0.6, 30)),
    dict(k="cabbage", size=130, at=(0.3, 60), anim="pulse"),
    dict(k="cabbage", size=120, at=(0.4, 65), anim="pulse"),
    dict(k="cabbage", size=130, at=(0.73, 60), anim="pulse"),
    dict(k="cabbage", size=120, at=(0.83, 65), anim="pulse"),
    dict(k="critter", kind="girl", size=190, at=(0.52, 90), anim=["hop", "sing"]),
    dict(k="critter", kind="boy", size=180, at=(0.62, 95), anim=["bounce", "sing"]),
    dict(k="critter", kind="frog", size=110, at=(0.93, 115), anim="hop"),
], short_props=[
    dict(k="sun", size=140, at=(0.8, 0.22), sky=True, anim="float"),
    dict(k="house", size=260, wall="#FFF1D6", roof="#5DB55A", at=(0.2, 10)),
    dict(k="fence", length=420, size=55, at=(0.7, 15)),
    dict(k="cabbage", size=130, at=(0.12, 100), anim="pulse"),
    dict(k="cabbage", size=130, at=(0.88, 100), anim="pulse"),
    dict(k="critter", kind="girl", size=180, at=(0.35, 115), anim=["hop", "sing"]),
    dict(k="critter", kind="boy", size=170, at=(0.62, 120), anim=["bounce", "sing"]),
])
