# Publication via YouTube Studio (navigateur intégré de l'app Claude)

La chaîne « Ding Dang comptines » est connectée dans le navigateur intégré de l'app Claude sur l'ordi Windows de l'utilisateur. Pas d'API YouTube : on remplit YouTube Studio comme un humain.

1. `git push` les fichiers de `out/<comptine>/` : ils deviennent lisibles sur
   `https://raw.githubusercontent.com/moustaphapro13/comptines/main/out/<comptine>/<fichier>` (CORS ouvert, YouTube Studio peut les `fetch`).
2. Ouvrir `https://studio.youtube.com` (demander l'accès au site si besoin), bouton « Créer » → « Importer des vidéos ».
3. Injecter la vidéo sans fenêtre Windows (javascript_tool) :
   ```js
   const b = await (await fetch(RAW_URL)).blob();
   const inp = document.querySelector('input[type=file]');
   const dt = new DataTransfer(); dt.items.add(new File([b], "video.mp4", {type: "video/mp4"}));
   inp.files = dt.files; inp.dispatchEvent(new Event('change', {bubbles: true}));
   ```
4. Après ~6 s, dans `ytcp-uploads-dialog` :
   - titre / description : `#textbox[contenteditable="true"]` [0] et [1] → `focus(); execCommand('selectAll'); execCommand('insertText', false, txt)`
   - miniature (vidéo longue) : même injection sur `#file-loader`
   - « conçu pour les enfants » : `tp-yt-paper-radio-button[name="VIDEO_MADE_FOR_KIDS_MFK"]`.click()
   - tags : `#toggle-button` (Plus) puis `#tags-container input` = tags séparés par des virgules + `,` + Entrée
5. `#next-button` ×3 → « Programmer » → choisir la date dans le calendrier et l'heure dans la liste (clics), puis `#done-button`.
6. Lire le lien dans `ytcp-video-share-dialog`, l'ajouter à `published.json`.

Créneaux : vidéo longue le mercredi 17:00, Short le samedi 11:00 (heure de Paris).

## Choisir la bonne chaîne
Avant d'importer, aller sur `https://www.youtube.com/channel_switcher` et cliquer la chaîne de la langue (Ding Dang comptines / Ding Dang Nursery Rhymes / …), puis ouvrir `https://studio.youtube.com` et vérifier le nom de la chaîne en haut du menu de Studio. Pour une chaîne anglaise ou espagnole, la langue de la vidéo est l'anglais / l'espagnol (titres, description, tags dans la langue).
