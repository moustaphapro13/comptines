"""python3 -m serie.build serie/ep01.py [check t1 t2 ...|render]"""
import sys, importlib.util, os
from .engine import Ep, Renderer, render_audio
from . import jingle
import cairo


def load(p):
    sp = importlib.util.spec_from_file_location("ep", p); m = importlib.util.module_from_spec(sp); sp.loader.exec_module(m); return m


def main():
    m = load(sys.argv[1]); slug = os.path.basename(sys.argv[1])[:-3]
    ep = Ep(m.S); R = Renderer(ep)
    print("durée", round(ep.end, 1), "s,", len(ep.lines), "répliques")
    if sys.argv[2] == "check":
        for t in sys.argv[3:]:
            s = cairo.ImageSurface(cairo.FORMAT_ARGB32, 1920, 1080); R.frame(float(t), s); s.write_to_png(f"/tmp/ep_{t}.png")
        return
    if sys.argv[2] == "times":
        for sc in ep.scenes:
            print("scene", sc["bg"], round(sc["start"], 1), round(sc["end"], 1))
        for L in ep.lines:
            print(round(L["t0"], 1), L["who"], L["text"][:50])
        return
    os.makedirs("out/serie", exist_ok=True)
    J = {"jingle": "/tmp/jingle.wav", "jingle_end": "/tmp/jingle_inst.wav"}
    if not os.path.exists(J["jingle"]):
        jingle.make(J["jingle"]); jingle.make(J["jingle_end"], instrumental=True)
    wav = f"/tmp/{slug}.wav"
    render_audio(ep, wav, J)
    out = f"out/serie/ding-et-dang-{slug}.mp4"
    print("ok" if R.render(out, wav) else "ÉCHEC", out)


if __name__ == "__main__":
    main()
