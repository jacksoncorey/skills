# Gathering evidence — detail

Read this when running §1 of SKILL.md. The theme throughout: verify, don't accept. A summary handed to you by the implementing agent is a claim, not evidence — check it against the real thing wherever you can.

## 1. Baseline (the real "before")

- If a pristine preview is already running (e.g. a builder skill or an earlier step set one up), open it and look — don't just read a description of it.
- If nothing is running, stand one up yourself: `scripts/checkout_worktree.sh <repo_root> <label> <base_ref>` creates a real git-checkout copy in a sibling directory (defaults `base_ref` to `HEAD` if not given). This is a real checkout, not a copy anyone typed out, so fidelity to the actual repo state is guaranteed by construction. If the app needs a port, `scripts/find_free_ports.py 2` reserves two free ones in a single call.
- Either way, also read the actual file(s) via `git show <base_ref>:<path>` so you have the literal baseline text to diff against, independent of anyone's summary of what changed.

## 2. Updated implementation (code + rendered result)

- Get the real diff yourself: `git diff <base_ref> <branch> -- <files>`. Don't rely on a bullet-point summary of "what changed" as a substitute for reading the actual hunks.
- If a live preview URL is given, navigate to it and screenshot it — `scripts/screenshot_diff.py --url-a <baseline_url> --url-b <proposed_url> --out-dir <dir>` captures both sides and produces a diff heatmap in one call. If you only have one URL (the proposed one) and a reference image (e.g. a Figma export) instead of a live baseline, use `--image-a <figma_export.png> --url-b <proposed_url>` — the script accepts either input type on either side.
- If no live preview is reachable at all, don't silently skip to a code-only review and call it complete. Say plainly in the verdict that visual behavior couldn't be independently confirmed, and treat check 2 (visual/pixel fidelity) and relevant parts of check 3 (functional/behavioral correctness) as **N/A — unable to verify** rather than guessing a PASS from the code alone.

## 3. Context / directions (what was actually asked for)

- If the directions reference a Figma frame, pull it directly rather than trusting a description of it: `get_design_context` for structure and positions, `get_screenshot` for a rendered reference to diff against, `get_variable_defs` for the actual token values in play, `get_metadata` for frame dimensions (useful for matching viewport size when you screenshot the implementation).
- If the directions reference an existing prototype instead of Figma, read the prototype's real code — the same "verify, don't paraphrase" rule applies to a prototype as it does to a design file.
- If the directions are a chat message, ticket, or brief handed to you as text, take them at face value but flag ambiguity rather than resolving it silently. If the directions say "make the button bigger" with no number, that's not something to privately decide is fine at any size — note in the verdict that the spec itself was underspecified on that point, so whoever reads the verdict knows the target was fuzzy, not that you skipped checking it.
- If two sources of directions conflict (the ticket says one thing, the Figma frame shows another), don't quietly pick one — surface the conflict as a finding. Grading against a target that contradicts itself isn't a real check.
