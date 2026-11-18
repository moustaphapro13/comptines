# Chaîne de comptines — pipeline automatique

Ce dépôt fabrique et publie des comptines pour enfants : une vidéo longue (16:9, 2–3 min) et un Short (9:16, ~30 s) par comptine.

## Règles de contenu
- Seulement des comptines du **domaine public** (paroles + mélodie traditionnelles). Jamais de vidéo, d'enregistrement ou d'illustration d'une autre chaîne.
- Images et musique fabriquées ici (Pillow + synthèse). Voix : Piper `fr-siwis-medium` (CC-BY 4.0, à créditer en description).
- Toujours `selfDeclaredMadeForKids: true`.

## Fichiers
- `song.py` — partition, structure des couplets, mixage audio.
- `sing.py` — voix chantée (Piper + WORLD), table syllabe → phonèmes.
- `render.py` — dessin de la scène et rendu vidéo (`python3 render.py long|short full`).
- `upload.py` — publication YouTube (`python3 upload.py auth` une fois, puis `python3 upload.py video.mp4 meta.json`).
- `out/<comptine>/` — vidéos, miniature, `long.json` / `short.json`.
- `queue.json` — comptines à faire, dans l'ordre ; `published.json` — journal des publications.

## Installation (session neuve)
```
pip install --break-system-packages piper-tts pyworld librosa praat-parselmouth pycairo onnxruntime google-api-python-client google-auth-oauthlib
mkdir -p /home/claude/voice/sherpa && cd /home/claude/voice
# voix anglaise (comptines EN)
curl -L -o /tmp/v.tgz https://github.com/rhasspy/piper/releases/download/v0.0.2/voice-en-us-lessac-medium.tar.gz && tar xzf /tmp/v.tgz -C /home/claude/voice
# voix françaises récentes (vraies voyelles nasales) : comptines FR + série Ding et Dang
cd sherpa && for m in vits-piper-fr_FR-siwis-medium vits-piper-fr_FR-upmc-medium vits-piper-fr_FR-tom-medium; do
  curl -sSL https://github.com/k2-fsa/sherpa-onnx/releases/download/tts-models/$m.tar.bz2 | tar xj; done
```
Voix chantée : synthèse Piper syllabe par syllabe puis PSOLA (Praat via parselmouth) pour caler hauteur et durée — plus de vocodeur WORLD (trop robotique).
Série « Ding et Dang » : `python3 -m serie.build serie/epXX.py render` (voir `serie/`).
`secrets/` (client OAuth + jeton) n'est jamais dans un dépôt public.

## Routine hebdomadaire
1. Prendre la première comptine de `queue.json` absente de `published.json`.
2. Adapter `song.py` (PHRASES, structure 2–3 min), `sing.py` (PHON) et la scène de `render.py` à cette comptine ; vérifier quelques images avant le rendu complet.
3. Rendre long + short, écrire miniature et métadonnées.
4. Publier : vidéo longue le mercredi 17 h, Short le samedi 11 h (heure de Paris) via `publishAt`.
5. Mettre à jour `published.json`, commit, push.

## Langues et chaînes (même compte Google)
| Langue | Chaîne YouTube | File | Voix Piper (release v0.0.2) |
|---|---|---|---|
| fr | Ding Dang comptines (@Dingdangcomptines) | `queue.json` | `voice-fr-siwis-medium` |
| en | Ding Dang Nursery Rhymes (@dingdangnurseryrhymes) | `queues_langues.json` → `en` | `voice-en-us-lessac-medium` |
| es | à créer (Ding Dang Canciones Infantiles) | `queues_langues.json` → `es` | `voice-es-mls_10246-low` |

Voix : `https://github.com/rhasspy/piper/releases/download/v0.0.2/voice-<nom>.tar.gz`, à extraire dans `/home/claude/voice/`, puis pointer `VOICE` de `sing.py` dessus et écrire la table `PHON` (syllabe → phonèmes IPA de la voix) pour la comptine. Vidéos par langue dans `out/<langue>/<comptine>/` (le français historique reste dans `out/<comptine>/`). Les journaux de publication : `published.json` (fr), `published_en.json`, `published_es.json`.

## Rythme de publication (heure de Paris)
- **Short (~1 min) : tous les jours à 11:00**, une nouvelle comptine par jour et par langue.
- **Vidéo longue (2–3 min) : seulement lundi, mercredi et vendredi à 17:00** — la version longue de la comptine du jour.
- TikTok : pas d'automatisation possible (TikTok bloque l'import par script) → déposer chaque Short + légende dans `C:\Users\moust\Videos\Comptines\TikTok\<langue>\` sur l'ordi de l'utilisateur ; il publie lui-même.
