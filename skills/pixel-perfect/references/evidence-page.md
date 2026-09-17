# Delivering the evidence page

Read this before SKILL.md §7. The evidence page is the deliverable the reviewer actually looks at — not the PR diff, not a paragraph saying "verified". It exists because "matches the design" is a claim, and a non-technical reviewer can't check a claim; they can check a picture next to another picture and a table of numbers with deltas. This is the concrete form of a pre-review evidence standard: side-by-side proof at the frame's native size, measured geometry, and a hunk-by-hunk self-audit, all in one link.

## What makes the page work (keep every one of these)

1. **Four-up strip per screen, in this order: Before · Approved Figma · After · Heatmap.** Before is the real current capture (a fresh capture of the base branch, or the before-screenshot your team already tracks for that screen), not a memory of it. Figma is the export you diffed against. After is your harness capture at the frame's native size. Heatmap is `screenshot_diff.py`'s output. Same width for all four so the eye can scan across a row.
2. **A measured parity table under each strip.** Rows are the screen's key elements (headline, each card, each CTA, dividers); columns are x / y / w / h as `Figma → built` with a delta chip: green ≤1px, amber ≤2px, red beyond. Figma values come from `get_metadata` (frame-relative coordinates + the frame's origin), built values from `measure_geometry.js`. Never type a measured number from a screenshot.
3. **Match percentages at both 1x and 2x** in the screen's meta line. 2x is the retina truth; 1x catches DPR-rounding artefacts (0.5px borders become 1px).
4. **"What was wrong, what changed"** as bullets a non-technical reviewer can read: the root cause in one clause, the fix in one clause. ("The in-flow header is 38px, not the ~66px the old recipe assumed, so every column sat 28px high.")
5. **"Accepted exceptions", each one named AND justified** — never a percentage that was quietly deemed close enough. Legitimate kinds: live data vs placeholder (avatars, names, counts); font-metric differences between Figma's renderer and Chrome (state the size and the offset); a design-file inconsistency you resolved deliberately (say which frame you followed); token reconciliations (frame names a hex the codebase has re-mapped); sub-pixel noise (state the magnitude).
6. **Diff self-audit table**: every changed file → what changed → the ticket or review finding it traces to. Reviewers use this to confirm nothing rode along. Follow it with one line naming what was deliberately left out of scope.
7. **Summary tiles at the top** (screens, match range, geometry tolerance, tickets) so the verdict is readable in five seconds; the method section explains how the numbers were produced so they can be re-run.
8. **Published wherever your team reviews work, and linked everywhere the work is judged**: a hosted page, an attachment on the PR, or a shared doc — then linked from the PR body's verification section and from the ticket(s) it closes. The page's `<title>` is a product-style name ("Onboarding Reskin"), never a caption.

## The harness that makes the diff honest

A pixel diff is only meaningful if the two images contain the same text. Real pages can't be reached in the frame's exact data state (auth walls, no test account in that state, a request that would email real people), and a real page with different copy produces a heatmap full of red that says nothing. So:

- Add a dev-only route (for example `src/app/dev/<screens>/page.tsx` reachable at `/dev/<screens>?s=NN` in a Next.js app — whatever dev-only route pattern your repo uses, not linked from the app) that renders the **real** screen components with the **frame's own placeholder data** — the same org name, the same "1 member • 1 brand space", the same email. Text becomes identical and the heatmap shows only layout and rendering.
- Where the frame draws a placeholder graphic (a solid black avatar tile), give the fixture a matching asset (a 1×1 black PNG data URI as `logo_url`) so the region diffs on geometry, not on the placeholder.
- Components that read hooks for their data (`useAuth`, workspace context) get a dev-only `__preview*` prop seam, defaulting to the real hook when absent. Note it in the PR description.
- Capture with `capture_frames.js` at the frame's width × height, `document.fonts.ready` awaited, and dev-only fixed overlays stripped (Next.js dev badge, design-tool widgets) — otherwise they pollute the corners of every heatmap.
- Print the h1's computed font family on every capture. A silent fallback font invalidates the whole run.

## Reading a diff that is "99% but all the text is red"

Percentages and even heatmaps can't tell a 2px shift from anti-aliasing. Run `shift_search.py` on each region: it reports the (dx, dy) that best aligns built to Figma. `(0,0)` with a low residual is rasterisation noise; `(+1,0)` or `(0,-2)` with a residual that drops sharply at that shift is a real offset. Run it at 2x too — an offset that persists at 2x is layout, one that vanishes was DPR rounding.

## Pitfalls found the hard way (check these first next time)

- **Assumed chrome heights.** Measure the in-flow header with `getBoundingClientRect` before choosing the column's top padding; derive the `vh` from the frame height (e.g. y=200 with a 38px header on an 838px frame → `pt-[19.33vh]`).
- **Figma insets are from the outer edge.** A 19px content inset on a card with a 0.5px stroke needs `pl-[18.5px]` in CSS, because padding sits inside the border. Verify at 2x, where a 0.5px border is a real device pixel.
- **Rows the frame doesn't centre.** A 40px tile at y=19 inside an 80px card is 19 above / 21 below, not centred; `items-center` plus `pb-0.5` reproduces it.
- **Large headlines sit ~2px low in Chrome** versus Figma's export for the same font/line-height (vertical metrics). It's systemic to the type style — name it as an exception, don't nudge it per screen.
- **Placeholder data that contradicts itself** (a label reading "(0)" beside one listed item) is a design-file slip; follow the consistent sibling frame and say so.
- **Before pushing branch pointers in zsh, arrays are 1-indexed.** Use explicit SHAs.
- **Back up any hand-maintained JSON before scripting against it** (`cp prs.json prs.json.bak`); check its top-level shape first.

## Minimal recipe

```
# 1. exports (1x and 2x) — get_screenshot / download_assets, save to figma/ and figma2x/
# 2. harness captures
node scripts/capture_frames.js --width 1512 --height 838 --dpr 1 --out dev   s19=http://localhost:3000/dev/harness?s=19 …
node scripts/capture_frames.js --width 1512 --height 838 --dpr 2 --out dev2x s19=…
# 3. diffs + heatmaps
python scripts/screenshot_diff.py --image-a figma/s19.png --image-b dev/s19.png --out-dir diff/s19
# 4. offsets vs noise
python scripts/shift_search.py --image-a figma2x/s19.png --image-b dev2x/s19.png --regions @regions.json --scale 2 --radius 4
# 5. measured geometry for the parity tables
node scripts/measure_geometry.js --width 1512 --height 838 --root ".content" s19=… > measure.json
# 6. the page
python scripts/build_evidence.py --manifest evidence.json --out evidence.html
# 7. publish wherever your team reviews work, then link from the PR + the ticket
```
