---
name: crav1-model-data
description: >-
  Use when the user wants a data model from the project's specs.
  manual-flow confirms each stage. auto-flow runs after a budget
  approval and leaves every unconfirmed result a proposal. Same
  modeling rules. Optional scope. Does not edit specs or generate
  schema code unless the user asks.
disable-model-invocation: true
icon: database
color: blue
---

# Model data

The user wants a data model for one scope. You read the project's docs and specs first. You do not start from a fixed questionnaire or from a medallion default.

Command: `/crav1-model-data`.

This is cross-cutting. It is not a lane. It may run from any lane. It does not move work into Specify, Plan, or Build. It does not start those lanes.

This command is a later skill. It is not a starter option. When the user asks for startup options, name only `/crav1-spark-to-spec`, `/crav1-ideas-to-spec`, `/crav1-bundle-to-specs`, `/crav1-existing-to-specs`, `/crav1-read-environment`, and `/crav1-fix-bug`. That ask names the list. It does not run this command. The six starter options stay unchanged.

Other skills do not run this one. It may name `/crav1-add-to-spec`, `/crav1-what-do-we-know-about-this`, and `/crav1-finalize-commit`. It does not run them.

## Flow words (1.118.0)

Route first, load second. The word after the command is the flow. A scope may follow it. The scope is an optional value. Do not ask the user to type the characters `[scope]`.

- **No flow word:** ask one question. Options: `manual-flow` (Recommended), `auto-flow`. A headless or bot run with no word stops and names those two words. It does not guess.
- **`manual-flow`:** read `references/manual-flow.md`, then `references/common.md`. Do not open `references/auto-flow.md`.
- **`auto-flow`:** read `references/auto-flow.md`, then `references/common.md`. Do not open `references/manual-flow.md`.

When you draw a diagram, read `references/diagrams.md`. Do not open it before that.

Both flows use `scripts/model_run.py` in this skill. That script is the state machine. Do not keep a second copy of its gates in chat, and do not hand-edit the model files. A change to a recorded decision, worked example, question, diagram, or the sources on a decision is `revise`. When you record, read `references/inputs.md`. Do not open it before that, and do not read the script to learn the fields.

## What the words change

The modeling rules are the same. Manual flow stops to confirm scope and to confirm the business model before physical design is recorded. Auto flow, after the budget is approved, runs the steps without those stops. Every unconfirmed result stays a proposal. Auto does not pass `--yes` to `approve` or `confirm-scope` while its run is open.

## Home

The saved model is `docs/data-model/<model>/`. The script creates it. Confirmed text, proposed revisions, questions, comparisons, and review exports stay in separate files. A link on a spec is the line `Data model: docs/data-model/<model>/`, written only after a yes, and only that line. Requirement edits are offered through `/crav1-add-to-spec` and are not written here.

## Stop

Do not edit a spec's requirements. Do not generate or apply schema or migration code. Do not write a detailed migration plan. Do not send anything externally. Do not start a watcher between runs. Do not commit.

End as `crav1-docs/reference/run-ending.md` says. Do not run the next step. Add the Uncommitted line when a model file changed.

- The user asked for the review in this run: `Next: /crav1-what-do-we-know-about-this report-data-model-full <model>, because they asked for the review.`
- Otherwise: `Next: nothing needed now.`
- Do not name add-to-spec in the ending.

## Hard rules

- One skill, two flow words, one state machine.
- A given scope guides discovery. A missing scope discovers candidates and explains inclusion and exclusion. Scope is not confirmed until the user says yes. Auto may propose a scope and must not mark it confirmed.
- Area and platform views both stay available. Neither is the default. A local obligation stays in the platform view and is not promoted to a platform-wide rule.
- Selection comes from the docs and specs. Ask only what could change a decision. Assess the existing model against the business need first. Poor documentation is not itself a reason to redesign.
- Best fit first, with reasons, then credible alternatives only. A genuine tie is explained. The user chooses. Do not manufacture a winner. Auto leaves the tie unresolved.
- A confirmed architecture decision constrains the recommendation. Flag a revisit. Do not override it in silence.
- Unknown feasibility is not disproof. Requirement evidence, candidate fit, and approval are different.
- Business meaning comes before a confirmed physical design. Inferred entities stay labeled as inference until the user approves that stage and revision.
- `Approved: <stage> r<n>, <date>` records that stage and revision only. A business-model approval does not approve physical design or a later revision.
- The last confirmed text stays until an explicit approval appends a new snapshot. Review comments become proposed revisions. They are not approval. A hand edit of a model file is not a revision. `revise` keeps the previous text and sets that item back to proposed.
- Schema, migration code, detailed migration planning, and spec edits are offered, not done.
