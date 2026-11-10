# Large batch

Read this only when there are more than 8 issues. Eight or fewer stay on the batch in `SKILL.md`.

## Count

One line, the kinds that have any, in this order. Do not print findings, whys, or options yet.

```text
12 issues to fix, 3 open questions, 4 small wording.
```

- **Open question.** The only work is an `Answered:` line, or the issue only repeats a question already under `## Open questions`. These are not walked here.
- **Small wording.** No change to what the product does. The only fitting patch is `sync-here`, or a wording fix that does not change a requirement.
- **Issue to fix.** Every other issue that needs a decision.

## Pass open questions on

One line, no menu, no finding:

```text
Left for /crav1-resolve-open-questions: I3, I10, I11.
```

## What to do now

Ask each time, for what remains. One by one is always offered, and it is first.

- Next one (Recommended). Show the full block for that issue only.
- A small group. They name at most 4 ids. Show the full block for those only.
- stop

Do not offer the whole list. After that group is done, give the short count again and ask the same way. A batch of `I#: letter` still works for the issues in front of them.
