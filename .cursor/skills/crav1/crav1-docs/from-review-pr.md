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
| Comment as posted | Confirm the comment, or paste it | When the follow-ups note has a drafted comment with nothing posted after it, first finds the posted comment on the pull request (read-only) or asks you to paste it, saves it word for word, and compares it with the draft (1.67.0) |
| Read | — | Reads the diff, the spec, and the pull request body, and whether a linter is required and green. When the slug has `plan.md`, also reads the plan and `verify.md`. When the slug has no `plan.md` or `tasks.md`, reads the test results that pull request's own pipeline already recorded. Does not edit. Does not run the tests |
| Must be true before ship | Read the findings | Each miss is its own finding. Three lines: what is off, what could happen, and the decision (ship, fix, or drop). Any fix or drop means the review does not say ship. An outside-the-kit note and a recorded-test note are info. They do not block ship |
| Lane | — | Names the lane and does not start it. Spec miss → Specify. Plan miss → Plan, only when that slug has `plan.md`. Verify miss, a file the plan already named but the diff lacks, or a red or missing linter → Build. Body mismatch → rewrite the pull request body, not a new spec |
| Suggestions | Read them | Style, patterns, and practices the repo already wrote down, plus dead code, or a name that hides what the code does. They do not block ship. A secret in the diff is a first-section fix |
| Paste-ready comment | Copy it, or wait for the post question | Says the verdict in the chat, then one Markdown block you can paste into the pull request as one comment: a short opening, then Blockers, Bugs, Tests to add with this PR, and A question, each point starting with a link to its file and line. Showing it posts nothing |
| Post | Post, I'll post it myself, or do not post | Asks once whether to post under your own account, naming the vote. On yes, posts the block as one comment, sets that vote and saves the posted text |
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

An outside pull request ends with one line. It names `/crav1-refresh-system-notes` as the next step after the pull request merges, to bring its changes into the spec and `docs/system/`. The review does not run that command.

A pull request that has a plan keeps the plan and `verify.md` checks in the section above. It does not get that line.

## Paste-ready comment

Every review ends with one fenced Markdown block you can paste into the pull request as one comment (1.66.0). The chat says the verdict on the line above it. The block itself:

- Starts with one short, plain line, such as "I've looked through the PR and run it through my checks. This is what I found:". No greeting, no praise.
- Has the sections **Blockers**, **Bugs**, **Tests to add with this PR**, and **A question** (or **Questions**). A section with nothing in it is left out.
- Starts each point with a link to its file and line on the pull request's source branch, then the explanation as an indented paragraph. A point with no file line starts with a link to the pull request overview, or to a branch for a merge-order point.
- Gives at most one fix per point, with no "or …" and nothing after the fix.
- Has no follow-ups, no table, no closing line, no HTML, and no kit details (no spec paths, skill names, or numbering that only the chat explains).
- Is in English, unless you ask for another language for that comment.

A merge-order point is a question that ends by suggesting to merge the base branch into this branch. The kit never suggests a rebase.

```markdown
I've looked through the PR and run it through my checks. This is what I found:

### Blockers

- [PR 42 overview](https://dev.azure.com/contoso/orders/_git/orders-api/pullrequest/42)

  **No required build:** I can't find any required build or check on the PR, so no green build or lint protects the merge. Could we add a build policy?

### Bugs

- [functions/orders-sync/store.py, line 401](https://dev.azure.com/contoso/orders/_git/orders-api?path=/functions/orders-sync/store.py&version=GBfeature/orders-retry-table&line=401&lineEnd=401&lineStartColumn=1&lineEndColumn=1)

  `RowKey` is random for every write, so a resent file adds a new row instead of an upsert. Maybe the key could be built from the file name and revision number?

### Tests to add with this PR

- [functions/orders-sync/store.py, line 401](https://dev.azure.com/contoso/orders/_git/orders-api?path=/functions/orders-sync/store.py&version=GBfeature/orders-retry-table&line=401&lineEnd=401&lineStartColumn=1&lineEndColumn=1)

  An idempotency test: the same file name and revision number twice should give one row.
```

On GitHub the same link is `https://github.com/contoso/orders-api/blob/feature/orders-retry-table/functions/orders-sync/store.py?plain=1#L401`. The full rules are in the skill's `references/comment-layout.md`.

The chat review above the block keeps its plain format for you, including `B` (bug), `T` (test to add) and `Q` (question) lines for the points in the block. The block is for the author.

## Comment style

The block, every posted comment, and every re-review reply use the style Thomas and Rhea agreed on 2026-10-12, tightened in 1.66.0. It is the default:

- Your own first-person voice, friendly, so the author never feels criticized.
- A vague source, such as "me and my checks". It never names a tool, a bot, or the kit.
- A short, plain opening that may vary slightly. Never praise, a greeting by name, or thanks.
- Soft wording with the same facts: "I noticed…", "Would it be worth adding a test that…?" One fix per point.
- The pull request description is read first. A choice it calls deliberate is not raised as a fault, unless it contradicts something written in the repo. Otherwise it becomes a follow-up.

## Post it

After the block, the review asks one question: post, I'll post it myself, or do not post. It posts under your own account, and nothing posts without your yes. On yes:

1. The block is posted as **one comment**, with no inline threads: on GitHub as the body of one review, on Azure DevOps as one thread.
2. The vote follows the verdict:

   | Verdict | Azure DevOps | GitHub |
   | --- | --- | --- |
   | Changes needed (any Blocker or Bug) | Wait for author | Request changes |
   | Approve with comments (only tests to add or a question) | Approve with suggestions | Comment |
   | Approve (nothing) | Approve | Approve |

   It never rejects. Follow-ups are never posted.

When a post fails, the review says what failed and what already posted, and does not retry another way.

On GitHub you can't approve or request changes on your own pull request, so there the review posts as a comment and says so.

## Comment as posted (1.67.0)

You often edit the comment before posting it. So the follow-ups note keeps both texts, each word for word in a code fence:

- `## Comment as drafted, <date>`: the paste-ready block of each review.
- `## Comment as posted, <date> (by <name>)`: what the reviewers see, with one line saying where it came from (read from the PR thread, pasted in chat, or posted from this review), which draft it was compared with, and which `Description as of` section of the PR note the review read. `by` is your name as the host shows it.

**How it gets the posted text.** When the review posts on your yes, it saves the text the host returns at once. When you pick **I'll post it myself**, say "posted" when it's up, or run `/crav1-review-pr orders-api 42 comment posted`. Every later run on that pull request also checks first. It looks read-only for your review or comment on the pull request (GitHub reviews and conversation comments; Azure DevOps top-level threads, or your reply in the earlier thread), posted after the draft, that matches it. One match: it asks you to confirm. Several: it lists them, and you may pick more than one. None: it says so in one line and goes on, since you may not have posted it yet. No `gh` or `az` session, or nothing found after `comment posted`: it asks you to paste it. An edit on the host later adds a new section ending `, edited`; the earlier one stays.

**Comparing.** Points are paired by their link and title. The chat lists them as drafted, changed, not in the posted comment, or added. A drafted point you left out stays in the note as a bullet ending `(Not in the posted comment, <date>; still open.)`. A cut question keeps its `Asked on the PR:` line, with the mark added. A question you added gets an `Asked on the PR:` line.

Example, with made-up names:

`````markdown
- `src/orders/retry_store.py`, line 9: an idempotency test for the row key. (Not in the posted comment, 2026-10-19; still open.)

## Comment as posted, 2026-10-19 (by Alex Doe)
Read from the PR thread: https://github.com/contoso/orders-api/pull/42#issuecomment-1001. Draft compared: 2026-10-19. Description reviewed: as of 2026-10-18 (PR note).

````markdown
I've looked through the PR and run it through my checks. This is what I found:

### Bugs

- [src/orders/retry_store.py, line 9](https://github.com/contoso/orders-api/blob/feat/orders-retry/src/orders/retry_store.py?plain=1#L9)

  The row key is random for every write. Maybe the key could be built from the file name and revision?
````
`````

The pasted or fetched text goes through the personal-data and secrets check first, like the PR note. Secrets are removed and named by kind, and the source line says `Verbatim except: <kind> removed.`

For bots: `comment posted` records only, `newest comment` takes the newest match, and `skip comment record` skips the step. A headless run with several candidates or none stops and names these words. No word posts.

## Re-review

When the pull request already has review comments, the next run is a re-review. It reads the earlier findings from the pull request's own comments and threads, from anyone, including the points of an earlier one-comment review. When the follow-ups note has the comment as posted, the earlier points are its points (1.67.0). When nothing was posted, the new comment has no **Since last time**; the chat still says which points of the newest drafted comment are fixed or open.

Each earlier finding gets one line first: **Fixed** (with the short commit SHA), **Partly fixed**, **Still open**, or **No longer relevant**. A resolved thread whose problem is still there is flagged `resolved but still open`. In the comment, earlier points go under **Since last time**, then new points under the normal sections. **Since last time** lists only points the reviewers saw. A finding you cut from the posted comment is shown in the chat with its mark and kept out of the new comment unless you say to include it.

On post, the re-review replies in the earlier comment's thread (Azure DevOps) or posts a new review (GitHub). Afterwards it offers to resolve existing threads whose points are fixed, and resolves them only on your yes.

## Specs in another repo (1.65.0)

The specs often live in their own repo (`orders-specs`) and the code pull requests in others (`orders-api` on Azure DevOps, merging into `develop`). The review works across that split in two ways:

- **From the specs repo**, for a pull request in a repo listed in `docs/system/repos.md`: `/crav1-review-pr orders-api 71`, or the pull request URL. The repo is matched on its `URL` cell.
- **With both repos open** in one workspace: the folder with `docs/specs/` is the specs repo, and the folder whose remote matches the pull request is the code repo.

It reads the pull request from the host (`gh` or `az`, read-only), and the spec, plan and `verify.md` from the specs repo's working tree. The spec is found by the head branch in its `Synced at` lines, Match `Branch:` list or task `(branch: orders-api …)` parts. A code pull request whose spec has a `plan.md` gets the full checks, not the outside-the-kit note. When the spec spans several repos, another repo's part is not a miss; an `I3` info note lists it with the Branches line.

A GitHub diff comes from `gh pr diff`. An Azure DevOps diff comes from the code repo's checkout (`../orders-api`). When that checkout's copy of the pull request branches is missing or older than the pull request, it asks once:

1. **Fetch only the PR's two branches (Recommended)**: fetches just those two branches there; nothing is checked out or committed.
2. **Use what's on disk**: diffs the copies there and says how old they are and that newer commits may be missed.
3. **Stop**: you fetch and rerun.

A bot passes `fetch pr branches`, `use disk` or `stop pr review`. When the copies already match, nothing is asked.

Run from the code repo with the specs repo not open, it finds the specs repo next door (`../orders-specs`, by its `repos.md` row), writes the notes there, never commits them, and names the full path.

## PR note (1.65.0)

Every review saves the pull request's title and description as a **PR note** in the specs repo, so specs can link to it locally: `docs/notes/YYYY-MM/YYYY-MM-DD-pr-orders-api-71.md`, filed by the pull request's created date, `kind: pull request`, `source: PR 71 dev.azure.com/contoso/orders/orders-api`. A later review reuses it; when the description changed, it appends a `## Description as of <date>` section and never removes the earlier text. The description goes through the same personal-data and secrets check as an imported mail, and each image gets the four options. Pull requests made by `/crav1-open-pr` get one too. `/crav1-merge-pr` writes or updates it after a merge, and `/crav1-add-to-spec code change orders-api PR 71` uses it. The follow-ups note links it with `pr_note:`.

## Follow-ups

Follow-ups are suggestions, and choices the description calls deliberate. They are not for this pull request, so they are not posted to the pull request and are not in the paste-ready comment. The comment has only Blockers, Bugs, Tests to add with this PR, and A question.

The chat review still lists them, then says where they were saved. They go into one note in `docs/notes/` of the specs repo, in the usual notes format: `docs/notes/YYYY-MM/review-pr-<n>-follow-ups.md`, or `docs/notes/YYYY-MM/review-pr-<repo>-<n>-follow-ups.md` (month of the review date) when two repos in the specs repo have the same pull request number, and always for a pull request in another repo (1.65.0). The note names the pull request, the repo, the date, and each follow-up with its file and line. The paths stay, because the note stays in the specs repo. The notes indexes are regenerated.

A re-review of the same pull request updates that note instead of writing a second one: it sets the imported date, adds new follow-ups, and marks one the code now addresses `(done in <short sha>)`. It removes no line. A question asked in the comment is saved there too, starting `Asked on the PR:` (1.66.0). From 1.67.0 every review with a paste-ready comment writes the note, because it holds the comment as drafted. The follow-ups come back through the existing note flow: [`/crav1-ado-sync`](from-ado-sync-suggest-features.md) reads open notes, and the spec that takes one adds itself to the note's `used_by`. Notes are never absorbed. The note is not committed; `/crav1-finalize-commit` does that.

## What does not get written

No code edit. No `spec.md` edit. No `plan.md` edit. No test run. No comment, vote, or thread resolve without your yes. The only files it writes are the PR note and the follow-ups note, in the specs repo. In the code repo it only fetches the pull request's two branches, and only after you pick that. No branch-protection change. No merge.

## After

A clean review stops. On an outside pull request, the last line names `/crav1-refresh-system-notes` and the review does not run it. Merge is a later turn, and only when that turn asks:

```text
/crav1-merge-pr
<the same pull request number or URL>
```

That command still stops on its own when a required host check is red. This review does not merge, and it does not clear that stop.

When a finding says fix or drop, start the lane it named in a later turn. Do not treat this review as that lane.

Reference page: [review-pr](reference/skills/crav1-review-pr.md)

## A branch with no pull request (1.80.0)

`/crav1-review-pr branch feature/orders-retry` reviews a branch before any pull request exists. `/crav1-review-pr branch` takes the current branch, and `/crav1-review-pr branch orders-api feature/orders-retry` a repo from `repos.md`. A branch named without the word is still not a pull request.

It diffs from the base with local git only, never fetching. The base comes from the spec's Match `Branch:` entry and its `(into …)` or `(spec branch)` marker, then the repo's `Merges into`, then the default branch, and the review shows it: `Base: develop (Merges into). Merge-base: 1a2b3c4. Remote copy: 2 days.` With no base it asks once, with up to 4 likely bases and Other; a headless run stops and says to name one.

The checks are those of a pull request review: spec, plan, `verify.md`, the secret rule, `F#` findings and suggestions. The body, the checks, the comment record and posting are skipped, and it says so once. The verdict stays in the chat. Nothing is checked out, committed, pushed or posted. When the base moved on, it suggests merging the base into the branch, never a rebase.
