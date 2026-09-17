# Designing in Figma

What a designer does on a canvas that an agent left to itself does not: grids, naming, hierarchy and the checks that prove them. The build sequence itself is `figma-generate-design` Steps 3 to 5 and is not restated here. Wrapper first, placeholder sections, one section per call, screenshots by id, bindings over hex, font family asserted. `figma-use` is loaded first and its rules on incremental calls, font loading, `return` values and page switching apply to every script below.

## Where these steps sit in the sequence

| `figma-generate-design` step | What this skill adds there |
| --- | --- |
| Step 1, understand the deliverable | The brief already holds the sections, the ramp and the grid. Read it instead of re-deriving |
| Step 2, collect keys, variables, styles | Also measure the file's own grid with the subtree dump; an existing grid wins over the recipe below |
| Step 3, wrapper frame | Put the column grid on the wrapper in the same call, and name it |
| Step 4, each section | Name every node in the creating call; set leading and tracking from the ramp; screenshot the section by id and look at it before starting the next one; run the check scripts below after every two or three sections (the fidelity reviewer is a separate pass) |
| Step 5, validate | Run all five checks, then a 2x composition screenshot read as a page |
| Step 6, update an existing view | Read the existing grid and names first and match them; the naming and on-grid checks run only on nodes you added |

## Grid recipes

Defaults for an empty file. Where the file already has screens, read their `layoutGrids` and match them.

| Frame width | Columns | Margin | Gutter | Content width |
| --- | --- | --- | --- | --- |
| 1440 desktop | 12 | 80 | 24 | 1280 |
| 1520 desktop | 12 | 120 | 24 | 1280 |
| 1024 tablet | 6 | 48 | 24 | 928 |
| 768 tablet | 6 | 32 | 16 | 704 |
| 375 mobile | 6 (4 only where the file already uses one) | 20 | 16 | 335 |

Apply it in the call that creates the wrapper:

```js
frame.layoutGrids = [{
  pattern: "COLUMNS", alignment: "STRETCH", count: 12, gutterSize: 24, offset: 80,
  visible: true, color: { r: 1, g: 0, b: 0, a: 0.08 },
}];
```

Column math for `STRETCH`: `columnWidth = (frameWidth - 2 * offset - (count - 1) * gutter) / count`. Column `i` starts at `offset + i * (columnWidth + gutter)`. A section's inner content aligns its left edge to a column start and its right edge to a column end. The on-grid script checks every text and shape edge against those lines. Set the wrapper's horizontal padding to the margin so auto-layout does the alignment rather than absolute x values.

## Naming

Names are how the next person, or the next agent, finds anything. The vocabulary is the product's, and the structure mirrors the hierarchy:

| Node | Pattern | Example |
| --- | --- | --- |
| Screen wrapper | `<Screen> / <Breakpoint>` | `Homepage / Desktop` |
| Section | `<Section>` | `Hero`, `Logos`, `Pricing`, `Footer` |
| Group inside a section | `<Section> / <Part>` | `Hero / Copy`, `Hero / Media` |
| Element | `<Section> / <Part> / <Role>` | `Hero / Copy / Headline`, `Pricing / Card / Plus` |
| Local component | `<Component>` with variants `Property=Value` | `Card`, `Size=Large, Tone=Muted` |
| Figma section grouping frames | The flow or milestone | `Homepage v2`, `Onboarding / Step 1–3` |

Rename in the same call that creates the node, so a failed call never leaves `Frame 427` behind.

## Hierarchy from the ramp

The brief's type ramp supplies role, family, size, weight, line-height and tracking. On the canvas that means:

- `lineHeight` is `{ unit: "PERCENT", value: 110 }` for display and `150` to `160` for body, or `{ unit: "PIXELS", value: n }` when the ramp gives pixels. Never leave `AUTO` on display text, because auto leading is the font's own metric and differs per family.
- `letterSpacing` is `{ unit: "PERCENT", value: -2 }` on large display, `+5` on small uppercase labels, `0` on body.
- Paragraph width: a body text node with `textAutoResize = "HEIGHT"` and a fixed width that keeps the measure at or under 75 characters at that size. Around 640 for 16 px body in most sans faces.
- Balance headlines by resizing the node until the lines even out, or with a line break where the ramp permits, never by shrinking the size.
- Kerning is on by default and stays on. If the brand family is not in `listAvailableFontsAsync`, pick the nearest available family and record it as an accepted exception; never fall back to Inter unasked. Above about 48 px, look at the pairs a face kerns badly (`AV`, `To`, `r.`, `Yo`) in the 2x screenshot. Fix them with `setRangeLetterSpacing` on that segment, not on the whole line.
- Bind text to the library's text styles with `setTextStyleIdAsync`. Load the style's own font first, since the style's font is what gets written:

```js
const [title, style] = await Promise.all([figma.getNodeByIdAsync("TEXT_ID"), figma.importStyleByKeyAsync("TEXT_STYLE_KEY")]);
if (!title || title.type !== "TEXT" || !style) return { error: "text node or style not found" };
if (style.type === "TEXT") await figma.loadFontAsync(style.fontName);
await title.setTextStyleIdAsync(style.id);
return { mutatedNodeIds: [title.id] };
```

Bind the text style last. Setting `textCase`, `fontSize`, `letterSpacing` or `lineHeight` after `setTextStyleIdAsync` detaches the style silently; the Opus eval run lost all ten mono bindings this way and reported them as bound. Read `textStyleId` back after the last write before claiming it.

Library variables come from `search_design_system` and `importVariableByKeyAsync`, or from `boundVariables` on existing screens where `remote` is true. An empty local variable list never means the file has no tokens. When the target file has no library at all, create local text styles and color and spacing variables from the brief's atomic tables before the wrapper; `figma-generate-library` owns the how. Then bind to those, and the hardcoded-values check applies in full.

## Checks

Read-only `use_figma` calls. Each returns a list of offenders, and an empty list is the pass condition. They are for nodes this skill created; on an audit of the user's own frame they describe the designer's habits, not defects.

### On-grid measurement

Reports every visible text or shape whose left or right edge is more than `TOLERANCE` px from a column edge. Full-bleed backgrounds, as wide as the frame, are skipped; content-width containers are not, because a drifted section container is exactly the error that matters.

```js
const ROOT_ID = "WRAPPER_ID", TOLERANCE = 1;
const root = await figma.getNodeByIdAsync(ROOT_ID);
if (!root) return { error: "wrapper not found" };
if (!("layoutGrids" in root)) return { error: "wrapper has no layoutGrids property (type " + root.type + ")" };
const g = root.layoutGrids.find(x => x.pattern === "COLUMNS");
if (!g) return { error: "no column grid on wrapper" };
const colW = (root.width - 2 * g.offset - (g.count - 1) * g.gutterSize) / g.count;
const edges = [];
for (let i = 0; i < g.count; i++) { const s = g.offset + i * (colW + g.gutterSize); edges.push(s, s + colW); }
const near = v => edges.some(e => Math.abs(e - v) <= TOLERANCE);
const off = [];
for (const n of root.findAllWithCriteria({ types: ["TEXT", "RECTANGLE", "FRAME", "INSTANCE"] })) {
  if (!n.visible || n.width >= root.width - 1) continue;
  if (n.id.startsWith("I")) continue; // nodes inside instances repeat their parent's row
  const bb = n.absoluteBoundingBox; if (!bb || !root.absoluteBoundingBox) continue;
  const left = bb.x - root.absoluteBoundingBox.x;
  const right = left + n.width;
  if (!near(left) && !near(right)) off.push({ id: n.id, name: n.name.slice(0, 60), left: Math.round(left), right: Math.round(right) });
}
return { columnWidth: colW, edges: edges.map(Math.round), offGrid: off.slice(0, 60), offGridCount: off.length };
```

Nested elements legitimately sit inside a card's padding rather than on a column edge, so read the list rather than treating the count as a score.

### Naming audit

```js
const root = await figma.getNodeByIdAsync("WRAPPER_ID"); if (!root) return { error: "wrapper not found" };
const bad = /^(Frame|Rectangle|Ellipse|Group|Text|Line|Vector|Union|Image|Component)\s*\d*$/;
return root.findAll(n => bad.test(n.name)).map(n => ({ id: n.id, name: n.name, type: n.type, parent: n.parent?.name }));
```

### Hardcoded values where a token exists

Lists fills, strokes and gaps with no bound variable, and text with no style or a mixed one. Where the brief says the system has tokens for these, every row is a defect.

```js
const root = await figma.getNodeByIdAsync("WRAPPER_ID"); if (!root) return { error: "wrapper not found" };
const byNode = new Map();
const add = (n, what) => { if (!byNode.has(n.id)) byNode.set(n.id, { id: n.id, name: n.name.slice(0, 60), what: [] }); byNode.get(n.id).what.push(what); };
for (const n of root.findAll(n => n.visible)) {
  const b = n.boundVariables ?? {};
  if ("fills" in n && Array.isArray(n.fills) && n.fills.some(f => f.type === "SOLID" && f.visible !== false) && !b.fills) add(n, "fill");
  if ("strokes" in n && n.strokes?.length && !b.strokes) add(n, "stroke");
  if ("itemSpacing" in n && n.layoutMode !== "NONE" && n.itemSpacing && !b.itemSpacing) add(n, "gap");
  if (n.type === "TEXT" && (!n.textStyleId || n.textStyleId === figma.mixed)) add(n, "text style");
}
const items = [...byNode.values()];
return { count: items.length, items: items.slice(0, 80) };
```

### Font family assertion

```js
const root = await figma.getNodeByIdAsync("WRAPPER_ID"); if (!root) return { error: "wrapper not found" };
const ALLOWED = ["Brand Grotesk"]; // from the brief's type ramp only; never add a fallback family here
const fams = new Map();
for (const t of root.findAllWithCriteria({ types: ["TEXT"] })) for (const s of t.getStyledTextSegments(["fontName"])) fams.set(s.fontName.family, (fams.get(s.fontName.family) ?? 0) + 1);
return { families: [...fams], offenders: [...fams.keys()].filter(f => !ALLOWED.includes(f)) };
```

### Leftover placeholders

```js
const root = await figma.getNodeByIdAsync("WRAPPER_ID"); if (!root) return { error: "wrapper not found" };
return root.findAll(n => n.placeholder === true).map(n => ({ id: n.id, name: n.name }));
```

## Sections and pages

Group related screens in a Figma section so the canvas reads as a flow. Sections do not resize to fit what you append, and an appended node keeps its old coordinates. Position and resize explicitly:

```js
const wrapper = await figma.getNodeByIdAsync("WRAPPER_ID"); if (!wrapper) return { error: "wrapper not found" };
const s = figma.createSection(); s.name = "Homepage v2";
s.x = wrapper.x - 80; s.y = wrapper.y - 80;
s.appendChild(wrapper); wrapper.x = 80; wrapper.y = 80;
s.resizeWithoutConstraints(wrapper.width + 160, wrapper.height + 160);
return { createdNodeIds: [s.id], mutatedNodeIds: [wrapper.id] };
```

New pages for new work, named for the milestone, and never a new top-level frame dropped at `(0, 0)` over someone else's.

## Images

A script cannot fetch external images, and its `return` cannot carry bytes. The supported path is `upload_assets`: local files, browser screenshots, or images pulled from another file with `download_assets`. Pass `nodeIds` so raster images become fills directly; SVGs land as vector trees instead. Only the product's own imagery goes in, and a cross-brand reference's images never do. Where the server exposes `generate_figma_design` and the source is a rendered web page, its capture also yields `imageHash` values to reuse. Only when neither is possible does a section get a named placeholder frame: neutral fill, a 10 percent black inset stroke, the exact aspect ratio. The report then says which images are placeholders.
