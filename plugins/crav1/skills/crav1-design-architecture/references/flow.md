# Design flow, step by step

Prompt budget for one run: one framing card for a new or changed goal (its scope round included), then one card per decision, plus at most 3 narrowing questions per decision when `ask-me` is picked. One decision per round. No cap on how many decisions a session may settle.

## Cards in this skill (1.189.0)

- At most 4 options per card. Typed input (your own idea, a point to talk through, a question for a person, research, skip) goes through the card's free-text Other answer; the card text says what Other is for. Never add an option that only says to type, to add an idea or to keep talking.
- One question per card. Never put a second question on the same card, least of all one that only matters if the first answer is yes.
- An empty Other, with no text, is a missing answer: ask that one question again. It is never a yes or a no.

## Saved inputs and notes (1.189.0)

Write every `--input` file in the topic folder, `docs/architecture/designs/<topic>/inputs/<move>.json`, never in a temp or session scratch folder; the script refuses an input file outside the specs repo. Discussion that is not yet a script move, such as an improvement scan, a vision or target sketch, a scope list or the user's answers, goes into `note --topic <topic> --kind scan|vision|scope|answers|goal|other --title "<title>" --input inputs/note.json`, which appends to `notes.md` in the topic folder.

## Step 0: Route

`status` reads and stops; it shows each topic's links both ways (`builds on` and `built on by`). `resume` runs the script move `resume --topic <topic>` and continues at the first open or reopened decision, or at a stage marked `needs another look`. `park` first saves anything discussed but not yet in a script move with `note`, then runs `park` and ends. `fan-out`, `stage-it`, `go-ahead`, `compare-topics` and `prepare` go to those steps.

A different goal for a topic that already exists goes to Step 2a, `change-goal`; do not offer to recreate the topic. Idea text that builds on an existing topic, or `builds-on <base>`, goes to Step 2b. On `resume` of a linked topic, name the decisions the base settled or reopened since the last run (`base_settled_since`, `base_reopened_since`) before the next decision. A run without the user passes `--headless`; the script then refuses every move except status, resume, lean, note, compare, compare-topics, review and ending.

When `resume` refuses because the topic is on its design branch, give its Run next as-is: it names `git switch design/<topic>`.

Design branch update: `resume`, `create` on an existing design branch, `fan-out`, `stage`, `go-ahead` and `change-goal` fetch and check whether `design/<topic>` is behind `origin/main`, and for a linked topic behind `design/<base>`. When it is, the result has `branch_sync` with a card; show it before going on.

Card: Merge origin/main into the design branch before going on?
- **Merge it in (Recommended)** (`yes`): run `branch-behind --topic <topic> --yes`, which merges with `git merge --no-ff`, never a rebase. Why: the design then reads what is on main now.
- **Stop** (`stop`): merge nothing; the design branch stays as it is and the step waits.

On a conflict the script merges nothing, names the conflicting files and gives a Run next with the merge command. A run without the user names `yes` and `stop` and never merges.

Base to linked update: after a change to a base topic (settle, a changed lean, `change-goal`, a revisit settled or reopened there, go-ahead) is committed, the ending lists each linked topic whose `design/<linked>` branch is behind `design/<base>` (a `Behind` line), and `settle`, `lean`, `change-goal` and `go-ahead` return `linked_sync` with one card for all of them.

Card: Merge the base design branch into the linked design branches?
- **Merge it into each (Recommended)** (`yes`): run `linked-behind --topic <base> --yes`, which switches to each linked branch, runs `git merge --no-ff design/<base>`, and switches back to the base branch; never a rebase. Why: the linked topics then read the base decisions as they are now.
- **Stop** (`stop`): merge nothing; the linked branches stay as they are.

One yes covers every branch listed. A conflict stops on that branch: the script merges nothing there, names the files, leaves the remaining branches untouched and gives a Run next. A run without the user names `yes` and `stop` and merges nothing.

## Step 1: Read what is already known (no writes)

Read widely and cite paths in the framing:

- `docs/architecture/spec.md` and `docs/architecture/left-out.md`
- `docs/system/landscape.md`, `repos.md`, `diagrams.md`, `glossary.md`, `security.md` (kept risks), `docs/system/adr/`
- environment, infrastructure and hosting docs, including `docs/environments/` and marks, plus config that shows how dev, test and prod actually run
- `docs/research/*.md` that touch the ask, with their stale marks. A stale note is shown as stale, never used as current
- slice specs, diagrams and ADRs when the ask touches a slice, and for every slice whose plan touches the ask (environments, pipelines, infrastructure, hosting): `docs/specs/<slug>/plan.md`, `tasks.md`, `build-map.md` and its open branches. Planned and in-flight work is an input or a fixed fact: name it as already planned, with its slug and task, and never propose it again as a new option or decision; saved data models under `docs/data-model/` when the ask touches data
- the topic's own sandbox; code and config in the linked repos when a fact or a check depends on them

When `docs/architecture/spec.md` is missing, say so once and offer `/crav1-existing-to-specs repos-only one-spec` as a first step. The user may still go on with system notes, environment docs and code only.

## Step 2: Frame the goal

One short reply: what they asked, quoted; the proposed goal (end goal, drivers, constraints, criteria, which may cover the whole landscape); what is fixed (accepted ADRs, constraints, approval items, current environment or hosting facts); what is already open; and the decisions that look necessary, dependencies first. That list is a starting map, not a cap.

Scope round, inside the framing: before any detailed decision, ask what else the change should cover, and list the candidate improvements the docs already raise (not the ones already planned, Step 1). Then order the decisions big shape first and detail last. Mark a detail decision (naming, resource groups, per-item settings) with `"detail": true` in `decisions`; `resume` proposes detail decisions only after every big one is settled, skipped or dropped.

Card: Is this the right goal, scope and decision order?
- **Yes (Recommended)** (`yes`): keep the goal, the scope and the order as shown and start the first big decision. Why: it follows the ask and what the docs show.
- **Not yet** (`not-yet`): keep talking about the goal before anything is written; nothing is created.

Other: type what to add, drop, reorder, split or change, and the goal is shown again. An Other that only adds a constraint may go ahead; quote the added line in the reply.

After the yes, run the script move `create --topic <topic> --input inputs/goal.json`. It creates or checks the design branch `design/<topic>`, writes `goal.md` and starts one design. Unknown input keys are refused by name; put anything else under `notes`, which is saved with `note`.

A change that needs no design choice is a small fix, not a decision: `small-fix --topic <topic> --text "<fix>"`. It is listed under `## Small fixes` in `design.md` and copied at go-ahead with no ADR.

## Step 2a: Change the goal of an existing topic

Write the new goal as JSON (only the fields that change: `ask`, `end_goal`, `drivers`, `constraints`, `criteria`, `decisions` in the new order, `renames`, `drop_reasons`, `reopen`). Run `change-goal --topic <topic> --input change.json --reason "<why>"` without `--yes`: it writes nothing and returns the old goal, the new goal, the change lines and the decisions it would flag. Show them side by side.

Card: Change the goal as shown?
- **Yes (Recommended)** (`yes`): rewrite the goal, log the change, and mark the flagged decisions for another look. Why: the history stays and nothing settled is lost.
- **Keep the old goal** (`keep-goal`): nothing is written and the topic keeps its goal.

Other: type what to adjust, and the card is shown again.

After the yes, run the same move with `--yes`. Name the flagged decisions, then `resume` continues at the first one.

A decision touches the change when it is dropped, when it is renamed while settled or leaning, when `reopen` lists it, or when it is settled or leaning and its title, lean, recommendation or draft ADR outcome names a word from a removed constraint, criterion or driver that no kept goal line still uses.

## Step 2b: A topic that builds on another

Frame the goal as in Step 2, and show the base topic's settled decisions as fixed. After the yes, run `create --topic <topic> --builds-on <base> --input inputs/goal.json`. The script cuts `design/<topic>` from `design/<base>` and returns the commands it stands for: `git switch design/<base>`, then `git switch -c design/<topic>`. Base updates come in with `git merge design/<base>`; never rebase.

When the user wants a base decision changed, the script refuses the local move. Offer the revisit on a card (`send-revisit` or `keep-it`); after `send-revisit`, run `revisit --topic <topic> --decision "<words>" --reason "<why>"` and give its ending.

## Step 3: Design the end state, one decision at a time

Index line every turn, titles only, in the stored order (the order added, or the goal's order after `change-goal`), current one marked. Decisions and open questions keep that order; `resume` picks the first reopened one, then the first open big one, then the first open detail one. For the current decision show the decision and what it unblocks, 2 to 5 drivers each citing a source or `(from you, this session)`, 2 or 3 options in the shape in `options.md`, and the recommendation first with *Why*. Then the card in `options.md`. Nothing is settled until the user picks a `choose-*` word. Save options and a lean with `lean`.

## Step 4: Back-and-forth

- `discuss` or plain chat: answer, adjust options or drivers, re-show only what changed. A `discuss` with no text never gets an open question back: show the two or three most likely talking points on a card instead.
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

Before the ending, anything discussed but not yet in a script move goes into `note`.

Recap settled decisions with their draft or accepted ADR paths, open questions, stages, designs still in play, any requirement routed out, and whether go-ahead has happened. Then the ending from the script.
