---
name: pixel-perfect
description: "Drive a UI implementation to true pixel parity with a Figma design — not a 'close enough' visual pass, but a verified match on spacing, padding, sizing, radius, typography, and color for every element in scope. Parses each focused element's exact properties via the Figma MCP before writing any code, then after implementing, runs a self-directed side-by-side screenshot comparison loop — reading the diff heatmap, not just the match percentage — and keeps fixing and re-checking until the implementation is indistinguishable from the design or any remaining gap is an explicitly justified exception (e.g. live data vs. placeholder text, unavoidable font-rendering noise), and finishes by publishing a self-contained evidence page (before / Figma / after / heatmap per screen, measured geometry with deltas, accepted exceptions, diff self-audit) that is linked from the PR and the ticket. Use whenever the user says 'pixel perfect', 'make this match Figma exactly', 'get this pixel-perfect', 'nail the spacing on this', 'this needs to be exact', or is implementing/refining any UI against an approved Figma frame where visual precision genuinely matters. Also trigger proactively on ordinary 'match the design' or 'build this from Figma' requests when the design reference is a real Figma file, not just a rough sketch — treat 'match the design' as match it exactly, not approximately."
---

# Pixel Perfect

## Why this exists

The default failure mode when an agent implements from a design isn't laziness — it's confidence. It looks at a Figma frame, forms a mental impression ("card, rounded corners, some padding, gray text"), writes code that matches the impression, glances at the result, and calls it done. Every step in that chain loses precision: the impression drops exact numbers, the code fills gaps with plausible-looking guesses, and the glance-check compares against the same mental impression that wrote the code, not against the actual source of truth. The output can look right at a glance and still be off by a few pixels in a dozen small ways that add up to "this doesn't feel right" without anyone being able to say why.

This skill closes that loop at both ends: extract exact values instead of impressions before writing code, and verify with a pixel diff instead of a glance after writing it — then actually act on what the diff shows, repeatedly, until there's nothing left to fix or what's left is a documented, legitimate exception.

## 0. Scope the unit you're matching

Pixel-perfect work has to happen at a scale small enough to actually verify. Trying to eyeball a whole dashboard against a whole Figma page and call it "98% matching" hides exactly the kind of small, concentrated error this skill exists to catch.

1. Identify the Figma frame or component you're matching, and the exact code component/section it corresponds to.
2. Break the work into **focus units** — usually one component or one clearly bounded section at a time (a card, a nav bar, a form row), not a whole page in one pass. Small enough that a side-by-side comparison has one obvious thing to look at.
3. Note the frame's exact dimensions and the breakpoint/viewport it was designed at (from `get_metadata` or `get_design_context`) — you'll screenshot your implementation at this same size later. A size mismatch alone will produce a misleading diff.
4. If the target already exists in code (a tweak, not a fresh build), treat this skill as the fidelity engine for that change — pair it with a scoped-change builder skill if the change also needs scoping discipline, an independent QA pass (see `front-end-qa`), and a shippable diff report. This skill on its own is just the "make it match, verifiably" loop.

## 1. Parse every element before writing any code

Read `references/figma-extraction.md` for the full checklist. The short version: query the Figma MCP directly on the focus unit rather than working from a screenshot or a description of one.

- `get_design_context` — the primary source. Pull this for the focus unit and read the actual structure and properties, not a summary of them: padding (each side, not just "some padding"), gap/spacing between children, corner radius per corner, stroke width and color, fill, and for every text node — font family, weight, size, line-height, letter-spacing, and color.
- `get_variable_defs` — the design tokens the frame actually uses. Map your implementation to the codebase's real equivalent tokens wherever they exist; only hardcode a raw value where the design genuinely deviates from the token system, and when that happens, use the design's exact number, not the nearest round one.
- `get_screenshot` — a rendered reference export of the focus unit. Save it locally at its native resolution; this is what you diff against in step 3.
- `get_metadata` — exact frame/node dimensions, used to match your screenshot's viewport and crop precisely.

Do this per focus unit, not once for the whole page — a component reused three times in the design can still have per-instance differences (a wider card in one spot, different text) that a single top-level query will smear over.

## 2. Implement against the parsed values

Write the code using the exact values from step 1, mapped to real tokens where they exist. This is normal implementation work — the discipline that matters here is that every spacing/sizing/color value in the code should trace back to something you actually read in step 1, not something that "looks about right" next to it.

## 3. Screenshot and diff — read the heatmap, not the percentage

1. Get your implementation running and screenshot the focus unit at the exact same dimensions/crop as the Figma export from step 1. **Render it through a harness, not the live route:** add a dev-only page (for example `src/app/dev/<screens>/page.tsx` reachable at `/dev/<screens>?s=NN` in a Next.js app — whatever dev-only route pattern your repo already uses, not linked from the app) that mounts the real components with the frame's own placeholder data — same names, same counts, same email — so the two images differ only in layout and rendering, never in copy. Capture with `scripts/capture_frames.js` (fonts settled, dev-only overlays stripped, h1 font family printed) **at both 1x and 2x**, against 1x and 2x exports; 2x is the retina truth, 1x exposes DPR rounding. Details and fixture tricks: `references/evidence-page.md`.
2. Run the comparison:
   ```
   python scripts/screenshot_diff.py --image-a <figma_export.png> --image-b <your_screenshot.png> --out-dir <scratch_dir>
   ```
   This prints a match percentage, whether dimensions matched, a bounding box of where the differences are concentrated, and a heatmap image with differing regions painted red. It already tolerates minor anti-aliasing/compression noise (see `references/common-gotchas.md`) so a reported diff is a real one, not rendering fuzz.
3. **A 99% match is not the same as done.** Read `references/iteration-loop.md` for why: a small percentage can be one glaring, concentrated miss (a button 6px off, a border that's the wrong side of a token boundary) rather than the harmless kind of difference spread evenly across the frame. Open the heatmap image and look at the flagged region directly — don't just read the number.
4. **When the heatmap paints every text block red, run `scripts/shift_search.py`** on each region. It reports the (dx, dy) that best aligns built to Figma: `(0,0)` with a low residual is anti-aliasing; `(+1,0)` or `(0,-2)` with a sharply lower residual is a real offset of that many pixels. Run it at 2x as well — an offset that survives 2x is layout, one that vanishes was DPR rounding.
5. **Measure, don't eyeball, the geometry.** `scripts/measure_geometry.js` dumps `getBoundingClientRect` for the headline, cards, buttons and dividers; compare those to the frame coordinates from `get_metadata`. This is the data the evidence page's parity tables are built from, and it is how a 28px column offset hiding behind a "matches" grade gets caught.

## 4. Diagnose and fix — then re-verify, don't assume the fix worked

For each region the heatmap flags:

1. Go back to Figma and re-query `get_design_context` scoped to that specific node, not the whole frame again — confirm the exact property you're suspecting (that padding value, that font weight) rather than guessing at what's likely wrong.
2. Fix the code.
3. Re-screenshot and re-run the diff. A fix you haven't re-verified is a guess wearing a done label — the whole point of this loop is that "should be fixed now" isn't a stopping condition, a clean diff is.
4. Repeat until either the diff is clean, or what remains is a genuine, explainable exception (see below) — never because the number looked close enough to stop checking.

**Legitimate exceptions** (document these explicitly rather than silently accepting them or silently grinding forever trying to eliminate them):
- Live/real data rendering differently than the design's placeholder text (different string length, a real avatar image vs. a placeholder).
- Font rendering/anti-aliasing differences between Figma's renderer and a browser that persist below the noise threshold the diff script already filters — if this is the entire remaining diff and it's small and diffuse (not concentrated in one spot), that's expected, not a bug.
- Dynamic states the static Figma export can't show (hover, focus, loading) — verify these against Figma's own interactive/variant frames if they exist, rather than the static export.

If you're not sure whether something is a legitimate exception or a real miss, say so explicitly rather than deciding unilaterally — this is exactly the kind of judgment call worth surfacing.

## 5. Move to the next focus unit, then do a composition pass

Once one focus unit is clean, move to the next. After every unit in scope passes individually, do one more comparison at the full assembled-screen level (still against the Figma frame at its real dimensions). Components can each be individually pixel-perfect and still be positioned wrong relative to each other — wrong gap between sections, misaligned columns — and that only shows up once they're all together.

## 6. Report what you found

When you finish, tell the user plainly:
- Which focus units were checked and their final match state.
- Any accepted exceptions from step 4, and why each one is legitimate rather than just unresolved.
- If something never converged and you're not sure why — say that too, rather than presenting a diff you couldn't close as if it were fine.

The report is a summary. The proof is §7.

## 7. Deliver the evidence page — this is the deliverable

A verbal "verified" is a claim; a reviewer needs proof they can check without reading code. Before announcing "ready for review", build one self-contained page with `scripts/build_evidence.py` (manifest shape documented in the script; rationale and pitfalls in `references/evidence-page.md`). It must carry, per screen:

- **Before · Approved Figma · After · Heatmap**, four-up, same width — Before is a real capture of the current base branch, never a description.
- **A measured parity table**: each key element's x / y / w / h as `Figma → built` with a delta chip (green ≤1px, amber ≤2px, red beyond), Figma values from `get_metadata`, built values from `measure_geometry.js`.
- **Match % at 1x and 2x** in the meta line, with the frame node, ticket(s) and PR.

And once for the page: summary tiles (screens, match range, geometry tolerance, tickets); the method, so the numbers can be re-run; **"What was wrong, what changed"** in one-clause-cause / one-clause-fix bullets; **accepted exceptions, each named and justified** (live data, font metrics with the size and offset stated, a design-file slip you resolved deliberately, token reconciliations, sub-pixel noise with its magnitude); a **diff self-audit table** (file → what changed → ticket or finding), and one line naming what was left out of scope on purpose.

Publish it wherever your team reviews work (a hosted page, an attachment on the PR, a shared doc) and **link it from the PR body's verification section and from the ticket(s) it closes**. A page nobody can find from the PR is not delivered.

## Non-negotiable checklist (self-check before calling it done)

- [ ] Every spacing/sizing/color/typography value in the implementation traces back to a value actually read from the Figma MCP for that specific node — not eyeballed from a screenshot or a description.
- [ ] The implementation screenshot was captured at the same dimensions/crop/scale as the Figma export before diffing — a size mismatch was resolved, not padded over and ignored.
- [ ] Every diff was read from the heatmap image, not just the percentage number.
- [ ] Every fix was re-screenshotted and re-diffed — no fix was assumed correct without a fresh comparison.
- [ ] Any remaining diff is either zero, or an explicitly named and justified exception — never a percentage that was quietly deemed "close enough."
- [ ] A full-composition pass ran after all individual focus units passed, catching any cross-component positioning issues.
- [ ] Captures came from a harness rendering the real components with the frame's placeholder data, at 1x and 2x, with the h1 font family confirmed — not from a live route with different copy.
- [ ] Every text-shaped residual was classified with `shift_search.py` (offset vs anti-aliasing), and every key element's geometry was measured with `measure_geometry.js` against `get_metadata`, not eyeballed.
- [ ] The evidence page (§7) is published and linked from the PR and the ticket before "ready for review" is said.

## Why this shape, briefly

Parsing before coding and diffing after coding are the same discipline applied at both ends of the same failure mode: don't let an impression stand in for a measurement. The heatmap-over-percentage rule exists because a single number can't distinguish "everything is slightly and harmlessly different" from "one thing is badly wrong and everything else is perfect" — and those need completely different responses. And the loop keeps running on the diff, not on a fix attempt, because "I think I fixed it" and "I verified it's fixed" are different claims, and only the second one is actually checkable.
