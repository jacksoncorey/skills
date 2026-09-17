# Parsing a focus unit before writing code

Read this before implementing (SKILL.md §1). The goal is to replace "I looked at it" with "I read the actual property values" for every element in the focus unit.

## The four tools and what each is for

- **`get_design_context`** — start here, always. It returns the real structure and properties of the node(s) you point it at. Scope it to the focus unit itself (the card, the nav bar, the row) rather than the whole page — a page-level query summarizes and smears exactly the detail you need.
- **`get_variable_defs`** — the design tokens actually bound to this frame's properties (spacing, color, radius, type scale). This is how you know whether a value is "the codebase's `space-4`" or "a one-off raw number the design deliberately deviates with." Query it for the same scope as `get_design_context`.
- **`get_screenshot`** — a rendered export of the focus unit, at a known scale (check whether it's 1x or 2x — this matters when you screenshot your implementation later to diff against it). This is your literal comparison target in SKILL.md §3, not just a visual reference.
- **`get_metadata`** — exact width/height and node tree. Use this to set your browser viewport and screenshot crop to match precisely, so a diff isn't contaminated by a size mismatch before it even gets to comparing content.

## Per-element checklist

For every element in the focus unit, don't move on until you can answer these from data you actually queried, not from memory of "what it looked like":

**Layout**
- Padding — all four sides independently, not "16px of padding" when top/bottom and left/right differ.
- Gap/spacing between children (auto-layout gap, or the effective margin between siblings).
- Width/height — fixed, hug-contents, or fill-container, and the actual resulting dimension.
- Corner radius — per corner if they differ (a card with square bottom corners is a real, common pattern).

**Border & fill**
- Stroke width and color, and which side(s) it applies to.
- Fill color (and opacity, if less than 100%) — check whether it's a solid token or a gradient.
- Shadow — offset x/y, blur, spread, color, and opacity. These map to CSS `box-shadow` values that are easy to eyeball-approximate and easy to get subtly wrong; read the actual numbers.

**Typography** (for every text node, not just the visually prominent ones)
- Font family and weight — a design using a 500 where the code defaults to 400 (or vice versa) produces a hard-to-name "this looks a little off" result.
- Font size and line-height — Figma sometimes expresses line-height as a percentage rather than a fixed value; resolve it to the actual pixel/rem value your CSS needs.
- Letter-spacing — often expressed as a percentage in Figma; convert correctly rather than assuming it maps 1:1 to a CSS `em`/`px` value.
- Color, including any opacity.
- Text alignment and truncation/wrap behavior, if relevant to the layout.

## Mapping to real tokens

Once you have the exact values, check whether the codebase's existing design-token system (spacing scale, color tokens, shared type styles) already produces them. If it does, use the token — this keeps the implementation consistent with the rest of the codebase and means future design-system updates propagate correctly. If the design's actual number doesn't match any existing token, that's a real deviation: use the design's exact number as a raw value rather than rounding to the nearest token, and consider flagging the mismatch (it may be an intentional new value, or it may be a small inconsistency in the design itself worth confirming).

## Per-instance, not per-component

If the same component appears more than once in the design (three cards in a row, repeated list items), don't assume they're identical just because they're visually the same component. Check at least one instance directly — sizes, text, and even spacing can vary per-instance in ways a single top-level extraction won't surface.
