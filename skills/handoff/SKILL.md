---
name: handoff
description: Produces one copy-paste-ready prompt that captures the complete context of the current Claude Code conversation — objective, decisions and why, everything completed, open questions, next steps, exact file paths/URLs/commands, user preferences expressed this session, and relevant saved memory — so you can paste it as the first message into a brand-new session and resume with zero information loss. Trigger on "/handoff", "handoff", "give me a handoff", "write a handoff prompt", "start a new session with this context", "I need to reset my context window", "spin up a fresh session for this", "this thread is getting long, help me continue elsewhere", or any request to move ongoing work into a new conversation without losing context. This is NOT the same as compacting or summarizing in place — it is specifically for STARTING a brand new thread.
---

# Handoff

Produce a single, self-contained, paste-ready prompt that lets the user start a
**brand-new** Claude Code session and pick up exactly where this one left off
— no re-explaining, no re-discovering state, no repeated mistakes.

The failure mode to design against: a summary that reads fine but is missing
the one exact port number, file path, or "no, don't do X" that the old session
only mentioned once. A real handoff preserves load-bearing specifics verbatim;
a lossy one paraphrases them into mush. When in doubt, quote exactly rather
than summarize.

## Process

### 1. Reconstruct the session from the transcript

Read back over the current conversation (not just the last few turns — the
whole thread) and pull out:

- **Objective** — what the user is actually trying to accomplish, in their
  words where possible, and why (the motivating context, not just the surface
  task).
- **Decisions locked in** — anything settled during this thread, plus the
  reason it was decided that way. A decision without its "why" gets silently
  re-litigated by the new agent; always carry the why.
- **Completed work** — concrete things already done: files created/edited
  (with paths), commands run, servers started, branches created, research
  findings established as fact. Write these as things that are true now, not
  as a changelog.
- **In-progress / partially done work** — anything started but not finished.
  Be explicit about exactly how far it got.
- **Open questions and blockers** — anything unresolved that needs the user's
  input or a judgment call the new agent shouldn't make unilaterally.
- **Next steps** — the concrete next actions, in order, as the old session
  understood them.
- **Exact references** — file paths, directory paths, repo names, branch
  names, URLs, port numbers, env var names, command flags, IDs. Copy these
  character-for-character out of the transcript. Do not retype from memory.
- **User preferences and feedback expressed this session** — corrections
  the user made ("don't do X", "no, use Y instead"), approaches they confirmed
  worked, and anything about how they want to collaborate that surfaced in
  this thread specifically. This is the material most likely to get silently
  dropped by a generic summary, and losing it means the new agent repeats a
  mistake the user already corrected once.

If the session touched a git repo, note the working directory, branch, and
whether there are uncommitted changes — the new agent should verify current
git state itself rather than trust a stale snapshot, but it needs to know
where to look.

### 2. Pull in relevant saved memory

Claude Code's auto-memory index for a project lives at
`~/.claude/projects/<project-slug>/memory/MEMORY.md` — the exact path for the
current project is usually already visible in this session's system context
(look for the "auto memory" section). If it isn't visible, derive it from the
current working directory using that same slug convention, or run:

```bash
find ~/.claude/projects -maxdepth 1 -iname "*$(basename "$PWD")*"
```

If the project has no memory directory at all, skip this step and say so in
the handoff rather than inventing one.

Read `MEMORY.md`, then read the individual memory files (linked from the
index) that are actually load-bearing for *this thread's* topic — not the
whole memory store. A memory file irrelevant to what this session was about
just bloats the handoff and dilutes the parts that matter. Pull in enough of
each relevant memory's content that the new agent doesn't need to re-open the
file to use it (paths, decisions, gotchas) — but skip memories the new agent
would trivially rediscover by reading the current code.

Also check `~/.claude/CLAUDE.md` (the user's global instructions) and any
project `CLAUDE.md` only if this session surfaced something that specifically
interacts with them (e.g. a decision about where a deliverable should live) —
don't restate boilerplate the new session will load automatically anyway.

### 3. Write the handoff prompt

Output **one fenced code block** containing the entire handoff, written in
first person addressed to the new agent, so pasting it in as the first
message re-establishes full context with zero extra framing needed from the
user. Use this structure inside the block:

```
You are picking up a Claude Code session already in progress after a context
reset. Everything below is verified context carried over from the prior
session — treat it as ground truth for what happened and was decided, but
re-verify anything time-sensitive (file existence, git status, running
servers, current prices/data) before acting on it, since real-world state may
have moved on since this was written.

## Objective
<what the user is trying to accomplish and why>

## Current state
- Working directory:
- Repo / branch / uncommitted changes (if applicable):
- Running servers / background processes (if any):
- Key files touched this session:

## Decisions locked in
- <decision> — why: <reason>

## Completed
- <concrete things already done, as present-tense facts>

## In progress
- <anything partially done, and exactly how far it got>

## Open questions / blockers
- <anything unresolved that needs the user's input>

## Next steps
1.
2.

## Exact references
<file paths, URLs, ports, commands, IDs — verbatim>

## User preferences / feedback from this session
- <corrections or confirmations the user gave, so you don't repeat a mistake>

## Relevant saved memory
<condensed, relevant pulls from MEMORY.md and its linked files — not the full index>

---
Resume exactly where this left off. Don't re-ask anything already answered above.
```

Omit any section that's genuinely empty (e.g. no open blockers) rather than
leaving a placeholder — an empty "Open questions" header just makes the new
agent wonder if something was cut off.

### 4. Don't save it anywhere by default

The handoff is meant to be copy-pasted directly, not filed away. Don't write
it to a file unless the user explicitly asks — if they do, it's scratch output
(the session scratchpad, or whatever scratch directory the user keeps for
transient files), never inside a repo.

### 5. Read-only

This skill only reads the conversation and memory files. It never edits code,
never modifies memory, and never takes any action beyond producing the prompt.
