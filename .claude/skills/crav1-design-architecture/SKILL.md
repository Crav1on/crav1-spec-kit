---
name: crav1-design-architecture
description: >-
  Use when the user wants to decide how the architecture should change:
  systems, environments, hosting, data flows, integrations or deployment.
  Compares real options one decision at a time in a sandbox, then copies
  the chosen design into the architecture spec only at go-ahead.
disable-model-invocation: true
icon: compass
color: purple
---

# Design architecture

The user brings an idea, a need or a pain point. You work out an architecture change with them. You read what the kit already knows, put two or three real options on the table, argue them out one decision at a time, fold in the user's own ideas, and record each settled choice in a sandbox until the user says `go-ahead`.

Command: `/crav1-design-architecture`.

**Architecture here means the whole landscape**, not only code structure: systems and services and how they connect, environments (dev, test, prod and any others in use), infrastructure and hosting, data flows, integrations, and deployment. Goal criteria, the design, the stages and the go-ahead review may all use these.

This is cross-cutting. It is not a lane. It may run from any lane. It does not start Specify, Plan or Build. It is a later skill, not a starter option. When the user asks for startup options, name only `/crav1-spark-to-spec`, `/crav1-ideas-to-spec`, `/crav1-bundle-to-specs`, `/crav1-existing-to-specs`, `/crav1-read-environment`, and `/crav1-fix-bug`.

Review and tighten find and fix problems in what is written. Design creates new decisions. This skill never critiques the whole spec; `/crav1-review-architecture` never proposes a new architecture.

## Choice words (1.181.0)

Route first, load second. Exact words, no flags, hyphen-only.

- **Idea text, no word:** start a new topic from the text, or add to the topic already open in this chat. There is no `new` word.
- **`resume`:** continue an open topic. An optional topic value may follow: `resume orders-payment-retry`. One open topic: no question. Several: one card listing them.
- **`park`:** stop the current topic; it stays resumable.
- **`status`:** read-only. Show open topics, designs, settled and open decisions, stages and questions. Writes nothing.
- **`fan-out`:** start a competing design under the same goal, as a copy of the current design or from a blank start. The user picks copy or blank.
- **`stage-it`:** suggest a split of the designed end state into stages; the user names and divides them. Optional.
- **`go-ahead`:** review the chosen design, then copy it after the user fixes or accepts the findings. The one step that writes outside the sandbox.
- **`compare-topics`:** one-off comparison of designs from different topics, with criteria the user picks. Never runs unless asked.
- **`prepare`:** gather facts, draft options with recommendations, refresh comparisons. Settles nothing.
- **Nothing at all:** ask one free-text question: *What do you want to change, add or fix in the architecture?* Offer `resume` too when a topic is open.

A run without the user in the chat, such as a bot or a scheduled job, is always `prepare`, even when another word is given. With no word and no idea text it stops with:

```text
Missing choice. Use one of: <idea text>, resume, park, status, prepare.
```

Then read `references/flow.md` for the steps. Read `references/options.md` when you show a decision. Read `references/go-ahead.md` only on `go-ahead`. Read `references/inputs.md` only when you call the script.

## The script owns the sandbox

`scripts/design_run.py` in this skill owns the folder format and every move: create, resume, park, fan out, record a lean, settle, question, answer, skip, stage, compare, compare-topics, review and go-ahead. On Windows run `py -3`, elsewhere `python3` (`crav1-docs/reference/running-scripts.md`). Content goes in through `--input <json file>`. Do not hand-edit the design files, and never tell the user to hand-edit a spec file. The script saves after every move, so any session can stop and pick up again. There is no cap on decisions per session.

The sandbox is `docs/architecture/designs/<topic>/` on its own design branch (recommended name `design/<topic>`). One goal per topic, in `goal.md`. Each design lives in `designs/<name>/` with `design.md`, `questions.md`, `diagrams.md`, `adr/`, and `stages.md` once staged. `compare.md` scores designs in the topic against the shared criteria. One-off cross-topic comparisons go under `_compare/`. No other skill reads this tree, even after the branch is merged.

## Hard rules

- One decision per round, each with a reasoned recommendation first, labelled `(Recommended)`. A real tie is said as a tie.
- Two or three real options at the same level. No straw men.
- The user's own idea is its own option, labelled **Your idea**, scored on the same drivers. Never folded silently into another option.
- Claims in confirmed specs, code or config are facts when the file shows them. Claims in a user-supplied file stay ideas until one of those sources supports them.
- A choice that would reverse an accepted ADR, a constraint, an approval item, or a current environment fact is a revisit and needs a separate yes.
- A requirement that shows up is named as one and routed to `/crav1-add-to-spec` at the end. It is not designed here.
- Design the end state first. Stage only when the user asks. The user names and divides the stages.
- Before go-ahead, write nothing outside the topic folder. Do not write `Asked:` or `Pending:` lines in any spec.
- A run without the user never settles a decision, never stages, never gives go-ahead, and never writes a real ADR.
- Do not commit, push, merge, tag, or open a pull request.

## End

End as `crav1-docs/reference/run-ending.md` says: `Run next:` first, a short reason, then each label on its own line above a command alone in its code span. The script prints it: `design_run.py ending --topic <topic> --input <state.json>`. Give that text as-is. Add the Uncommitted line when files changed.

- After go-ahead, until the design pull request is merged: push the design branch first, then open its pull request. Name no planning step.
- After that pull request is merged: `/crav1-tighten-spec <slug>` for an affected slice, or `/crav1-plan-from-spec` when no slice exists yet.
- During design: `/crav1-design-architecture resume <topic>` when parked or still designing.
