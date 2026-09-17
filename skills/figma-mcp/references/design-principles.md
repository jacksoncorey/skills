# Design principles for the canvas

The rules below are extracted from Jakub Krehel's `better-*` skills (`better-layout`, `better-typography`, `better-ui`, `better-colors`, `better-writing`, `explain-interface`), published at [github.com/jakubkrehel/skills](https://github.com/jakubkrehel/skills) under the MIT license and written about at [interfaces.dev](https://interfaces.dev/). Those skills state each rule in CSS terms for code. This file restates the ones that apply when the output is a Figma frame, with the values translated to canvas properties. Install the originals for the full rules, the reasoning and the code recipes; nothing here replaces them, and when a rule below disagrees with its source, the source wins.

## Layout (from `better-layout`)

**Group with space, not lines.** Three tools create grouping, in order of preference: negative space, then a background shape, then a separator line as a last resort for dense data. The gap between groups is at least 2x the gap within one. On the canvas: nested auto-layout frames where the outer `itemSpacing` is at least double the inner, and a stroke or line node only where space alone cannot carry the structure.

**Align to shared edges.** Pick a small set of alignment edges and put everything on them. On the canvas that is the column grid on the wrapper, and one spacing step per level of subordination where 16 is the default with no scale.

**Order by importance.** The most important content near the top and the leading edge. Within a row, identifying content leads and metadata and actions trail. The first screenful is a table of contents, not the whole book.

**Keep controls distinct from content.** Every interactive element gets a background shape, a border or a consistent placement zone. A non-clickable badge shaped like the buttons beside it collects dead clicks.

**Breathing room between targets.** 12 between adjacent bordered or filled controls, 24 around borderless text and icon buttons, 24 or more between unrelated control groups.

**Inset buttons from the edges, let content bleed.** Backgrounds and media extend to the frame edges; controls and text stay inside the margins.

**Hold structure until it breaks.** Breakpoints come from where the content stops fitting, not from device presets. Design the smallest and largest sizes first.

**Plan for growth.** No fixed-width text container sized to one string. A one-word button label is the riskiest thing on the screen once translated.

## Typography (from `better-typography`)

**Fewer fonts, sizes and weights.** Rarely more than three families. Pair for contrast, not similarity: a serif display with a sans body reads as deliberate, two near-identical sans faces read as a mistake.

**A type scale with semantic names.** A small set of sizes, deviated from as little as possible, named by role on a team: `heading/32`, `body/16`, not a one-off 17.

**Line-height by role.** Headings around 1.1, body 1.5 to 1.6. On the canvas, set `lineHeight` explicitly in percent or pixels rather than leaving `AUTO`, because auto leading is the font's metric and varies by family.

**Letter-spacing by size.** Large headings slightly negative, small uppercase labels slightly positive, body copy neither.

**Cap the measure.** Long-form text at 60 to 75 characters per line. Around 640 wide at 16 px for most sans faces.

**Wrap deliberately.** Balance headings across lines; avoid a single short word alone on the last line of a description.

**Tabular numbers on changing values.** Timers, counters and prices use tabular figures so digits do not shift.

**Size and contrast floors.** Body 16. UI text 14, captions 13, rarely below 12. Contrast 4.5:1 for regular text and 3:1 for large text, roughly 24 and up.

**Copy in natural case, styled by the property.** Store text as written and set `textCase` for uppercase labels, so a restyle never rewrites copy. Curly quotes in prose, en dash for ranges.

**Kerning is the font's job.** It is on by default. Letter-spacing is the property you adjust; kerning you only ever switch off deliberately.

## UI polish (from `better-ui`)

**Concentric border radius.** Outer radius equals inner radius plus the padding between them. A card at 20 with 8 padding holds an inner element at 12. Above 24 of padding, treat the layers as separate surfaces and choose radii independently. Mismatched nested radii are the most common thing that makes an interface feel off.

**Optical over geometric alignment.** A button with a trailing icon takes 2 less padding on the icon side. Play triangles shift right. Asymmetric icons get nudged, ideally in the vector itself.

**Shadows for elevation, borders for structure.** Where a border exists only to create depth, replace it with a layered shadow. The recipe is a 1 px ring at 6 percent black, a 1 to 2 blur at 6 percent, and a 2 to 4 blur at 4 percent. Keep borders that communicate structure. Dividers, table cells, input outlines and selected states stay borders. In dark mode a single white ring at 8 percent.

**Image outlines.** A 1 px inset stroke at 10 percent pure black on every photo in light mode, 10 percent pure white in dark. Never a tinted near-black from the palette, which reads as dirt on the image edge.

**Minimum hit area.** 44 by 44 on touch, at least 40 by 40 on desktop. A 20 px checkbox still gets a 44 px target, and two targets never overlap.

**Interruptible, subtle motion.** Enter with a small translate and a fade, exit softer than enter, stagger staged entrances by about 100 ms. On the canvas this is a prototype transition choice, and the defaults are smart animate with ease-out around 200 to 300 ms.

## Color (from `better-colors`)

**Work in a perceptually uniform space.** Palettes ramped in OKLCH keep hue constant and lightness steps even; HSL ramps drift toward purple in the blues.

**Fix contrast by lightness alone.** When a pair fails, move the lightness channel and leave chroma and hue where they are.

**Lightness gaps.** On a light background above 0.85 L, text below 0.45 L. On a dark background below 0.25 L, text above 0.75 L.

**Same relative chroma across hues.** Match the percentage of each hue's maximum chroma, not the absolute number, or some hues look washed out beside others.

**Derive dark mode from light** by reversing the lightness mapping rather than hand-picking a second palette.

**Semantic tokens over primitives at the point of use.** `color/bg/primary` aliases `gray/25`; the frame binds to the semantic name. Primitives are hidden from the picker.

## Writing (from `better-writing`)

**Recon the existing voice** before writing a word. The product has one voice and its existing copy establishes it; a local edit does not invent a new one.

**Verb-first buttons.** "Send", "Save draft", "Delete project". A confirmation repeats the consequence so the dialog is answerable without reading the body.

**Links describe their destination.** "Read the billing docs", never "click here", and no bare "Learn more" twice on one page.

**One vocabulary per flow.** "Continue" or "Next", not both. "Archive" in the menu is "Archive" in the toast.

**Plain words over clever ones.** Delete every word that does no work. No idioms or humor that will not translate. Address the reader as "you".

**Tone flexes with stakes.** Warm for success and empty states, neutral for settings, calm and plain for errors and destructive confirmations.

## Reading a live interface (from `explain-interface`)

**Tokens first.** A page that exposes custom properties on its root has already told you most of the answer. Group them by prefix; the prefixes are the system's own layer names.

**A fingerprint is not a fact.** Report each detection with its evidence, and treat a false as a fingerprint that did not fire, not as an absence.

**Read a second state.** One width and one theme is one state. Resize to 375, toggle the theme, tab to the first control, and note what changed. The probes themselves are in [grounding.md](grounding.md).

## How these apply to the review loop

The fidelity reviewer checks the atomic rules above: gaps at 2x, radii concentric, line-height by role, tracking by size, measure capped, contrast floors, tokens bound. The vision reviewer checks the ones that need judgment: importance order, one primary action, voice, whether the density and mood match the brief. Neither reviewer invents a rule that is not here or in the brief; a preference is not a finding.
