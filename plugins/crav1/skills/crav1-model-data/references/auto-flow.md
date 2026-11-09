# auto-flow

Read `references/common.md` after this file. Do not open the other flow file.

Init with `--flow auto`.

## Budget, once per run

Before `auto-begin`, show the budget and wait:

- **20 minutes**
- **5 correction passes**, shared by the whole run, not reset when the stage changes

The user may keep those numbers or give others. Pass the approved numbers. Do not hide them and do not reuse a budget from an earlier run.

A headless run that does not name the budget stops and shows 20 and 5. It does not start.

`auto-begin --minutes <n> --passes <n>` opens the run. The script reads its own clock. There is no watcher after it finishes.

## During the run

Do not stop for scope, business, or physical confirmation. Do not pass `--yes` to `approve` or `confirm-scope`. The script rejects both while the run is open.

You may `propose-scope`. Scope confirmed stays no.

Complete the shared parts. Where a choice is open, record the useful alternatives and mark what cannot be implemented. Physical detail before business approval is allowed only as a conditional proposal that depends on `business-model`.

Do not set `user_chose`. A tie stays a tie.

## Passes

The first proposal is a baseline, not a correction pass. Record it with `auto-baseline`. If you call `auto-pass` before a baseline exists, that call is the baseline and does not use a pass. The approved pass budget stays available for corrections.

A correction pass is one cycle: find the issue, revise the proposal, revalidate what that change affects. Change a recorded decision, worked example, question, diagram, or the sources on a decision with `revise`. Do not edit the model files by hand. During an open run, `revise` stays inside the current pass and does not use another pass. Record the pass with `auto-pass`.

- `--fingerprint` is a stable id for the proposal text after the pass.
- `--text-file` is that text, so a rewording of the same lines can be seen. `--text` is only for a short value. The match is a heuristic. Say so. It is not proof two texts mean the same thing.
- `--unresolved` is the count of open decision-changing gaps.
- `--progress yes` only when the pass closed a gap, changed a status on cited evidence, or removed an inconsistency. A rewording is `--progress no`.
- The script checks the time limit when the pass is recorded, not during the pass. It does not preempt mid-pass. Do not pass a clock time.
- `--stage` is a label. It does not reset the pass count.

Stop when the script returns one of these:

- `stable` — the same proposal and no unresolved gaps. Success.
- `stall` — the same proposal, or a second pass with no progress, while gaps remain.
- `cycle` — the proposal returned to an earlier one. Say it is a possible cycle.
- `time` or `passes` — the approved limit. The script writes `checkpoint.md` and does not apply that pass.

`auto-finish` runs drift. If a pinned source changed in a material way, or an internal inconsistency remains, a stable result is not finished while passes remain. The budget is not reset. If nothing material remains, the result may stand. The statement lists what was checked. It is not a claim that nothing else drifted.

On any stop, say what is unfinished, what is conditional, and that the confirmed model was not changed.

## Again later

A later `auto-flow` is a new invocation. Show the budget again. `auto-begin` starts a new count. Run `drift` first and revisit only affected decisions. Nothing runs between invocations.
