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

## 1. Start with an idea

Type the idea after the command:

`/crav1-design-architecture orders should retry failed payments without blocking checkout`

The skill reads the architecture spec, system notes, environment docs, research and code, then shows one framing card: the proposed goal with its drivers, constraints and criteria, what is already fixed, and the decisions that look necessary. Say yes, or type what to change. After the yes it starts a topic, for example `orders-payment-retry`, with one design.

Work it on its own branch, for example `design/orders-payment-retry`.

## 2. One decision at a time

Each decision shows two or three real options, the recommended one first with its reason. Each option says what changes, how environments differ, cost, risks, how it fits the drivers, and what it would reverse. Reply with one word:

- `choose-a`, `choose-b`, `choose-c`, or `choose-mine` settles the decision and writes a draft ADR in the design folder.
- `discuss` keeps talking; `ask-me` asks up to three short questions first; `add-my-idea` adds your own option, scored the same way.
- `to-question` or `to-research` writes an open question in the design folder, naming who has the fact or who decides.
- `skip-for-now` moves on.

Every move is saved, so you can stop at any point. `park` stops on purpose; `resume orders-payment-retry` picks up at the first open decision in a later chat.

## 3. Fan out and stage, when you want

- `fan-out` starts a competing design under the same goal, as a copy or from a blank start. `compare.md` scores the designs against the shared criteria.
- `stage-it`, once the end state is designed, suggests a split with reasons. You name, merge, split, reorder or rename the stages. A stage can wait on someone else's decision.
- `compare-topics` compares designs from two different topics, only when you ask, with criteria you pick.

A run without you, such as a bot, may only `prepare`: gather facts, draft options and refresh comparisons. It never decides.

## 4. Go-ahead

`go-ahead` first reviews the chosen design for gaps against the goal, conflicts with what is already built or documented, and missing decisions. Fix the findings or accept them. Then the skill copies the design as one block under `## Decided, not built yet` in `docs/architecture/spec.md`, copies its ADRs as accepted with a "Designed in" link, and copies still-open questions into that spec. Rejected designs stay in the topic folder.

## After

After go-ahead the ending names pushing the design branch first, then opening its pull request. Merge it with no tag. Planning comes only after that pull request is merged: then the ending names `/crav1-tighten-spec <slug>` for an affected slice, or `/crav1-plan-from-spec` when no slice exists yet. This command does not run them. See [How a run ends](reference/run-ending.md).

Reference page: [design architecture](reference/skills/crav1-design-architecture.md)
