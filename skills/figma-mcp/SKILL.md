---
name: figma-mcp
description: Gets the best possible result out of the Figma MCP in either direction. Reads a design thoroughly enough to reproduce it faithfully, or designs in Figma the way a designer would. Use when a figma.com/design link or a Figma design MCP tool is in play and the job is to reproduce, extend, audit or create a design. Trigger even when the user never says "Figma". Not for FigJam or Slides, not for a bare screenshot or export, and not for UI work with no Figma file behind it.
---

# Figma MCP

The Figma MCP hands an agent a narrow window onto a design: one node, one screenshot at one size, one page. Thoroughness here is measured rather than felt: every unit in scope inspected, every value traced to a source, every claim checked by a reviewer who did not do the work.

Figma's own skills own the mechanics and this skill nests inside them. `figma-use` owns every Plugin API rule and is loaded before any `use_figma` call. `figma-design-to-code` owns the `get_design_context` workflow and is loaded before the first call to it. `figma-generate-design` and `figma-generate-library` own the build sequence for screens and components. Load them as `/figma-<name>` when the Figma plugin is installed, otherwise with `get_figma_skill` on `skill://figma/<name>/SKILL.md`. Where this skill tightens one of their rules it says so. Verified pixel parity belongs to `pixel-perfect`. Domain rules for layout, type, color, polish and copy belong to the `better-*` skills.

## Tool names vary, questions do not

The same tools ship under different prefixes (`mcp__figma__`, `mcp__Figma__`, or a server id) and in two flavours. The desktop server reads the file open in the Figma app, falls back to the current selection when no node id is given, and has no size control on screenshots. The remote server needs `fileKey` on every call and a concrete `nodeId` on the node tools; `get_metadata` without one lists the pages. It adds `use_figma`, `get_figma_skill`, `search_design_system`, `get_libraries`, `get_code_connect_map`, `upload_assets`, `download_assets` and `create_new_file`. If `use_figma` is absent, designing inside Figma is not possible from this session: say so rather than drawing in code and calling it a design. Reading still works through the browser; the desktop section of [node-inspection.md](references/node-inspection.md) says how.

## Pick the mode first

| The user wants | Mode | The benchmark and the target |
| --- | --- | --- |
| A design turned into code, a doc, a spec or another tool's format | Design to output | Grounding does the target side: the source-token to target-token map, from Code Connect first (snippets inside `get_design_context` on either server, `get_code_connect_map` on the remote one), `get_variable_defs` second, the project's token files third |
| A new or changed design in Figma, from a prompt, code, a reference or another brand's site | Input to design | The brief, built from the ladder below. The target file is the one the user names for the product; a reference file is never the target. With no target named, ask in one line, or when the user said "new", load `figma-create-new-file` and call `create_new_file`. The returned key is then the key for every write, the reference key is read-only, and the report says which file was written to |
| A comparison: design against build, file against reference, two versions | Audit | The file, read per unit, against the build measured per unit. Confirm three inputs first: the build URL, the route and state (the user logs in or supplies fixture data; never enter credentials), and the frame's width. Ask for what is missing in one line and read the Figma side while waiting |

Mixed requests ground once and then run both. Whatever the mode, the phases run in order: ground, read, work, review. Design to output and audit skip the design phase.

## Ground before you touch anything

Establish the reference frame in this priority order and record which rung you landed on:

1. A design system or library the user linked or named.
2. A reference design or file the user pointed at. A reference from another brand settles layout, density and mood only. Its tokens, fonts, colors, imagery and copy never cross over; those come from rungs 1, 3 or 4 for the product the work is for. Its foundation and token pages are listed, never read.
3. The public website of the product or brand the work is for, measured with the probes in [grounding.md](references/grounding.md).
4. Existing screens in the same Figma file, which carry the file's conventions.
5. Something found by searching: auto-memory and project memory, `CLAUDE.md`, `DESIGN.md`, token and theme files, Code Connect files, figma.com URLs in project docs, every page of `get_libraries`.
6. Nothing. Say so, and design from the principles below.

For design to output the codebase items of rung 5 always run, because they fill the target column.

**Never adopt a found system without checking.** Rung 5 is a search result, not a decision. The adopt rule and the one-line question are in [grounding.md](references/grounding.md). The short form: a found system is used unasked only when it is named for the product the task is for. Keep doing everything that does not depend on the answer.

**Write the brief.** Grounding ends with a design brief on disk: an aesthetic paragraph and atomic tables, each row citing where it was seen or saying `unknown`. For design to output the target token sits beside each source value. Template in [grounding.md](references/grounding.md). The brief and the coverage ledger live in the session scratchpad, or a dated scratch folder if there is none, never inside a code repo. Every reviewer gets their absolute paths.

## Read the file like an inspector, not a viewer

A **focus unit** is a node a designer would name: the nav, the hero, one card, the footer. Never the page. Define it as a node set or a y-range so a reviewer can find the same thing. This tightens `figma-design-to-code`, which splits only when a response comes back sparse; here the split happens first.

1. Orient with `get_metadata`: the page list, then the tree for the pages in scope, to cut the page into focus units. Also list the linked node's sibling frames at depth one; frames named for the same screen (tabs, states, breakpoints) are in scope unless the user says otherwise.
2. Load `figma-design-to-code`, then call `get_design_context` once per focus unit. Its G1 is passed by the set of per-unit calls. For design to output, G2 to G4 are passed by the brief's target columns, G5 becomes a fidelity-reviewer row, and you emit its three gate lines. In other modes only G1 applies, and you say so once.
3. `get_variable_defs` on each unit for the tokens it binds.
4. Screenshots per unit. On the remote server the response is a URL, so download it before you look. Set `maxDimension` to at least the node's native long edge; the tool downscales to fit and never upscales. Capture from the browser at 2x where the tooling allows, and say when a comparison was made at 1x.
5. `use_figma` read-only scripts for what those tools hide. Scripts and the full property checklist are in [node-inspection.md](references/node-inspection.md).

A unit counts as **inspected** only when the ledger names `get_design_context` or a `use_figma` dump for it. Metadata and a screenshot alone mark it as seen, and seen is a coverage finding. A ledger row is `| node id | unit name | tools that inspected it | what was noted |`.

**Which pages.** Always the linked page, and every page of the product's own file named for foundations, tokens, styles, components or a design system. Skipping one of those is never acceptable. Pages named archive, old, WIP or explorations are listed, not read. Everything else gets metadata at depth one to decide. Read pages in parallel, one call per page, and say which were read and which were not.

**The MCP is not the only window.** Open the file in the harness's browser tool at `figma.com/design/<key>?node-id=<id>`. That is where comments, the prototype, a zoomed region and any page the tools return as sparse live. Compare the design against the shipped product where one exists.

**Audit mode.** Open the build at the frame's width with the same state and data, and per focus unit read the matching element's computed styles against the unit's `get_design_context` values. A screenshot diff locates a difference; the numbers decide it. The findings table is the output, and "matches" means no HIGH or MEDIUM rows.

## Design in Figma the way a designer would

The build sequence is `figma-generate-design` Steps 3 to 5 with `figma-use` Section 6's placeholder shimmer. Follow it there, not here. This section adds what a designer does that the sequence does not say, detailed in [designing-in-figma.md](references/designing-in-figma.md).

**Grid first.** Put a column grid on the wrapper before placing anything. 12 columns at desktop widths, 6 at tablet and below, and a 4-column mobile grid only where the file already uses one. Margins and gutters come from the brief or the file's own grid. Content sits on column edges and the on-grid script proves it.

**Name everything with the vocabulary of the product.** Never `Frame 427`. Rename in the call that creates the node. Group the work in a Figma section named for the flow.

**Hierarchy from the ramp.** Sizes, weights, leading and tracking come from the brief and are set explicitly, never left to `AUTO`. The canvas values and the kerning rule are in [designing-in-figma.md](references/designing-in-figma.md). If the brand family is not available in Figma, pick the nearest available family and record it as an accepted exception in the brief and the report. Never fall back to Inter unasked.

**No library, no excuse.** When the target file has no library, `figma-generate-design`'s published-system prerequisite is overridden. Create local variables and then text styles from the brief's atomic tables before the wrapper, following the variable and style steps of `figma-generate-library`. Bind to those.

**Images.** Upload the product's own imagery with `upload_assets` from browser captures or files, or take image hashes from a `generate_figma_design` capture of the product site where the server exposes it. A placeholder is named and reported, never silent. Reference imagery is never uploaded.

## Design principles that survive the canvas

The measurable subset of [design-principles.md](references/design-principles.md), which restates Jakub Krehel's `better-*` rules for the canvas with attribution. The fidelity reviewer checks these; the vision reviewer checks the ones that need judgment.

- **Group with space, not lines.** The gap between groups is at least twice the gap within one.
- **Align to shared edges,** and order by importance: the most important content near the top and the leading edge, one primary action per view.
- **Controls look like controls.** A background shape, a border, or a consistent placement zone.
- **Concentric radius.** Outer radius equals inner radius plus the padding between them.
- **Shadows for elevation, borders for structure.** A divider stays a border; a border that only creates depth becomes a layered shadow.
- **A type scale, few weights, tabular numbers on anything that changes.** Body 16, UI text 14, captions 13, rarely below 12. Contrast 4.5:1 for text and 3:1 for large text.
- **Breathing room between targets.** 12 between bordered controls, 24 around borderless ones, 44 by 44 hit areas on touch.
- **Image outlines** at 10 percent black, inset, on every photo.
- **Verb-first buttons, destination-describing links, one vocabulary per flow.**

## Review with eyes that did not do the work

Review is done by sub-agents with fresh context, briefed from the files on disk, with tool access to re-query Figma and the browser themselves. The briefs in [feedback-loop.md](references/feedback-loop.md) are self-contained; fill every angle bracket from the session before sending. Reviewers never edit. A preference with no source behind it is not a finding. A reviewer that returns an empty table without naming the tools it called has not reviewed.

| Reviewer | Reads | Asks |
| --- | --- | --- |
| Brief check | The brief and the request, before any work | Does every atomic row have a source, and does the aesthetic paragraph restate what the user asked for |
| Coverage auditor | The ledger, the page list, the metadata tree | Which units and pages in scope were only seen, never inspected; which Figma tools the mode needed that the ledger never names; which hidden layers were missed |
| Fidelity reviewer | The brief's atomic layer, the output, node ids | Where does the output disagree with the source on a number, a token, a font, a name, a grid position |
| Vision reviewer | The brief's aesthetic layer, the user's own words, screenshots | Would the person who asked recognise it, and what would a senior designer change first |

Cadence, stop rule, budget and harness mechanisms are in [feedback-loop.md](references/feedback-loop.md). The short form: brief check after grounding. Fidelity after each section for input to design, and once on the finished page for design to output. All three before the final report. An audit needs fidelity once. Nothing above LOW ends the loop. After a fix, re-run the same reviewer on the fixed items with the previous table attached; three rounds per unit, then the user. Scale it to the blast radius and say what you ran. Self-review from disk only when the session has no sub-agent tool at all, and the report then says the loop did not run.

## Before you finish

| Mistake | Fix |
| --- | --- |
| Screenshot URL never downloaded, or judged below native size | Set `maxDimension` to the native long edge, fetch it, or capture from the browser at 2x where the tooling allows |
| Font family loaded without error but wrong for the product | Assert against `getStyledTextSegments` and the brief |
| Competitor's token pages read into the brief | A cross-brand reference's foundations are listed, never read |
| Brand font unavailable in Figma, Inter loaded silently | Nearest family, recorded as an accepted exception |

## Reporting

The final message carries, in this order:

1. The mode and the grounding rung, with which sources the user confirmed.
2. Coverage: pages read against pages present, units inspected against units in scope, skips named.
3. The brief, or a link to it.
4. The findings resolved through the loop, grouped by reviewer.
5. Accepted exceptions, each named and justified.
6. What could not be verified, and why.

For an audit, the findings table leads and the rest follows.
