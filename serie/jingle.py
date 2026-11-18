"""Chanson du générique « Ding et Dang » (mélodie et paroles originales)."""
import types
from engine.music import Song, render_audio

M = types.SimpleNamespace(
    TITLE="Ding et Dang", LANG="fr", BPM=120, CHORD_LEN=2, INTRO=4,
    PARTS={"v1": [
        "Ding|E et|G Dang,|C5|2 Ding|E et|G Dang,|C5|2",
        "deux|A pe~|A tits|G hé~|E ris~|F sons|G|2 |-|1",
        "dans|E la|E fo~|F rêt|G en|A chan~|G tant,|E|2|tˈɑŋ",
        "on|D rit,|E on|F joue,|D Ding|G et|B3 Dang_!|C|2",
    ]},
    CHORDS={"v1": "C C C C F C G C C C F C G G7 G C"},
)
M.SHORT = [("v1", "ensemble")]
M.LONG = M.SHORT


def make(path, instrumental=False):
    M.SHORT = [("v1", "karaoke" if instrumental else "ensemble")]
    return render_audio(Song(M), "short", path)
