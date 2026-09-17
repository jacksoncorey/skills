# skills

Agent skills for working with design tools and shipping interface work with proof. Each one exists because an agent did the job badly in a way that was repeatable, and the fix was repeatable too.

[![skills.sh](https://skills.sh/b/jacksoncorey/skills)](https://skills.sh/jacksoncorey/skills)

## Skills

- [**figma-mcp**](skills/figma-mcp/SKILL.md): Gets the best possible result out of the Figma MCP in either direction. Reads a design thoroughly enough to reproduce it faithfully, or designs in Figma the way a designer would, with a grounding brief, a coverage ledger, a preflight gate, a design craft canon with a self-check, a reference library of measured marketing pages, and a sub-agent review loop.
- [**pixel-perfect**](skills/pixel-perfect/SKILL.md): Drives a UI implementation to verified parity with a Figma frame. Parses exact values before coding, diffs screenshots after, reads the heatmap not the percentage, and ships an evidence page.
- [**front-end-qa**](skills/front-end-qa/SKILL.md): An independent, adversarial final check on a front-end change before it ships, run by a context that did not build it.
- [**verify-before-ship**](skills/verify-before-ship/SKILL.md): A pre-ship verification pass for anything high-stakes. Finds the load-bearing claims, re-derives every number, bins claims as verified, inferred or assumed, and returns an answer-first verdict.
- [**handoff**](skills/handoff/SKILL.md): One paste-ready prompt that moves a long session into a fresh one with zero information loss.
- [**delegate**](skills/delegate/SKILL.md): One scannable brief that hands work to a human teammate with everything they need and nothing they have to ask for.

## How figma-mcp was tested

Same prompt, same Figma file, same tools, one arm with the skill and one without, graded by fresh sub-agents against eleven evidence-based assertions (brief before the first write, site probes recorded, every page listed, reference used for mood only, found systems surfaced, grid script run, no default names, type ramp on canvas, reviewers spawned and applied, report structure, screenshots per section).

| Model | With skill | Without skill |
| --- | --- | --- |
| Claude Fable 5.1 | 10 / 11 | 1 / 11 |
| Claude Opus 5 | 8 / 11 | 3 / 11 |

The eval, its assertions and the runbook ship in `skills/figma-mcp/evals/`.

## Install

```bash
npx skills add jacksoncorey/skills
```

## Claude Code plugin

```text
/plugin marketplace add jacksoncorey/skills
/plugin install jacksoncorey@jacksoncorey
```

## Credits

`figma-mcp` restates design rules from [Jakub Krehel's skills](https://github.com/jakubkrehel/skills) with attribution; install those for the full versions. The repository layout and authoring conventions follow the same collection.

## License

MIT
