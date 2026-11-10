# Model the data

Kit not in this project yet? [Install first](install.md) (Cursor and Claude Code; the slash commands match, the files do not). After a Cursor plugin install, the short command loop is [plugins/crav1/README.md](../plugins/crav1/README.md).

Use this when you want a data model from the specs. The command is [`/crav1-model-data`](reference/skills/crav1-model-data.md).

This is cross-cutting. It may run from any lane. It does not move work into Specify, Plan, or Build. It is a later skill, not a starter option.

## Two flows

The word picks the flow. A scope may follow it. The scope is a value, such as `orders dispatch`. You do not type brackets.

| You type | What happens |
| --- | --- |
| `/crav1-model-data manual-flow` | Discovery, then you confirm the scope, the business model, and later the physical design |
| `/crav1-model-data manual-flow orders dispatch` | The same, with that scope guiding which specs are in |
| `/crav1-model-data auto-flow` | You approve a budget, then the run continues. Unconfirmed results stay proposals |
| `/crav1-model-data` | Asks which flow. A headless run with no word stops and names the two words |

Both flows follow the same modeling rules and the same state machine, `scripts/model_run.py` in the skill. Pick the interpreter as [Running a kit script](reference/running-scripts.md) says. Content goes in a file (`--input` or `--text-file`). The fields are in the skill's `references/inputs.md`. Do not edit a model file by hand. `revise` records the new text, keeps the previous text, and sets that item back to proposed.

## What you should see

Discovery lists candidate specs and says why each is in or out. It does not confirm the scope. The area view and the platform view are both available. Neither is the default. A local rule stays local inside the platform view.

The recommendation starts from the business need and the model you already have. Thin documentation is not a reason to replace a model that fits. A tie is explained and left for you. Unknown feasibility is not treated as a disproof.

Manual flow shows the business meaning, small worked examples, and diagrams before any physical design is confirmed. History and corrections are part of that check. A seven-day landing window is not a year of history. A schema with no history columns does not prove history is impossible.

Physical design, once the business model is approved, says what to build and why in ordinary words. Schema and migration code are offered, not generated. A short transition note covers data, history, consumers, and coexistence. A detailed migration plan is a separate offer.

## Auto flow

Before each auto run you see the budget: **20 minutes** and **5 correction passes**, shared across the whole run. You can keep those numbers or change them. The run does not stop to ask you to confirm each stage. It also does not pretend you did. Conditional physical detail stays marked conditional and not implementable.

The first proposal is a baseline. It does not use one of the five passes. A later change to a recorded decision or worked example is `revise`, and during the run that revise stays inside the current pass. The script reads its own clock. Time is checked between passes, not in the middle of one. The run stops when the proposal is stable, when it stalls, when it cycles, or when the budget is used. It says what is unfinished. Nothing watches between runs. A later run is a new invocation and shows the budget again.

## Where it is saved

`docs/data-model/<model>/` holds the confirmed snapshots, the proposal, the questions, the two comparison views, and the review exports. An approval line names the stage and the revision, for example `Approved: business-model r2, 2026-11-08`. That line does not approve physical design, and it does not approve a later revision.

Questions stay with the model and name the specs they affect. The command can add `Data model: docs/data-model/<model>/` to a spec after a yes. It does not edit the spec's requirements. Those edits are `/crav1-add-to-spec`, which this command does not run.

## Review

`/crav1-what-do-we-know-about-this report-data-model-full <model>` reads the saved model and writes one Markdown review and a PDF. It does not model again. The review is built from the saved records: one title, each section once, a line when a section is empty, and a run-ending line near the top (flow, why it stopped, passes and minutes used, checkpoint). The PDF carries the same prose, and diagrams are titled by name, wrapped so the text stays readable, or split across a landscape page. The export is a snapshot. Comments brought back become a proposed revision. They do not approve the model and they do not change the export.

## After

When you asked for the review: `Next: /crav1-what-do-we-know-about-this report-data-model-full <model>, because you asked for the review.` Otherwise `Next: nothing needed now.` When a model file changed: `Uncommitted: 1 file; commit with /crav1-finalize-commit when ready.` A requirement change is later, through `/crav1-add-to-spec`, and is not listed here. This command does not run them. See [How a run ends](reference/run-ending.md).

Reference page: [model data](reference/skills/crav1-model-data.md)
