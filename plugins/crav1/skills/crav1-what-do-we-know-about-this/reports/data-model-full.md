# report-data-model-full

Read `reports/common.md` for the exception that belongs to this word. Do not open any other file in `reports/`. Do not open `references/walk.md`. There is no short form and no walk.

This word reviews one saved model. It does not model again. It does not run `/crav1-model-data`.

## Find the model

The question names a model slug or a `docs/data-model/<model>/` path. A spec may carry `Data model: docs/data-model/<model>/`. None of those: say so and stop. Do not pick a model by scanning. Two models named: list them and ask.

Read the saved files only: `index.md`, `confirmed.md`, `proposed.md`, `questions.md`, `comparisons.md`, `sources.md`, and `checkpoint.md` when it exists.

## Write the snapshot

Run `scripts/model_run.py report` from skill `crav1-model-data`. Pick the interpreter as `crav1-docs/reference/running-scripts.md` says. Do not pass `--now`. The script reads its own clock.

`<interpreter> <crav1-model-data>/scripts/model_run.py report --home docs/data-model/<model> --kit <version>`

The script writes `reviews/<revision>-<time>/report.md` and `report.pdf` for that revision. It does not change `confirmed.md` or `proposed.md`. The snapshot stays immutable.

The Markdown is the maintained source and keeps the Mermaid fences. The PDF is the same revision with those diagrams drawn. It must contain image objects. If the script exits with an error, show the error and do not invent a PDF. A missing or unsupported diagram is a failure, not a text-only PDF.

No C4. The pictures are the ER diagram and the labelled flow stored on the model.

## What the reader sees

The script builds the review from the saved records. It does not paste the model files in. There is one title. Sections and items use heading levels under that title. Each section appears once. An empty section is one line: Approvals says `None yet.`, and Confirmed says `Nothing confirmed yet.`

A run-ending line sits near the top: the flow, the stop reason (`stable`, `stall`, `cycle`, `time`, or `passes`, or that no auto run was recorded), the passes and minutes used of the budget, and whether a checkpoint was written.

Then a plain summary, status, the recommendation, the decisions with their short sources, worked examples in their own section, the confirmed text, approvals, comparisons, questions with their full text, the diagrams, the transition, and the full source list. Obligations are listed once. Dates are ISO (`2026-11-09`). Approval says `Approval: none` when nothing is approved. It does not prefix "Current" to a sentence about no stage.

The PDF carries that same prose: the run-ending line, the recommendation, the decisions, the worked examples, and the questions with their text. Diagrams are titled by their id, such as `platform-structure`. Nodes wrap into rows, or top-down when the flow says so, at a readable text size. A wide diagram gets its own landscape page. If it is still too big, it is split into numbered parts and the page says so.

Every review names `Review-Version`, the model revision, and the approval lines. `Approved:` on `confirmed.md` is the approval. A missing line means that stage is not approved. Proposed, conditional, and implementable stay distinct. A business-model approval is not a physical-design approval.

Say that a drawn diagram is not method conformance, an enforced constraint, or an empirical result.

## After

The snapshot is immutable. A later model change gets a new review directory. Do not edit the old files.

Comments come back through `/crav1-model-data` as proposed revisions tied to `Review-Version`. That is not approval and it does not change this export. Name that command. Do not run it.

In chat: the revision, the approval lines, and the path of the new snapshot.
