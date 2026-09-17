# Preflight and budget

What to check before a long run, how to present it, when to stop for confirmation, and where the strong model's judgment is worth paying for.

## The preflight card

Run these checks after grounding and before the first write or reviewer. Each is one cheap call, and together they tell the user what the run can and cannot do before it costs anything.

| Check | How | What a failure means |
| --- | --- | --- |
| Figma server flavour | Is `use_figma` in the tool list | Without it, nothing can be built in Figma; reading still works through the browser |
| File access | `get_metadata` with the file key and no node id (desktop: the open file, selection cleared) returns at least one page | A 403 or empty list means the file is not shared with the MCP account; ask for access |
| Page count | The page-listing script where `use_figma` exists, since `get_metadata` has returned one page of 22 | Confirms scope before fan-out; a 22-page file costs more than a 3-page one |
| Brand font | `figma.listAvailableFontsAsync()` filtered to the brief's family | Missing means every text node will fall to a substitute; the user chooses the nearest family now, not after the build |
| Library reach | `get_libraries`, then one `search_design_system` for a token the brief names | Empty means no published system: local variables and text styles are created from the brief before the wrapper, and the hardcoded-values check applies in full |
| Images | `upload_assets` present, and a browser tool for captures | Without them, image slots are placeholders |
| Browser | A navigate and evaluate tool the harness exposes | Without it, a website reference cannot be measured and rung 3 is unavailable |
| Sub-agents | The Agent tool or equivalent | Without it, the loop degrades to a self-review and the report must say so |
| Memory | The auto-memory path, if the harness has one | Without it, rung 5 is a codebase search only |

On the desktop server the font, library and image rows read `n/a (desktop, read-only session)`; library reach is then judged from `boundVariables` on existing screens through the browser's Inspect panel and marked not verified.

Present the result as a short card, one line per row, merging rows that pass, then the plan:

```
Preflight
- Server: remote (use_figma available)
- File: AbC1… 22 pages; will read 2 in full, 8 at depth one, 12 listed
- Font: Brand Grotesk not loadable here; nearest available is Inter Tight
- Library: Acme Website (9 tokens found); no spacing tokens
- Images: upload_assets + a browser available, captures at 1x
- Browser: available. Memory: found, no design-system entries
- Sub-agents: available; planned reviewers: brief check, fidelity per section, coverage + fidelity + vision at the end
- Estimated cost: ~40 write calls, 6 reviewer runs, 60 to 90 minutes

Brief: <path>. Open questions: <list>.
Proceed?
```

## When to stop for confirmation

Stop for input to design before the first write, because a frame is expensive to build and cheap to redirect before it exists. A pre-authorised run (an eval harness, a "don't ask, just build", a `/loop` charter that lists its assumptions) skips that stop but not the next two:

- A preflight row that failed in a way the charter did not name: the font, the library, the images, the sub-agents, or the browser when the site is the grounding source.
- An open question in the brief that changes more than one section: the target file, the headline, the CTA vocabulary, the found system.

Those stop even a pre-authorised run, because a charter cannot cover an assumption it never listed. The card always states the estimate, and over 20 write calls is the line above which the estimate is a question, not a note. When a run continues, state every assumption in one line each and put the same lines at the top of the report. For design to output and audit, the card is informational: show it, note what is missing as "not verified", and continue.

## Spend the strong model where it judges

Adapted from the `efficient-fable` pattern: the orchestrating model keeps the decisions, and bounded work that returns evidence goes to cheaper sub-agents. Quality does not drop when the split follows one rule. A cheap agent gathers, the strong agent decides, and nothing a cheap agent reports is acted on until the orchestrator has reopened the cited node or file.

| Keep on the strong model | Delegate to a cheaper model |
| --- | --- |
| Grounding decisions, the brief and the brief check | Page-listing and depth-one metadata across every page |
| Which rung a source lands on, and the adopt question | Subtree dumps of units the brief already names |
| Every write to the canvas | Website probes and screenshot capture, download and cropping |
| The vision reviewer | The coverage auditor (a ledger diff) |
| The fidelity reviewer's judgment on numbers against source | The fidelity reviewer's script half: on-grid, naming, hardcoded values, font, placeholders |
| Fixes after a review, and the final report | The comparison of a reviewer's table against the previous round |

Every delegated prompt is a handoff packet, because the sub-agent has none of the conversation. It carries the file key and node ids, the exact tool names to load, the read-only rule and the evidence format to return. It also carries the stop condition: if a node is missing or a call fails twice, report instead of improvising. The briefs in `feedback-loop.md` have this shape, and its "Filling the briefs" section gives the two lines a cheaper model needs added.

## Cut the calls that buy nothing

Learned on a real 22-page file where the first run spent 56 write calls and six reviewer runs:

- One subtree dump of a section replaces a `get_design_context` call per child. Read the dump; call `get_design_context` only on the unit you will reproduce.
- `get_metadata` verifies structure, counts and names after a write. Screenshots verify colour, type and effects. Do not screenshot to check a rename.
- Screenshot a section once by id at its native long edge when it is finished, and the composition once at the end. Re-shoot only what a fix changed.
- Import every variable, style and component a section needs in one `Promise.all`, and build the section in one call. Three calls per section is the ceiling.
- A fix round touches only the rows in the findings table. Never rebuild a section to fix a padding value.
- Never re-dump a section the ledger says is unchanged.

## Budget by mode

| Mode | Reads | Writes | Reviewers |
| --- | --- | --- | --- |
| Audit, one screen | 1 dump per unit, 1 screenshot per unit, the site probes | none | fidelity once |
| Design to output, one screen | 1 dump plus 1 `get_design_context` per unit, tokens once | none in Figma | brief check, fidelity once on the finished page |
| Input to design, one page | pages at depth one, 1 dump per source unit, probes | wrapper 1, then 2 to 3 per section, fixes by row | brief check on the strong model; the script half of fidelity per section and the coverage diff on a cheap model; numbers-against-source fidelity and vision on the strong model |

Say in the report what the run actually spent: write calls, reviewer runs, and which model ran each.
