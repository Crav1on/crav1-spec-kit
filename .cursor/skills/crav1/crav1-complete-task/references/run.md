# Complete-task worker (one T#, one isolated chat)

You run **only** this `T#`. You do not start another task. You do not launch another complete-task agent.

Follow these skills in order (drop-in `.cursor/skills/crav1/<name>/SKILL.md` or plugin sibling `skills/<name>/SKILL.md`):

`crav1-implement-task` → loop-commit → `crav1-verify-spec` → loop-commit → (optional) fix loop → `crav1-verify-spec` again.

Commit **style** is already persisted (or the parent just wrote the rule). Use that persist. Do **not** ask style.

## Loop-commit

After a step that may have changed files:

1. If the tree is clean, skip. Say skipped.
2. Follow `crav1-finalize-commit` **draft** (persist rule) and its **commit** + **Cursor attribution** sections.
3. Show Summary/Description, then **`commit` immediately**. No copy / edit / rewrite / stop menu.
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
- Inner-loop queue non-empty after verify-spec → `STATUS: needs_fix` (do not enter Phase C until parent says `resume: fix`)
- They / parent said `stop`

## Resume

| Parent said | You do |
| --- | --- |
| (start / omitted) | Phase A |
| `resume: ready` | Finish live-host wait; continue the phase that was waiting (usually B or C evidence) |
| `resume: fix` | Phase C |
| `resume: stop` | `STATUS: blocked` — do not edit |

## Phase A — implement

Follow **`crav1-implement-task`** for this `T#` only.

Then loop-commit.

If the row did not go `[x]`, `STATUS: blocked`. Do not verify-spec as if the task shipped.

## Phase B — verify-spec

If Phase A changed a hosted API/UI, follow `live-host.md` first. Then **`crav1-verify-spec`**.

Loop-commit if verify files changed.

Inner-loop = verify failed → claimed/unverified → wiring `G#`. Other unimplemented `T#`s are not inner-loop.

- Empty → Phase D
- Non-empty → `STATUS: needs_fix` (parent asks the user)

## Phase C — fix loop

Only after `resume: fix`:

1. **`crav1-fix-from-verify`** with no Gap.
2. Loop-commit.
3. If inner-loop empty → verify-spec again, loop-commit if needed; still dirty → `STATUS: needs_fix`; clean → Phase D.
4. If queue remains after the fix, continue (1) until empty or a gate.

Do not implement a new `T#`.

## Phase D

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
PHASE: A|B|C|D
COMMITS: <hashes>
DETAIL: <one short paragraph>
```

## Hard rules

- One `T#`. Do not edit `spec.md`. Do not push. Do not open a PR.
- Do not skip loop-commit when the tree is dirty after a phase.
