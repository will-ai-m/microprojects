// Fetch YC RFS theme texts for all batch tabs on https://www.ycombinator.com/rfs
// Run (from yc-rfs/):
//   playwright-cli open https://www.ycombinator.com/rfs
//   playwright-cli --raw run-code --filename=pipeline/02_fetch_rfs.js > data/raw/rfs/_all.json
//   playwright-cli close
//   python3 pipeline/02_split_rfs.py   # splits _all.json into per-batch files
// (run-code's vm sandbox has no fs access, so data goes via stdout)
async (page) => {
  const EXTRACT = () => {
    const batch = [...document.querySelectorAll('h2')].map(e => e.textContent.trim()).find(t => /20\d\d/.test(t));
    const themes = [...document.querySelectorAll('h3')].filter(h => h.textContent.trim().endsWith('#')).map(h3 => {
      let node = h3, container = null;
      for (let i = 0; i < 5 && node; i++) {
        node = node.parentElement;
        if (node && node.querySelectorAll('h3').length === 1 && node.textContent.length > 150) { container = node; break; }
      }
      const title = h3.textContent.trim().replace(/#$/, '');
      const isByline = (t) => /^By .{2,70}$/.test(t) && !t.includes('\n');
      let author = null;
      if (container) {
        const cands = [...container.querySelectorAll('*')].filter(e => isByline(e.textContent.trim()));
        const leaves = cands.filter(e => !cands.some(o => o !== e && e.contains(o)));
        if (leaves.length) author = leaves[leaves.length - 1].textContent.trim().replace(/^By /, '');
      }
      let description = '';
      if (container) {
        const clone = container.cloneNode(true);
        [...clone.querySelectorAll('*')]
          .filter(e => isByline(e.textContent.trim()) || e.tagName === 'H3')
          .forEach(e => { try { e.remove(); } catch (_) {} });
        const paras = [...clone.querySelectorAll('p')].map(p => p.textContent.trim()).filter(Boolean);
        description = paras.length ? paras.join('\n\n') : clone.textContent.trim();
      }
      return { title, author, description };
    });
    return { batch, themes };
  };

  const tabNames = await page.$$eval('button', els =>
    els.map(e => e.textContent.trim()).filter(t => /^(Winter|Spring|Summer|Fall) 20\d\d$/.test(t)));
  const results = [];
  for (const name of tabNames) {
    await page.getByRole('button', { name, exact: true }).click();
    await page.waitForFunction(
      (n) => [...document.querySelectorAll('h2')].some(h => h.textContent.trim() === n),
      name, { timeout: 10000 }
    );
    await page.waitForTimeout(300);
    const data = await page.evaluate(EXTRACT);
    if (data.batch !== name) throw new Error(`Tab mismatch: clicked ${name}, page shows ${data.batch}`);
    results.push({
      batch: name,
      scraped_at: new Date().toISOString().slice(0, 10),
      source: 'https://www.ycombinator.com/rfs',
      themes: data.themes,
    });
  }
  return JSON.stringify(results);
}
