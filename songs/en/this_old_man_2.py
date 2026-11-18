from pathlib import Path
exec(Path(__file__).with_name("this_old_man.py").read_text())
_N = [int(x) for x in "4 5 6".split()]
TITLE = f"This Old Man ({NUM[_N[0]][0].capitalize()} to {NUM[_N[-1]][0].capitalize()})"
SHORT = [(f"v{n}", MODES[n], LAB[n]) for n in _N]
