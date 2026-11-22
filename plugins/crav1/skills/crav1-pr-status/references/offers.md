# crav1-pr-status: offers

Read only when there is something to offer, from **Hand-offs** in `SKILL.md`.

**Merged since sync (1.194.0).** Before the closing prompt, for each spec this pull request carries, run `scripts/merged_since_sync.py check --spec <spec.md> --code-repo <code checkout> --base <Merges into>` in `crav1-add-to-spec` (the one shared check), as `crav1-docs/reference/running-scripts.md` says. It fetches origin once first (1.196.0; `--no-fetch` skips it), prefers `origin/<branch>` over a stale local branch, catches a tip that is already merged, and compares each branch in the spec's `Synced at:` lines with that branch's base, found per branch (1.195.0): `--base`, which callers pass as the repo's `Merges into` branch from `docs/system/repos.md` when it names one (leave `--base` out otherwise), then that `Merges into` column, then the base branch's own `Synced at` line, then `origin/develop`, then the default branch and writes nothing. When `offer` is `take-in`, ask its one yes card with its `question` and two `options`. On yes, Open `../crav1-add-to-spec/SKILL.md` for its `command` and follow the PR or branch step inline with that skill's own confirms, then run its `after_yes` (`merged_since_sync.py stamp ... --yes`) to move `Synced at` to the merge. On `not now`, write nothing. Either way the closing prompt follows. This card counts toward the run's one question only when it is asked. With no card (`not-merged`, `already-synced` or `skipped`), say nothing. Run it once per run and read its short `line` (1.199.0); never run it again to re-read its output. A pull request that carries no spec skips it, and the slice ready check runs only when this pull request closes a task.

## The closing prompt

All offers go in **one** prompt at the end of the run, the run's only prompt. Ask it before the run ending (1.199.0), then print the one ending that reflects the answers. Never print an ending, ask a card, and print a second ending. Each offer is its own question with its own answer; one answer never covers two threads. The recommended option is first, labelled ` (Recommended)`, at most 4 options.

Order of questions:

1. **Thread status**, one question per thread with a flag or a settled point you may change:
   Background, one sentence before the card: `Thread 112 (src/orders/handler.py:238) is resolved, but the code is unchanged since the request.`

   Card: Set thread 112 back to active?
   - **Leave it (Recommended)**: keep thread 112 resolved and change nothing on the host. Why: undoing someone else's resolve is their call.
   - **Set to active**: reopen thread 112 so the author sees it again.

   Background: `Thread 98 (tests/test_retry_store.py:45) is done in 3c9d2e1 and still active.`

   Card: Set thread 98 to fixed?
   - **Set to fixed (Recommended)**: mark thread 98 fixed on the host. Why: commit 3c9d2e1 already does what it asked.
   - **Leave it**: keep thread 98 active.

   **Reply and status together (1.199.0).** When a drafted reply of yours and a status change are for the same thread, that thread gets one card, not two:

   Background: `Your drafted reply answers thread 195 (settings.json:4).`

   Card: Post your reply in thread 195 and set it to fixed?
   - **Post and set fixed (Recommended)**: post your drafted reply inside thread 195, then set it to fixed. Why: the reply answers it.
   - **Post only**: post the reply and leave the status as it is.
   - **Leave it**: post nothing; the draft stays in the PR note with its thread link.

   The draft's words match the recommended option: `I've marked this thread fixed.` only on that path, never `I'll resolve this thread`. On **Post only**, drop that sentence before posting.

   - GitHub uses the same card. **Post and set resolved** posts the drafted reply and resolves the thread.
   Recommend **Leave it** for any change that undoes someone else's resolve.
2. **Follow-ups**, one question. Background: `These 2 points are follow-ups; marking them creates no work item.`

   Card: Mark these 2 points as follow-ups for /crav1-ado-sync?
   - **Mark them (Recommended)**: tag them as follow-up drafts in the PR record, and no work item is created. Why: /crav1-ado-sync can pick them up later.
   - **Not now**: leave the points as they are.

Signed out, headless, or a bot run: list the same questions as text under `Offers (not asked):`, say `Run /crav1-pr-status pr<n> again to answer them.`, and change nothing on the host.

## On a yes

- **Thread status:** set only that thread's status, as `crav1-add-to-spec` `references/pr-threads.md` **Change a thread's status** (Azure DevOps) or **Resolve a thread** (GitHub) says, then read the thread again and show its new status. A failure is shown and not retried. Update the Point's `host <status>` tag.
- **Reply (1.199.0, GitHub 1.200.0):** `ado_threads.py reply --pr <n> --thread <id> --file <draft file> --status fixed --note <PR note> --yes` from skill `crav1-review-pr` (leave `--status fixed` out on **Post only**). It replies inside the thread, sets the status, reads it back and marks the draft's heading in the PR note `thread <id> posted <date>`. GitHub: `gh_threads.py reply --repo <owner>/<name> --pr <n> --thread <id> --file <draft file> --note <PR note> --resolve --yes` (leave `--resolve` out on **Post only**). Preview first; `--yes` only after the card's yes.
- **Follow-ups:** set each chosen Point to `follow-up`, keep its text, and print the draft item (title, description with the pull request link and the anchor) for `/crav1-ado-sync`. Do not run `/crav1-ado-sync`; name it. It reads `follow-up` Points as open items.

A no changes nothing and is not asked again in the same run.

Spec and decision candidates are never asked (1.100.0): the output names `/crav1-add-to-spec pr<n> candidates`, which only runs when you type it. Pick some by retagging a Point in the record, or with `pr<n> candidates 1,3`.

## Hand-offs

Moved word for word from `SKILL.md` in 1.158.0; the rules are unchanged.

- **Spec or decision candidates.** A point that settles how the system works, accepts a limit for now, or drops a goal is a candidate. The record tags it `to spec` or `to decision`. Name the command to type, `/crav1-add-to-spec pr<n> candidates`; never run it or ask about it (1.100.0).
- **Follow-up work items.** A point accepted for later becomes a drafted item for `/crav1-ado-sync` (title and description, in the format of that skill's push branch). The record marks its Point `follow-up` only on a yes. Never create a work item.
- **Thread status changes.** One question per thread, each its own yes. Only a yes sets that one thread's status on the host, as `references/pr-threads.md` says. Never several threads on one yes.
