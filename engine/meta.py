"""Génère les métadonnées YouTube/TikTok de la semaine : python3 -m engine.meta"""
import json, os
from .build import load
from .music import parse_line

CREDIT = {"fr": "Voix de synthèse : Piper, voix « siwis » (CC-BY 4.0). Comptine traditionnelle (domaine public), animation et musique originales.",
          "en": "Synthetic voice: Piper (\"lessac\" voice). Traditional nursery rhyme (public domain), original animation and music."}
TAGS = {"fr": ["comptine", "comptines", "chanson pour enfants", "comptine maternelle", "karaoké enfant", "chanson enfant"],
        "en": ["nursery rhymes", "kids songs", "nursery rhyme", "songs for kids", "sing along", "toddler songs"]}
HASH = {"fr": "#comptine #chansonpourenfants #maternelle", "en": "#nurseryrhymes #kidssongs #singalong"}


def lyrics(m, part):
    out = []
    for line in m.PARTS[part]:
        txt = ""
        for s in parse_line(line):
            if s["txt"]:
                txt += s["txt"] + ("" if s["join"] else " ")
        out.append(txt.strip())
    return "\n".join(out)


def make(path, kind, date, time):
    m = load(path)
    slug = os.path.basename(path)[:-3].replace("_", "-")
    parts = []
    for sec in (m.LONG if kind == "long" else m.SHORT):
        if sec[0] not in parts:
            parts.append(sec[0])
    lyr = "\n\n".join(lyrics(m, p) for p in parts)
    L = m.LANG
    if kind == "short":
        title = f"{m.TITLE} 🎶 #shorts" + (" #comptine" if L == "fr" else " #nurseryrhymes")
        intro = "Chante avec nous ! 🎶" if L == "fr" else "Sing along with us! 🎶"
    else:
        title = f"{m.TITLE} 🎶 " + ("Comptine pour enfants avec paroles (karaoké)" if L == "fr" else "Nursery Rhyme with Lyrics | Sing Along")
        intro = ("Chante avec nous ! Paroles à l'écran, couplets variés et un passage karaoké pour chanter tout seul. 🎶" if L == "fr"
                 else "Sing along with us! Lyrics on screen, fun verses and a karaoke part to sing on your own. 🎶")
    desc = f"{intro}\n\n{'Paroles' if L == 'fr' else 'Lyrics'} :\n{lyr}\n\n{CREDIT[L]}\n\n{HASH[L]}"
    tags = [m.TITLE.lower()] + TAGS[L]
    d = os.path.join("out", L, slug); os.makedirs(d, exist_ok=True)
    meta = dict(file=f"{d}/{slug}_{kind}.mp4", title=title[:100], description=desc, tags=tags, lang=L,
                kind=kind, date=date, time=time,
                channel="Ding Dang comptines" if L == "fr" else "Ding Dang Nursery Rhymes")
    if kind == "long" and os.path.exists(f"{d}/miniature.jpg"):
        meta["thumbnail"] = f"{d}/miniature.jpg"
    json.dump(meta, open(f"{d}/{kind}.json", "w"), ensure_ascii=False, indent=1)
    cap = (f"{m.TITLE} 🎶 " + ("Chante avec nous !" if L == "fr" else "Sing along!") + " " + HASH[L])
    open(f"{d}/tiktok.txt", "w").write(cap + "\n")
    return meta


WEEK = [
    ("songs/en/hot_cross_buns.py", "short", "2026-11-10", "11:00"),
    ("songs/fr/au_clair_de_la_lune.py", "short", "2026-11-10", "11:00"),
    ("songs/en/twinkle_twinkle.py", "short", "2026-11-11", "11:00"),
    ("songs/en/twinkle_twinkle.py", "long", "2026-11-11", "17:00"),
    ("songs/fr/joyeux_anniversaire.py", "short", "2026-11-11", "11:00"),
    ("songs/en/row_your_boat.py", "short", "2026-11-12", "11:00"),
    ("songs/fr/ah_vous_dirai_je.py", "short", "2026-11-12", "11:00"),
    ("songs/en/mary_lamb.py", "short", "2026-11-13", "11:00"),
    ("songs/en/mary_lamb.py", "long", "2026-11-13", "17:00"),
    ("songs/fr/au_clair_pierrot.py", "short", "2026-11-13", "11:00"),
    ("songs/fr/au_clair_de_la_lune.py", "long", "2026-11-13", "17:00"),
    ("songs/en/london_bridge.py", "short", "2026-11-14", "11:00"),
    ("songs/en/brother_john.py", "short", "2026-11-15", "11:00"),
    ("songs/fr/au_clair_lubin.py", "short", "2026-11-15", "11:00"),
    ("songs/en/old_macdonald.py", "short", "2026-11-16", "11:00"),
    ("songs/en/old_macdonald.py", "long", "2026-11-16", "17:00"),
    ("songs/fr/frere_jacques_canon.py", "short", "2026-11-16", "11:00"),
    ("songs/fr/ah_vous_dirai_je.py", "long", "2026-11-16", "17:00"),
]

if __name__ == "__main__":
    sched = [make(*w) for w in WEEK]
    json.dump(sched, open("semaine_2026-11-10.json", "w"), ensure_ascii=False, indent=1)
    for s in sched:
        print(s["date"], s["time"], s["channel"][:14], s["kind"], s["title"])
