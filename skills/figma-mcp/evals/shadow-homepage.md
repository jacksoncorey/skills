# Eval: the Shadow homepage

A test of the `figma-mcp` skill on a real task with three real inputs. It exercises every part of the skill: grounding across a live site, a half-finished design and a cross-brand reference; reading a multi-page file; designing in Figma on a grid with named layers; and the review loop.

## Inputs

| Input | Value | Fill in |
| --- | --- | --- |
| Current site | https://shadow.co (a Framer site, so there is no codebase to read; the browser probes are the source) | ready |
| Half-baked design | Node `10467:103080` in the Shadow-Website file `RSG7AXjCTu8e4i0fkGIwn5` | filled |
| Cross-brand reference | https://www.moving.parts, a public site from a different brand | filled |
| Known trap | The Shadow Launch product library `HonTXfmNxjH1I7AMXzYK4t` is in this machine's auto-memory with a full token set. The marketing site does not necessarily share it. A correct run surfaces it and asks; a wrong run binds to it silently or ignores it | in place |

Both inputs are filled in `evals.json` (eval 1).

## How to run it

Two arms per iteration, launched in the same turn so they finish together, following the `skill-creator` convention:

- **with_skill**: a sub-agent given the eval prompt and the skill path `~/dev/skills/skills/figma-mcp`, with the Figma remote MCP, a browser and the Agent tool available. It must be told to save its brief, ledger and report under `<workspace>/iteration-N/eval-1/with_skill/outputs/`.
- **without_skill**: the same prompt, no skill path, same tools, saving to `without_skill/outputs/`.

Both arms build into the same Figma file, so each must create its own named Figma section (`Eval: with skill`, `Eval: without skill`) and put everything inside it. Delete both sections after grading, or keep the better one as the actual draft.

Workspace: `~/dev/skills/figma-mcp-workspace/` (a sibling of the skill directory, ignored by git).

## Grading

The assertions in `evals.json` are binary and evidence-based. Grade each from the transcript and the Figma file, not from the agent's own summary:

| Assertion | Evidence to look for |
| --- | --- |
| Brief on disk before mutation | Timestamp of the brief file precedes the first `use_figma` call that creates a node |
| Site probes run | Probe results (type scale table, spacing counts, radii) quoted in the brief |
| All pages listed and read or skipped | A page list in the transcript, and a skip reason per unread page in the report |
| Reference used for mood only | No hex, font family or token name from the reference appears on the built frame; check with the subtree dump |
| Found system surfaced, not adopted silently | A one-line question naming the Launch library, and work continuing after it |
| 12-column grid and on-grid script run | `layoutGrids` on the wrapper; the on-grid script's output in the transcript |
| No default names | Naming audit script returns an empty list on the final frame |
| Type ramp on canvas | Subtree dump: display text `lineHeight` explicit near 110 percent with negative tracking; body 150 to 160 percent |
| Reviewers spawned | Sub-agent calls with the brief and ledger paths; findings tables; fixes after them |
| Report structure | The six items from the skill's Reporting section, present in order |
| Section screenshots per section, no shimmer | `get_screenshot` per section by id, taken before the next section was built, with `maxDimension` at the node's native long edge (or a 2x browser capture); the placeholder script returns empty |

Score is the count of assertions passed out of eleven, per arm. The skill is doing its job when the with-skill arm passes at least nine and the without-skill arm passes fewer than five, and when a designer looking at the two frames prefers the with-skill one without being told which is which.

## Qualitative review

Beyond the score, open both frames side by side and ask a designer, or the vision-reviewer prompt from `feedback-loop.md`:

1. Which one is on a grid?
2. Which one has layers you could hand to a designer?
3. Which one reads as Shadow, and which one reads as the reference brand with Shadow's logo on it?
4. Which one used Shadow's real typeface and spacing rhythm from the live site?

## Results so far

| Iteration | Model | With skill | Without skill | With-skill wall clock |
| --- | --- | --- | --- | --- |
| 1 (2026-09-17) | Claude Fable 5.1 | 10 / 11 | 1 / 11 | about 90 min |
| 2 (2026-09-17) | Claude Opus 5 | 8 / 11 | 3 / 11 | 50 min |

Both with-skill runs missed the same two things: sections were screenshotted in a batch after the build instead of one at a time, and a second library found in memory was read but never named. The Opus run also reported a text-style binding that the final dump did not show. All three went back into the skill as v0.2: a hard screenshot-before-next-section step, a "candidates not adopted" table in the brief template, and a read-back rule for every claimed binding. The Opus reviewers caught a fabricated "trusted by" claim and a missed Pricing design before delivery, which is the loop doing its job; a provenance question was added to the vision brief so that catch is guaranteed rather than lucky.

## What this eval does not test

It does not test design-to-code, which evals 2 and 3 cover. It does not test the desktop Figma server, since the Plugin API scripts need the remote one. And it cannot test taste; the vision reviewer approximates it and the final judgment is a person's.
