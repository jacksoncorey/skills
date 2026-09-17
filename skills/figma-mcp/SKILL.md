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
2. A reference design or file the user pointed at. A reference from another brand settles layout, density and mood only. Its tokens, fonts, colors, imagery and copy never cross over; those come from rungs 1, 3 or 4 for the product the work is for. Its foundation and token pages are listed, never read. Copy comes from the product's own sources or is a named placeholder; the skill never invents a claim.
3. The public website of the product or brand the work is for, measured with the probes in [grounding.md](references/grounding.md).
4. Existing screens in the same Figma file, which carry the file's conventions.
5. Something found by searching: auto-memory and project memory, `CLAUDE.md`, `DESIGN.md`, token and theme files, Code Connect files, figma.com URLs in project docs, every page of `get_libraries`.
6. Nothing. Say so, and design from the principles below.

At any rung, [reference-library.md](references/reference-library.md) gives real marketing pages to look at, cited by section with measured observations and the patterns that recur across them. Open the two it names for the brief's cue when the brief names a mood, when the product has no site, or when a section has no precedent in the sources. References are for looking, never for copying, and their tokens never cross over. When the Mobbin tools are present, search them by brand and section; when absent, the descriptions stand in.

**Never adopt a found system without checking.** Rung 5 is a search result, not a decision. Name every candidate the search turned up in the brief, including the ones you did not adopt and why they lost, so the user can overrule the choice. The adopt rule and the one-line question are in [grounding.md](references/grounding.md). The short form: a found system is used unasked only when it is named for the product the task is for.

**Write the brief.** Grounding ends with a design brief on disk: an aesthetic paragraph and atomic tables, each row citing where it was seen or saying `unknown`. For design to output the target token sits beside each source value. Template in [grounding.md](references/grounding.md). The brief also lists every candidate system the search found and did not adopt, with the reason. Location rule and template in [grounding.md](references/grounding.md); every reviewer gets the absolute paths.

## Check access before the long loop

After grounding and before the first write or reviewer, run the preflight in [preflight-and-budget.md](references/preflight-and-budget.md) and present it as a card with the plan and an estimated cost. For input to design, stop at the card. Pre-authorisation (an eval harness, a "don't ask, just build", a `/loop` charter that lists its assumptions) lifts that stop. It does not lift a failed row the charter never named or an open question spanning sections. Over 20 write calls is always a question. Every assumption goes at the top of the report. For design to output and audit, the card is informational: show it and continue.

## Read the file like an inspector, not a viewer

A **focus unit** is a node a designer would name: the nav, the hero, one card, the footer. Never the page. Define it as a node set or a y-range so a reviewer can find the same thing. This tightens `figma-design-to-code`, which splits only when a response comes back sparse; here the split happens first.

1. Orient with `get_metadata`: the page list, then the tree for the pages in scope, to cut the page into focus units. Also list the linked node's sibling frames at depth one; frames named for the same screen (tabs, states, breakpoints) are in scope unless the user says otherwise.
2. Load `figma-design-to-code`, then call `get_design_context` once per focus unit. Its G1 is passed by the set of per-unit calls. For design to output, G2 to G4 are passed by the brief's target columns, G5 becomes a fidelity-reviewer row, and you emit its three gate lines. In other modes only G1 applies, and you say so once.
3. `get_variable_defs` on each unit for the tokens it binds.
4. Screenshots per unit. The download and size rules are in [node-inspection.md](references/node-inspection.md).
5. `use_figma` read-only scripts for what those tools hide. Scripts and the full property checklist are in [node-inspection.md](references/node-inspection.md).

A unit counts as **inspected** only when the ledger names `get_design_context` or a `use_figma` dump for it. Metadata and a screenshot alone mark it as seen, and seen is a coverage finding.

**Which pages.** Always the linked page, and every page of the product's own file named for foundations, tokens, styles, components or a design system. Skipping one of those is never acceptable. Pages named archive, old, WIP or explorations are listed, not read. Everything else gets metadata at depth one to decide. Read pages in parallel, one call per page, and say which were read and which were not.

**The MCP is not the only window.** Open the file in the harness's browser tool at `figma.com/design/<key>?node-id=<id>`. That is where comments, the prototype, a zoomed region and any page the tools return as sparse live. Compare the design against the shipped product where one exists.

**Audit mode.** Open the build at the frame's width with the same state and data, and per focus unit read the matching element's computed styles against the unit's `get_design_context` values. A screenshot diff locates a difference; the numbers decide it. The findings table is the output, and "matches" means no HIGH or MEDIUM rows.

## Design in Figma the way a designer would

The build sequence is `figma-generate-design` Steps 3 to 5 with `figma-use` Section 6's placeholder shimmer. Follow it there, not here, with one rule this skill tightens: section N+1 is not started until the screenshot of section N has been taken by id and looked at. Both eval runs batched the screenshots and built seven sections on top of an empty hero. The starting structure is the source's structure: add a section only when the request or a source calls for it, and say so in the report. This section adds what a designer does that the sequence does not say, detailed in [designing-in-figma.md](references/designing-in-figma.md).

**Grid first.** Put a column grid on the wrapper before placing anything. 12 columns at desktop widths, 6 at tablet and below, and a 4-column mobile grid only where the file already uses one. Margins and gutters come from the brief or the file's own grid. Content sits on column edges and the on-grid script proves it.

**Name everything with the vocabulary of the product.** Never `Frame 427`. Rename in the call that creates the node. Group the work in a Figma section named for the flow.

**Craft canon.** Before the wrapper, load [design-craft.md](references/design-craft.md): directive values in build order, a marketing-page defaults block, and a 17-row self-check answered from a screenshot or a dump before a section is done. The product's own system and the file's conventions outrank it; it fills gaps.

**Hierarchy from the ramp.** Sizes, weights, leading and tracking come from the brief and are set explicitly, never left to `AUTO`. The canvas values and the kerning rule are in [designing-in-figma.md](references/designing-in-figma.md). A brand family Figma cannot load becomes the nearest available family, recorded as an accepted exception, never Inter unasked.

**No library, no excuse.** When the target file has no library, `figma-generate-design`'s published-system prerequisite is overridden. Create local variables and then text styles from the brief's atomic tables before the wrapper, following the variable and style steps of `figma-generate-library`. Bind to those.

**Images.** Upload the product's own imagery with `upload_assets` from browser captures or files, or take image hashes from a `generate_figma_design` capture of the product site where the server exposes it. A placeholder is named and reported, never silent. Reference imagery is never uploaded.

## Design principles that survive the canvas

[design-craft.md](references/design-craft.md) is the operational canon: every value, in build order, with a 17-row self-check. [design-principles.md](references/design-principles.md) restates Jakub Krehel's `better-*` rules for the canvas with attribution and splits its checks between the two reviewers. The builder answers the 17-row self-check before a section is done; the fidelity reviewer runs the Measurable checks and the five scripts, citing craft defaults only via the brief. Five rules hold even when neither file is open:

- **Group with space, not lines.** Outer gap at least 2x the inner: 8 inside, 16 or more between. A separator is the last resort.
- **One filled action per view.** Peers neutral, the accent only on interactive or selected nodes, secondaries behind a menu past three. A nav CTA carrying the hero's label is the same action.
- **Type by role, leading explicit.** Sizes from a role-named scale, body 16, nothing below 12; display 110, title 120, heading 130, body 150 to 160; never `AUTO`; bind the style last.
- **Tokens in their role.** A frame binds semantic variables only, never a primitive, never a hex where a token exists.
- **Contrast and hit areas are measured.** 4.5:1 under 24 px (18.5 bold), 3:1 above and for UI; targets 44 touch, 40 desktop, never under 24, never overlapping.

## Review with eyes that did not do the work

Review is done by sub-agents with fresh context, briefed from the files on disk, with tool access to re-query Figma and the browser themselves. The briefs in [feedback-loop.md](references/feedback-loop.md) are self-contained; fill every angle bracket from the session before sending. Reviewers never edit. A preference with no source behind it is not a finding.

| Reviewer | Reads | Asks |
| --- | --- | --- |
| Brief check | The brief and the request, before any work | Does every atomic row have a source, and does the aesthetic paragraph restate what the user asked for |
| Coverage auditor | The ledger, the page list, the metadata tree | Which units and pages in scope were only seen, never inspected; which Figma tools the mode needed that the ledger never names; which hidden layers were missed |
| Fidelity reviewer | The brief's atomic layer, the output, node ids | Where does the output disagree with the source on a number, a token, a font, a name, a grid position |
| Vision reviewer | The brief's aesthetic layer, the user's own words, screenshots | Would the person who asked recognise it, and what would a senior designer change first |

Spend the strong model where it judges and delegate what returns evidence. Nothing a cheaper model reports is acted on before the orchestrator reopens the cited node. The split, the per-mode budget and the calls that buy nothing are in [preflight-and-budget.md](references/preflight-and-budget.md).

Cadence, stop rule, budget and harness mechanisms are in [feedback-loop.md](references/feedback-loop.md). Nothing above LOW ends the loop. After a fix, re-run the same reviewer on the fixed items with the previous table attached; three rounds per unit, then the user.

## Before you finish

| Mistake | Fix |
| --- | --- |
| Screenshot URL never downloaded, or judged below native size | Set `maxDimension` to the native long edge, fetch it, or capture from the browser at 2x where the tooling allows |
| Font family loaded without error but wrong for the product | Assert against `getStyledTextSegments` and the brief |
| Competitor's token pages read into the brief | A cross-brand reference's foundations are listed, never read |
| Brand font unavailable in Figma, Inter loaded silently | Nearest family, recorded as an accepted exception |
| Fifty-six write calls and six strong-model reviewers for one page | Preflight card first; cheap models for listings, dumps, captures and the coverage diff; one screenshot per finished section |
| Built for an hour before the user saw the plan | Preflight card and brief, then ask, unless the run was pre-authorised |
| Seven sections built before the first one was looked at | Screenshot section N by id before starting N+1 |
| A section that answers none of the craft self-check rows | Run the 17 rows in design-craft.md from a dump before calling it done |
| Report says a style is bound; the final dump says it is not | Read back after the last write; bind text styles last |
| A "trusted by" line or a feature claim no source contains | Copy from the sources or a named placeholder; the vision reviewer checks provenance |

## Reporting

The final message carries, in this order:

1. The mode and the grounding rung, with which sources the user confirmed.
2. Coverage: pages read against pages present, units inspected against units in scope, skips named.
3. The brief, or a link to it.
4. The findings resolved through the loop, grouped by reviewer.
5. Accepted exceptions, each named and justified.
6. What could not be verified, and why.

Every claim of a binding, a check or a count comes from a read-back after the last write, never from the write call that set it.

For an audit, the findings table leads and the rest follows.
