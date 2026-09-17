---
name: verify-before-ship
description: Rigorous pre-ship verification pass for high-stakes deliverables, run before anything goes to a client or backs an irreversible decision. Use whenever the user says "run fable", "fable this", "verify before ship", "check this before it ships", "verify this", "sanity check this", "is this right?", "pressure test this", "run a verification pass", "can I trust these numbers", or hands over a report, dashboard, deck, financial figure, contract summary, or analysis and asks whether to ship, send, sign, or act on it. Also self-trigger at the end of producing any client-facing report or any recommendation with money, legal, or reputational consequences — even if verification wasn't requested. Do NOT use for casual drafts, brainstorms, or throwaway summaries.
---

# Verification Pass

Also known as **fable** — "run fable" and "fable this" invoke this skill. The
public name is `verify-before-ship` because "fable" collides with a model name;
the skill itself is unchanged.

A deliverable that sounds right and one that is right feel identical to read. This skill exists because fluent errors ship: they arrive well-phrased, nobody re-derives them, and they get discovered downstream where they're expensive. Your job here is to be the adversary the deliverable meets before the client does.

The full operating manual behind this pass is in `references/fable_handover.md`. Read it when the deliverable is unusually high-stakes (contract, pricing decision, board material) or when this condensed workflow feels insufficient. For routine passes, the workflow below is enough.

## Workflow

Work through these five steps in order. Do not skip to the verdict.

### 1. Identify the load-bearing claims

List the claims that, if wrong, change what the reader does — numbers that drive a decision, causal statements ("the campaign drove the spike"), and anything that will be quoted upward. Ignore decoration. A 40-page deck usually has 5-10 load-bearing claims; find them before checking anything, so effort goes where silent failure lives, not where checking is easiest.

### 2. Re-derive every load-bearing number

Recompute each one from its raw inputs, by a different route than the document used where possible. For every percentage: find both endpoints yourself and divide — that's where flipped signs, wrong bases, and inherited errors hide. For quoted facts: trace to the source, not to the last document that repeated it. Never let the artifact supply the evidence for its own correctness. If the raw inputs aren't available, say so explicitly in the verdict — an unverifiable number is a finding, not a pass.

### 3. Bin every claim: verified / inferred / assumed

Verified: checked against something independent. Inferred: follows from verified facts by reasoning you can show. Assumed: needed but unchecked. The dangerous bin is "assumed wearing verified's clothes" — a claim everyone treats as checked because it's been repeated. Flag those loudest.

### 4. Attack the conclusion

If the deliverable's main conclusion is wrong, what's the most likely way it's wrong? Check that specific way. Three attacks that pay best: the boundary case (does it hold at zero, at the max, at the edge of the date range?); the alternative explanation (what else produces the same evidence — a pricing change, seasonality, a tracking change?); the wanted-answer check (is this the conclusion the author hoped for, and did that leak into what got checked?).

### 5. Deliver the verdict answer-first

Use this exact structure:

```
**Verdict:** Ship / Don't ship / Ship with fixes — one sentence, with confidence.
**Blocking issues:** each one with the wrong value, the correct re-derived value, and where it lives. "None" if clean.
**Flagged assumptions:** what the deliverable relies on that wasn't verifiable, and what would settle each.
**Checked and clean:** one line listing what was re-derived and passed, so the reader knows the pass's coverage.
```

A caveat that changes whether to ship belongs in the verdict line itself, not buried below.

## Example

Input: "Report says revenue grew from $4.0M to $4.2M, a 20% gain. Ship it?"

Output: **Verdict:** Don't ship — the headline growth figure is wrong by 4x. **Blocking issues:** (4.2 − 4.0) / 4.0 = 5%, not 20%; appears in the summary line and likely wherever it was copied from — check sibling figures for the same inherited error. **Flagged assumptions:** the $4.0M and $4.2M endpoints themselves weren't traceable to source data in what was provided. **Checked and clean:** all other percentages in the summary re-derive correctly.

## Quality bar

The pass fails its own purpose if it: rubber-stamps because the document reads smoothly (that's recognition, not verification); hedges everything equally so the real warning drowns; or reports only pass/fail without the re-derived values that let the reader check you. Every "don't ship" must include the corrected value or the specific question that needs answering — a verdict without a path forward just moves the problem.

Before sending, run the five-question self-test at the end of `references/fable_handover.md`.
