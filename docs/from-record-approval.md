# Record a person's yes

Kit not in this project yet? [Install first](install.md) (Cursor and Claude Code; the slash commands match, the files do not).

Use this when a named person has already said yes to something an Approval needed item is holding, and you want that yes written down. The command shows the line, the constraint, and the tasks it unblocks. It writes only after you accept in this run. An earlier quote does not count by itself.

## First prompt

```text
/crav1-record-approval

Person: the partner
Source: https://github.com/example/widgets/pull/12#discussion_r9 2026-10-02
Quote: "Yes, apply the policy."
```

Name the spec when more than one is open (`@docs/specs/<slug>/`). Name the item by its first words when the person has more than one.

## Steps

| Step | You | Agent |
| --- | --- | --- |
| Quote | Give the person, the source, its date, and their words | Shows the `Approved:` line, the constraint that still asks for the yes, and the tasks it unblocks |
| Accept | `accept`, or stop | `accept` writes the line. Stop writes nothing. A quote that already says yes is not acceptance |

The source date stays the date on the quote. The accepted date is today. Both stay on the line.

## What gets written

One line under that item in `docs/specs/<slug>/spec.md`:

```text
- The partner approves applying the CI build policy.
  - Person: the partner
  - Holds: T4
  - Approved: the partner, 2026-10-02, https://github.com/example/widgets/pull/12#discussion_r9, "Yes, apply the policy." (accepted by Alex 2026-11-12)
```

The item, the constraint, and any `Asked:` or `Pending:` line stay. Nothing is sent. The task is not ticked. A live `apply` still needs your own yes in the build run.

## After

`Next: /crav1-build-tasks T4, because that approval is on record and the task can start.` When a mark was written: `Uncommitted: 1 file; commit with /crav1-finalize-commit when ready.`

Reference page: [record-approval](reference/skills/crav1-record-approval.md)
