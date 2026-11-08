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
pip install --break-system-packages piper-tts pyworld librosa google-api-python-client google-auth-oauthlib
curl -L -o /tmp/v.tgz https://github.com/rhasspy/piper/releases/download/v0.0.2/voice-fr-siwis-medium.tar.gz
mkdir -p /home/claude/voice && tar xzf /tmp/v.tgz -C /home/claude/voice
```
`secrets/` (client OAuth + jeton) n'est jamais dans un dépôt public.

## Routine hebdomadaire
1. Prendre la première comptine de `queue.json` absente de `published.json`.
2. Adapter `song.py` (PHRASES, structure 2–3 min), `sing.py` (PHON) et la scène de `render.py` à cette comptine ; vérifier quelques images avant le rendu complet.
3. Rendre long + short, écrire miniature et métadonnées.
4. Publier : vidéo longue le mercredi 17 h, Short le samedi 11 h (heure de Paris) via `publishAt`.
5. Mettre à jour `published.json`, commit, push.
