"""Aide à l'écriture des comptines originales.
line("bub-bles on my lit-tle nose", "E:.5 F:.5 G A:.5 G:.5 E C:2 -:2")
- syllabes séparées par des espaces ; « - » à l'intérieur d'un mot = la syllabe continue le mot ;
- « mot|||phonèmes » force la prononciation (ex. Ding|||dˈiŋ) ;
- notes « NOTE:durée » (durée 1 par défaut), « - » = silence, autant de notes que de syllabes puis des silences."""


def line(text, notes):
    toks = []
    for w in text.split():
        ph = None
        if "|||" in w:
            w, ph = w.split("|||")
        parts = w.split("-")
        for i, p in enumerate(parts):
            t = p + ("~" if i < len(parts) - 1 else "")
            toks.append((t, ph if (ph and len(parts) == 1) else None))
    ns = []
    for n in notes.split():
        a, _, d = n.partition(":")
        ns.append((a, d or "1"))
    out = []
    k = 0
    for (note, dur) in ns:
        if note == "-":
            out.append(f"|-|{dur}")
            continue
        if k >= len(toks):
            raise ValueError(f"trop de notes pour « {text} »")
        t, ph = toks[k]; k += 1
        out.append(f"{t}|{note}|{dur}" + (f"|{ph}" if ph else ""))
    if k != len(toks):
        raise ValueError(f"{len(toks)} syllabes mais {k} notes pour « {text} »")
    return " ".join(out)
