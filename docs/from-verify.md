# Verify and fix

Kit not in this project yet? [Install first](install.md) (Cursor and Claude Code; the slash commands match, the files do not). After a Cursor plugin install, the short command loop is [plugins/crav1/README.md](../plugins/crav1/README.md). Claude Code has no plugin.

Use this after tasks are built. Verify maps every v0 acceptance line in `spec.md` to a test or a browser check and reports pass, fail, or missing. Fix takes the inner-loop gaps one at a time and proves each again. A bug in work that is already shipping is not this page: that is [`/crav1-fix-bug`](from-fix-bug.md).

## First prompt

```text
/crav1-verify-spec
@docs/specs/<slug>/
```

## Steps

| Step | You | Agent |
| --- | --- | --- |
| Verify | — | Reads `spec.md`, `tasks.md`, `plan.md`, and the running tree. Leads with a TL;DR: which tasks are implemented and verified, which are not, and acceptance lines with no task. Then the details in `verify.md`. Ends by naming the next command |
| Read the result | Decide: fix, build more, or ship | Each task is implemented and verified, implemented but verify failed, not implemented, or claimed done but unverified. Wiring gaps are numbered `G#`. A task that is not implemented goes back to [Build tasks](from-plan-to-build.md), not to fix |
| Fix | `/crav1-fix-from-verify`, or name a gap `G#` | Takes one gap in order: failed, then unverified, then `G#`. Omit the gap to take the next. Makes the smallest fix inside the spec, appends to `fix-log.md`, and updates that one `verify.md` row |
| Live wiring | `/crav1-fix-live` when the gap is a live path (ports, proxy, SQL, an unpublished URL) | Same queue and same writes as fix-from-verify, preferring live or untested wiring rows. When the fix changes how the parts connect, asks once whether to run `/crav1-keep-current` and does not run it |
| Prove again | `/crav1-verify-spec` | Re-runs the matrix |

## What gets written

- `docs/specs/<slug>/verify.md`: the acceptance matrix.
- `docs/specs/<slug>/fix-log.md`: one entry per gap, with the fix and the re-proof.
- The smallest code fix for that gap.

Not written: `spec.md`, unimplemented tasks. Verify does not run `/crav1-fix-bug` or `/crav1-review-pr`. Nothing is committed.

## After

When the matrix is green: [From commit to merge](from-commit.md). When the spec itself was wrong, fix the spec first ([From a draft spec to an accepted spec](from-draft-spec.md)), then the plan, then build again.

Reference pages: [verify-spec](reference/skills/crav1-verify-spec.md) · [fix-from-verify](reference/skills/crav1-fix-from-verify.md) · [fix-live](reference/skills/crav1-fix-live.md)
