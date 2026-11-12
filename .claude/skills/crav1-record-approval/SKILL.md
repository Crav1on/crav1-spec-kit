---
name: crav1-record-approval
description: >-
  Use when a named person's yes should be recorded on an Approval needed
  item. Shows the Approved line, the constraint, and the tasks it unblocks.
  Writes that line only after accept in this run. Does not send, apply, or
  commit.
disable-model-invocation: true
icon: badge-check
color: green
---

# Record an approval

You record one named person's yes on an `## Approval needed` item. You do not send anything. You do not run `apply`. You do not tick a task. You do not commit.

This is cross-cutting. It may run from any lane. It does not move work into Specify, Plan, or Build. It is not a starter option.

## Input

The user names the person, the source, and the quote. The source is a pull-request or thread link, or `mail`, or `meeting`, plus the date on that source. They may name the spec and the item (the first words of its line).

A missing person, source, or quote: stop and ask for that value. Do not guess. A headless run with one of them missing stops and names it.

Find the spec with `scripts/resolve_spec.py` (skill `crav1-tasks-ready-to-build`) when they did not point at a folder. Several matches: list them and stop.

## Show, then accept

Read [references/line.md](references/line.md). Pick the interpreter as `crav1-docs/reference/running-scripts.md` says. Run `scripts/approval_needed.py show` and show what it prints: the `Approved:` line, the constraint, and the tasks it unblocks. An earlier quote never counts by itself. The word `yes` inside the quote is not acceptance.

The choice word is `accept`. It has to be in this run, after the line is shown. A yes from an earlier chat, or a quote that already says yes, is not `accept`.

1. **accept (Recommended).** Write the line.
2. **stop.** Write nothing.

A headless run without `accept` stops. `Missing choice. Use: accept.` It does not write.

## Write

Only after `accept` in this run. Run `scripts/approval_needed.py write` with `--yes`. That is the only write. It appends the `Approved:` line under that item. It does not remove the item, `Person:`, `Holds:`, `Asked:`, `Pending:`, or the constraint.

No item, or two items: stop and list them. Do not invent an item. Plan and build create items.

The personal-data and secrets check runs on the quote before the write. Follow skill `crav1-add-to-spec`, `references/sources.md`. A secret is removed and is never a choice.

## Stop

You do not edit `plan.md`, `tasks.md`, `verify.md`, or `docs/system/`. You do not send, post, or reply. You do not commit, push, or open a pull request.

End with the line, who it is for, and which tasks it unblocks. `Next: /crav1-build-tasks <T#>, because that approval is on record and the task can start.` When the task is a live `apply`, say the build still needs the user's own yes in that run, and the task stays unticked until then. Leave the Uncommitted line when the spec changed.

## Run ending (1.122.0)

End as [run-ending.md](../crav1-docs/reference/run-ending.md) says.
