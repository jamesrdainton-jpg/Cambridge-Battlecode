// Bulk-download replay files from a Cambridge Battlecode platform page.
// Use: open the page that shows the replay download buttons, press F12, open the Console tab, paste this
// whole file and press Enter (the browser asks you to type "allow pasting" the first time).
// It lists the download buttons it found, asks before starting, then clicks one every 1.5 seconds.
// Allow "download multiple files" if the browser asks, then move the files into replays\platform\.
(async () => {
  const shown = el => el.getClientRects().length > 0 && !el.closest('nav, header');
  const label = el => [el.textContent, el.getAttribute('aria-label'), el.title]
    .filter(Boolean).join(' ').replace(/\s+/g, ' ').trim();
  // Links that open the web visualiser ("?replay=<url>") would leave the page, so skip them.
  const viewer = el => /[?&]replay=/i.test(el.getAttribute('href') || '');
  // Prefer real file links; otherwise any visible button or link labelled "download".
  let items = [...document.querySelectorAll('a[download], a[href*=".repl26a"], a[href*="replay"]')]
    .filter(el => shown(el) && !viewer(el) && /download|\.repl26a|\.zip/i.test(el.outerHTML));
  if (!items.length) {
    items = [...document.querySelectorAll('a, button, [role="button"]')]
      .filter(el => shown(el) && !viewer(el) && /download/i.test(label(el)));
  }
  // When a card and the button inside it both match, keep only the button.
  items = items.filter(el => !items.some(other => other !== el && el.contains(other)));
  console.table(items.map(el => ({ text: label(el).slice(0, 60), href: el.getAttribute('href') || '' })));
  if (!items.length) {
    console.warn('No download buttons found. Right-click one, choose Inspect, copy its outer HTML and send it to Claude.');
    return;
  }
  if (!confirm(`Download ${items.length} replay files, one every 1.5 seconds?`)) return;
  for (const [i, el] of items.entries()) {
    el.click();
    console.log(`${i + 1}/${items.length} ${label(el).slice(0, 60)}`);
    await new Promise(resolve => setTimeout(resolve, 1500));
  }
  console.log('Done. Move the downloaded files into replays\\platform\\ in the project folder.');
})();
