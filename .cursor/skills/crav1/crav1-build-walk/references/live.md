# Runs live

Read this when the task line contains `(Runs live)`, or an `## Approval needed` item holds the task. A `(host setup)` task without `(Runs live)` is an ordinary build task.

`(Runs live)` means the build runs something live, such as a CI policy or a host setting. The order is fixed.

1. An unapproved Approval needed item holds the task. Do not write the script yet. When the item has no `Asked:` line, Run next is the draft request, and the Waiting line says why (1.157.0).

```text
Run next:

`/crav1-show-or-ask-open-questions`
branch feat/orders-host-setup-scripts, T4 Apply the CI build policy

Waiting: T4 Apply the CI build policy is held and that Approval needed item is unanswered.
```

When it was asked, Run next is the record command.

```text
Run next:

`/crav1-record-approval`
branch feat/orders-host-setup-scripts, T4 Apply the CI build policy

Waiting: T4 Apply the CI build policy is held and that Approval needed item can be recorded.
```

An `Approved:` line clears that hold. It never replaces the user's own yes for the live run.

2. Write the script. Run the dry run, the `check` mode. Do not run the live change.
3. Ask for `yes` before the live run. `yes` records `(live yes: <name>, <date>)` on the task line and then runs it. `stop` leaves the script written. The task stays `[ ]`.
4. The tick stays a later step, after `check` reads back ok.
5. When the live command was refused by the assistant's permission check, and the user's yes is already on record (`(live yes: …)` or yes in this run), do not say the yes is missing. Follow skill `crav1-build-tasks`, `references/permission-block.md`, with `--rerun /crav1-build-walk`. Print that script's `lines`. The task stays `[ ]`. Do not suggest working around the check.

The normalized hash ignores `(live yes: …)`, the same way it ignores a checkbox.
