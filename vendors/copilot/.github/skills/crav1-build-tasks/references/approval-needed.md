# Approval needed, from a build

Read this when a worker returns `needs_yes` because a named person's yes is not on record.

The worker does not edit `spec.md` and does not write `Approved:`.

The parent looks for an `## Approval needed` item whose `Person:` is that person and whose `Holds:` includes this `T#`. When that item exists, the Waiting line names it. Do not add a second item.

When no item exists, show the item that would be written:

```text
- <who> approves <what>.
  - Person: <who>
  - Holds: <T#>
```

`<what>` is the worker's DETAIL, without the person's name. `<T#>` is this task, plus a later task only when the worker named it.

Ask once: `write the item (Recommended)` or `leave it`. `write the item` runs `<interpreter> -X utf8 <skill crav1-record-approval>/scripts/approval_needed.py add-item --root <spec-folder> --person "<who>" --what "<what>" --holds <T#> --yes`, as `crav1-docs/reference/running-scripts.md` says. `leave it` writes nothing. A headless run writes the item and says `Wrote the Approval needed item. No Approved line.`

Do not write `Approved:` here. That is `/crav1-record-approval`, after `accept` in that run.

End with `Waiting: <who>'s yes to <what>.` The task stays unticked.

When the item has no `Asked:` line:

the Run next reason "that approval is not asked yet" and the command alone in its code span `/crav1-show-or-ask-open-questions <slug>`

When the item already has `Asked:`:

the Run next reason "that yes is not on record yet" and the command alone in its code span `/crav1-record-approval <slug>`
