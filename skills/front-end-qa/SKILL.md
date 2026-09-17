---
name: front-end-qa
description: "Runs an independent, adversarial final check on a front-end implementation before it ships — compares the actual current repo code, the updated implementation's live browser preview, and the original context/directions (ticket, Figma frame, chat spec) against each other, and reports a rigorous PASS/FAIL with itemized, evidence-backed findings. Must run with fresh eyes: if invoked by the same agent/session that built the change, spawn a separate subagent with no memory of the implementation work rather than review your own output — self-grading is the exact failure mode this exists to prevent. Use whenever the user wants a final check, QA pass, sanity check, unbiased review, or 'before this ships' review of a front-end change, whether it was built by hand, by an agent, or by a builder skill. Triggers: 'QA this', 'give this a final check', 'review this without bias', 'double check this implementation', 'does this match the design', 'sanity check this before I ship it'."
---

# Front-End QA

## Why this is its own skill, not a step inside the builder

The agent that builds a change is structurally the worst-positioned agent to grade it — not from dishonesty, but because it already believes its reasoning was sound and will read ambiguous evidence charitably. Splitting this into its own skill, run by a separate context, is what makes "unbiased" a property of the process rather than a claim about the agent's character. This skill's only job is to find problems in someone else's work. It authors nothing, and it doesn't fix anything it finds.

## 0. Non-negotiable: this review needs fresh eyes

- If you are the agent — or in the same conversation as the agent — that implemented the change being reviewed, **do not grade it yourself.** Spawn a genuinely separate subagent (e.g. Claude Code's Task/Agent tool) and load this skill there instead: one with no visibility into the implementation session's reasoning, only the three inputs in §1.
- When handing off to that subagent, package the three inputs **neutrally**. Give it the raw baseline code, the raw updated code plus a way to see it rendered, and the raw directions/context. Do not include any narrative about intent, confidence, or self-assessment — no "I built this because X, I think it's correct." That framing is itself a bias vector: a reviewer primed with the implementer's confidence tends to inherit it before it's looked at anything.
- If no subagent capability exists in the current environment, still run every check in §2 — but say so plainly in the verdict: *"This review was not run with an independent context — treat it as a stronger self-check, not a substitute for independent QA."* A compromised review that's disclosed is useful; one that silently passes as clean is worse than no review.

## 1. Gather the three inputs — verify them yourself, don't just accept a summary

1. **Baseline: the actual current repo state.** Check it out yourself — `git show <base-ref>:<path>`, or open the pristine preview directly if one's already running — rather than trusting a description of what "before" looked like. If nothing is running, `scripts/checkout_worktree.sh <repo_root> <label> <base_ref>` stands up a real git-checkout copy on its own.
2. **Updated implementation: code and a live rendering.** Read the real diff (`git diff <base-ref> <branch>`), and actually look at the rendered result — navigate to the preview URL yourself and screenshot it with `scripts/screenshot_diff.py` (or a plain screenshot if there's nothing to diff against yet), rather than trusting a description of what it looks like. Code-only review, with no rendered screen ever seen, is not a visual QA pass — say so explicitly if that's all that's available.
3. **Context/directions: what was actually asked for.** The original request, ticket, or chat instruction; a Figma frame (pull it directly via the Figma MCP — `get_design_context`, `get_screenshot`, `get_variable_defs` — don't work from a paraphrase of it); or an existing prototype's real code. If this is missing, vague, or self-contradictory, say so. Grading against an undefined target isn't a real check, and a confident-sounding PASS against a vague spec is worse than no review at all.

Full detail on pulling each input independently, including what to do when a preview isn't already running: `references/gathering-evidence.md`.

## 2. Four checks, each with its own verdict

Run all four. Don't let a strong result on one substitute for a weak one on another.

1. **Scope compliance** — every changed line traceable to the directions; nothing incidental (formatting, renames, unrelated cleanup) folded in.
2. **Visual/pixel fidelity** — if a design reference exists, diff the rendered proposal against it with `scripts/screenshot_diff.py`; read the heatmap, not just the percentage. A small, concentrated miss (a button 4px off) matters more than a larger, expected difference (live data vs. placeholder text).
3. **Functional/behavioral correctness** — does the implementation actually do what the directions asked, including states and interactions implied but not spelled out (hover, empty state, error state, loading, keyboard focus) — not just match a static screenshot.
4. **Regression check** — spot-check that things outside the stated scope still behave the way they did in the baseline. A visually perfect change that silently breaks something adjacent is still a FAIL.

Full rubric, and what counts as sufficient evidence for each: `references/qa-checks.md`.

## 3. Report the verdict — evidence or it didn't happen

For each of the four checks: **PASS** or **FAIL** (or **N/A** with a reason, e.g. no design reference existed for check 2), an itemized findings list — empty only if genuinely nothing to report, never a placeholder for "seemed fine" — and the specific evidence behind each finding (a line number, a diff hunk, a pixel region, a described interaction that didn't work as specified). Exact template: `references/verdict-format.md`. The template is stable on purpose: if you use a builder skill that accepts a verdict file (for example a `--qa-verdict-file` argument that renders the verdict verbatim into its diff report), the output drops straight in without any translation step; if you don't, it's still the format to hand a human.

## 4. Stay in your lane

This skill reviews; it doesn't fix. If a check fails, hand the itemized findings back to whoever's implementing the change — don't patch the code yourself inside this review, even if the fix looks obvious. Fixing and reviewing are different jobs on purpose: the same agent doing both reintroduces exactly the bias this skill exists to remove. Once a fix is made, run this skill again from a fresh context — don't let the subagent that just found the problems be the one that confirms they're solved, for the same reason an implementer shouldn't grade their own work.
