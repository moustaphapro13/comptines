# Publication via YouTube Studio (navigateur intégré de l'app Claude, ordi Windows de l'utilisateur)

Chaînes (même compte Google) : **Ding Dang comptines** (fr, UCmC_G9eVJ6ePrs3XI3m1ttQ) et **Ding Dang Nursery Rhymes** (en, UCoMhaBackdsRCc_1A1c4EyQ).

1. Pousser d'abord les vidéos sur GitHub (dépôt public) : YouTube Studio les récupère via `raw.githubusercontent.com`.
2. Changer de chaîne : `https://www.youtube.com/channel_switcher` → cliquer la chaîne (mettre l'onglet au premier plan avec tabs_select si la page reste blanche), puis ouvrir `https://studio.youtube.com` et vérifier le nom de la chaîne (`#entity-name`). Ouvrir directement l'URL Studio de l'autre chaîne donne une erreur 403.
3. Coller `tools/studio_helpers.js` avec javascript_tool, puis pour chaque vidéo (planning dans `semaine_<date>.json`) :
   - `await __A("out/fr/xxx/short.json", "17 nov. 2026")` → doit finir par `ready 17 nov. 2026` ou `same`
   - vraie touche **Entrée** (outil computer, key "Return") — la date ne se valide qu'avec un vrai appui clavier
   - `await __C("17 nov. 2026", "11:00")` → date, heure et lien
   Une vidéo par appel (les appels longs peuvent être coupés). Si une étape renvoie `STOP`, regarder l'écran avant de continuer : ne jamais relancer `__A` pour une vidéo peut-être déjà importée (doublon).
4. Contrôler à la fin les listes `…/videos/short` et `…/videos/upload` de chaque chaîne (titre + « Programmée »).
5. Shorts + légendes pour TikTok : copiés sur l'ordi dans `C:\Users\moust\Videos\Comptines\TikTok\<langue>\<date>_<slug>.mp4/.txt` (device_commit_files). TikTok bloque l'import par script : l'utilisateur choisit le fichier dans TikTok Studio, ensuite Claude peut remplir légende (saisie clavier, pas de execCommand), étiquette IA et programmation.

Créneaux : Short tous les jours 11:00 ; vidéo longue lundi, mercredi, vendredi 17:00 (heure de Paris). Toujours « conçu pour les enfants ». Ne jamais publier immédiatement : toujours programmer.
