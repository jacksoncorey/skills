# Design craft canon

The operational layer over [design-principles.md](design-principles.md). This file says what to set, in build order, on a Figma canvas, citing rules there by heading. Grid recipes, naming patterns and check scripts live in [designing-in-figma.md](designing-in-figma.md).

## Precedence

1. The product's own system: its library, variables, text styles and components.
2. The target file's conventions: grid, naming, ramp and components.
3. The brief written during grounding.
4. This canon.

The canon fills gaps and never overrides a token, style or component that exists above it. A value marked "default" is this skill's starting point, not a source rule; record each one used in the brief.

## 1. Frame and grid

- Create the wrapper with `layoutMode: "VERTICAL"` and `layoutGrids` in the same call. Set `paddingLeft` and `paddingRight` to the grid margin.
- Take columns, margin and gutter from the grid recipes: 12 columns at desktop, 6 at tablet and below. An existing grid in the file wins.
- Set sections to `layoutSizingHorizontal: "FILL"` and the wrapper's `itemSpacing` to 0.
- Put every content edge within 1 px of a column line. The on-grid script is the pass condition.
- One frame per breakpoint, named for the width the content broke at ("Hold structure until it breaks").
- Name every node in the call that creates it. `Frame 427` is a defect. `clipsContent: true` only on scroll regions.

## 2. Section rhythm and spacing scale

- One spacing step, default scale 4, 8, 12, 16, 24, 32, 48, 64, 96, 128, for every padding, `itemSpacing` and `counterAxisSpacing`.
- Set the outer `itemSpacing` to at least 2x the inner on every nested group: 8 inside, 16 or more between. See "Group with space, not lines".
- Set `itemSpacing` 12 between bordered or filled controls, 24 around borderless ones, 24 or more between unrelated groups.
- Indent one step per level of subordination, 16 by default, as `paddingLeft`.
- Draw a separator only in tables and long settings lists: 1 px at 8 percent of the text colour (default), never beside a gap.
- Let 16 to 32 px of the next item show past a scroller's `clipsContent` edge.
- Full-width actions stay inside the margins: 16 horizontal padding on mobile, visible `cornerRadius`.
- Set text and buttons to `layoutSizingHorizontal: "HUG"`. Body copy gets `textAutoResize: "HEIGHT"` at a fixed width. Never a fixed height on text.

## 3. Type ramp and hierarchy

Role scale when the brief supplies none; the overline row and title tracking are defaults.

| Role | `fontSize` | `lineHeight` PERCENT | Weight | `letterSpacing` PERCENT |
| --- | --- | --- | --- | --- |
| Display | 36 | 110 | 600 | -2 |
| Title | 24 | 120 | 600 | -1 (default) |
| Heading | 18 | 130 | 600 | 0 |
| Body | 16 | 150 | 400 | 0 |
| Caption | 13 | 140 | 400 | 0 |
| Overline (default) | 12 | 140 | 500 | +5, `textCase: "UPPER"` |
| Hero (marketing, default) | 64 | 110 | 600 | -2 |
| Lead (marketing, default) | 20 | 150 | 400 | 0 |
| Price (marketing, default) | 48 | 110 | 600 | -1, TNUM |

- Bind every text node to a role style through `textStyleId`, and bind last: setting `fontSize`, `letterSpacing`, `lineHeight` or `textCase` afterwards detaches it silently.
- Emphasis within a role is one weight step up, never a size change.
- Never leave `lineHeight` at `AUTO` on display or title. Text that wraps to three or more lines gets 140 or more.
- Weight floors: 400 or heavier below 18 px, under 300 only at 28 px and above, never a stroke on text.
- Size floors: body 16, inputs and menus 14, captions 13, nothing below 12 without a note; inputs 16 on mobile frames.
- Cap the measure: body nodes 560 to 680 wide at 16 px, 640 by default.
- Balance a headline by resizing the node, never by shrinking `fontSize`. Labels get `textAutoResize: "WIDTH_AND_HEIGHT"`.
- Store copy in sentence case with `textCase: "ORIGINAL"`. Uppercase only through `textCase: "UPPER"`.
- Set TNUM on every timer, counter and price; the API only reads `openTypeFeatures`, so a person sets it.
- Truncate with `textTruncation: "ENDING"` and `maxLines`. Never `textAlignHorizontal: "JUSTIFIED"`; numeric columns align `RIGHT`.
- Above 48 px, fix a bad pair with `setRangeLetterSpacing` on that segment only.

## 4. Color and tokens

- One neutral ramp, one accent ramp, only the status ramps the product renders. See "A system is ramps, not colours".
- Step roles per "Every step has a job": background 50, component 100, hover 200, border 300, focus ring 400, solid 500, solid hover 600, low-contrast text 700, high-contrast text 900.
- Bind only semantic variables, through `boundVariables` on `fills`, `strokes`, `itemSpacing` and `cornerRadius`. Never a hex where a token exists.
- Put the accent hue only on interactive or selected nodes. Fill exactly one action per view, colour on the background rather than the label.
- Keep every status solid more than 15 degrees of hue from the accent; every status variant carries a glyph or label beside the colour.
- Measure contrast against the nearest painted ancestor, per mode, on resolved values. WCAG AA: 4.5:1 below 24 px or 18.5 px bold, 3:1 above that and for UI components.
- APCA: Lc 75 body (90 preferred), Lc 60 non-body, Lc 45 large text at 36 px and up, Lc 30 for UI, placeholder and disabled text.
- Fix a failing pair by lightness, hold hue, remeasure, using the gap approximations under "Fix contrast by lightness first". Report before repainting.
- Dark mode is a `Dark` mode with re-pointed aliases: accent one or two steps less vivid, every pair remeasured.
- Ramp hue spread stays at 10 degrees or less. Text over an image measures the worst region or gets a scrim.

## 5. Surfaces

- Concentric radius: outer `cornerRadius` equals inner plus padding whenever padding is 24 or less, on all four corners. Above 24, choose independently.
- `cornerSmoothing`: match the file. Default 0; where the system uses continuous corners, 0.6 on every rounded node (default).
- Depth is a shadow, structure is a stroke: dividers, cells, input outlines, selected and focus states keep `strokes`; nothing else does.
- Light elevation is three `DROP_SHADOW` `effects`, all `#000000`. Layer 1: offset 0/0, radius 0, spread 1, alpha 0.06. Layer 2: offset 0/1, radius 2, spread -1, alpha 0.06. Layer 3: offset 0/2, radius 4, spread 0, alpha 0.04. Hover: 0.08, 0.08, 0.06.
- Dark elevation is one ring: offset 0/0, radius 0, spread 1, `#FFFFFF` alpha 0.08, hover 0.13.
- Every image fill and placeholder frame: `strokes` `#000000` alpha 0.10, `strokeWeight` 1, `strokeAlign: "INSIDE"`; `#FFFFFF` at 0.10 in dark. Never tinted, never the accent.
- Focus variant per control: a 2 px `OUTSIDE` stroke in the focus token on a wrapper padded by 2.
- Media bleeds to the frame edge; text and controls stay inside the margins.

## 6. Controls and hit areas

- The component frame is the target: 44 by 44 on touch, 40 on desktop, never under 24. Neighbouring `absoluteBoundingBox` values never intersect.
- Button sizes (default): heights 32, 40, 48; horizontal padding 12, 16, 20; `itemSpacing` 8 between icon and label.
- Icon-side padding is the text side minus 2: `paddingRight` 14 beside `paddingLeft` 16 with a trailing icon.
- Every control reads as a control: fill, stroke, underline or a control zone; a static badge never borrows the button.
- Variants per control: Default, Hover, Focus, Pressed at 96 percent, Disabled, Loading with the label kept beside a spinner. States differ by a fill or glyph, never by motion alone.
- Forms: a visible label node above every field, errors inline with an icon or text, submit never disabled.
- A destructive action gets a confirmation; secondary actions go behind an overflow menu past three.

## 7. Iconography

- One library per surface on its native grid of 16, 20 or 24, never an arbitrary scale; inline icons at 1 to 1.25 em.
- `strokeWeight` follows the label's weight: 1.5 beside 400, 2 beside 500 to 600, 2.5 beside 700.
- Bind icon fills to the text-colour token; states come from colour and opacity (disabled 0.4). Outline default, fill active.
- Optical nudges: the play glyph shifts 2 px right. Fix asymmetric glyphs in the vector, otherwise offset 1 px.
- Every icon-only control carries its accessible name in the layer name or a note.

## 8. Motion and prototype transitions

Set these on `reactions[].actions[].transition`; blur goes in the handoff, since prototypes do not interpolate it.

- Enter: y 12 to 0, opacity 0 to 1, blur 4 to 0, 300 ms ease-out. Canvas: `type: "SMART_ANIMATE"`, `duration: 0.3`, `easing: { type: "EASE_OUT" }`.
- Exit: y to -12, opacity to 0, blur to 4, 150 ms ease-out. `duration: 0.15`.
- Stagger chunks 100 ms apart, words 80 ms, only on infrequent entrances (first load, success, empty state), never on hovers or tab changes.
- Press: the Pressed variant at scale 0.96, never below 0.95, `duration: 0.15`.
- Icon swap: scale 0.25 to 1, opacity 0 to 1, blur 4 to 0, spring 0.3 s with bounce 0. Canvas: `easing: { type: "CUSTOM_CUBIC_BEZIER", easingFunctionCubicBezier: { x1: 0.2, y1: 0, x2: 0, y2: 1 } }`, `duration: 0.3`, both icons in the component.
- High-frequency interactions: instant, or 150 ms or less on opacity and colour.
- Every animated state change also has a static cue (colour, glyph or label).
- Under reduced motion, only opacity crossfades. Nothing autoplays without a pause control.

## 9. Copy

- Sentence case on every element type, stored in `characters` as written.
- Buttons start with a verb: "Save draft", "Delete project". Never "OK!", "Let's go", or a bare "Yes" and "No". A confirmation button repeats the consequence.
- One vocabulary per flow: "Get started", then "Continue" or "Next", then "Done".
- Links name their destination: "Read the billing docs", never "click here".
- Errors say how to fix, beside the field that failed, no blame, no exclamation marks.
- Empty states carry a title, one line and one button. Placeholders are examples. Settings labels describe the on state.
- Write "you", never "the user"; keep "we" out of errors; calm for errors, warm only for success.
- Never invent a claim, metric, logo or testimonial; copy from the product's sources or use a named placeholder.

## Marketing page defaults

All defaults for a landing page; the brief and the file overrule any row.

- Grid: 1440 wide, 12 columns, margin 80, gutter 24, content 1280 for feature grids, logo rows and bleeds; hero copy and section headers hold to 10 columns (about 1063, 74 percent).
- Button shape: rounded rectangle at 8 unless the brief or the site says pill; one shape per page, never mixed.
- Section rhythm: `paddingTop` and `paddingBottom` 128 at desktop, 96 at tablet, 64 at mobile (the reference brands pad 86 to 130 at 1440). Header block to content 48. Cards 24 apart.
- Nav: 64 high, logo leading, links at 16, "Log in" as text beside one filled CTA 40 high that repeats the hero's label; a nav CTA carrying the hero's label is the same action, not a second one.
- Hero: 720 high at 1440, never under 640 (a default, not measured). Headline 64 / 110 / 600 / -2, one to three lines, two is the mode. Subhead 20 / 150 / 400 at 560 wide or less. One filled CTA 48 high; a quieter second only when the brief names a second action. Centred headline, subhead and CTA, with media below at 10 columns or full bleed; a 1 to 6 / 7 to 12 split only when copy is dense or the product bleeds right.
- Logo strip: an overline label, one row of 5 to 8 logos at 24 to 32 tall, gap 48, neutral at 0.6 opacity.
- Section header: overline, title 36 / 110 / 600 / -2 at most two lines, lead 18 / 150 at 640 wide or less.
- Feature grid: three text columns spanning 4 each (two at 6, four at 3, never 5), each an icon, a title and a two to four line caption, split by space or a hairline, no card surface. A card (`cornerRadius` 16, padding 32) only when it holds media or a chart.
- Pricing: 3 cards at 4 columns, padding 32, radius 16. Plan name 18, price 48 / 110 / 600 with TNUM. Feature rows 16 at gap 12. CTA 48 high, full width. The recommended plan carries the only filled CTA and a 1 px accent-400 stroke as its selected state, never a larger card.
- Closing CTA: the last section before the footer, padding 96, a title and one filled button with the hero's label.
- Footer: `paddingTop` 64, `paddingBottom` 40. Brand column spanning 4, four link columns at 2 each, caption 13 at gap 12. Legal row below a 1 px separator at 8 percent.
- Media frames 16:10, real imagery through `upload_assets`, otherwise a named placeholder.

## 10. The composition pass

Take a 2x screenshot of the frame by id and read it as a page.

- Alignment: every content edge on a column line, no icon 2 px off its text.
- Rhythm: equal section gaps, group gaps at 2x the inner, nothing tighter than 12 between controls.
- One primary: exactly one filled button in the screenful, peers neutral, the accent nowhere static.
- Contrast: every text pair measured per mode, worst region over images.
- Widows: no short word alone on a last line, headlines balanced, labels unbroken.
- Clipping: no text cut by `clipsContent`, no critical action at a scroll or resize edge, no leftover placeholder.
- Then run the naming, hardcoded-value and font-family checks and read bindings back.

## Craft self-check

Answer each from a screenshot or a dump; a "no" is a fix.

| # | Question | Directive |
| --- | --- | --- |
| 1 | Every content edge within 1 px of a column line? | 1, on-grid |
| 2 | Every padding and gap on the scale, outer gaps 2x inner, controls 12 or 24 apart? | 2, rhythm |
| 3 | Every text node bound to a role style, bound last, read back? | 3, `textStyleId` |
| 4 | `lineHeight` explicit on display and title, 140 or more on three lines? | 3, leading |
| 5 | Body 560 to 680 wide, nothing below 12, TNUM on changing numbers? | 3, measure |
| 6 | Every fill, stroke, gap and radius bound to a semantic variable? | 4, tokens |
| 7 | Accent only on interactive nodes, one filled action per view? | 4, accent |
| 8 | Every text pair measured against its painted ancestor, per mode? | 4, contrast |
| 9 | Every nested radius equal to outer minus padding where padding is 24 or less? | 5, radius |
| 10 | Depth-only strokes gone, three shadow layers in their place? | 5, elevation |
| 11 | Every image carrying the 1 px inside outline at 0.10? | 5, outline |
| 12 | Every target 44 touch or 40 desktop, none intersecting? | 6, hit area |
| 13 | Every control with Hover, Focus, Pressed, Disabled, Loading and a static cue? | 6, variants |
| 14 | Icon `strokeWeight` matching label weight on a 16, 20 or 24 grid? | 7, stroke |
| 15 | Transitions 0.3 s in, 0.15 s out, staggered only on infrequent entrances? | 8, motion |
| 16 | Buttons verb-first, sentence case, no invented claim? | 9, copy |
| 17 | One primary, no widow, no clipped text, no `Frame 427` in the 2x screenshot? | 10, composition |
