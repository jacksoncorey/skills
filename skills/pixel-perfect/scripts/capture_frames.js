#!/usr/bin/env node
/**
 * Capture one or more pages at a Figma frame's native size, at a chosen
 * device-pixel ratio, with web fonts settled and dev-only chrome stripped.
 *
 *   node capture_frames.js --width 1512 --height 838 --dpr 1 --out ./dev \
 *        s19=http://localhost:3000/dev/harness?s=19 s20=http://localhost:3000/dev/harness?s=20
 *
 * Writes <out>/<name>.png per page and prints the h1's computed font family
 * so a silent font fallback is caught before any diff is read.
 *
 * Env: PLAYWRIGHT_PATH — absolute path of a node_modules/playwright to require
 * when the current project doesn't ship one.
 */
const path = require("path");
const fs = require("fs");
const { chromium } = require(process.env.PLAYWRIGHT_PATH || "playwright");

const args = process.argv.slice(2);
const opt = { width: 1512, height: 838, dpr: 1, out: "./captures", settle: 400 };
const pages = [];
for (let i = 0; i < args.length; i++) {
  const a = args[i];
  if (a.startsWith("--")) opt[a.slice(2)] = args[++i];
  else pages.push(a);
}
if (!pages.length) { console.error("usage: capture_frames.js [--width W --height H --dpr N --out DIR] name=url …"); process.exit(2); }
fs.mkdirSync(opt.out, { recursive: true });

(async () => {
  const browser = await chromium.launch();
  const ctx = await browser.newContext({
    viewport: { width: +opt.width, height: +opt.height },
    deviceScaleFactor: +opt.dpr,
  });
  const page = await ctx.newPage();
  for (const spec of pages) {
    const eq = spec.indexOf("=");
    const name = spec.slice(0, eq), url = spec.slice(eq + 1);
    await page.goto(url, { waitUntil: "networkidle" });
    await page.evaluate(() => document.fonts.ready);
    await page.waitForTimeout(+opt.settle);
    // Strip dev-only overlays (Next.js dev badge, design-tool widgets):
    // anything position:fixed that is not part of the screen's own header.
    await page.evaluate(() => {
      document.querySelectorAll("nextjs-portal").forEach((e) => e.remove());
      for (const el of Array.from(document.body.querySelectorAll("*"))) {
        if (getComputedStyle(el).position === "fixed" && el.getBoundingClientRect().top > 300) el.style.display = "none";
      }
    });
    await page.screenshot({ path: path.join(opt.out, `${name}.png`) });
    const fam = await page.evaluate(() => getComputedStyle(document.querySelector("h1") || document.body).fontFamily);
    console.log(`${name} captured @${opt.dpr}x · h1 font: ${fam}`);
  }
  await browser.close();
})().catch((e) => { console.error(e); process.exit(1); });
