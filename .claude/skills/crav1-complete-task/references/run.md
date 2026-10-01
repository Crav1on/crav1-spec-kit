# Complete-task worker (one T#, one isolated chat)

You run **only** this `T#`. You do not start another task. You do not launch another complete-task agent.

Follow these skills in order (drop-in `.claude/skills/<name>/SKILL.md` or plugin sibling `skills/<name>/SKILL.md`):

`crav1-implement-task` → loop-commit → `crav1-verify-spec` → loop-commit → (optional) fix loop → `crav1-verify-spec` again.

Commit **style** is already persisted (or the parent just wrote the rule). Use that persist. Do **not** ask style. Do **not** pause for Cursor Allow/Stop or Settings directions (`approvals: already-done`).

Phase names in STATUS (never A/B/C/D): **`implement`**, **`verify`**, **`fix`**, **`done`**.

## Loop-commit

After a step that may have changed files:

1. If the tree is clean, skip. Say skipped.
2. Follow `crav1-finalize-commit` **draft** (persist rule) and its **commit** + **Cursor attribution** sections.
3. Show Summary/Description, then **`commit` immediately**. No copy / edit / rewrite / stop menu. When the Description ends with a blank line and a work-item mention (`#<id>` or `AB#<id>`), that line is part of the message. Commit it. Keep it when you compare HEAD and when you amend away Cursor attribution. A missing `work-item.md` does not fail this worker.
4. Do not push.

If commit fails or attribution comes back after one strip: stop with `STATUS: failed`.

## Gates (return to the parent; do not start the next T#)

Stop and return a **status block** (below) if:

- `crav1-implement-task` would stop (parked Q, non-goal, playbook-only, missing `tasks.md`)
- That task’s row verify failed or you could not run it (`[ ]`)
- Spec disagrees with the code → tell them `/crav1-tighten-spec`; do not edit `spec.md`
- `crav1-fix-from-verify` would stop (spec frozen, non-goal)
- Commit / attribution needs them
- Live host refresh needs them (`crav1-verify-spec` `references/live-host.md`) → `STATUS: needs_ready`
- Inner-loop queue non-empty after verify-spec → `STATUS: needs_fix` (do not enter **fix** until parent says `resume: fix`)
- They / parent said `stop`

## Resume

| Parent said | You do |
| --- | --- |
| (start / omitted) | **implement** |
| `resume: ready` | Finish live-host wait; continue the phase that was waiting (usually **verify** or **fix** evidence) |
| `resume: fix` | **fix** |
| `resume: stop` | `STATUS: blocked` — do not edit |

## implement

Follow **`crav1-implement-task`** for this `T#` only.

Then loop-commit.

If the row did not go `[x]`, `STATUS: blocked`. Do not verify-spec as if the task shipped.

## verify

If **implement** changed a hosted API/UI, follow `live-host.md` first. Then **`crav1-verify-spec`**.

Loop-commit if verify files changed.

Inner-loop = verify failed → claimed/unverified → wiring `G#`. Other unimplemented `T#`s are not inner-loop.

- Empty → **done**
- Non-empty → `STATUS: needs_fix` (parent asks the user)

## fix

Only after `resume: fix`:

1. **`crav1-fix-from-verify`** with no Gap.
2. Loop-commit.
3. If inner-loop empty → verify-spec again, loop-commit if needed; still dirty → `STATUS: needs_fix`; clean → **done**.
4. If queue remains after the fix, continue (1) until empty or a gate.

Do not implement a new `T#`.

## done

```text
STATUS: done
T#: <id> <title>
Implement verify: pass
Spec verify: inner-loop empty
COMMITS: <hashes or none>
Left unchecked: <other T#s or none>
```

## Status block (always end with this)

```text
STATUS: done | blocked | needs_fix | needs_ready | failed
T#: Tn
PHASE: implement | verify | fix | done
COMMITS: <hashes>
DETAIL: <one short paragraph>
```

`PHASE` is the step you were in (or just finished). Do not write A, B, C, or D.

## Hard rules

- One `T#`. Do not edit `spec.md`. Do not push. Do not open a PR. Do not run `/crav1-open-pr` (the parent may name it after `done`).
- Do not skip loop-commit when the tree is dirty after a phase.
