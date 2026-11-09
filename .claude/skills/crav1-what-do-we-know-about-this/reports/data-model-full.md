# report-data-model-full

Read `reports/common.md` for the exception that belongs to this word. Do not open any other file in `reports/`. Do not open `references/walk.md`. There is no short form and no walk.

This word reviews one saved model. It does not model again. It does not run `/crav1-model-data`.

## Find the model

The question names a model slug or a `docs/data-model/<model>/` path. A spec may carry `Data model: docs/data-model/<model>/`. None of those: say so and stop. Do not pick a model by scanning. Two models named: list them and ask.

Read the saved files only: `index.md`, `confirmed.md`, `proposed.md`, `questions.md`, `comparisons.md`, `sources.md`, and `checkpoint.md` when it exists.

## Write the snapshot

Run `scripts/model_run.py report` from skill `crav1-model-data`:

`python3 <crav1-model-data>/scripts/model_run.py report --home docs/data-model/<model> --now <ISO time> --kit <version>`

The script writes `reviews/<revision>-<time>/report.md` and `report.pdf` for that revision. It does not change `confirmed.md` or `proposed.md`.

The Markdown is the maintained source and keeps the Mermaid fences. The PDF is the same revision with those diagrams drawn. It must contain image objects. If the script exits with an error, show the error and do not invent a PDF. A missing or unsupported diagram is a failure, not a text-only PDF.

No C4. The pictures are the ER diagram and the labelled flow stored on the model.

## What the reader sees

The script's report is the review. It leads with a plain summary, then status, the model, comparisons, worked examples, questions, short sources beside decisions, the diagrams, and the full source list.

Every review names `Review-Version`, the model revision, and the approval lines. `Approved:` on `confirmed.md` is the approval. A missing line means that stage is not approved. Proposed, conditional, and implementable stay distinct. A business-model approval is not a physical-design approval.

Say that a drawn diagram is not method conformance, an enforced constraint, or an empirical result.

## After

The snapshot is immutable. A later model change gets a new review directory. Do not edit the old files.

Comments come back through `/crav1-model-data` as proposed revisions tied to `Review-Version`. That is not approval and it does not change this export. Name that command. Do not run it.

In chat: the revision, the approval lines, and the path of the new snapshot.
