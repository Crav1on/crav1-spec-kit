# From a pull request review

Kit not in this project yet? [Install first](install.md) (Cursor and Claude Code; the slash commands match, the files do not). After a Cursor plugin install, the short command loop is [plugins/crav1/README.md](../plugins/crav1/README.md). Claude Code has no plugin.

Use this when an **open pull request** is already named and you want to know whether it can ship.

This is cross-cutting. It is not its own lane. It is not a bot. It is the same command family as `/crav1-open-pr` and `/crav1-merge-pr`. `/crav1-open-pr` may name this command and does not run it. `/crav1-merge-pr` does not run it. A review is not a merge ask. Spark, specify, and verify do not run it.

Any open pull request. Not only a feature branch.

## First prompt

New chat. Name the pull request in this message. A number or a URL.

```text
/crav1-review-pr
https://github.com/<owner>/<repo>/pull/<n>

Read the diff. Do not edit. Do not run the tests. Do not merge.
```

That slash command *is* the prompt.

If the message does not name a pull request, the command asks which one and stops. It does not pick the newest.

## Steps

| Phase | You | Agent |
| --- | --- | --- |
| Which pull request | Named it by number or URL | Asks which one and stops when none was named. Does not pick the newest |
| Read | — | Reads the diff, the spec and the plan when they are on the branch, `verify.md` when it is already there, the pull request body, and whether a linter is required and green. Does not edit. Does not run the tests |
| Must be true before ship | Read the findings | Each miss is its own finding. Three lines: what is off, what could happen, and the decision (ship, fix, or drop). Any fix or drop means the review does not say ship |
| Lane | — | Names the lane and does not start it. Spec miss → Specify. Plan miss → Plan. Verify miss, a file the plan already named but the diff lacks, or a red or missing linter → Build. Body mismatch → rewrite the pull request body, not a new spec |
| Suggestions | Read them | Style, patterns, and practices the repo already wrote down, plus dead code, or a name that hides what the code does. They do not block ship. A secret in the diff is a first-section fix |
| Stop | Glance | A clean review says so and stops. It does not merge. It does not comment or vote |

## What it checks

These have to be true before the review says ship:

- **Spec.** The diff does not add product behavior the spec never asked for, and it does not leave out something the spec said must be true.
- **Plan.** The files and the checks named on the plan tasks are in the diff. A task that never named a needed file or check is a plan miss.
- **Verify.** It quotes `verify.md` when that file is already on the branch. It says so when the file is missing. It does not run the tests.
- **Pull request body.** The description matches that same scope, not wider or narrower than the diff. A body mismatch stays on the pull request. This command does not open a new spec for it.
- **Linter.** A linter or checker covers the code in the diff, and that check is required and green. If none exists, or it exists but is not required, or it is required and red, the decision is fix. This command does not install a linter.

## What does not get written

No code edit. No `spec.md` edit. No `plan.md` edit. No test run. No comment. No vote. No branch-protection change. No merge.

## After

A clean review stops. Merge is a later turn, and only when that turn asks:

```text
/crav1-merge-pr
<the same pull request number or URL>
```

That command still stops on its own when a required host check is red. This review does not merge, and it does not clear that stop.

When a finding says fix or drop, start the lane it named in a later turn. Do not treat this review as that lane.
