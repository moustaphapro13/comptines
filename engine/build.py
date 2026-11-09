"""python3 -m engine.build songs/<lang>/<slug>.py [long|short|thumb|check T...|audio]"""
import importlib.util, os, sys, json
from .music import Song, render_audio
from . import video


def load(path):
    spec = importlib.util.spec_from_file_location(os.path.basename(path)[:-3], path)
    m = importlib.util.module_from_spec(spec); spec.loader.exec_module(m)
    return m


def outdir(m, path):
    slug = os.path.basename(path)[:-3].replace("_", "-")
    d = os.path.join("out", m.LANG, slug)
    os.makedirs(d, exist_ok=True)
    return d, slug


def main():
    path, what = sys.argv[1], sys.argv[2]
    m = load(path)
    song = Song(m)
    d, slug = outdir(m, path)
    if what == "check":
        kind = sys.argv[3]
        v = video.Video(song, kind)
        for t in sys.argv[4:]:
            v.frame(float(t)).save(f"/tmp/check_{slug}_{kind}_{t}.png")
        print(kind, "duration", round(v.tl["end"] * song.beat + 1, 1), "s")
        return
    if what == "thumb":
        v = video.Video(song, "long")
        t = (v.tl["song_end"] + 2.5) * song.beat
        v.frame(t).resize((1280, 720)).save(os.path.join(d, "miniature.jpg"), quality=92)
        return
    if what in ("long", "short"):
        wav = f"/tmp/{slug}_{what}.wav"
        dur = render_audio(song, what, wav)
        ok = video.render(song, what, os.path.join(d, f"{slug}_{what}.mp4"), wav, dur)
        print(what, "ok" if ok else "FAILED", round(dur, 1))
        return
    if what == "audio":
        print(render_audio(song, sys.argv[3], f"/tmp/{slug}_{sys.argv[3]}.wav"))


if __name__ == "__main__":
    main()
