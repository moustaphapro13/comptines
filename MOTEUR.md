# Moteur générique (engine/)

Chaque comptine = un fichier `songs/<langue>/<slug>.py` (données seulement) :
- `TITLE`, `LANG` (fr/en/es), `BPM`, `INTRO` (temps), `CHORD_LEN` (temps par accord, 2 par défaut)
- `PARTS` : couplets → lignes de karaoké. Jeton `texte|note|durée|phonèmes` :
  `~` en fin de texte = la syllabe continue le mot ; `_` = espace affichée ; texte finissant par `-` ou `'` = collé à la suite à l'écran ;
  note `C D E F G A B` (+#/b, octave 4 par défaut, ex. `G3`, `C5`), `-` = silence ; durée en temps (`0.5`, `2/3`) ;
  phonèmes facultatifs (sinon calculés par la voix Piper et découpés en syllabes ; à forcer pour les élisions, ex. `le_est|D|1|lˈɛ`).
  Ponctuation détachée : toujours avec `_` (`dit_:`, `ment_?`), jamais d'espace dans un jeton.
- `CHORDS` : un accord par `CHORD_LEN` temps et par couplet (`C G Am F7`…)
- `SHORT` / `LONG` : liste de sections `(couplet, mode, étiquette, [décalage canon])` ; modes : normal, ensemble (2e voix aiguë),
  soft, loud (claps), karaoke (sans voix), canon (2e voix décalée de N temps). Short ≈ 45–65 s, long 2–3 min.
- `SCENE` : `sky` (night/day/dusk/winter/party), `ground` (hills/snow/water/floor), `stars`, `snow`, `clouds`,
  `props` / `short_props` : `dict(k=<sprite>, size, at=(x 0-1, y), sky=True si y est une fraction de la ligne d'horizon, anim=…, z=…)`.
  Sprites (engine/sprites.py) : moon sun star cloud house tree fir barn fence bridge boat oar cake flame balloon stall bun bell tower
  candy_jar lollipop snowman clock pendulum critter(kind=lamb sheep mouse cow pig duck girl boy pierrot bear cat wolf egg frog).
  Animations : bounce hop sway float drift twinkle swing pendulum bob row flicker pulse walk sing (bouche qui chante sur la voix).

Commandes (depuis la racine du dépôt) :
```
python3 -m engine.build songs/fr/xxx.py check long 12 30   # images de contrôle dans /tmp
python3 -m engine.build songs/fr/xxx.py short               # rendu → out/fr/xxx/xxx_short.mp4
python3 -m engine.build songs/fr/xxx.py long
python3 -m engine.build songs/fr/xxx.py thumb               # miniature 1280x720
python3 -m engine.meta                                      # métadonnées + planning de la semaine (WEEK)
```
Voix : `/home/claude/voice/` (voir README pour le téléchargement : fr-siwis-medium, en-us-lessac-medium, es-mls_10246-low).

**Mélodies : n'utiliser que des airs dont on est sûr** (vérifier sur une partition du domaine public si besoin).
Comptines déjà faites : voir `songs/`. Ne pas refaire une comptine déjà publiée la même semaine.
