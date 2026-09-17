# Node inspection

What each Figma MCP tool answers, what it hides, the full checklist of properties a node can carry, and read-only `use_figma` scripts that surface the rest. Load `figma-use` before running any script here; its rules on `return`, page switching and property guards apply. Its preferred idioms, `node.query()` and `findAllWithCriteria`, are used where a type filter is enough; `findAll` appears only where a predicate over every node is needed.

## Which tool answers which question

| Question | Tool | Notes |
| --- | --- | --- |
| What pages exist | `get_metadata` with no node id, or the page-listing script | Both servers. On desktop, clear the selection first or the selected node's tree comes back instead. The remote tool has returned only the first page on a real 22-page file; the script is the reliable path |
| What is on this page or inside this node | `get_metadata` with the id | Ids, types, names, x, y, width, height. No styling |
| What does it look like | `get_screenshot` | Remote: set `maxDimension` to at least the node's native long edge (default 1024, a downscale cap that never upscales) and download the returned URL. Desktop: no size parameter; capture from the browser at 2x where the tooling allows. In a script: `await node.screenshot({ scale: 2 })` |
| What are the exact values for this unit | `get_design_context` | Per focus unit, after loading `figma-design-to-code`. Large nodes fall back to sparse metadata and need child requests |
| Which tokens does this unit bind | `get_variable_defs` | Name to value. Modes are not shown |
| Which codebase component maps to this node | `get_code_connect_map` | Remote only. Empty where Code Connect was never set up |
| Which library components, variables, styles exist | `get_libraries`, then `search_design_system` | Page `get_libraries` with `offset` until the next offset is null. Search with `queries: [{ entity: "component" \| "variable" \| "style", query }]`, one intent per entry, scoped with `includeLibraryKeys` |
| Image bytes | Asset URLs in the `get_design_context` response, then `download_assets` | URLs expire in about a week. `exportAsync` plus `figma.io.write` is the last resort, since a script's `return` is JSON and cannot carry raw bytes |
| Anything else | `use_figma` read-only | Scripts below. Every call needs `fileKey`, `code` and `description`, and passes `skillNames: "figma-use"`, prefixed `resource:` when the skill was read through `get_figma_skill` |

## What `get_design_context` hides

Each of these has bitten a real implementation. Check them explicitly when the task touches them.

| Hidden | Why it matters | Where to get it |
| --- | --- | --- |
| Hidden layers (`visible: false`) and hidden fills | Designers park alternates and states as hidden layers; a hidden image fill is a swapped photo | Hidden-layers script below |
| Layout grids on frames | The column system the design was built on | `node.layoutGrids` |
| Per-corner radius and corner smoothing | A 20 radius with 60 percent smoothing is a squircle, not a rounded rectangle | `topLeftRadius` and siblings, `cornerSmoothing` |
| Prototype reactions | Which element navigates where, with which transition | `node.reactions` |
| Variable modes | Light and dark, or brand A and B, resolve differently | `(await figma.variables.getVariableByIdAsync(id)).valuesByMode` and the collection's `modes` |
| Styled text segments | One text node can carry two weights or a highlighted word | `getStyledTextSegments([...])` |
| Component property definitions | Which text, boolean and swap props an instance exposes | On the `COMPONENT_SET`, or a non-variant `COMPONENT`. Never on a variant |
| Constraints and absolute positioning | How a child behaves when the parent resizes | `constraints`, `layoutPositioning` |
| Min and max sizes on auto-layout children | Why a column stops growing | `minWidth`, `maxWidth`, `minHeight`, `maxHeight` |
| Effects with layer order and spread | Multi-layer shadows a single CSS shadow cannot reproduce | `effects` |
| Blend modes, masks, clipping | A screenshot shows the result but not the mechanism | `blendMode`, `isMask`, `clipsContent` |
| Comments, branches, version history | Design intent and rejected directions | Open the file in a browser |
| Components that live in another file | The library the file subscribes to | `get_libraries`, then import by key |
| Other pages | Foundations, tokens, explorations | Page list, then one read per page in parallel |

## The property checklist

When the coverage auditor asks whether a unit was inspected, this is what "inspected" means. Not every node needs every row, but every row was considered.

- **Identity**: `id`, `name`, `type`, `visible`, `locked`, `opacity`, `blendMode`, `isMask`.
- **Geometry**: `x`, `y`, `width`, `height`, `rotation`, `constraints`, `layoutPositioning`, `minWidth`, `maxWidth`, `minHeight`, `maxHeight`.
- **Auto-layout on the frame**: `layoutMode`, `layoutWrap`, `primaryAxisSizingMode`, `counterAxisSizingMode`, `primaryAxisAlignItems`, `counterAxisAlignItems`, `itemSpacing`, `counterAxisSpacing`, `paddingTop`, `paddingRight`, `paddingBottom`, `paddingLeft`, `clipsContent`, `layoutGrids`.
- **Auto-layout on the child**: `layoutSizingHorizontal`, `layoutSizingVertical`, `layoutGrow`, `layoutAlign`.
- **Surface, paint**: `fills` (type, color, opacity, gradient stops and transform, image hash and scale mode), `strokes`, `strokeWeight` and per-side weights, `strokeAlign`, `dashPattern`.
- **Surface, shape**: `cornerRadius`, per-corner radii, `cornerSmoothing`, `effects` (type, color, offset, radius, spread, visible, blend), `effectStyleId`, `fillStyleId`, `strokeStyleId`.
- **Text, type**: `characters`, `fontName` (family and style), `fontSize`, `fontWeight`, `lineHeight` (unit and value), `letterSpacing` (unit and value), `paragraphSpacing`, `paragraphIndent`, `textCase`, `textDecoration`.
- **Text, box**: `textAlignHorizontal`, `textAlignVertical`, `textAutoResize`, `textTruncation`, `maxLines`, `textStyleId`, and the styled segments where any of those vary within the node.
- **Bindings**: `boundVariables` on every property that supports it, and the variable's collection, modes and code syntax.
- **Components**: on an instance, the main component (`getMainComponentAsync()`), `componentProperties`, `overrides`; on a set, `componentPropertyDefinitions`, variant axes, `defaultVariant`; on either, `description` and `documentationLinks`.
- **Prototype**: `reactions` (trigger, action, destination, transition), `overflowDirection`.
- **Handoff**: `exportSettings`, `annotations`, `devStatus`.

## Read-only scripts

Each returns JSON and mutates nothing. Large responses have come back truncated in practice at around 20 KB, so the dump returns its own length first and defaults to a shallow depth. A depth-2 dump of a 5,500 px tall page frame measured 18.7 KB; wider pages need depth 1 or one dump per section.

### List pages with child counts

```js
return figma.root.children.map(p => ({ id: p.id, name: p.name, children: p.children.length }));
```

### Dump a subtree with the properties that matter

`MAX_DEPTH` 2 for a screen wrapper, 4 for one section, 6 for a single component. The root must be a frame, section, group or component; for a page, iterate `page.children` and dump each.

```js
const ROOT_ID = "1:2"; const MAX_DEPTH = 2; const NAME_LEN = 60;
const root = await figma.getNodeByIdAsync(ROOT_ID);
if (!root) return { error: "no node with id " + ROOT_ID + " on a loaded page" };
if (!("x" in root)) return { error: "root must be a scene node, not a page (type " + root.type + ")" };
const mx = v => v === figma.mixed ? "mixed" : v;
const paint = p => p.type === "SOLID"
  ? { type: p.type, hex: "#" + ["r","g","b"].map(k => Math.round(p.color[k]*255).toString(16).padStart(2,"0")).join(""), opacity: p.opacity ?? 1, visible: p.visible ?? true }
  : { type: p.type, opacity: p.opacity ?? 1, visible: p.visible ?? true, imageHash: p.imageHash, scaleMode: p.scaleMode, stops: p.gradientStops?.length };
const bound = n => n.boundVariables ? Object.keys(n.boundVariables) : [];
const walk = (n, d) => {
  const o = { id: n.id, name: n.name.slice(0, NAME_LEN), type: n.type, visible: n.visible, x: Math.round(n.x), y: Math.round(n.y), w: Math.round(n.width), h: Math.round(n.height) };
  if (n.opacity !== undefined && n.opacity !== 1) o.opacity = n.opacity;
  if ("layoutMode" in n && n.layoutMode !== "NONE") o.layout = { mode: n.layoutMode, wrap: n.layoutWrap, gap: n.itemSpacing, cgap: n.counterAxisSpacing, pad: [n.paddingTop, n.paddingRight, n.paddingBottom, n.paddingLeft], primary: n.primaryAxisAlignItems, counter: n.counterAxisAlignItems, sizing: [n.primaryAxisSizingMode, n.counterAxisSizingMode] };
  if ("layoutSizingHorizontal" in n && n.parent && "layoutMode" in n.parent && n.parent.layoutMode !== "NONE") o.childSizing = [n.layoutSizingHorizontal, n.layoutSizingVertical];
  if ("layoutPositioning" in n && n.layoutPositioning === "ABSOLUTE") o.absolute = true;
  if ("layoutGrids" in n && n.layoutGrids?.length) o.grids = n.layoutGrids.map(g => ({ pattern: g.pattern, count: g.count, gutter: g.gutterSize, offset: g.offset, alignment: g.alignment, section: g.sectionSize }));
  if ("fills" in n && Array.isArray(n.fills) && n.fills.length) o.fills = n.fills.map(paint);
  if ("strokes" in n && n.strokes?.length) o.strokes = { paints: n.strokes.map(paint), weight: mx(n.strokeWeight), align: n.strokeAlign, dash: n.dashPattern };
  if ("cornerRadius" in n && n.cornerRadius !== 0) o.radius = n.cornerRadius === figma.mixed ? [n.topLeftRadius, n.topRightRadius, n.bottomRightRadius, n.bottomLeftRadius] : n.cornerRadius;
  if ("cornerSmoothing" in n && n.cornerSmoothing) o.smoothing = n.cornerSmoothing;
  if ("effects" in n && n.effects?.length) o.effects = n.effects.map(e => ({ type: e.type, visible: e.visible, radius: e.radius, spread: e.spread, offset: e.offset, color: e.color }));
  if ("clipsContent" in n && n.clipsContent) o.clips = true;
  if ("constraints" in n && (n.constraints.horizontal !== "MIN" || n.constraints.vertical !== "MIN")) o.constraints = n.constraints;
  if (n.type === "TEXT") {
    const segs = n.getStyledTextSegments(["fontName","fontSize","lineHeight","letterSpacing","fills","textCase","textDecoration"]);
    o.text = { chars: n.characters.slice(0, NAME_LEN), autoResize: n.textAutoResize, align: n.textAlignHorizontal, truncation: n.textTruncation, maxLines: n.maxLines, styleId: n.textStyleId ? mx(n.textStyleId) : null,
      segments: segs.map(s => ({ family: s.fontName.family, style: s.fontName.style, size: s.fontSize, lh: s.lineHeight, ls: s.letterSpacing, case: s.textCase, deco: s.textDecoration, fill: s.fills?.[0] ? paint(s.fills[0]) : null })) };
  }
  if (n.type === "INSTANCE") o.instance = { props: n.componentProperties ? Object.fromEntries(Object.entries(n.componentProperties).map(([k,v]) => [k, v.value])) : null };
  const b = bound(n); if (b.length) o.bound = b;
  if ("reactions" in n && n.reactions?.length) o.reactions = n.reactions.map(r => ({ trigger: r.trigger?.type, action: r.action?.type ?? r.actions?.[0]?.type, dest: r.action?.destinationId ?? r.actions?.[0]?.destinationId }));
  if ("children" in n && d < MAX_DEPTH) o.children = n.children.map(c => walk(c, d + 1));
  else if ("children" in n) o.childCount = n.children.length;
  return o;
};
const tree = walk(root, 0);
return { jsonLength: JSON.stringify(tree).length, tree };
```

### Hidden layers and hidden fills under a node

```js
const root = await figma.getNodeByIdAsync("1:2"); if (!root) return { error: "node not found" };
const hiddenLayers = root.findAll(n => n.visible === false).map(n => ({ id: n.id, name: n.name, type: n.type, parent: n.parent?.name }));
const hiddenFills = root.findAll(n => "fills" in n && Array.isArray(n.fills) && n.fills.some(f => f.visible === false)).map(n => ({ id: n.id, name: n.name, hidden: n.fills.filter(f => f.visible === false).map(f => f.type) }));
return { hiddenLayers, hiddenFills };
```

### Instances and the main components they point at

Reveals which library the file leans on, and where a component came from another file (`remote: true`).

```js
const root = await figma.getNodeByIdAsync("1:2"); if (!root) return { error: "node not found" };
const out = new Map();
for (const inst of root.findAllWithCriteria({ types: ["INSTANCE"] })) {
  const mc = await inst.getMainComponentAsync(); if (!mc) continue;
  const set = mc.parent?.type === "COMPONENT_SET" ? mc.parent : null;
  const key = set ? set.key : mc.key;
  if (!out.has(key)) out.set(key, { name: set ? set.name : mc.name, key, remote: mc.remote, sample: mc.name, count: 0 });
  out.get(key).count++;
}
return [...out.values()];
```

### Every variable bound under a node, with its collection and modes

```js
const root = await figma.getNodeByIdAsync("1:2"); if (!root) return { error: "node not found" };
const ids = new Set(root.findAll(() => true).flatMap(n => Object.values(n.boundVariables ?? {}).flatMap(b => Array.isArray(b) ? b : [b]).map(b => b?.id).filter(Boolean)));
const out = [];
for (const id of ids) {
  const v = await figma.variables.getVariableByIdAsync(id); if (!v) continue;
  const c = await figma.variables.getVariableCollectionByIdAsync(v.variableCollectionId);
  out.push({ name: v.name, type: v.resolvedType, remote: v.remote, key: v.key, collection: c?.name, modes: c?.modes.map(m => m.name), values: v.valuesByMode, codeSyntax: v.codeSyntax });
}
return out;
```

### Text and effect styles used under a node

```js
const root = await figma.getNodeByIdAsync("1:2"); if (!root) return { error: "node not found" };
const text = new Map(), effect = new Map();
for (const n of root.findAll(() => true)) {
  if ("textStyleId" in n && n.textStyleId && n.textStyleId !== figma.mixed) { const s = await figma.getStyleByIdAsync(n.textStyleId); if (s) text.set(s.id, { name: s.name, key: s.key, remote: s.remote }); }
  if ("effectStyleId" in n && n.effectStyleId) { const s = await figma.getStyleByIdAsync(n.effectStyleId); if (s) effect.set(s.id, { name: s.name, key: s.key, remote: s.remote }); }
}
return { text: [...text.values()], effect: [...effect.values()] };
```

### Component property definitions, safely

```js
const n = await figma.getNodeByIdAsync("1:2"); if (!n) return { error: "node not found" };
const owner = n.type === "COMPONENT_SET" ? n : (n.type === "COMPONENT" && n.parent?.type === "COMPONENT_SET") ? n.parent : n.type === "COMPONENT" ? n : null;
if (!owner) return { error: "not a component or set" };
return { name: owner.name, props: owner.componentPropertyDefinitions, variants: owner.type === "COMPONENT_SET" ? owner.children.map(c => c.name) : null };
```

## Focus units and the coverage ledger

Cut the page into focus units the way a designer would name them: nav, hero, a feature row, a pricing card, the footer. Define each as a node set or a y-range, because a frame named "hero" in the file may not hold everything a designer calls the hero. One `get_design_context` per unit, one screenshot per unit, one line in the ledger per unit. A ledger row looks like:

```
| 10432:76812 | Hero | get_design_context, get_variable_defs, use_figma dump | 2 hidden layers (hover states) noted |
```

A row counts as inspected only when it names `get_design_context` or a `use_figma` dump. Metadata and a screenshot alone mark the unit as seen, and the coverage auditor reports seen units as findings. Keep the ledger in the same directory as the brief. The auditor's first move is to diff the ledger against the metadata tree, so anything not in it counts as uninspected regardless of what the agent remembers looking at.

## When the desktop server is the only one

The desktop server reads the file open in the Figma app and works from the current selection when no node id is given. It has no `use_figma`, so the scripts above are unavailable. Compensate with the browser. Open the node URL, read per-corner radii and effects in the Inspect panel, toggle layer visibility to find hidden states, and screenshot at 2x where the tooling allows. State in the report that hidden layers and bindings were checked visually rather than programmatically, and mark them as not verified where you could not.
