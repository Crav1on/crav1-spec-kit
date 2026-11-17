# Design flow, step by step

Prompt budget for one run: one framing card for a new or changed goal, then one card per decision, plus at most 3 narrowing questions per decision when `ask-me` is picked. One decision per round. No cap on how many decisions a session may settle.

## Step 0: Route

`status` reads and stops. `resume` runs `design_run.py resume` and continues at the first open or reopened decision, or at a stage marked `needs another look`. `park` runs `park` and ends. `fan-out`, `stage-it`, `go-ahead`, `compare-topics` and `prepare` go to those steps. A run without the user passes `--headless`; the script then refuses every move except status, resume, lean, compare, compare-topics, review and ending.

## Step 1: Read what is already known (no writes)

Read widely and cite paths in the framing:

- `docs/architecture/spec.md` and `docs/architecture/left-out.md`
- `docs/system/landscape.md`, `repos.md`, `diagrams.md`, `glossary.md`, `security.md` (kept risks), `docs/system/adr/`
- environment, infrastructure and hosting docs, including `docs/environments/` and marks, plus config that shows how dev, test and prod actually run
- `docs/research/*.md` that touch the ask, with their stale marks. A stale note is shown as stale, never used as current
- slice specs, diagrams and ADRs when the ask touches a slice; saved data models under `docs/data-model/` when the ask touches data
- the topic's own sandbox; code and config in the linked repos when a fact or a check depends on them

When `docs/architecture/spec.md` is missing, say so once and offer `/crav1-existing-to-specs repos-only one-spec` as a first step. The user may still go on with system notes, environment docs and code only.

## Step 2: Frame the goal

One short reply: what they asked, quoted; the proposed goal (end goal, drivers, constraints, criteria, which may cover the whole landscape); what is fixed (accepted ADRs, constraints, approval items, current environment or hosting facts); what is already open; and the decisions that look necessary, dependencies first. That list is a starting map, not a cap.

Card: Is this the right goal and starting list of decisions?
- **Yes (Recommended)** (`yes`): keep the goal and the list as shown and start the first decision. Why: it follows the ask and what the docs show.
- **Change it**: type what to add, drop, reorder, split or change in the criteria, and the goal is shown again.

After the yes, run `design_run.py create`. It writes `goal.md` and starts one design.

## Step 3: Design the end state, one decision at a time

Index line every turn, titles only, current one marked. For the current decision show the decision and what it unblocks, 2 to 5 drivers each citing a source or `(from you, this session)`, 2 or 3 options in the shape in `options.md`, and the recommendation first with *Why*. Then the card in `options.md`. Nothing is settled until the user picks a `choose-*` word. Save options and a lean with `lean`.

## Step 4: Back-and-forth

- `discuss` or plain chat: answer, adjust options or drivers, re-show only what changed.
- `ask-me`: at most 3 multiple-choice questions about this decision only, then re-show it.
- `add-my-idea`: the idea becomes its own **Your idea** option.
- A point that needs another decision first: say so, offer to move it up, move on only after a yes.

## Step 5: Settle a decision

On `choose-*`, run `settle`. It writes a draft ADR from the ADR template in `designs/<name>/adr/` (status `draft`, every option shown under Considered options, the user's idea among them), marks the decision settled in `design.md`, updates the end state, adds the draft diagram (planned parts dashed and labelled `planned`), and refreshes `compare.md` when the topic has more than one design. A stage the change affects is marked `needs another look`. A revisit needs `--revisit-yes` after a separate yes. Recap: **Added / Changed / Still open**.

Optional batch: when 3 or more decisions remain and each has a clear recommendation, offer the kit's batch card from `question-cards.md`. `D#` is display only. A run without the user never uses it.

## Step 6: Unsettled points

- `to-question`: `question --kind question`. The text ends with who has the fact or who decides, for example `(person A decides whether prod may use the new queue)`. The ending can name that person under `Waiting:`. When the answer comes back, run `answer`.
- `to-research`: `question --kind research --research <topic>`. The ending may name `/crav1-show-or-ask-open-questions ask research <topic>`. No `Pending:` mark is written in a spec.
- `skip-for-now`: `skip`. The decision stays open.

## Step 7: Fan out

`fan-out --mode copy` or `--mode blank`. From then on `compare.md` scores the designs against the shared criteria. Still one decision at a time, on one design at a time.

## Step 8: Stage it

Only after enough of the end state is designed. Suggest a split with reasons, for example "stage 1 can ship the retry in test without a new queue in prod". The user merges, splits, reorders or renames. Then run `stage`. A stage that waits on a stakeholder decision has an open question naming who decides. Staging is never required.

## Step 9: Compare across topics

Only when asked. Ask which criteria to use, then run `compare-topics --asked`. It writes one file under `_compare/` and changes neither topic's `goal.md` nor `compare.md`.

## Step 10: Go-ahead

Read `go-ahead.md`.

## Step 11: End

Recap settled decisions with their draft or accepted ADR paths, open questions, stages, designs still in play, any requirement routed out, and whether go-ahead has happened. Then the ending from the script.
