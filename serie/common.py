"""Briques communes aux épisodes : générique, fin."""


def opening(num, title):
    return dict(bg="titre", music="jingle", iris=False, lead=0.0, tail=0.6,
                props=dict(title=True, subtitle=f"Épisode {num} : {title}", snow=True, nosub=True),
                cast={"ding": dict(x=700, emo="happy"), "dang": dict(x=1220, emo="happy", face=-1)},
                beats=[("act", ["ding", "dang"], "jump", 4.2), ("act", "ding", "wave", 3.0, {"wait": False}),
                       ("act", "dang", "wave", 3.0), ("act", ["ding", "dang"], "cheer", 3.5), ("wait", 0.8),
                       ("narr", f"Ding et Dang. Épisode {NUM_WORDS[num]} : {title.lower()}.", {"gap": 0.2})])


def ending(next_title):
    sub = f"Prochain épisode : {next_title}" if next_title else "Fin de la saison"
    return dict(bg="titre", music="jingle_end", lead=0.0, tail=0.4,
                props=dict(title=True, subtitle=sub, snow=True, nosub=True),
                cast={"ding": dict(x=700, emo="happy"), "dang": dict(x=1220, emo="happy", face=-1)},
                beats=[("act", ["ding", "dang"], "wave", 6.5)])


NUM_WORDS = {1: "un", 2: "deux", 3: "trois", 4: "quatre", 5: "cinq", 6: "six", 7: "sept", 8: "huit", 9: "neuf", 10: "dix"}
