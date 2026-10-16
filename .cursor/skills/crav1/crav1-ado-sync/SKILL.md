---
name: crav1-ado-sync
description: >-
  Keep specs and Azure Boards (ADO) in step. Opens with one question:
  suggest Features (read only), push Features, push tasks, pull task
  changes, or pull spec changes from Features. Skips the question when
  the message already says which. Each choice keeps its own checks:
  az first, previews, writes to Azure Boards only after a yes, ids
  recorded in work-item.md, work-item homes per repo. Later skill. Not a
  starter option. Replaces feature-candidates, specs-to-ado, tasks-to-ado,
  ado-to-tasks, and ado-to-specs (their rules are kept as branches).
disable-model-invocation: true
icon: refresh-cw
color: blue
---

# Azure Boards sync

You move information between the specs and Azure Boards (ADO), one direction per run. You write to Azure Boards only after a yes, as each branch says.

This replaces `/crav1-feature-candidates`, `/crav1-specs-to-ado`, `/crav1-tasks-to-ado`, `/crav1-ado-to-tasks`, and `/crav1-ado-to-specs` (1.56.0). Their rules are kept, unchanged, as the branches below. Follow the branch the answer picks, in full. Shared rules for every branch: [work item homes](branches/push-features/references/work-item-homes.md) and [Azure Boards](branches/push-features/references/azure-boards.md).

## Opening question

Ask one question, with the questions tool when it is available:

1. **Suggest Features.** List Feature candidates from the landscape, specs, research, sources, and open notes. Read only. Follow [branches/suggest-features/BRANCH.md](branches/suggest-features/BRANCH.md).
2. **Push Features.** Create or update Features from picked candidates or specs. Follow [branches/push-features/BRANCH.md](branches/push-features/BRANCH.md).
3. **Push tasks.** Send one spec's tasks as child work items of its Feature. Follow [branches/push-tasks/BRANCH.md](branches/push-tasks/BRANCH.md).
4. **Pull tasks.** Read back the task items a spec records and bring kept changes into the spec and `tasks.md`. Follow [branches/pull-tasks/BRANCH.md](branches/pull-tasks/BRANCH.md).
5. **Pull spec changes.** Read back the Features the specs record and bring kept changes into the spec. Follow [branches/pull-spec-changes/BRANCH.md](branches/pull-spec-changes/BRANCH.md).

Skip the question when the message already says which: "candidates" or "which Features" is 1; "create Features", "send the spec" is 2; "send the tasks" is 3; "read back the tasks", "task states" is 4; "read back the Features", "what changed in Boards" is 5.

Where a branch says it calls or names another of these five, that is the matching choice of this skill. Run it only where that branch says so.

When the message or the files make one option the better fit, list it first and end its label with ` (Recommended)`. Otherwise keep the order above with no label.

## Choice words

Exact words for bots and scripted runs. There are no `--flags`.

- Which sync: `suggest features` / `push features` / `push tasks` / `pull tasks` / `pull spec changes`.

When the invocation contains one of these words (for example `/crav1-ado-sync suggest features`), take that choice and do not ask. This holds for a person, a bot, or a headless run.

When a choice is missing and the run is headless or started by a bot (no person in the chat to answer), do not guess. Stop and name the valid words, for example: `Missing choice. Use one of: suggest features, push features, push tasks, pull tasks, pull spec changes.`

## After

Each branch ends with its own recap and next step.

## Parked and retired specs (1.60.0)

Skip every spec under `docs/specs/retired/`, and every old-path `spec.md` that is only a `Moved:` pointer. A spec whose `spec.md` has a `Parked:` line is parked: the push branches (`suggest features`, `push features`, `push tasks`) do not push it. The pull branches still read it. Say `skipped: <slug> (parked)` and name `/crav1-retire-spec un-park docs/specs/<slug>/`. Do not remove the mark.
A note under `docs/notes/` that says `Waiting for <slug> (parked)` is read like any other note.
