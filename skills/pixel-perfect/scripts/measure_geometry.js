#!/usr/bin/env node
/**
 * Dump the rendered geometry of a page's key nodes as JSON so the parity table
 * in the evidence page is measured, not eyeballed.
 *
 *   node measure_geometry.js --width 1512 --height 838 [--root ".content-column"] \
 *        s19=http://localhost:3000/dev/harness?s=19 … > measure.json
 *
 * Output per page: { h1: [x,y,w,h], h1font, paragraphs, cards, buttons, links,
 * dividers } — rects are CSS px rounded to 0.1. Selectors are deliberately
 * generic (h1, p, [class*="rounded-"], button, a, span.uppercase); pass
 * --root to scope them to the content column so header/nav nodes don't leak in.
 *
 * Env: PLAYWRIGHT_PATH — see capture_frames.js.
 */
const { chromium } = require(process.env.PLAYWRIGHT_PATH || "playwright");
const args = process.argv.slice(2);
const opt = { width: 1512, height: 838, root: "body" };
const pages = [];
for (let i = 0; i < args.length; i++) {
  const a = args[i];
  if (a.startsWith("--")) opt[a.slice(2)] = args[++i];
  else pages.push(a);
}
(async () => {
  const browser = await chromium.launch();
  const page = await (await browser.newContext({ viewport: { width: +opt.width, height: +opt.height }, deviceScaleFactor: 1 })).newPage();
  const all = {};
  for (const spec of pages) {
    const eq = spec.indexOf("=");
    const name = spec.slice(0, eq), url = spec.slice(eq + 1);
    await page.goto(url, { waitUntil: "networkidle" });
    await page.evaluate(() => document.fonts.ready);
    all[name] = await page.evaluate((rootSel) => {
      const r = (el) => { const b = el.getBoundingClientRect(); return [+b.x.toFixed(1), +b.y.toFixed(1), +b.width.toFixed(1), +b.height.toFixed(1)]; };
      const type = (el) => { const cs = getComputedStyle(el); return `${cs.fontFamily.split(",")[0]} ${cs.fontWeight} ${cs.fontSize}/${cs.lineHeight} ls=${cs.letterSpacing} ${cs.color}`; };
      const root = document.querySelector(rootSel) || document.body;
      const h1 = root.querySelector("h1");
      return {
        h1: h1 ? r(h1) : null, h1font: h1 ? type(h1) : null,
        paragraphs: Array.from(root.querySelectorAll("p")).map((p) => [p.innerText.trim().slice(0, 40), ...r(p), type(p)]),
        cards: Array.from(root.querySelectorAll('[class*="rounded-"]')).filter((c) => c.getBoundingClientRect().width > 200).map((c) => { const cs = getComputedStyle(c); return [...r(c), cs.backgroundColor, `${cs.borderTopWidth} ${cs.borderTopColor}`, cs.boxShadow.slice(0, 48)]; }),
        buttons: Array.from(root.querySelectorAll("button")).filter((b) => b.innerText.trim()).map((b) => [b.innerText.trim().slice(0, 30), ...r(b), type(b)]),
        links: Array.from(root.querySelectorAll("a")).filter((a) => a.innerText.trim()).map((a) => [a.innerText.trim().slice(0, 30), ...r(a)]),
        dividers: Array.from(root.querySelectorAll("span.uppercase, .h-px")).map((d) => [(d.innerText || "").trim(), ...r(d)]),
      };
    }, opt.root);
    console.error(`${name} measured`);
  }
  console.log(JSON.stringify(all, null, 2));
  await browser.close();
})().catch((e) => { console.error(e); process.exit(1); });
