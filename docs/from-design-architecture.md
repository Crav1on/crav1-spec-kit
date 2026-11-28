# Design the architecture

Kit not in this project yet? [Install first](install.md) (Cursor and Claude Code; the slash commands match, the files do not). After a Cursor plugin install, the short command loop is [plugins/crav1/README.md](../plugins/crav1/README.md).

Use this when you want to decide how the architecture should change, by comparing options and discussing them. The command is [`/crav1-design-architecture`](reference/skills/crav1-design-architecture.md). It is a preview in 1.181.0.

Architecture here means the whole landscape: systems and services and how they connect, environments such as dev, test and prod, infrastructure and hosting, data flows, integrations, and deployment.

This is cross-cutting. It may run from any lane. It does not move work into Specify, Plan, or Build. It is a later skill, not a starter option.

| You want to… | Use |
| --- | --- |
| Have the current spec critiqued | `/crav1-review-architecture` |
| Fix numbered defects in one spec | `/crav1-tighten-spec` |
| Answer questions already written in a spec | `/crav1-resolve-open-questions` |
| Decide how the landscape should change | `/crav1-design-architecture` |
| Design a slice's screens before the plan | [`/crav1-design-ui`](from-design-ui.md); when a slice needs both, it runs first (1.211.0) |

## 1. Start

`/crav1-design-architecture` with or without a topic, and with or without the word `resume`, opens the same status screen. It says where you are, what is waiting, and the commands you can type, each label above one command. `resume` does not change that screen.

With no topic yet the screen offers to start one. With decisions still open, **Next decision** is first. When every decision is settled it offers stages, the proposal and go-ahead.

Since 1.201.1 the screen starts with Run next and one reason. A topic that lives only on `design/<topic>` while this checkout is another branch offers the switch card. When every open decision is waiting on named people, Run next names `/crav1-show-or-ask-open-questions` and the proposal. A parked screen has no Park command. An ended screen's one command is `reopen`. Each question records `Asked: <date>`, and a waiting line names each person once. Dated pages under `docs/architecture/proposals/<date>/` count as the proposal. A JSON resume leaves Status as it is, including parked. A source that changed still marks that one decision reopened. Run the design script from the repo root, the folder that holds `docs/`.

Type an idea when you start a topic:

`/crav1-design-architecture orders should retry failed payments without blocking checkout`

After you say yes it starts a topic, for example `orders-payment-retry`, with one design, on a branch such as `design/orders-payment-retry`. The session stays open until you park or end it.

## 2. One decision at a time

Each decision shows two or three real options, the recommended one first with its reason. Each option says what changes, how environments differ, cost, risks, how it fits the drivers, and what it would reverse. Reply with one word:

- `choose-a`, `choose-b`, `choose-c`, or `choose-mine` settles the decision and writes a draft ADR in the design folder. `settle-preview` lists what is still open and recommends one by one; a yes there settles nothing, and there is no settle batch (1.200.0).
- `discuss` keeps talking; `ask-me` asks up to three short questions first; `add-my-idea` adds your own option, scored the same way.
- `to-question` or `to-research` writes an open question in the design folder, naming who has the fact or who decides.
- `skip-for-now` moves on.

Every move is saved. `park` prints `Session parked` and `/crav1-design-architecture orders-payment-retry`. Typing that command again opens the same status screen. `next` is the guided card.

## 3. Fan out and stage, when you want

- `fan-out` starts a competing design under the same goal, as a copy or from a blank start. `compare.md` scores the designs against the shared criteria.
- `stage-it`, once the end state is designed, suggests a split with reasons. You name, merge, split, reorder or rename the stages. A stage can wait on someone else's decision.
- `compare-topics` compares designs from two different topics, only when you ask, with criteria you pick.

A run without you, such as a bot, may only `prepare`: gather facts, draft options and refresh comparisons. It never decides.

## 3a. Change the goal, or build on another topic

- `change-goal` changes an open topic's goal in place: the ask, the end goal, drivers, constraints, criteria, and which decisions are on the list and in what order. A card shows the old and the new goal before anything is written. Each change is logged in `goal.md` with the date and the reason. A dropped decision stays, marked dropped with its reason. A settled decision the change touches, for example one that leaned on a constraint you removed, is marked for another look, and `resume` starts there. You never have to recreate a topic to change its goal.
- `builds-on orders-platform` followed by your idea starts a topic that builds on `orders-platform`. Its design branch is cut from `design/orders-platform`, and updates come in by merging that branch, never by a rebase. The base topic's settled decisions are fixed inputs; to change one, the skill sends a revisit to the base topic instead. `resume` names what the base settled since your last run, and `status` shows the link both ways.
- Each topic has its own go-ahead and design pull request. Go-ahead on the linked topic waits until the base topic's design pull request is merged; until then the ending names the base pull request under `Waiting:`.

## 3b. Order, cards, notes and small fixes (1.189.0)

- Decisions and open questions keep the order they were added, or the goal's order after `change-goal`; `resume` starts at the first open one in that order. Framing has a scope round: what else the change should cover, then big decisions first and detail decisions (marked detail) last.
- Each card has at most four options and one question. Your own idea, a point to talk through, a question for a person, research or skip go in the card's free-text answer. An empty free-text answer is asked again.
- Step 1 reads the plans, tasks and build maps of slices the ask touches, so work that is already planned is named as planned and never proposed again.
- Script input files live in the topic folder under `inputs/`. `note` keeps scans, visions, scope lists and your answers in the topic's `notes.md`, and the skill saves open discussion there before it parks.
- `small-fix` records a change that needs no design choice; go-ahead copies it with the design, with no ADR.
- `create` creates or checks the design branch `design/<topic>`. On another branch, a move on that topic tells you which branch to switch to.
- When you resume or start work on a topic, the skill fetches and checks whether the design branch is behind main (or, for a linked topic, its base topic's branch). If it is, a card offers to merge it in with `git merge --no-ff`; it never rebases, and a conflict stops with the file names.
- After you commit a change to a base topic, the ending lists linked topics whose design branch is now behind the base, and one yes merges the base branch into each of them (`git merge --no-ff`, then back to the base branch). A conflict stops on that branch with the file names and leaves the others alone.

## 3c. Order numbers, branches and commits (1.190.0)

- Decisions are stored by title in `design.md`, so two people adding decisions in parallel do not conflict. Each decision carries an order number, which sets the order you see and where `resume` starts.
- On the wrong branch, a card offers to switch to the topic's design branch, and the skill switches itself after your yes. It stops and names the files when you have uncommitted changes.
- A goal file you saved in the topic's `inputs/` folder and that is not in the goal yet is offered as a goal change; the skill never recreates an existing topic.
- When the kit version in the docs and the skill's own files differ, the skill warns and offers `/crav1-update-kit`; when the design branch has an older kit than main, it offers to merge main in first.
- Before the session ends with uncommitted design files, a card offers to commit them. To start a topic that builds on this one, the ending names `/crav1-design-architecture builds-on <base> <idea>`.

## 4. Go-ahead

`go-ahead` first reviews the chosen design for gaps against the goal, conflicts with what is already built or documented, and missing decisions. Fix the findings or accept them. Then the skill copies the design as one block under `## Decided, not built yet` in `docs/architecture/spec.md`, copies its ADRs as accepted with a "Designed in" link, and copies still-open questions into that spec. Rejected designs stay in the topic folder.

## After

After go-ahead the ending names pushing the design branch first, then opening its pull request. Merge it with no tag. Planning comes only after that pull request is merged: then the ending names `/crav1-tighten-spec <slug>` for an affected slice, or `/crav1-plan-from-spec` when no slice exists yet. This command does not run them. See [How a run ends](reference/run-ending.md).

Since 1.188.0 a topic's goal changes in place with `change-goal`, and `builds-on` starts a linked topic whose go-ahead waits for the base topic's design pull request.

Since 1.189.0 decisions keep their order, cards hold at most four options and one question, and `note` and `small-fix` keep discussion and small changes in the topic folder.

Reference page: [design architecture](reference/skills/crav1-design-architecture.md)

Since 1.190.0 decisions carry order numbers, the skill offers to switch branches and to commit before it ends, and saved goal files are offered as a goal change.

Since 1.191.0 the branch checks use your repo's default branch (for example master), not always main.

Since 1.200.0 a requirement that comes up on the design branch ends with Run next first and a full `/crav1-add-to-spec <slice> <text>` command. `stop and commit` commits only because this skill says that phrase is a yes.
