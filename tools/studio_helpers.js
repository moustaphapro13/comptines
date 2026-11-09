// À coller (javascript_tool) dans un onglet YouTube Studio de la bonne chaîne, après chaque rechargement de page.
// Procédure par vidéo :
//   1) JS : await __A("out/<lang>/<slug>/<short|long>.json", "16 nov. 2026")   -> doit finir par "ready 16 nov. 2026" (ou "same")
//   2) clavier : touche Entrée (vraie touche, via l'outil computer key "Return") pour valider la date
//   3) JS : await __C("16 nov. 2026", "11:00")   -> renvoie la date/heure + le lien ; "STOP ..." = vérifier à l'écran
// Si __A renvoie "STOP FILL", attendre 5 s puis relancer __fill(meta) (la boîte de dialogue était encore grisée).
window.RAW = "https://raw.githubusercontent.com/moustaphapro13/comptines/main/";
window.sleep = ms => new Promise(r => setTimeout(r, ms));
window.__close = async () => { [...document.querySelectorAll('ytcp-button, button')].filter(b => b.offsetParent && b.innerText.trim() === 'Fermer').forEach(b => b.click()); await sleep(1000); };
window.__hidePops = () => [...document.querySelectorAll('tp-yt-iron-dropdown')].filter(e => e.offsetParent && /#\w/.test(e.innerText)).forEach(p => p.style.display = 'none');
window.__open = async () => {
  const direct = [...document.querySelectorAll('ytcp-button, button')].find(e => e.innerText && e.innerText.trim() === 'Importer des vidéos' && e.offsetParent);
  if (direct) direct.click(); else { document.querySelector('#create-icon')?.click(); await sleep(1000); [...document.querySelectorAll('tp-yt-paper-item')].find(i => /Importer des vidéos/.test(i.innerText))?.click(); }
  for (let i = 0; i < 25; i++) { await sleep(400); const inp = [...document.querySelectorAll('ytcp-uploads-file-picker input[type=file]')].find(x => x.closest('ytcp-uploads-dialog')); if (inp) return inp; }
  return null;
};
window.__fill = async (meta) => {
  const d = document.querySelector('ytcp-uploads-dialog');
  d.querySelector('#step-badge-0')?.click(); await sleep(1500);
  let boxes = [];
  for (let i = 0; i < 30; i++) { boxes = [...d.querySelectorAll('#textbox[contenteditable="true"]')]; if (boxes.length >= 2 && d.querySelector('tp-yt-paper-radio-button[name="VIDEO_MADE_FOR_KIDS_MFK"]')) break; await sleep(500); }
  const setBox = (el, txt) => { el.focus(); const s = getSelection(); const r = document.createRange(); r.selectNodeContents(el); s.removeAllRanges(); s.addRange(r); document.execCommand('insertText', false, txt); };
  for (let k = 0; k < 3 && !boxes[0].innerText.startsWith(meta.title.slice(0, 10)); k++) { setBox(boxes[0], meta.title); await sleep(700); }
  setBox(boxes[1], meta.description + '\n'); await sleep(700); __hidePops();
  if (meta.thumbnail) { const tb = await (await fetch(RAW + meta.thumbnail)).blob(); const ti = d.querySelector('#file-loader');
    const dt2 = new DataTransfer(); dt2.items.add(new File([tb], "miniature.jpg", {type: "image/jpeg"})); ti.files = dt2.files; ti.dispatchEvent(new Event('change', {bubbles: true})); await sleep(1500); }
  const mfk = d.querySelector('tp-yt-paper-radio-button[name="VIDEO_MADE_FOR_KIDS_MFK"]'); if (mfk.getAttribute('aria-checked') !== 'true') mfk.click(); await sleep(400);
  const res = [boxes[0].innerText.slice(0, 40), 'mfk ' + mfk.getAttribute('aria-checked')];
  document.activeElement?.blur(); __hidePops();
  d.querySelector('#step-badge-3')?.click(); await sleep(1800);
  if (!d.querySelector('#datepicker-trigger')) { [...d.querySelectorAll('*')].find(e => e.childElementCount === 0 && e.textContent.trim() === 'Programmer' && e.offsetParent)?.click(); await sleep(1000); }
  res.push('trigger ' + !!d.querySelector('#datepicker-trigger'));
  return res.join(' | ');
};
window.__dateType = async (label) => {
  const d = document.querySelector('ytcp-uploads-dialog');
  if (d.querySelector('#datepicker-trigger').innerText.trim() === label) return 'same';
  let ins = [...document.querySelectorAll('ytcp-date-picker input')].filter(i => i.offsetParent);
  if (!ins.length) { d.querySelector('#datepicker-trigger').click(); await sleep(900); __hidePops(); ins = [...document.querySelectorAll('ytcp-date-picker input')].filter(i => i.offsetParent); }
  if (!ins.length) return 'noinput';
  const inp = ins[0]; inp.focus(); inp.value = label; inp.dispatchEvent(new Event('input', {bubbles: true})); await sleep(300);
  return 'ready ' + inp.value;
};
window.__A = async (metaPath, label) => {
  await __close();
  const meta = await (await fetch(RAW + metaPath)).json();
  const inp = await __open(); if (!inp) return 'STOP NOOPEN';
  const b = await (await fetch(RAW + meta.file)).blob(); if (b.size < 100000) return 'STOP NOFILE';
  const dt = new DataTransfer(); dt.items.add(new File([b], meta.file.split('/').pop(), {type: "video/mp4"}));
  inp.files = dt.files; inp.dispatchEvent(new Event('change', {bubbles: true}));
  await sleep(13000);
  const f = await __fill(meta);
  if (!f.startsWith(meta.title.slice(0, 10))) return 'STOP FILL ' + f;
  return f + ' | ' + (await __dateType(label));
};
window.__time = async (time) => {
  const d = document.querySelector('ytcp-uploads-dialog');
  const t = d.querySelector('#time-of-day-container input'); t.click(); await sleep(700);
  const its = [...document.querySelectorAll('tp-yt-paper-item')].filter(i => i.innerText.trim() === time);
  (its.find(i => i.offsetParent) || its[its.length - 1])?.click(); await sleep(600);
  return t.value;
};
window.__done = async () => {
  const d = document.querySelector('ytcp-uploads-dialog');
  d.querySelector('#done-button').click();
  let txt = '';
  for (let i = 0; i < 25; i++) { await sleep(700);
    const dlg = [...document.querySelectorAll('ytcp-video-share-dialog, ytcp-uploads-still-processing-dialog')].find(x => x.offsetParent && /publique/i.test(x.innerText));
    if (dlg) { txt = dlg.innerText; break; } }
  const link = (txt.match(/https:\/\/(youtu\.be|youtube\.com\/shorts)\/[^\s?]+/) || ['nolink'])[0];
  const when = (txt.match(/\d+ \S+ \d{4} à [\d:]+/) || ['?'])[0];
  await __close();
  return link + ' @ ' + when;
};
window.__C = async (label, time) => {
  const tm = await __time(time); const d = document.querySelector('ytcp-uploads-dialog');
  const s = d.querySelector('#datepicker-trigger').innerText.trim() + ' ' + tm;
  return s === label + ' ' + time ? s + ' | ' + (await __done()) : 'STOP ' + s;
};
'helpers ok';
