---
name: delegate
description: Produces one clean, copy-paste-ready brief that hands the current work off to a human teammate so they can pick it up exactly where the user left off and carry it to completion — the goal and what "done" looks like, high-level context, decisions already made (with the why), open questions, and every resource/access/link the person will need so there's zero back-and-forth. Optimized to be scannable by a human, not a wall of text, AND structured so the teammate can paste it straight into their own AI agent session to keep going. Trigger on "/delegate", "delegate this", "hand this off to [someone]", "package this up for a teammate", "write a delegation brief", "someone else is taking this over", "I need to hand this to [person]", or any request to hand ongoing work to another person. This is DIFFERENT from handoff — handoff is for the same user resuming in their own fresh agent session, while delegate is for another human picking the work up. Use delegate whenever the receiver is a person, not a future session of the same user.
---

# Delegate

Produce a single, self-contained brief that lets a **human teammate** take over
the work the user has been doing and carry it through to completion — without
a single "wait, where's X?" follow-up.

Two things make a delegation brief different from a session handoff, and this
skill lives or dies on both:

1. **A human reads it first.** It must be scannable in thirty seconds, written
   in plain language, free of the user's private shorthand, and free of
   anything the teammate would trivially know. Short bullets over paragraphs.
   Never a wall of text. If a section can be one line, make it one line.

2. **The one missing thing is the whole failure mode.** The pain this solves:
   someone hands over context, the teammate is missing one or two critical
   things — a link, an access grant, the name of the person who knows Y — and
   now it's a back-and-forth. So the brief captures every dependency the
   teammate needs and doesn't already have, and for each one either provides it
   inline or says exactly where to get it.

The output is also structured so the teammate can drop the whole thing into
their own AI agent (Claude, etc.) as a first message and have it act with full
context. That means concrete specifics — exact paths, URLs, commands — not
vague gestures.

## Process

### 1. Reconstruct the work from the session

Read back over the whole conversation (not just the last few turns) and pull
out, translating everything out of internal shorthand into language a teammate
who wasn't here will understand:

- **The goal** — the outcome the teammate is being asked to deliver, in one or
  two sentences. Not the task history — the target.
- **Definition of done** — a concrete, checkable description of what finished
  looks like. This is the most important line in the brief; a delegation
  without it drifts. Make it something the teammate can point at and say "yes,
  that's complete."
- **Why it matters** — a few sentences of high-level context so the teammate
  can make good judgment calls, not just follow steps. Keep it tight.
- **Where things stand** — what's already done (as facts that are true now),
  and what's in progress and exactly how far it got.
- **Decisions already made** — what's been settled, each with its one-line
  *why*, so the teammate doesn't unknowingly re-open or reverse them. These are
  the "hard decisions" — carry the reason or they get re-litigated.
- **Open questions** — what's genuinely unresolved and needs the teammate's (or
  the user's) judgment. Be honest about what's a real fork vs. already decided.
- **Where to start** — the concrete next actions, in order.

If any of this was informed by context the user has saved elsewhere, **inline
the relevant facts as plain context** — do not point the teammate at the
user's personal memory files, local paths like `~/.claude/...`, or anything
they can't open. The teammate gets self-contained prose, never a pointer to
something private to the user.

### 2. Capture everything they'll need (the anti-back-and-forth step)

This is the step that earns the skill its keep. Walk the work and list every
dependency the teammate needs and probably doesn't already have. For each one,
either give it inline or say exactly where to get it. Cover at least:

- **Files & docs** — links and exact paths. Name what each is, not just the URL.
- **Repo / branch / environment** — where the code lives, which branch, any
  setup or run commands, exact ports.
- **Access & tools** — accounts, connectors, permissions, or systems they'll
  need, and *how to get access* (who grants it, where to request it). **Never
  paste secrets** — API keys, passwords, tokens. Point to where they live
  (password manager, etc.) instead.
- **People** — who knows what. For each name: the one thing they're the go-to
  for, and when to loop them in. This is often the single most valuable line
  and the one most likely to be missing.
- **Reference material** — prior examples, style guides, tickets, threads the
  teammate should read before starting.

Flag anything you suspect the teammate lacks access to right now, so getting
unblocked is their first move rather than a surprise three steps in.

### 3. Write the brief

Output **one clean markdown block**, written first person from the user to the
teammate, scannable, plain-language. It should read like a sharp, respectful
handoff from a colleague — warm but concise, not robotic, not chatty. Use this
shape:

```
Hey — handing this one to you. Everything you need to pick it up and run with
it is below, and you can paste this whole thing into an AI agent (Claude, etc.)
as a first message if you want it working alongside you with full context.

**The goal:** <the outcome, 1–2 sentences>
**Done looks like:** <concrete, checkable definition of done>

**Why it matters:** <2–4 sentences, high level, plain language>

**Where it stands:**
- Done: <…>
- In progress: <… and how far it got>

**Decisions already made** (please don't reverse these without checking with me):
- <decision> — <why>

**Open questions / your call:**
- <…>

**What you'll need:**
- Files & docs: <names + links/paths>
- Repo / branch / setup: <… incl. exact commands + ports>
- Access & tools: <what, and how to get it — no secrets here; those live in <where>>
- People: <name — what they're the go-to for, when to loop them in>
- Worth reading first: <…>

**Where to start:**
1. <…>
2. <…>

If something here is genuinely missing, ping me — but I've tried to make sure
it isn't.
```

Omit any section that's actually empty (no open questions, no in-progress work)
rather than leaving an empty header — a stray "Open questions:" with nothing
under it just makes the teammate wonder what got cut. Keep every section as
short as it can be while still being complete. Concrete beats comprehensive:
one exact path is worth a paragraph of description.

### 4. Don't save it anywhere by default

The brief is meant to be copy-pasted straight to the teammate, not filed. Don't
write it to a file unless the user asks. If they do, it's scratch output, never
committed inside a repo.

### 5. Read-only

This skill only reads the conversation. It never edits code, never modifies
memory, and never takes any action beyond producing the brief.
