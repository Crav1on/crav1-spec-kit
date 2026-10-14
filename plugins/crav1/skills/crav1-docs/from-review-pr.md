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
| Read | — | Reads the diff, the spec, and the pull request body, and whether a linter is required and green. When the slug has `plan.md`, also reads the plan and `verify.md`. When the slug has no `plan.md` or `tasks.md`, reads the test results that pull request's own pipeline already recorded. Does not edit. Does not run the tests |
| Must be true before ship | Read the findings | Each miss is its own finding. Three lines: what is off, what could happen, and the decision (ship, fix, or drop). Any fix or drop means the review does not say ship. An outside-the-kit note and a recorded-test note are info. They do not block ship |
| Lane | — | Names the lane and does not start it. Spec miss → Specify. Plan miss → Plan, only when that slug has `plan.md`. Verify miss, a file the plan already named but the diff lacks, or a red or missing linter → Build. Body mismatch → rewrite the pull request body, not a new spec |
| Suggestions | Read them | Style, patterns, and practices the repo already wrote down, plus dead code, or a name that hides what the code does. They do not block ship. A secret in the diff is a first-section fix |
| Paste-ready comment | Copy it, or wait for the post question | Ends with one Markdown block you can paste into the pull request as one comment: a verdict line, then Blocker, Bugs, and Tests to add with this PR. Showing it posts nothing |
| Post | Answer yes or no | Asks once whether to post under your own account. On yes, posts each remark inline on its file and line, posts the summary, then asks which verdict to set |
| Stop | Glance | A clean review says so and stops. It does not merge. It never resolves a thread without your yes |

## What it checks

These have to be true before the review says ship:

- **Spec.** The diff does not add product behavior the spec never asked for, and it does not leave out something the spec said must be true.
- **Plan.** Only when the slug has `plan.md`. The files and the checks named on the plan tasks are in the diff. A task that never named a needed file or check is a plan miss.
- **Verify.** Only when the slug has `plan.md`. It quotes `verify.md` when that file is already on the branch. It says so when the file is missing. It does not run the tests.
- **Pull request body.** The description matches that same scope, not wider or narrower than the diff. A body mismatch stays on the pull request. This command does not open a new spec for it.
- **Linter.** A linter or checker covers the code in the diff, and that check is required and green. If none exists, or it exists but is not required, or it is required and red, the decision is fix. This command does not install a linter.
- **Secrets.** A secret in the diff is a fix. The review names the path and does not print the secret.

## Built outside the kit

When the slug has no `plan.md` or `tasks.md`, the pull request was built outside the kit. The review records that as an info note, not a fix finding. It does not report a missing `verify.md`. It does not apply the plan or verify checks above.

It still checks spec fit, the pull request body against the diff, the required green linter, and secrets.

Instead of `verify.md`, it reads the test results that pull request's own pipeline already recorded. The info note says which tests ran, whether they passed, and which changed files no test touches. The skill does not run tests and does not ask to. When the pipeline shows no test run, the note names the tests the pull request includes and tells the user they can run them manually and then rerun the review. A rerun only sees results the pipeline recorded, so a local run shows up only if the user pastes its output. The note states that these are the pull request's own tests, not a check against the spec.

An outside pull request ends with one line. It names `/crav1-keep-current` as the next step after the pull request merges, to bring its changes into the spec and `docs/system/`. The review does not run that command.

A pull request that has a plan keeps the plan and `verify.md` checks in the section above. It does not get that line.

## Paste-ready comment

Every review ends with one fenced Markdown block you can paste into the pull request as one comment:

- The first line is the verdict: `Approve`, `Approve with comments`, or `Changes needed`.
- Then an opening line, then the sections **Blocker**, **Bugs**, and **Tests to add with this PR**. A section with nothing in it is left out.
- Each remark links its file in the pull request files view, then gives `<path>`, line `<n>`: the remark, so each one can become an inline comment.
- It has no kit details: no spec paths, no skill names, no numbering that only the chat explains.

The chat review above the block keeps its plain format for you. The block is for the author.

## Comment style

The block, every posted comment, and every re-review reply use the style Thomas and Rhea agreed on 2026-10-12. It is the default:

- Your own first-person voice, friendly, so the author never feels criticized.
- A vague source, such as "me and my checks". It never names a tool, a bot, or the kit.
- A different opening each time, for example "So I have had a look, and run the PR through some of my checks".
- Soft wording with the same facts: "I noticed…", "Would it be worth adding a test that…?"
- The pull request description is read first. A choice it calls deliberate is not raised as a fault. It becomes a follow-up.

## Post it

After the block, the review asks one question: post, or do not post. It posts under your own account, and nothing posts without your yes. On yes:

1. Each remark is posted as an inline comment on its file and line. A remark with no line in the diff goes in the summary only.
2. The summary is the block without the verdict line. Follow-ups are never posted.
3. The review asks which verdict to set: **Approve**, **Comment**, or **Request changes** (on Azure DevOps (ADO): approve, no vote, wait for author, or reject). It names the one the review points to and sets only the one you pick.

When a post fails, the review says what failed and what already posted, and does not retry another way.

## Re-review

When the pull request already has review comments, the next run is a re-review. It reads the earlier findings from the pull request's own comments and threads, from anyone. A block still in the chat is used only when the pull request has no comments.

Each earlier finding gets one line first: **Fixed** (with the short commit SHA), **Partly fixed**, **Still open**, or **No longer relevant**. A resolved thread whose problem is still there is flagged `resolved but still open`. New findings follow under `New findings`.

On post, the re-review replies in each earlier finding's own thread instead of adding a duplicate comment. Afterwards it offers to resolve the threads marked Fixed, and resolves them only on your yes.

## Follow-ups

Follow-ups are suggestions, and choices the description calls deliberate. They are not for this pull request, so they are not posted to the pull request and are not in the paste-ready comment. The comment has only Blocker, Bugs, and Tests to add with this PR.

The chat review still lists them, then says where they were saved. They go into one note in `docs/notes/` of the specs repo, in the usual notes format: `docs/notes/review-pr-<n>-follow-ups.md`, or `docs/notes/review-pr-<repo>-<n>-follow-ups.md` when two repos in the specs repo have the same pull request number. The note names the pull request, the repo, the date, and each follow-up with its file and line. The paths stay, because the note stays in the specs repo. The note gets an `open` row in `docs/notes/index.md`.

A re-review of the same pull request updates that note instead of writing a second one: it changes the date, adds new follow-ups, and marks one the code now addresses `(done in <short sha>)`. It removes no line. A review with no follow-ups writes no note. The follow-ups come back through the existing note flow: [`/crav1-ado-sync`](from-feature-candidates.md) reads open notes, and the spec that takes one marks it Used by, or Absorbed by. The note is not committed; `/crav1-finalize-commit` does that.

## What does not get written

No code edit. No `spec.md` edit. No `plan.md` edit. No test run. No comment, vote, or thread resolve without your yes. The only file it writes is the follow-ups note. No branch-protection change. No merge.

## After

A clean review stops. On an outside pull request, the last line names `/crav1-keep-current` and the review does not run it. Merge is a later turn, and only when that turn asks:

```text
/crav1-merge-pr
<the same pull request number or URL>
```

That command still stops on its own when a required host check is red. This review does not merge, and it does not clear that stop.

When a finding says fix or drop, start the lane it named in a later turn. Do not treat this review as that lane.

Reference page: [review-pr](reference/skills/crav1-review-pr.md)
