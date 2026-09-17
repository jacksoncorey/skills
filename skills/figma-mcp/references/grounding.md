# Grounding

How to establish the reference frame before any design work, what to search, when to ask, and the brief template that the review loop grades against.

## The priority ladder, with what each rung gives you

| Rung | Source | What it settles | What it cannot settle |
| --- | --- | --- | --- |
| 1 | A design system or library the user linked | Tokens, components, type ramp, radii, the file's naming | Layout of a new screen, copy, mood beyond what the components imply |
| 2 | A reference frame or file the user pointed at | Layout, density, hierarchy, mood | Tokens the reference does not use, states it does not show |
| 3 | The brand's public website | Real fonts, real spacing rhythm, real color, real motion | Anything the site does badly; a site is evidence, not a spec |
| 4 | Existing screens in the same file | Conventions: naming, frame sizes, how sections are built | Whether those screens are current or abandoned |
| 5 | Something found by search | A candidate for rung 1 or 2 | Whether it applies. This rung always ends in a question or a confidence statement |
| 6 | Nothing | Permission to design from principles | Nothing else. Say it plainly in the report |

Land on the highest rung that exists, and record the rung. A reference from a different brand (common in a redesign brief) is rung 2 for layout, density and mood only. Its tokens, fonts, colors, imagery and copy never cross over; those come from rungs 1, 3 or 4 for the product the work is for. Its foundation and token pages are listed, never read.

## The search recipe for rung 5

Run these before deciding nothing exists. Each takes seconds and any one of them can change every downstream value. For design to output the codebase items always run, whatever rung the source side landed on, because they fill the target column. In the Figma file, keep `figma-generate-design`'s order: Code Connect files, then existing screens (the instances script in node-inspection.md), then `get_libraries` and `search_design_system`. Grounding is that skill's Step 2; do not repeat it, and carry the keys into the brief's Components table.

- Auto-memory and project memory: search for `figma.com`, the product name, `design system`, `tokens`, `DESIGN.md`. In Claude Code the index is `~/.claude/projects/<project-slug>/memory/MEMORY.md`; a sub-agent gets the path from whoever spawned it.
- The project's instruction files: `CLAUDE.md`, `AGENTS.md`, `.cursorrules`, a `docs/design` folder.
- The codebase: `DESIGN.md`, `tokens.*`, `theme.*`, `tailwind.config.*`, `globals.css` custom properties, and Code Connect files (`*.figma.ts`, `*.figma.tsx`, or `FigmaConnect` in Swift and Kotlin), which carry Figma URLs. Code Connect snippets also arrive inside `get_design_context` on either server.
- The Figma file itself: `get_libraries` for subscribed and available libraries, paging with `offset` until the next offset is null. Then a page list for anything named foundations, tokens, components or system.
- Published libraries the file has not subscribed to: `search_design_system` with `queries: [{ entity, query }]` scoped by `includeLibraryKeys` from the previous step.

Then apply the adopt rule. High confidence means all three hold: the found system is named for the same product, the task is for that product, and nothing in the request contradicts it. A token file inside the target repo passes by default. One miss means ask. The question is one line and names the candidate:

> Found the Acme product library (file key AbC1…) in memory with a full token set. Use it for this marketing page, or is the site on a different system?

Keep working on everything that does not depend on the answer: page inventory, reading the reference, the aesthetic layer of the brief.

## Reading a public website as a design reference

A live site answers the atomic questions faster than any Figma file, because the values are computed rather than authored. Open it in whatever browser tooling the harness has, then run these probes in the page context and record the results in the brief. They are adapted from the `explain-interface` skill's system read, credited in [design-principles.md](design-principles.md). Each returns data rather than printing, so the result comes back whole.

Tokens declared on the root:

```js
const tokens = {}; const unreadable = [];
const walk = rules => { for (const r of rules ?? []) {
  if (r.selectorText === ':root' || r.selectorText === 'html') {
    for (const prop of r.style) if (prop.startsWith('--')) tokens[prop] = r.style.getPropertyValue(prop).trim();
  }
  if (r.cssRules) walk(r.cssRules);
}};
for (const sheet of document.styleSheets) {
  let rules; try { rules = sheet.cssRules } catch { unreadable.push(sheet.href); continue }
  walk(rules);
}
({ tokens, unreadable, count: Object.keys(tokens).length });
```

The type scale, leaf text nodes only, sorted by usage so the body size comes first:

```js
const seen = new Map();
for (const el of document.querySelectorAll('body *:not(script):not(style):not(noscript):not(template)')) {
  const own = [...el.childNodes].some(n => n.nodeType === 3 && n.textContent.trim());
  if (!own) continue;
  const s = getComputedStyle(el);
  const key = `${s.fontFamily.split(',')[0]} ${parseFloat(s.fontSize)}px w${s.fontWeight} lh ${s.lineHeight} ls ${s.letterSpacing}`;
  seen.set(key, (seen.get(key) ?? 0) + 1);
}
[...seen].sort((a, b) => b[1] - a[1]).slice(0, 25);
```

The spacing rhythm, to find the base unit and check the 2x grouping rule:

```js
const vals = new Map();
for (const el of document.querySelectorAll('*')) {
  const s = getComputedStyle(el);
  for (const p of ['paddingTop', 'paddingLeft', 'marginTop', 'gap', 'rowGap']) {
    const v = parseFloat(s[p]); if (v > 0) vals.set(v, (vals.get(v) ?? 0) + 1);
  }
}
[...vals].sort((a, b) => b[1] - a[1]).slice(0, 20);
```

Radii and shadows, where one or two recipes mean a system and nine mean nobody chose:

```js
const grab = (prop, skip) => { const m = new Map();
  for (const el of document.querySelectorAll('*')) { const v = getComputedStyle(el)[prop]; if (v && v !== skip) m.set(v, (m.get(v) ?? 0) + 1); }
  return [...m].sort((a, b) => b[1] - a[1]).slice(0, 10); };
({ radius: grab('borderRadius', '0px'), shadow: grab('boxShadow', 'none') });
```

Fonts and the content width:

```js
({
  loaded: [...document.fonts].map(f => `${f.family} ${f.weight} ${f.style}`),
  body: getComputedStyle(document.body).fontFamily,
  maxContent: Math.max(...[...document.querySelectorAll('main, section, header')].map(e => e.getBoundingClientRect().width)),
  viewport: document.documentElement.clientWidth,
});
```

Take screenshots with the harness's browser tool at desktop and at 375 wide, at 2x where the tooling allows, and keep them beside the brief. Note the site's builder if it is obvious (Framer, Webflow, Next) because it tells you whether a codebase exists to read.

`sheet.cssRules` throws on cross-origin stylesheets, and the `unreadable` list says which ones were skipped. A brief that silently skipped the main stylesheet describes a site nobody is looking at.

## The brief template

Write it to the session scratchpad, or a dated scratch folder when there is none, never inside a code repo, and give the absolute path to every reviewer. Fill what the sources support and mark the rest `unknown`; an `unknown` is honest, a guess dressed as a value is not.

```markdown
# Design brief: <task>

Grounding rung: <1 to 6>: <source, link or path>
Confirmed by user: <yes / asked, pending / not needed because …>
Reference for layout and mood only (no token crossover): <link, if any>

## Aesthetic layer
<One paragraph. Mood in three adjectives. Density (airy / standard / compact).
Color temperament (monochrome with one accent / warm neutrals / …). Type
personality (grotesk, geometric, editorial serif, …) and how display and body
differ. Motion (none / subtle / expressive). What the system refuses to do:
gradients, drop shadows, colored chips, more than one accent, …>

## Atomic layer

### Color
| Token or role | Value | Where seen | Target token (design-to-output only) |
| --- | --- | --- | --- |

### Type ramp
| Role | Family | Size | Weight | Line-height | Tracking | Where seen | Target token (design-to-output only) |
| --- | --- | --- | --- | --- | --- | --- | --- |

For design-to-output the target column is the source-token to target-token map: Code Connect first (snippets in `get_design_context`, or `get_code_connect_map` on the remote server), `get_variable_defs` second, the project's token file third. A source value with no target is a row the fidelity reviewer will ask about.

### Spacing scale
<base unit; the steps actually used; the section rhythm>

### Radii, strokes, shadows
| Use | Value |
| --- | --- |

### Grid
<columns / margin / gutter per breakpoint; content max width>

### Components in play
| Component | Source (library key, node id, or "to build") | Variants needed |
| --- | --- | --- |

## What the user said, verbatim
<Every sentence of intent from the request, quoted. The vision reviewer grades against this.>

## Open questions
- …
```
