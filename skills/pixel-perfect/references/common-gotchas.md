# Common causes of false or misleading diffs

Some diffs are real bugs. Some are artifacts of comparing two different rendering systems and don't mean the implementation is wrong. Knowing which is which keeps the loop from either stopping too early (accepting a real bug as "just rendering noise") or running forever chasing something that was never fixable.

## Real, fixable causes (fix these)

- **Box-sizing mismatches.** If a border or padding is being added on top of a fixed width instead of `box-sizing: border-box`, the element will be a few pixels larger than the design in a way that looks like "everything is slightly off."
- **Line-height percentage vs. fixed value.** Figma's "percentage" line-height and a CSS `line-height` set to what looks like the same number are not automatically equivalent — resolve to the actual pixel value the design renders at.
- **Letter-spacing units.** Figma often expresses tracking as a percentage of font size; naively copying the number into a CSS `em` or `px` value produces a real, visible difference in tighter/looser text, especially at larger sizes.
- **Border vs. outline vs. box-shadow-as-border.** A 1px border implemented as `outline` instead of `border` (or vice versa) can shift adjacent layout in ways a plain color/width check won't catch — check the box model, not just the visual line.
- **Image export scale mismatch.** Comparing a 2x Figma export against a 1x browser screenshot (or vice versa) produces a dimension mismatch that looks like a sizing bug but is actually a capture-setup bug. Match device pixel ratio to the export scale before diffing (SKILL.md §3).
- **Wrong viewport/breakpoint.** Screenshotting at the wrong width entirely will produce a diff that looks like everything is wrong, when actually you're just comparing the wrong responsive state. Confirm the frame's designed viewport from `get_metadata` first.
- **Gap vs. margin double-counting.** Auto-layout `gap` in Figma and manually-added margins on children in code can stack, producing extra space that a top-level "padding looks right" check won't surface — this is why the per-element checklist in `figma-extraction.md` checks gap separately from padding.

## Expected, non-fixable differences (document, don't chase)

- **Anti-aliasing/subpixel rendering.** Figma's renderer and a browser's renderer will produce very slightly different edge pixels on curves, rounded corners, and text, even with identical property values. `screenshot_diff.py`'s threshold already filters small per-channel differences as noise — if remaining diff is small, diffuse across the whole image (not concentrated in one region), and shows up mainly around text/curve edges in the heatmap, this is very likely this category.
- **Live vs. placeholder content.** Real data (actual username length, actual avatar image, actual timestamp) will differ from whatever static content the Figma frame shows. This is expected and correct — don't force the implementation to match placeholder text.
- **Font hinting/OS-level rendering differences**, if the Figma export and the browser screenshot were captured on different operating systems. If reasonably possible, capture both on the same machine/OS to eliminate this as a variable rather than having to reason about whether a small diff is this or a real bug.
- **Missing font files.** If the exact font isn't installed/loaded in the environment doing the screenshotting, the browser will substitute a fallback font that can look close but never pixel-match. This produces a diff that looks like a typography bug but is actually an environment gap — confirm the correct font is actually loading (check computed styles, not just visually) before concluding the spacing/sizing values themselves are wrong.

## The general rule

A diff that's concentrated in one bounded region, especially one that lines up with a specific element's boundary (a card edge, a button, a text block), is almost always a real, fixable issue. A diff that's diffuse, faint, and spread across text and curved edges throughout the whole image is much more likely rendering noise. When genuinely unsure which category a diff falls into, say so rather than guessing — this is exactly the kind of judgment call worth surfacing rather than silently resolving either direction.
