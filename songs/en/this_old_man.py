TITLE = "This Old Man"
LANG = "en"
BPM = 120
# Traditional melody, C major.
NUM = {1: ("one", "on my thumb"), 2: ("two", "on my shoe"), 3: ("three", "on my knee"), 4: ("four", "on my door"),
       5: ("five", "on my hive"), 6: ("six", "on my sticks"), 7: ("seven", "up in heaven"), 8: ("eight", "on my gate"),
       9: ("nine", "on my spine"), 10: ("ten", "once again")}


def verse(n):
    num, where = NUM[n]
    l1 = "This|G old|E man,|G|2 he|G played|E " + (f"{num},|G|2" if n != 7 else "sev~|G|1|sˈɛ ven,|G|1|vən")
    w = where.split()
    if n == 7:
        tail = f"{w[0]}|D {w[1]}|E heav~|F en.|F"
    elif n == 10:
        tail = "once|D a~|E|1|ə gain.|F|2"
    else:
        tail = f"{w[0]}|D {w[1]}|E {w[2]}.|F|2"
    l2 = "he|A played|G knick-|F knack|E " + tail
    l3 = ("With|E|0.5 a|F|0.5|ə knick-|G knack|C pad~|C|0.5 dy~|C|0.5 whack,|C "
          "give|C|0.5 the|D|0.5 dog|E|0.5 a|F|0.5|ə bone,|G")
    l4 = "this|G old|D man|D came|F roll~|E|0.5 ing|D|0.5 home.|C|2 |-|1"
    return [l1, l2, l3, l4]


PARTS = {f"v{n}": verse(n) for n in NUM}
CH = "C C C C F C G G7 C C C C G G7 C C"
CHORDS = {k: CH for k in PARTS}
INTRO = 4
LAB = {1: "One!", 2: "Two!", 3: "Three!", 4: "Four!", 5: "Five!", 6: "Six!", 7: "Seven!", 8: "Eight!",
       9: "Nine!", 10: "Ten!"}
MODES = {1: "normal", 2: "normal", 3: "ensemble", 4: "normal", 5: "loud", 6: "normal", 7: "ensemble",
         8: "soft", 9: "normal", 10: "ensemble"}
SHORT = [(f"v{n}", MODES[n] if n != 3 else "ensemble", LAB[n]) for n in (1, 2, 3)]
LONG = [(f"v{n}", MODES[n], LAB[n]) for n in NUM] + [("v1", "karaoke", "Your turn to sing!")]
SCENE = dict(sky="day", ground="hills", props=[
    dict(k="sun", size=140, at=(0.1, 0.2), sky=True, anim="float"),
    dict(k="cloud", size=170, at=(0.7, 0.15), sky=True, anim="drift"),
    dict(k="house", size=300, wall="#E9F1FF", roof="#8E6CCF", at=(0.85, 40)),
    dict(k="tree", size=230, at=(0.12, 40), fruit="#FF6F61"),
    dict(k="critter", kind="man", size=200, at=(0.4, 85), anim=["walk", "sing"]),
    dict(k="drum", size=110, at=(0.53, 95), anim="pulse"),
    dict(k="critter", kind="dog", size=140, at=(0.64, 95), anim="hop"),
    dict(k="bone", size=90, at=(0.72, 110), anim="bounce"),
], short_props=[
    dict(k="sun", size=140, at=(0.8, 0.22), sky=True, anim="float"),
    dict(k="house", size=260, wall="#E9F1FF", roof="#8E6CCF", at=(0.2, 10)),
    dict(k="critter", kind="man", size=190, at=(0.45, 115), anim=["walk", "sing"]),
    dict(k="drum", size=100, at=(0.5, 130), anim="pulse"),
    dict(k="critter", kind="dog", size=130, at=(0.68, 125), anim="hop"),
    dict(k="bone", size=80, at=(0.86, 140), anim="bounce"),
])
