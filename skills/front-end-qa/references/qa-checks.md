# The four checks — detail

Read this when running §2 of SKILL.md. Each check has a different failure mode; running all four is what makes this a real QA pass rather than a vibe check.

## 1. Scope compliance

**Question:** does the diff do exactly what the directions asked, and nothing else?

- Walk every hunk in the diff. For each one, point to the specific line in the directions that justifies it. If you can't, that's a finding — regardless of whether the extra change looks like an improvement.
- Look for incidental changes hiding inside a legitimate hunk: a reformatted line next to a real change, a reordered import, a renamed variable "while I was in there." These are easy to miss because they sit right next to justified changes — check line-by-line, not hunk-by-hunk.
- Look for whole-file or whole-component rewrites presented as a "tweak." If a diff replaces a large block instead of editing specific lines, that's a finding on its own even if the resulting code looks correct — a rewrite that happens to be equivalent is still evidence the underlying discipline (edit, don't regenerate) wasn't followed, and the next rewrite might not be equivalent.

**Evidence to cite:** the specific diff hunk, and the specific line in the directions (or its absence) that does or doesn't justify it.

## 2. Visual / pixel fidelity

**Question:** does the rendered result match the design reference, precisely — not approximately?

- If there's a Figma frame or prototype, diff the rendered proposal against it with `scripts/screenshot_diff.py`. Read the heatmap yourself; don't just report the percentage. A 97% match can still contain one glaring, important 3% error exactly where someone will look first (a CTA button, a price, a headline).
- Compare specific values where you can: position, spacing, sizing, color. "Looks close" is not a finding — "the gap between cards is 12px in the implementation vs. 16px in the design" is.
- If there's no design reference at all, mark this **N/A** with the reason ("no Figma frame or prototype provided in the directions") rather than skipping it silently or inventing a judgment call about whether it "looks fine."

**Evidence to cite:** the diff heatmap, the match percentage, and the specific pixel region or value where a real difference exists.

## 3. Functional / behavioral correctness

**Question:** does the implementation actually do what was asked — not just look right in one static state?

- Directions often imply states they don't spell out. "Show the discount" implies: what does it look like with no discount? A discount of $0.00? A discount larger than the price? Check the states the directions logically require, not just the one screenshot shows.
- Check interaction states relevant to the change: hover, focus, active, disabled, loading, error, empty. If the tweak touches a component with these states, at least the states plausibly affected by the change should be checked, not assumed unchanged.
- If the directions include explicit behavior ("clicking X should do Y"), verify it actually happens in the live preview — don't infer correctness from the code looking like it should work.

**Evidence to cite:** the specific state or interaction tested, what was expected per the directions, and what actually happened.

## 4. Regression check

**Question:** does anything outside the stated scope now behave differently than it did in the baseline?

- Compare the baseline and proposed previews side by side for anything not mentioned in the directions — layout of nearby elements, other interactive states, responsive behavior at a different viewport width.
- If the touched component is shared/reused elsewhere in the app (check for other import sites), consider whether the change could affect those call sites even if this particular screen looks fine — this is the class of regression that's easy to miss because it doesn't show up anywhere in the diff of the one screen you're looking at.
- A visually perfect, on-spec change on the target screen that silently changes something adjacent is still a FAIL on this check, even though it would PASS checks 1–3.

**Evidence to cite:** what was compared (baseline vs. proposed, or a shared component's other call sites), and the specific difference found, if any.
