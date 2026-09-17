# Verdict format — exact template

Use this template for the output of §3 in SKILL.md. It's designed to be handed straight to a human, or — if you use a builder skill that accepts a verdict file (e.g. a `--qa-verdict-file` argument that renders it verbatim into a diff report) — piped into that without any translation. Don't restructure it per-run.

```markdown
# Front-End QA Verdict — <slug or short description of the change>

**Review context:** [Independent subagent, no prior context | Same-session self-check — NOT independent]
**Reviewed:** <date>
**Baseline:** <base ref / pristine URL used>
**Proposed:** <branch / proposed URL used>
**Directions source:** <ticket link / Figma frame link / chat excerpt / prototype path>

## 1. Scope compliance — PASS / FAIL
Findings:
- <specific finding, or "None — every changed line traces to the directions.">
Evidence:
- <diff hunk / line reference per finding>

## 2. Visual / pixel fidelity — PASS / FAIL / N/A (<reason if N/A>)
Findings:
- ...
Evidence:
- <match %, heatmap region, specific value comparison>

## 3. Functional / behavioral correctness — PASS / FAIL / N/A (<reason if N/A>)
Findings:
- ...
Evidence:
- <state/interaction tested, expected vs. actual>

## 4. Regression check — PASS / FAIL
Findings:
- ...
Evidence:
- <what was compared, what changed>

## Overall: SHIP / DO NOT SHIP
<one or two sentences — if DO NOT SHIP, name the specific check(s) blocking it. If SHIP despite an N/A above, say why that N/A doesn't block shipping (e.g. no design reference existed and none was required).>
```

Rules for filling it in:

- Never leave a Findings list empty *and* unexplained — write "None — <what was checked instead>" so it's clear the check ran rather than got skipped.
- Every FAIL needs at least one piece of concrete evidence. A FAIL with no evidence is not usable by whoever fixes it.
- "Overall" is not a majority vote. One check failing is enough to block shipping even if the other three are clean — the checks aren't measuring the same thing, so they don't average.
