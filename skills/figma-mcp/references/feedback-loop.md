# The feedback loop

Why the review is done by someone else, how to brief each reviewer, what they return, and when the loop stops.

## Why fresh eyes

An agent verifying its own work compares the output to the mental image that produced it, so the two agree by construction. A reviewer with no memory of the build compares the output to the sources. That only works if the reviewer really is fresh: briefed from files on disk, not from a summary the builder wrote. It re-queries Figma and the browser itself rather than trusting screenshots the builder chose.

Reviewers never edit. They return findings; the core agent decides and fixes. A reviewer that returns an empty table without listing the tools it called has not reviewed, and the loop has not passed.

## Which model runs which reviewer

Reviewers that diff and measure can run on a cheaper model; reviewers that judge stay on the strong one. The findings format and the stop rule are the same either way, and the orchestrator reopens every cited node before acting on a cheap model's row.

| Reviewer | Model | Why |
| --- | --- | --- |
| Brief check | strong | One short run; questions 2 and 5 are judgment against the request |
| Coverage auditor | cheap | A ledger diff against a metadata tree |
| Fidelity, script half per section | cheap | Runs the five checks in designing-in-figma.md and returns offender lists with values; the orchestrator grades them |
| Fidelity, numbers against source, per section and on the finished page | strong | Judges which differences the user would notice first |
| Vision | strong | Taste against the brief and the request |

Pass the model in the harness's own way (a `model` parameter on the Agent tool, a sub-agent definition) and record which model ran each reviewer in the report.

## Filling the briefs

The briefs below are the whole message the sub-agent receives, so everything in angle brackets is filled by the core agent from its own session before sending:

- `<TOOL NAMES>`: the exact deferred tool names the core agent resolved, comma-separated, including `get_figma_skill` on the remote server and the harness's browser tools when a website is involved. Sub-agents start with these deferred and will otherwise report that they have no Figma access.
- `<SKILL LOADING>`: either "run `/figma-use`" when the Figma plugin is installed, or "read `skill://figma/figma-use/SKILL.md` with `get_figma_skill`" on the remote server. Same for `figma-design-to-code`.
- Absolute paths to the brief, the coverage ledger and this skill's `references/` directory.
- The mode, the file key, the target node ids, the page list, the reference (if any) and the grounding rung claimed. The user's request verbatim, with any answers they gave.
- For design to output: the run command, port, route, and how the state is reached (the user logged in, fixture data, flags). For an audit: the build URL, route, state and frame width. For input to design: the created node ids.
- On a re-run: the previous findings table.
- The brief check reads files only and needs no tool slot.
- On a cheap model, append: "Return node ids and the values you read beside the source values; do not summarise beyond the table. Grade severity only by the definitions given; if unsure, write MEDIUM and say why."
- Every tool-using brief ends with: "If a node is missing or a call fails twice, stop and report what failed instead of improvising."

## The briefs

Copy one, fill the brackets, send it as a separate sub-agent. The three end-of-work reviewers run in parallel; they do not depend on each other.

### Brief check, after grounding

```
You are read-only. Do not edit files, run no use_figma script that mutates,
create nothing. Return findings only; the caller decides.

There is no output yet. You are checking a design brief before work starts.

Brief: <abs path>. Rules you may cite: <abs path>/references/design-principles.md.
The request, verbatim: <quote>. Mode: <mode>. Grounding rung claimed: <n>.

Answer, citing the brief's rows:
1. Every atomic row has a "where seen" or says unknown. List the rows that
   have a value and no source.
2. Does the aesthetic paragraph restate what the user asked for? Quote the
   sentence of the request it serves least.
3. Does the grounding rung match the sources the brief actually cites? If a
   found system is used, was the user asked, and is that recorded?
4. For design to output: which source rows have no target token?
5. Does anything in the brief come from a cross-brand reference other than
   layout, density or mood?

Return one table, most severe first:
| Severity | Location | Source says | Output shows | Fix |
HIGH contradicts the source or the request in a way the user would notice
first; MEDIUM is a measurable miss on a second look; LOW is polish. A
preference with no source is not a finding. Then list the files you read.
```

### Coverage auditor

```
You are read-only. Do not edit files, run no use_figma script that mutates,
create nothing. Return findings only; the caller decides.

You are auditing whether a design was read thoroughly. You did not do the work.

Tools are deferred. Run exactly: ToolSearch query="select:<TOOL NAMES>".
Then <SKILL LOADING> before any use_figma call. If use_figma is not among
the tools, skip every script step and say "not verified" for it.
Scripts: <abs path>/references/node-inspection.md.

Brief: <abs path>. Coverage ledger: <abs path>. Mode: <mode>.
Figma file key: <key>. Pages: <list>. Target node(s): <ids>.
Reference file, if any: <key, read-only>. Previous findings, if a re-run:
<table or "none">.

Do this, in order:
1. Run the page-listing script (or get_metadata with no node id; on the
   desktop server clear the selection first) and get_metadata on each page
   in scope. List every node at depth ≤ 3 that a
   designer would call a unit (nav, hero, card, footer, a component, a
   hidden state), plus the target's sibling frames named for the same screen.
2. Diff that list against the ledger. A unit is inspected only if its row
   names get_design_context or a use_figma dump; metadata or a screenshot
   alone is "seen". Every unit missing or merely seen is a finding, with the
   tool that would have revealed what was missed.
3. Run the hidden-layers script on the target if use_figma is available;
   otherwise report hidden-layer coverage as not verified. Any hidden layer or
   hidden fill that looks like a state (hover, active, error, empty, open) and
   is absent from the ledger is a finding.
4. Pages in the product's own file named for foundations, tokens, styles,
   components or a design system: if any was not read, that is a HIGH
   finding. A cross-brand reference's foundation pages are listed, never
   read, and are not a finding.
5. List the Figma tools the ledger never names. Each is a finding only if
   the mode needed it: get_variable_defs for any mode with tokens;
   get_code_connect_map or Code Connect snippets for design to output when
   the repo has Code Connect files; search_design_system and get_libraries
   for input to design; a use_figma dump wherever hidden states matter.
6. Every atomic row in the brief cites a source. A row with a value and no
   "where seen" is a finding.

Return one table, most severe first, one row per root cause:
| Severity | Location | Source says | Output shows | Fix |
HIGH contradicts the source or the request in a way the user would notice
first; MEDIUM is a measurable miss on a second look; LOW is polish. A
preference with no source is not a finding. Under the table, list the tools
you called. If everything was covered, say "No coverage findings" and still
list what you checked. If a node is missing or a call fails twice, stop and
report what failed instead of improvising.
```

### Fidelity reviewer

```
You are read-only. Do not edit files, run no use_figma script that mutates,
create nothing. Return findings only; the caller decides.

You are checking whether an output matches its source at the level of
numbers, tokens, fonts, names and grid. You did not build it. Use the tools
rather than trusting any screenshot you were handed.

Tools are deferred. Run exactly: ToolSearch query="select:<TOOL NAMES>".
Then <SKILL LOADING> for figma-design-to-code before get_design_context and
for figma-use before use_figma. If use_figma is not among the tools, skip
step 2 and any subtree dump and say "not verified" for them. Browser tools,
if a URL is involved, are in the same select list; save screenshots where
that tool allows and copy them beside the brief.
Scripts: <abs path>/references/node-inspection.md and
<abs path>/references/designing-in-figma.md.
Rules you may cite: <abs path>/references/design-principles.md.

Brief: <abs path>. Ledger: <abs path>. Mode: <mode>.
Source: Figma <key> node <id>, or the reference <url>.
Output: <path, or URL with viewport width, or created node ids>.
Run: <command, port, route, or "n/a">. State: <how to reach it, or "n/a">.
The request, verbatim: <quote>. Previous findings, if a re-run: <table or "none">.

Do this:
1. For every focus unit in the ledger, pull the source values yourself
   (get_design_context, get_variable_defs, or the subtree dump) and the
   output values (computed styles, the created node's properties, or the
   document) and compare: size, weight, line-height, tracking, font family,
   fills and their tokens, gaps, padding, radii per corner, stroke weight,
   shadow layers, grid position.
2. If the output is nodes this skill created, run the checks in
   designing-in-figma.md: on-grid measurement, naming audit, hardcoded
   values, font family assertion, leftover placeholders. Do not run them on
   the user's own frame.
3. For design to output or an audit, open the output at the frame's width
   with the given state and compare against the Figma screenshot (download
   the URL first; set maxDimension to the node's native long edge, the tool
   never upscales). Capture at 2x where the browser tool allows and say when
   you compared at 1x. The diff locates a difference; the measured values
   decide it. Report concentrated differences, not a percentage.
4. Run every row of the "Measurable checks" table in design-principles.md
   that the brief adopts, citing the canvas property named in the row beside
   the observed value.
5. Read back every binding the builder claims (text styles, variables) from
   the final state, not from the ledger; a claimed binding the dump does not
   show is a HIGH finding.

Return one table, most severe first, one row per root cause:
| Severity | Location | Source says | Output shows | Fix |
Every row carries the source value and the observed value. "Looks off" is
not a finding. HIGH contradicts the source in a way the user would notice
first; MEDIUM is a measurable miss on a second look; LOW is polish. Under
the table, list the tools you called. If a node is missing or a call fails twice, stop and
report what failed instead of improvising.
```

### Vision reviewer

```
You are read-only. Do not edit files, run no use_figma script that mutates,
create nothing. Return findings only; the caller decides.

You are judging whether an output is what the person asked for. You did not
build it, and you are reading it as that person and as a senior designer.

Tools are deferred. Run exactly: ToolSearch query="select:<TOOL NAMES>".
Take your own screenshots: on the remote server get_screenshot needs the file
key and node id, returns a URL to download, and maxDimension is set to the
node's native long edge; in a browser, capture at 2x where the tool allows.
Rules you may cite: <abs path>/references/design-principles.md and the
brief. Nothing outside them is a finding.

The request, verbatim: <quote>. Brief: <abs path>, read the aesthetic layer
and the "what the user said" section first. Mode: <mode>.
Figma file key: <key>. Target: <node id, or URL with viewport width and
state>. Reference, if any: <node id or URL>. Previous findings, if a
re-run: <table or "none">.

Answer, with evidence from what you can see:
1. Does the output match the mood, density, color temperament and type
   personality in the brief? Name the first three things that break it.
2. Does it do anything the brief says the system refuses to do (gradients,
   shadows, extra accents, ornament)?
3. Is the importance order right: one primary action, the most important
   thing first, the first screen a table of contents?
4. Would the person who wrote the request recognise this as what they asked
   for? Quote the sentence of the request that is least served.
5. What would a senior designer change first, and does the brief support
   that change? If not, mark it as a preference and put it last.
6. Walk the "rules that need judgment" list in design-principles.md: controls
   distinct from content, voice and copy, hidden-content cues and clipping,
   and the RTL mirror where the product ships to RTL locales. Cite the rule.
7. Provenance: every claim, customer name, number and label on the frame
   traces to one of the inputs or is a named placeholder. A line the sources
   do not contain is a HIGH finding, whatever it says.

Return one table, most severe first:
| Severity | Location | Source says | Output shows | Fix |
Location is a screenshot region or node id; "Source says" cites the brief or
the user's sentence. HIGH contradicts the brief or the request in a way the
user would notice first; MEDIUM is a measurable miss on a second look; LOW is
polish. Then at most five lines of narrative, and the tools you called. If a node is missing or a call fails twice, stop and
report what failed instead of improvising.
```

## Cadence and stop rule

| Moment | Reviewers | Purpose |
| --- | --- | --- |
| After grounding, before work | Brief check | The brief describes what the user asked for and every row has a source. Cheap to fix now, expensive later |
| After each section, input to design only | Fidelity | Catch a drift before it is copied into the next section |
| On the finished page, design to output | Fidelity | One pass over the units in the ledger |
| Before the final report | Coverage, fidelity, vision | The composition pass |

A pass with nothing above `LOW` ends the loop. After a fix, the core agent re-runs the same reviewer on the fixed items with the previous table attached, and the loop ends when that re-run is clean. Cap it at three rounds per unit; a finding that survives three rounds goes to the user with the evidence rather than a fourth attempt.

## Mechanisms by harness

- **Sub-agents available** (Agent tool, Task, a worker pool): one sub-agent per reviewer, in parallel, with tool access. The default whenever the tool exists.
- **`/loop` or a self-pacing scheduler**: use it to drive the cadence above without babysitting, with the ledger and the findings tables as the loop state.
- **Workflow orchestration the user opted into**: a pipeline of build-section then review-section per unit, verifying each as soon as its build completes.
- **No sub-agent tool in the session at all**: write the brief, ledger and screenshots to disk, finish the work, then review as a separate pass that re-reads them cold. Say in the report that the loop did not run, because a self-review is weaker and the reader should know. Cost is not a reason to take this path when the tool exists.

## Reviewer budget

Three reviewers at three moments for three rounds is the ceiling, not the plan. A single-section change needs the fidelity reviewer once. A grounding-only task needs the brief check and vision once. An audit needs fidelity once, on the units in question. Scale the loop to the blast radius of the work, and say what you ran.
