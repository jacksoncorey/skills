# AGENTS.md

This file is the single source of guidance for coding agents working in this repository. `CLAUDE.md` imports it and adds nothing, so put repository facts here.

## What this repository is

A collection of agent skills for working with design tools and shipping interface work with proof, distributed two ways: via `npx skills add jacksoncorey/skills` and as the Claude Code plugin `jacksoncorey` served by the marketplace in this same repository. It is documentation plus a few helper scripts; there is no build or test tooling beyond `claude plugin validate .` and the per-skill evals.

`.claude-plugin/plugin.json` and `.claude-plugin/marketplace.json` define the plugin and its marketplace. Skills are discovered from `skills/` automatically, so adding a skill needs no manifest change. Bump `version` in `plugin.json` in the same commit as any change under `skills/`: that number is the only signal plugin users update on.

`opencode.json` registers `skills/` so opencode loads the collection while this repository is open.

## Structure

Each skill lives in `skills/<skill-name>/`, with `SKILL.md` as the entry point, supporting `.md` files in `references/`, executable helpers in `scripts/`, evals in `evals/` and an `agents/openai.yaml` for Codex.

Every `SKILL.md` carries frontmatter with `name` (matching the directory) and `description`; a plain H1 and a short opener saying what the skill does; a calibration line saying how hard to press; headings in sentence case that carry the point; a hand-off line naming sibling skills that own adjacent topics; a `## Before you finish` table where the domain has recurring mistakes; and a `## Reporting` section where the skill produces a report.

Rules live in exactly one skill. Other skills point to them by skill name in backticks, never by cross-skill relative link, because each skill directory ships on its own.

## Authoring conventions

- Explain the why. A rule with its reason survives contact with a case the author did not foresee; a bare imperative does not.
- Prescriptive and specific: exact values, exact tool names, exact scripts.
- Skills match the target project's conventions rather than imposing one.
- The frontmatter `description` is how a skill gets found and loads on every turn, so it earns harder pruning than the body. It says what the skill does and when to use it, in one paragraph.
- Straight quotes, sentence-case headings, no em dashes.
- No sentence over 30 words. Split the long ones; leave the rest alone.
- Attribute borrowed material. `figma-mcp` restates rules from Jakub Krehel's `better-*` skills with credit and a link; keep that pattern for anything else borrowed.
