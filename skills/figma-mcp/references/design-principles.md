# Design principles for the canvas

The rules below are extracted from Jakub Krehel's `better-*` skills (`better-layout`, `better-typography`, `better-ui`, `better-colors`, `better-writing`, `better-accessibility`, `explain-interface`), published at [github.com/jakubkrehel/skills](https://github.com/jakubkrehel/skills) under the MIT license and written about at [interfaces.dev](https://interfaces.dev/). Those skills state each rule in CSS terms for code. This file restates the ones that apply when the output is a Figma frame, with the values translated to canvas properties. Install the originals for the full rules, the reasoning and the code recipes; nothing here replaces them, and when a rule below disagrees with its source, the source wins. Wording follows the upstream repository as of its 2026-08-29 commits. A rule marked "this skill's rule" has no source and is ours.

## Layout (from `better-layout`)

**Group with space, not lines.** Negative space first, a background shape second, and a separator line last, only for dense data such as tables and long settings lists. The gap between groups is at least 2x the gap within one: 8 inside a group means 16 or more between groups. On the canvas that is nested auto-layout frames where the outer `itemSpacing` is at least double the inner. A separator is a 1 px line node at low contrast, never placed beside a gap that already did the job.

**Align to shared edges.** Pick a small set of alignment edges and put everything on them, with one spacing step per level of subordination and 16 as the default where no scale exists. Numbers in tables align to the trailing edge, text to the leading edge. On the canvas: the column grid on the wrapper (`layoutGrids`), one `paddingLeft` step per nesting level, and `textAlignHorizontal: "RIGHT"` on numeric columns.

**Order by importance.** The most important content sits near the top and the leading edge, and the one number the user came for is never buried under rows of secondary detail. Within a row, identifying content leads and metadata and actions trail.

**Do not overload the entry point.** The first screenful is a table of contents, not the whole book. One primary action per view, and secondary actions go behind a menu once they exceed three. A short view that links deeper beats a long view at level one. On the canvas: one filled-button instance per frame and an overflow menu past three actions.

**Keep controls distinct from content.** Every interactive element gets a background, a border, an underline, or a consistent control zone such as a toolbar or footer row. The inverse holds: a non-clickable badge shaped like the buttons beside it collects dead clicks, so a static badge never reuses the button component.

**Breathing room between targets.** 12 between adjacent bordered or filled controls, 24 around borderless text and icon buttons, and 24 or more between unrelated control groups (2x the intra-group gap). Compact professional tools may use less as long as hit areas stay distinct and never overlap. On the canvas that is `itemSpacing` on the control row.

**Hint at hidden content.** The next item in a horizontal scroller peeks 16 to 32 past the edge, and a collapsed section shows a chevron or "Show 12 more results", never a bare "More". On the canvas: a carousel frame with `clipsContent` sized so 16 to 32 px of the next card shows, and a disclosure label that names what is hidden.

**Inset buttons from the edges.** In content layouts a full-width button stays inside the layout margins with a visible radius, starting near 16 inline on mobile. Edge-to-edge actions are only for deliberate platform chrome that accounts for safe areas. On the canvas: 16 horizontal padding on the action bar and a visible `cornerRadius` on the button.

**Content bleeds, controls float.** Backgrounds and media extend to the frame edges; text and controls stay inside the margins and safe areas, and sticky chrome floats above the content layer rather than blocking it.

**Hold structure until it breaks.** Breakpoints come from where the content stops fitting, not from 768 or 1024 because a preset says so; collapse late, and design the smallest and largest supported sizes first. On the canvas: one frame per breakpoint, named for the width the content broke at, with children on `layoutSizingHorizontal: "FILL"`.

**Plan for growth and clipping.** No fixed width or height on a text container, buttons size from their label, and a one-word label is the riskiest string on the screen once translated. A critical action never sits where a resize or scroll clips it; when a modal's content scrolls, its action row does not. On the canvas: text and buttons on `layoutSizingHorizontal: "HUG"`, body text on `textAutoResize: "HEIGHT"` with a `maxWidth`, and the action row outside the scrolling frame.

**Mirror for RTL (audit item).** Layout mirrors leading to trailing, sequences that encode progression (steps, ratings, progress) mirror, and digit order never reverses. Directional icons flip (back arrows, chevrons, text-block glyphs); logos, checkmarks, physical objects and media playback do not. Figma has no logical direction, so an RTL frame is a separate variant checked by hand and the spec names which icons flip.

## Typography (from `better-typography`)

**Fewer fonts, sizes and weights.** Rarely more than three families, paired for contrast, not similarity: a serif display over a sans body reads as deliberate, two near-identical sans faces read as a mistake. Below 18, stay at weight 400 or heavier; weights under 300 are display-only at 28 and above.

**No fake weights.** Load the faces the design uses; a synthesized weight or style distorts the real face. On the canvas, `fontName.style` is a style the family ships. A weight is never faked with a stroke on text, nor an italic with a skew (this skill's canvas reading).

**A type scale with semantic names.** A small set of sizes, deviated from as little as possible, named by use on a team, not by size: `text/body-sm`, not `text/14`. A starting role scale (from the source's spacing table), as size, leading and weight: display 36, 1.1, 600. Title 24, 1.2, 600. Heading 18, 1.3, 600. Body 16, 1.5, 400. Caption 13, 1.4, 400. Emphasis within a role is one weight step up (400 to 500), never a size change. On the canvas: text styles named by role, `fontSize` only from the scale.

**Heading sizes descend with level.** Each heading level maps to a descending step, so a child heading never renders more prominently than its parent. Adjacent levels may share a size at the small end if weight or spacing keeps them distinct. A heading is never smaller than body text unless it is an overline label.

**Line-height by role.** Display around 1.1, title 1.2, heading 1.3, body 1.5 to 1.6, and anything that wraps to three or more lines at least 1.4 even in a tight row. On the canvas: `lineHeight` `{ unit: "PERCENT", value: 110 }` on display, 150 to 160 on body, 140 minimum on text that renders three lines; PERCENT is the unitless analogue. This skill's rule: never leave `AUTO` on display text, because auto leading is the font's own metric and differs per family.

**Letter-spacing by size.** Large headings slightly negative, about -0.02 em; small uppercase labels slightly positive, about +0.05 em; body copy neither. On the canvas: `letterSpacing` `{ unit: "PERCENT", value: -2 }` on display, `+5` on small uppercase labels, `0` on body.

**Kerning is the font's job.** It is on by default and is switched off only deliberately; letter-spacing is the property you adjust. This skill's rule: above about 48 px, a bad pair is fixed with `setRangeLetterSpacing` on that segment, never on the whole line.

**Cap the measure.** Long-form text at 60 to 75 characters per line, which at 16 px is roughly 560 to 680 wide depending on the font; recheck when the body size changes. On the canvas: body nodes at a fixed width in that range with `textAutoResize: "HEIGHT"`. This skill's default is 640 for a 16 px sans.

**Wrap deliberately.** Balance headings across lines and avoid a single short word alone on the last line of a description. Keep labels and badges on one line, and skip both treatments in long-form text. Figma has no `text-wrap`, so resize the heading node until the lines even out or break manually, never by shrinking the size; labels use `textAutoResize: "WIDTH_AND_HEIGHT"`.

**Truncate without losing content.** Single line ends in an ellipsis, several lines get a line clamp, and when the hidden text matters the full value is reachable in a tooltip or an expanded state. On the canvas: `textTruncation: "ENDING"` with `maxLines`, plus a variant or note showing where the full value lives.

**Tabular numbers on changing values.** Timers, counters and prices use tabular figures so digits do not shift. On the canvas the `TNUM` feature is set in the type details panel. The Plugin API reads `openTypeFeatures` but does not set it, so a script verifies and a person sets.

**Size floors.** Body 16 as the starting point, moved off only for a reason you can name; UI text 14 for inputs and menus; captions 13; rarely below 12. Inputs still need 16 on mobile frames.

**Copy in natural case, styled by the property.** Store text as written and set `textCase: "UPPER"` for uppercase labels, so a restyle never rewrites copy. Smart punctuation: curly quotes in prose, straight quotes in code, an en dash for ranges, the em dash character for an aside. Also the single ellipsis character and a non-breaking space inside "16 px".

**Justified text stays out of interfaces.** `textAlignHorizontal: "JUSTIFIED"` belongs to specific editorial layouts and nowhere else.

## UI polish (from `better-ui` and `better-accessibility`)

**Concentric border radius.** Outer radius equals inner radius plus the padding between them: a card at 20 with 8 padding holds an inner element at 12. Above 24 of padding, treat the layers as separate surfaces, and keep an established component token where the layers are independent or the padding is deliberately asymmetric. On the canvas: `cornerRadius` per layer, and the four per-corner radii checked too.

**Optical over geometric alignment.** A button with a trailing icon takes 2 less padding on the icon side as a starting point. Play triangles shift right about 2, and asymmetric icons get nudged, ideally in the vector itself. On the canvas: `paddingRight` equals `paddingLeft` minus 2 on the icon side, and a 2 px offset on the play glyph inside its frame.

**Shadows for elevation, borders for structure.** A border that exists only for depth becomes a three-layer shadow; dividers, table cells, input outlines, selected and focus states stay borders. Light mode is three layers. A ring at offset 0, blur 0, spread 1, black 6%. Then offset y 1, blur 2, spread -1, black 6%. Then offset y 2, blur 4, spread 0, black 4%. Hover raises the three alphas to 8%, 8% and 6%. Dark mode is a single white ring at offset 0, blur 0, spread 1, 8%, and 13% on hover. On the canvas: three `DROP_SHADOW` effects with `offset`, `radius` (blur), `spread` and `color` alpha as above, with hover and dark as variants.

**Image outlines.** A 1 px inside stroke at 10% pure black on every photo in light mode, 10% pure white in dark. Never a tinted near-black from the palette and never the accent or ink colour. On the canvas: `strokes` `#000000` at opacity 0.1, `strokeWeight` 1, `strokeAlign: "INSIDE"`, on placeholder image frames too.

**Icons match the text.** Stroke 1.5 beside regular (400) text, 2 beside medium or semibold (500 to 600), 2.5 beside bold (700). One icon library per surface, icons at the set's native grid of 16, 20 or 24, sized 1 em to 1.25 em inline. Outline is the default variant and fill marks the active state. On the canvas: icon `strokeWeight` follows the label's weight, and icon fills bind to the text-colour token rather than a hex per state.

**Minimum hit area.** 44 by 44 on touch, at least 40 by 40 on desktop, and 24 by 24 is the WCAG 2.5.8 hard floor. A 20 checkbox still gets a 44 target, two targets never overlap, and when extended areas would collide each shrinks to the largest size that does not. Under the spacing exception, 20 px targets need a 4 px gap. On the canvas the component frame is the target even when the glyph is 20, and neighbours' `absoluteBoundingBox` never intersect.

**Decorative layers do not swallow clicks.** A glow, scrim or sheen painted over a control is named as decorative in the layer tree and the handoff says pointer-events none. A scrim that dismisses on click is a control, not decoration.

**Focus rings.** Every keyboard-reachable control has a focus state with at least a 2 px solid perimeter at 2 px offset, verified against every adjacent colour it crosses. On the canvas: a Focus variant per control with a 2 px `OUTSIDE` stroke on a wrapper padded by 2, never a state with no ring.

**Press feedback.** Scale to 0.96 on press, never below 0.95. On the canvas: a pressed variant at 96% or a `SMART_ANIMATE` reaction to it.

**Enter and exit motion.** Staged entrances are for infrequent moments only: the first load of a hero, a success or empty state. Split the content into semantic chunks and stagger them about 100 ms apart (words about 80). Each chunk enters with opacity 0 to 1, y 12 to 0 and blur 4 to 0 over about 300 ms. Exits are softer: y -12, opacity to 0, about 150 ms, ease-out in both directions. An element is removed immediately when motion adds nothing or the interaction repeats. On the canvas: `reactions` with `transition.type: "SMART_ANIMATE"`, `duration` 0.3 in and 0.15 out, `easing.type: "EASE_OUT"`. Prototypes do not interpolate blur reliably, so the 4 px blur goes in the handoff.

**Contextual icon swaps.** Scale 0.25 to 1, opacity 0 to 1, blur 4 to 0. The curve is a spring of 0.3 s with bounce 0, or cubic-bezier(0.2, 0, 0, 1) at 300 ms without a motion library. On the canvas: `easing` `CUSTOM_CUBIC_BEZIER` with `{ x1: 0.2, y1: 0, x2: 0, y2: 1 }` and `duration` 0.3, both icons present in the component with opacity swapped.

**Motion restraint.** High-frequency interactions get instant feedback or a transition of 150 ms or less on opacity and colour. Every animated state change also has a static cue: a colour, an icon or a label. On the canvas: hover and selected variants differ in a fill or glyph, not only in the transition.

**Do not rely on colour alone.** Status carries a redundant cue, an icon, text or an underline, beside the colour. On the canvas every status variant has a glyph or label.

**Forms.** A placeholder is an example, never the only label, so every field keeps a visible label node. Errors render inline beside the field with an icon or text, never a red border alone, and the loading state keeps the button label with a spinner beside it.

## Color (from `better-colors`)

**Match the project's colour system.** Reuse its tokens and notation; oklch is the best default only for a new system, and a colour library produces the same ramp in any notation. On the canvas notation is irrelevant because Figma stores RGB; what is checkable is the ramp's properties below and the token binding.

**A system is ramps, not colours.** One neutral ramp, one accent ramp, and only the status ramps the product actually renders. A second accent earns its place only when two things must be distinguishable at a glance. Neutrals carry the most roles and never get fewer steps than the accent. On the canvas: one variable collection per ramp.

**Every step has a job.** Page background 50, subtle background 50, component background 100, hover 200, active 200, subtle border 200. Border 300, strong border and focus ring 400, solid fill 500, solid hover 600, low-contrast text 700, high-contrast text 900. Radix numbers the same roles 1 to 12. Generate no step that no role consumes. On the canvas: one primitive variable per step and one semantic variable per role.

**Hold the hue across the ramp.** Steps are evenly spaced in perceived lightness and hue stays constant end to end (a spread over 10° reads as drift). Vividness peaks mid-ramp, steps sit denser at the light end, and both ends stop short of pure black and white. Use a colour library, never the eye, and measure on the resolved variable values.

**Same relative vividness across hues.** Match each hue to the same proportion of its own maximum chroma and the same perceived lightness per step, so `danger/500` and `brand/500` weigh the same. Status hues stay distinct from the accent: if the brand is red, danger moves to a deeper crimson and the two are checked side by side.

**Name primitives by hue, semantics by role.** `gray/25` or `blue/500` is never bound in a component; `color/bg/primary` aliases it and is the only tier a frame binds. Use a token only in its role (a separator token never becomes a text colour), reserve `accent` for the brand, and let `primary` mean most prominent of its group. On the canvas: two collections, semantics aliasing primitives through `VariableAlias`; this skill's mechanism gives primitives an empty `scopes` array or `hiddenFromPublishing` so the picker offers semantics only.

**One colour, one meaning.** Anything within 15° of hue is the same colour, so if the accent means interactive, no static text wears it and no interactive element goes neutral. On the canvas the accent hue appears only on interactive or selected nodes.

**Fill exactly one action per view.** One filled primary, peers neutral, with the colour on the background rather than the label. Selected states may carry the accent on glyph and label, because state is not emphasis. On the canvas: one instance of the filled button variant per frame.

**Measure the rendered pair, then report.** Contrast is the foreground against the background it actually sits on, the card rather than the page. WCAG AA: 4.5:1 for text under 24 px or under 18.5 px bold, 3:1 at or above those sizes, and 3:1 for UI components and graphics. APCA, preferred for design decisions: Lc 75 body (90 preferred), 60 non-body, 45 large text at 36 px and up, 30 for UI components, placeholder and disabled text. Report a failing pair with its value and the threshold it misses and leave the colours alone unless asked. On the canvas: resolve the bound variable for the mode, then measure; text over an image measures the worst region or gets a scrim.

**Fix contrast by lightness first.** Move the foreground away from the background in perceived lightness, hold hue and saturation, then remeasure. Approximations for body text at Lc 75: a light background above about 90% lightness wants text below about 35%. A dark background below about 25% wants text above about 90%, and the light or dark crossover sits near 73%.

**Derive dark mode from light, then tune.** Reversing the lightness mapping is the starting point, not the output. The accent loses a step or two of vividness, the dark end gets more separation, and every pair is rechecked because contrast is not symmetric. Increased contrast widens the gap by at least 15 points of perceived lightness and remeasures at Lc 90 body and 75 non-body. On the canvas: a `Dark` mode in the semantic collection with re-pointed aliases, measured per pair.

## Writing (from `better-writing`)

**Recon the existing voice** before writing a word. The product has one voice and its existing copy establishes it; a local edit does not invent a new one, and a deliberate brand voice is not a defect.

**Tone flexes with stakes.** Warm for success, onboarding and empty states; neutral for routine actions and settings. Calm, plain and never playful for errors and destructive confirmations; serious and explicit for data loss and security.

**Address the reader as "you".** "We" in an error reads as deflection, so "Unable to load content" beats "We're having trouble loading this content". Possessives sparingly: "Favorites", not "Your Favorites".

**Plain words over clever ones.** Words a tired reader gets on the first pass, every idle word deleted, no idioms or humour that will not translate. Match the input device: "tap" on touch, "click" with a pointer, "select" when both are possible.

**Verb-first buttons.** "Send", "Save draft", "Delete project"; never "OK!", "Let's go!", or a bare "Yes" and "No" on a consequential action. A confirmation button repeats the consequence so the dialog is answerable without reading the body: "Delete this project?" offers Delete project and Cancel.

**One vocabulary per flow.** "Get started" to enter, "Continue" or "Next" (pick one) to advance, "Done" to finish. "Archive" in the menu is "Archive" in the toast.

**Links describe their destination.** "Read the billing docs", never "click here", and a bare "Learn more" breaks as soon as two appear on one page: "Learn more about exports".

**One capitalization policy.** Title case or sentence case per element type, applied to every instance of that type; sentence case is the safer default because it localizes cleanly. On the canvas copy is stored in sentence case with `textCase: "ORIGINAL"`.

**Settings describe the ON state.** "Send read receipts" lets the user infer the off state; the negative turns the toggle into a double negative. Link straight to a referenced setting rather than describing the path to it.

**Errors say how to fix, next to where it broke.** "Choose a password with at least 8 characters", not "That password is too short"; no blame, no "oops", no exclamation marks. Hints are phrased positively ("Use only letters") and shown before the mistake.

**Empty states point forward.** What this place is, how to fill it, and one clear next action. A search or filter empty state names the query and offers an exit ("No results for 'quarterly'. Clear filters"). On the canvas: a title, one line and one button, never persistent information that disappears when content exists.

**Placeholders are examples, not labels.** `name@example.com`, `DD/MM/YYYY`; the placeholder vanishes on input, so the field keeps a visible label node.

## Reading a live interface (from `explain-interface`)

**Tokens first.** A page that exposes custom properties on its root has already told you most of the answer. Group them by prefix; the prefixes are the system's own layer names, and a two-tier structure such as `--blue-500` feeding `--color-text-primary` is the semantic seam.

**A fingerprint is not a fact.** Report each detection with its evidence, and treat a false as a fingerprint that did not fire, not as an absence.

**Read a second state.** One width and one theme is one state. Resize to 375, toggle the theme, tab to the first control, and note what changed; the probes themselves are in [grounding.md](grounding.md).

## How these apply to the review loop

The fidelity reviewer checks the rules that reduce to a number and cites the source value beside the observed one. The vision reviewer checks the ones that need judgment against the brief and the user's own words. Neither reviewer invents a rule that is not here or in the brief; a preference is not a finding. The split is spelled out below so a brief can name exactly what each reviewer runs.

## Measurable checks

### Fidelity reviewer: rules a script can verify

Each row is a number or a property a `use_figma` read-only script or a computed-style probe can return. The source column is the value to cite.

| Check | Pass condition | Canvas property read |
| --- | --- | --- |
| Gap ratio | Outer `itemSpacing` at least 2x the inner on every nested group | `itemSpacing`, `counterAxisSpacing` per frame |
| Control clearance | 12 or more between bordered controls, 24 or more around borderless ones, 24 or more between groups | `itemSpacing` on control rows |
| Spacing step | Every padding and gap sits on the project's scale (4, 8, 12, 16, 24, 32, 48, 64 by default); 16 is the indent step per level of subordination | `paddingTop/Right/Bottom/Left`, `itemSpacing` |
| On-grid | Every content edge within 1 px of a column edge | `layoutGrids`, `absoluteBoundingBox` |
| Leading by role | Display 110%, title 120%, heading 130%, body 150 to 160%, three-plus-line text 140% or more, no `AUTO` on display | `lineHeight.unit`, `lineHeight.value`, `height` divided by the line height for the line count |
| Tracking by size | Display -2%, small uppercase +5%, body 0 | `letterSpacing`, `textCase`, `fontSize` |
| Scale membership | Every `fontSize` is a scale step and every text node binds a role style | `fontSize`, `textStyleId` |
| Weight floors | 400 or heavier below 18 px; under 300 only at 28 px and above; no stroke on text | `fontWeight`, `fontSize`, `strokes` on TEXT |
| Heading order | Heading size descends with nesting depth and never falls below body | `fontSize` by depth |
| Size floors | Body 16, UI 14, captions 13, nothing below 12 without a note | `fontSize` |
| Measure | Body nodes 60 to 75 characters per line, about 560 to 680 wide at 16 px | node width, `characters`, `fontSize` |
| Tabular numbers | `TNUM` on every timer, counter and price | `openTypeFeatures` |
| Radius concentricity | Outer equals inner plus padding where padding is 24 or less; all four corners | `cornerRadius`, per-corner radii, padding |
| Icon padding | Icon-side padding is text-side minus 2 | `paddingLeft`, `paddingRight` |
| Shadow layers | Three `DROP_SHADOW` layers at 1 / 6%, y1 b2 s-1 / 6%, y2 b4 / 4%; dark one white ring at 8% | `effects[].offset`, `radius`, `spread`, `color.a` |
| Border purpose | Dividers, cells, inputs and selected states keep a stroke; depth-only strokes are absent | `strokes` vs `effects` per surface |
| Image outline | 1 px inside stroke, pure black or white, alpha 0.10, on every image fill | `strokes`, `strokeAlign`, `strokeWeight`, fill type IMAGE |
| Icon stroke | 1.5 / 2 / 2.5 against label weight 400 / 500 to 600 / 700; icons at 16, 20 or 24 | icon `strokeWeight`, sibling text `fontName.style`, width |
| Hit area | Target frame 44 on touch, 40 on desktop, never under 24, and no two targets intersect | `absoluteBoundingBox` on interactive components |
| Focus state | Every control component has a Focus variant with a 2 px ring | variant names, wrapper `strokes` |
| Press state | Pressed variant at 96% scale | variant size ratio or reaction target |
| Motion values | Enter 0.3 s, exit 0.15 s, ease-out; icon swap 0.3 s with cubic-bezier(0.2, 0, 0, 1); high-frequency 0.15 s or less | `reactions[].actions[].transition.duration`, `easing` |
| Contrast | 4.5:1 or 3:1 per WCAG size class, Lc 75 / 60 / 45 / 30 per APCA class, against the nearest painted ancestor, per mode | resolved variable values, `fills` |
| Lightness gap | Text below about 35% on backgrounds above 90%, above about 90% on backgrounds below 25% | resolved values per mode |
| Token binding | Every fill, stroke, gap, radius and text style binds a semantic variable or style; no primitive bound directly | `boundVariables`, collection of the bound variable |
| Ramp shape | Even perceived-lightness steps, hue spread 10° or less, vividness peaking mid-ramp, ends short of 0 and 1 | primitive collection values |
| Status hue | Every status solid step differs from the accent solid step by more than 15° of hue | primitive values |
| Accent scope | Accent hue only on interactive or selected nodes; one filled primary per frame | `fills` hue, component names |
| Case storage | `characters` in sentence case, uppercase only through `textCase` | `characters`, `textCase` |
| Truncation | `maxLines` nodes have a reachable full-value state | `textTruncation`, `maxLines`, variants |
| Text alignment | No `JUSTIFIED` in interface text | `textAlignHorizontal` |

### Vision reviewer: rules that need judgment

- Importance order: the most important thing first, the first screen a table of contents, the key number not buried.
- One primary action per view, secondaries demoted, and nothing prominent that is not primary.
- Controls read as controls and content as content; no dead-click badges.
- Voice: one voice across the frame and tone matched to the stakes. Verb-first buttons, destination-describing links, one vocabulary per flow, sentence case, errors that say how to fix, empty states that point forward.
- Density and mood against the brief: whether the whitespace, ramp and type personality are what the user asked for.
- Restraint: separators only where space could not carry the grouping, staged motion only on infrequent moments, no ornament the brief refuses, colour used for one meaning only.
- Hidden content has a visible cue and nothing critical sits where a resize or scroll clips it.
- The RTL mirror, when the product ships to RTL locales: sequence, alignment and which icons flip.
