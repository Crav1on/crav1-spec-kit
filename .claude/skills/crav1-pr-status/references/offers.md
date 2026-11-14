# crav1-pr-status: offers

Read only when there is something to offer, from **Hand-offs** in `SKILL.md`.

## The closing prompt

All offers go in **one** prompt at the end of the run, the run's only prompt. Each offer is its own question with its own answer; one answer never covers two threads. The recommended option is first, labelled ` (Recommended)`, at most 4 options.

Order of questions:

1. **Thread status**, one question per thread with a flag or a settled point you may change:
   - `Thread 112 (src/orders/handler.py:238) is resolved, but the code is unchanged since the request. Set it back to active?` **Leave it (Recommended)** / **Set to active**
   - `Thread 98 (tests/test_retry_store.py:45) is done in 3c9d2e1 and still active. Set it to fixed?` **Set to fixed (Recommended)** / **Leave it**
   - GitHub: **Resolve thread** / **Unresolve thread** in the same way.
   Recommend **Leave it** for any change that undoes someone else's resolve.
2. **Follow-ups**, one question: `Mark these as follow-ups for /crav1-ado-sync? (drafts; no work item is created)` **Mark them (Recommended)** / **Not now**.

Signed out, headless, or a bot run: list the same questions as text under `Offers (not asked):`, say `Run /crav1-pr-status pr<n> again to answer them.`, and change nothing on the host.

## On a yes

- **Thread status:** set only that thread's status, as `crav1-add-to-spec` `references/pr-threads.md` **Change a thread's status** (Azure DevOps) or **Resolve a thread** (GitHub) says, then read the thread again and show its new status. A failure is shown and not retried. Update the Point's `host <status>` tag.
- **Follow-ups:** set each chosen Point to `follow-up`, keep its text, and print the draft item (title, description with the pull request link and the anchor) for `/crav1-ado-sync`. Do not run `/crav1-ado-sync`; name it. It reads `follow-up` Points as open items.

A no changes nothing and is not asked again in the same run.

Spec and decision candidates are never asked (1.100.0): the output names `/crav1-add-to-spec pr<n> candidates`, which only runs when you type it. Pick some by retagging a Point in the record, or with `pr<n> candidates 1,3`.

## Hand-offs

Moved word for word from `SKILL.md` in 1.158.0; the rules are unchanged.

- **Spec or decision candidates.** A point that settles how the system works, accepts a limit for now, or drops a goal is a candidate. The record tags it `to spec` or `to decision`. Name the command to type, `/crav1-add-to-spec pr<n> candidates`; never run it or ask about it (1.100.0).
- **Follow-up work items.** A point accepted for later becomes a drafted item for `/crav1-ado-sync` (title and description, in the format of that skill's push branch). The record marks its Point `follow-up` only on a yes. Never create a work item.
- **Thread status changes.** One question per thread, each its own yes. Only a yes sets that one thread's status on the host, as `references/pr-threads.md` says. Never several threads on one yes.
