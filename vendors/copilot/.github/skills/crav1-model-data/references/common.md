# Shared modeling rules

Read this with the one flow file the command picked. The other flow file stays closed.

The state machine is `scripts/model_run.py` in skill `crav1-model-data`. Pick the interpreter as `crav1-docs/reference/running-scripts.md` says. Check that `--version` is 3.10 or later. Pass paths the user can see.

Content goes through files so the command line stays small. Use `--input <file.json>` (or `--json <file.json>`) and `--text-file <path>`. Inline `--text` and other short flags stay allowed for small values. Do not put a model, a proposal, or a long comment on the command line. Every command's fields and one example file are in `references/inputs.md`. Read that file when you record. Do not read the script to learn the fields.

The script accepts or rejects the record. It does not score candidates and it does not use a research ledger. It reads its own UTC clock. Do not pass `--now`. That switch exists only for tests, with `--test-clock`.

Never edit model files directly. The script stores a content hash on each write. If a file was changed outside the script, the next command refuses until you restore the last script write and record the change with `revise`. `revise --id <id> --reason "<why>" --input <file.json>` bumps the model revision, keeps the previous text in `history.md`, and sets the item back to proposed. A question stays open. During an open auto run, `revise` stays inside the current correction pass and does not use another pass.

## Discover

Run `discover --root <repo>`. Add `--scope` only when the user gave a scope value.

The output lists candidate specs, why each is in or out of the area view, and the platform view of every candidate. System files are context, not containers. `scope_confirmed` is false. `default_view` is null. Say that in chat. Do not treat a discovered scope as confirmed.

A supplied scope does not widen what you read. Do not open specs the scope excluded in order to complete a platform picture. The platform view is the candidates already found, with local obligations kept.

Starting notes and a saved conversation summary are context. They are not requirements and they are not a transcript.

## Select

Read the included docs and specs before you ask anything. Ask only gaps that could change the recommendation, in one batch. Do not use a fixed questionnaire. Do not default to medallion, a warehouse, or any other method.

Layers, architecture, modeling method, and ownership are separate axes. A choice on one axis does not decide the others. Name them in plain language.

Judge the existing model against the business need first.

- It meets the need: recommend retain, even when the write-up is thin.
- A real gap is small: recommend targeted changes.
- The need is unmet: recommend redesign, with the reason.

Put the best fit first and the reason with it. Add a credible alternative only when one exists. When the evidence does not separate them, record a tie and no best fit. The user chooses. Auto must not set `user_chose`.

When a decision-changing gap is open, the record stays provisional or held. Do not mark it final.

A confirmed decision on an axis stays in force. You may record a revisit. `overrides_binding` is rejected.

Keep three labels apart: what the source requires, whether a candidate fits, and whether the user approved. A supported requirement is not fit. Fit is not approval. Unknown feasibility is not a failure and not an exclusion.

Write the recommendation with `recommend --json`. The script rejects a record that breaks these gates.

## Business meaning, then physical design

Establish questions, concepts, relationships, grain, history, and corrections before a physical design is confirmed. Start concise. Go deeper only where a requirement or an uncertainty needs it.

Propose inferred entities, rules, and relationships with a reason. Set `evidence` to `inference`. Do not describe an inference as a documented requirement.

Record decisions with `decide --json`. Use a short slug. Fields the script stores: `id`, `stage` (`business-model` or `physical-design`), `evidence`, `requirement`, `fit`, `outcome`, `scope`, `axis`, `sources`, `depends`, `conditional`, `implementable`, `grain`, `measure`, `short_source`, `body`.

Check worked examples with `example` before physical approval:

- `double-count` when two grains would be added together.
- `history-window` when a short retained window is asked to cover a longer period. It cannot, unless another source is named and its coverage is known (`other_source_days`). A named source whose coverage is unknown is an open question, not a reconstruction. A start date alone does not prove coverage.
- `schema-not-disproof` when a schema has no history columns. That is unknown feasibility, not proof that history is impossible.
- `correction` when a restatement or void is in the question. A missing correction meaning blocks physical approval.
- `views` for the area and platform obligations.

Store a passing or failing example on the model with `--home` so the review can show it.

Draw one ER diagram for structure and one labelled flowchart for movement, layers, or ownership. Read `references/diagrams.md` first. Store them with `diagram`. An unsupported diagram fails. Do not claim the picture proves a method or a physical constraint.

Physical design must be enough for someone who is not a data scientist to implement: what to build and why, in ordinary words. Types, keys, and grain belong there once the business meaning is confirmed. Manual flow cannot record physical design before the business model is approved. Auto flow may record physical detail only as `status: conditional`, `conditional: true`, `implementable: false`, depending on `business-model`.

A concise transition note (`transition --kind concise`) covers data, history, consumers, and coexistence when the model changes. `Kind: none` blocks physical approval. Detailed migration planning is a sentence that it is offered, not a plan.

## Questions, sources, and drift

Unanswered questions go to `questions.md` through `question`. Name the spec they affect and the provider when you know it. They are not copied into the spec.

Pin each source you relied on with `pin` (path and content hash). `drift` compares those hashes and also looks for internal contradictions, including two grains for one measure, and a recommendation whose best fit leans one way while a decision on that axis is a tie. Clear a real exclusion with the words `tie on axis <axis> excluded` in the reason or in `tie_excluded`. It reports what it checked. It never says that nothing drifted anywhere.

`note-drift` marks the affected proposed decisions, and decisions that depend on them, for review. It does not change unaffected decision text. It does not change `confirmed.md`.

On resume, run `drift` before you revisit anything. Revisit only the affected decisions. Leave the rest.

Missing evidence stays on the question. The choices it blocks stay conditional. Other work continues.

## Approval

`approve` needs `--stage`, the exact `--revision` from `index.md`, `--date`, and `--yes`. Use `--yes` only after the user in this turn approved that stage and that revision. Business-model approval appends one snapshot. It does not approve physical design. A later revision needs its own approval. The older snapshot stays in the file.

An open auto run cannot approve and cannot confirm scope.

## Offers, not actions

The index lists three offers. Leave them as offers until the user asks in a later turn:

- schema or migration code
- a detailed migration plan
- spec edits, through `/crav1-add-to-spec`

`link-line --name <model>` prints `Data model: docs/data-model/<model>/`. After a yes, add only that line to the spec. Do not run `/crav1-add-to-spec`.

## Review

Do not write the review here. Name `/crav1-what-do-we-know-about-this report-data-model-full <model>`. Bringing comments back is `feedback` on this skill: it appends a proposed revision and does not change the export or `confirmed.md`.
