# Why the loop keeps going past a "good" percentage

A match percentage is an average over every pixel in the image. Averages hide exactly the failure mode this skill exists to catch: a small number of badly-wrong pixels concentrated in one place produces a similar percentage to a large number of trivially-different pixels spread everywhere. Those two situations need opposite responses — one is a real bug to fix, the other is expected noise to document — and the percentage alone can't tell you which one you're looking at.

## Read the heatmap, then decide

1. Open the heatmap image `screenshot_diff.py` produces. The differing regions are painted in red over a grayscale copy of the reference image.
2. Look at where the red is:
   - **Concentrated in one bounded shape** (a rectangle matching a button, a strip matching a border, a block matching a text element) → this is very likely a real, specific, fixable difference. Go find out what it is (SKILL.md §4).
   - **Diffuse, faint, and following the edges of text and curves throughout the image** → this is the signature of anti-aliasing/rendering noise (see `common-gotchas.md`). Worth a second look to confirm it's not masking something real underneath, but not something to chase indefinitely.
3. Check the `diff_bbox` the script reports — it's the bounding box of all differing pixels. A tight, small bbox in one corner is a very different situation from a bbox that spans nearly the whole image.

## Setting a stopping point

There is no universal percentage threshold that means "done" — a 99.8% match with one glaring, concentrated 2% miss is not done, and a 97% match that's entirely diffuse anti-aliasing noise across a large, detailed image might genuinely be as good as it gets. The actual stopping condition is:

- Every concentrated region in the heatmap has been individually investigated against a fresh, scoped Figma query (not assumed) and either fixed-and-reverified, or confirmed to be a legitimate exception (live data, dynamic state, missing font in the screenshotting environment, etc.).
- What remains, if anything, is diffuse and consistent with rendering noise, or has been explicitly named as an accepted exception.

Getting to zero visible diff is the goal and often achievable for static, well-specified components. When it's genuinely not achievable (a font that can't be loaded in the current environment, content that's inherently dynamic), the honest version of "done" is a documented list of exactly what's outstanding and why — not a percentage presented without that context.

## Don't stop on an unverified fix

Each iteration through the loop should end with a fresh screenshot and a fresh diff run, not with "that should fix it." The value of this whole process is that every claim of correctness is backed by a comparison someone could re-run and get the same answer from — that guarantee breaks the moment a fix is assumed correct instead of checked.
