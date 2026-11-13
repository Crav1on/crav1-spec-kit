# Build progress

Read this when `docs/specs/<slug>/build-progress/<branch>.md` exists, and again when you record a step. `<branch>` is the branch name with each `/` written as `--`. The file stores the real name on `Branch:`.

One file per work branch. It is not `walk-progress.md`. The two walks do not reopen each other.

```text
Walk: build-walk
Slice: docs/specs/orders-capacity/
Branch: feat/orders-host-setup-scripts
Owner: self
Tasks: T3 Apply the CI build policy
Cut from: develop
Merge list: none

- Step: build
  Done: 2026-11-12T13:00:00+00:00
  Result: done
  Tasks version: a1b2c3d4e5f6
  Content stamp: normalized
```

`Owner: other` is other-owner mode, only after `switch`. `Cut from:` is the branch this one was cut from. `Merge:` lines are the ordered merge list. `Merge list: none` means this branch was cut from the base.

## Stamp

Each step records `Done`, `Result`, and the normalized hashes: `Spec version`, `Plan version`, `Tasks version`, `Verify version`, and `Content stamp: normalized`. The hash ignores line endings, a checkbox, a `(PR n)` or `(done)` note, and a `(live yes: …)` note. A sentence change still counts.

`scripts/build_walk.py` settles a merge conflict in this file when every hunk is only those hash lines. It takes the upstream side and may write the merged file's normalized hash. `Done` and `Result` stay. A hunk that also changes those lines is not rewritten. `/crav1-finalize-commit` runs that settle on the pull path. Do not reimplement the hash. Nothing is pushed.

Resume that matches the stored hash stays on the recorded step. It does not ask to clear. Record the next step only after `yes`, one step per call.

## Commit the progress file (1.150.0)

Writing this file is not the end of the step. After the yes that recorded the step, commit `build-progress/<branch>.md`. When that step already commits other files, such as a tick or a verify edit, include this file in that same commit. Otherwise commit this file on its own. Use the persisted commit style, the draft-commit rule already in the repo. Nothing is pushed.

Paused: `Paused at <step>.` Then print `ending`.

```text
Run next:

`/crav1-build-walk T3`
branch feat/orders-host-setup-scripts, T3 Apply the CI build policy

Next: /crav1-build-walk T3, because the walk paused before verify.
```
