"""Génère les métadonnées YouTube/TikTok de la semaine : python3 -m engine.meta"""
import json, os
from .build import load
from .music import parse_line

CREDIT = {"fr": "Voix de synthèse : Piper, voix « siwis » (CC-BY 4.0). Comptine traditionnelle (domaine public), animation et musique originales.",
          "en": "Synthetic voice: Piper (\"lessac\" voice). Traditional nursery rhyme (public domain), original animation and music."}
TAGS = {"fr": ["comptine", "comptines", "chanson pour enfants", "comptine maternelle", "karaoké enfant", "chanson enfant"],
        "en": ["nursery rhymes", "kids songs", "nursery rhyme", "songs for kids", "sing along", "toddler songs"]}
CREDIT_ORIG = {"fr": "Comptine originale Ding Dang comptines : paroles, musique et animation originales. Voix de synthèse : Piper, voix « siwis » (CC-BY 4.0).",
               "en": "Original song by Ding Dang Nursery Rhymes: original lyrics, music and animation. Synthetic voice: Piper (\"lessac\" voice)."}
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
    desc = f"{intro}\n\n{'Paroles' if L == 'fr' else 'Lyrics'} :\n{lyr}\n\n{(CREDIT_ORIG if getattr(m, 'ORIGINAL', False) else CREDIT)[L]}\n\n{HASH[L]}"
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
    ("songs/fr/brosse_les_dents.py", "short", "2026-11-26", "11:00"),
    ("songs/en/brushy_brush.py", "short", "2026-11-26", "11:00"),
    ("songs/fr/plouf_dans_le_bain.py", "short", "2026-11-27", "11:00"),
    ("songs/fr/brosse_les_dents.py", "long", "2026-11-27", "17:00"),
    ("songs/en/bubble_bath.py", "short", "2026-11-27", "11:00"),
    ("songs/en/brushy_brush.py", "long", "2026-11-27", "17:00"),
    ("songs/fr/les_couleurs_de_dang.py", "short", "2026-11-28", "11:00"),
    ("songs/en/colors_with_dang.py", "short", "2026-11-28", "11:00"),
    ("songs/fr/bonne_nuit_ding_et_dang.py", "short", "2026-11-29", "11:00"),
    ("songs/en/goodnight_ding_and_dang.py", "short", "2026-11-29", "11:00"),
    ("songs/fr/brosse_les_dents_2.py", "short", "2026-11-30", "11:00"),
    ("songs/fr/plouf_dans_le_bain.py", "long", "2026-11-30", "17:00"),
    ("songs/en/brushy_brush_2.py", "short", "2026-11-30", "11:00"),
    ("songs/en/bubble_bath.py", "long", "2026-11-30", "17:00"),
    ("songs/fr/plouf_dans_le_bain_2.py", "short", "2026-12-01", "11:00"),
    ("songs/en/bubble_bath_2.py", "short", "2026-12-01", "11:00"),
    ("songs/fr/les_couleurs_de_dang_2.py", "short", "2026-12-02", "11:00"),
    ("songs/en/colors_with_dang_2.py", "short", "2026-12-02", "11:00"),
]

if __name__ == "__main__":
    sched = [make(*w) for w in WEEK]
    json.dump(sched, open("semaine_2026-11-26.json", "w"), ensure_ascii=False, indent=1)
    for s in sched:
        print(s["date"], s["time"], s["channel"][:14], s["kind"], s["title"])
