# Comment layout (1.66.0)

The paste-ready comment that `/crav1-review-pr` ends with, and the one comment it posts after a yes. It follows [Comment style](../SKILL.md#comment-style) in `SKILL.md`. Examples use made-up names: the code repo `orders-api` on Azure DevOps (`dev.azure.com/contoso/orders`), the source branch `feature/orders-retry-table`, pull request 42.

## The block, in order

1. **No verdict line.** The chat says the verdict on the line just above the block: `Verdict: <Approve | Approve with comments | Changes needed>`. See [Verdict](#verdict).
2. **Opening:** one short, plain line, for example `I've looked through the PR and run it through my checks. This is what I found:`. The wording may vary slightly. Never praise, never greet by name, never thank, and no lead-in about merging. Never name a tool, a skill, a bot, or the kit.
3. **Sections**, in this order, each as a `###` heading, with fixed English text:
   1. `### Blockers`
   2. `### Bugs`
   3. `### Tests to add with this PR`
   4. `### A question` (exactly one), or `### Questions` (two or more)

   Leave out a section with nothing in it, heading included. **Follow-ups are never in the block.** The chat lists them under **Follow-ups (not for this PR)** and the PR record keeps them as `follow-up` Points.
4. **Bullets**, one per point, link first:

   ```text
   - [<path>, line <n>](<file-line link>)[ (and [line <m>](<file-line link>))]

     [**<short title>:** ]<what I saw, why it matters, at most one soft fix>
   ```

   - The link line, a blank line, then the explanation indented two spaces. A second paragraph is allowed, also indented.
   - Ranges: `lines <a>–<b>` (en dash) in the text, the host's range form in the URL.
   - More places in the same file go in brackets after the link: `(and [line 16](…))`, `(also [line 449](…) and [line 623](…))`. A place in another file goes in the explanation as plain text (`` `function_app.py` lines 238 and 449 ``), or gets its own bullet when it needs its own action.
   - **No file line:** open with the best pull-request-level link: `[PR <n> overview](…)` for a point about the whole pull request (a required build, a reviewer, the description), `[Branch <name>](…)` for the other branch in a merge-order point, or the target branch for a point about the base. A question about a team goal may open with its text.
   - **One fix per point:** at most one suggested fix, softly worded ("Maybe the key could be built from the file name and revision number?"). No second option ("or …"). Nothing after the fix or the question: no "your call", "I'd just like it written down", or "let me know".
5. **No table** of any kind.
6. **No closing line and no files-view link.** The block ends with its last bullet.
7. **Plain Markdown only:** headings, bullets, bold, inline code, links. No HTML tags, footnotes, task-list boxes, or diagrams. It renders the same in Azure DevOps and GitHub.
8. **No kit details:** no spec paths or names, no `docs/sources/`, no vault, no `F1`. A plan or verify miss is said in plain words about the change. The PR note and its record are never mentioned.
9. **English**, unless the user asks for another language for this comment in this turn.

## Which section

| In the chat | In the block |
| --- | --- |
| `F` Spec, Plan, Verify, Body, Secret, Linter (fix or drop) | **Blockers**. A secret names the path and line, never the value. A linter miss with no file line opens with the PR overview link |
| A merge-order problem the spec, the plan, or the user states (another branch must merge first and is not in the target) | **Blockers**, opening with that branch's link, phrased as a question (see [Merge order](#merge-order)) |
| `B` bug: a defect that is not a first-section miss | **Bugs** |
| A choice the description calls deliberate that contradicts something written in the repo (a code comment, a README, a design rule) | **Bugs** (or a question): "I understand … was deliberate. If so, maybe … should be updated?" |
| `T` test to add: a concrete test for a changed behavior or a bug | **Tests to add with this PR** |
| `Q` question: something the author or team must answer about the code repo (two written goals disagree, an unclear intent) | **A question** / **Questions** |
| `S` suggestion, and drift in the repo's own docs | Not in the block. Chat and PR record |
| A choice the description calls deliberate, with nothing in the repo against it | Not in the block. Chat and PR record |
| The description's own "might like" or "may be a good idea" items | Not in the block. PR record |
| `I1`, `I2`, `I3` info notes | Not in the block |

A question in the block is about the code repo. The kit's open questions in a spec (`## Open questions`) are never copied into the block, and the block never names a spec. When a pull request question also touches a spec decision, the chat says so and names `/crav1-show-or-ask-open-questions` for that spec, and does not run it.

## Verdict

| Block has | Verdict | Azure DevOps vote | GitHub review |
| --- | --- | --- | --- |
| Any Blocker or any Bug | `Changes needed` | Wait for author | Request changes |
| Only tests to add or a question | `Approve with comments` | Approve with suggestions | Comment |
| Nothing | `Approve` | Approve | Approve |

Never Reject. The vote is set only after the yes in [Post it](../SKILL.md#post-it). The ship line in the chat still follows the first section.

## Merge order

Phrase it as a question. Say what you understood, what you can see (no pull request yet, not in `<base>`, this pull request was built without it), ask whether it is still planned to go in first, and then the merge-the-base-in step:

> As I understood it, the `feat/orders-config-move` branch should go into develop before any other orders-sync change. It has no PR yet, and this PR was built without it. Is that branch still planned to go in first? If so, could it get a PR and be merged first, and then develop merged into this branch so the two don't clash?

No commit SHAs. `<base>` is the pull request's target branch.

## Merge the base in, never rebase

Any advice about a branch that is behind its base, has conflicts, or must take another branch first says to **merge `<base>` into this branch** (and resolve conflicts there). Never suggest a rebase, `pull --rebase`, `--onto`, "Rebase and merge", or a force-push. When the chat shows the steps:

```text
git switch <base>
git pull --ff-only
git switch <branch>
git merge <base>
git push
```

GitHub's **Update branch**: choose **Update with merge commit**. Seeing that someone else rebased a branch is still reported as before; that is not advice.

## Links

Line numbers come from the source branch head: the right-hand line of the diff hunk for a changed line, else the file at the head (GitHub `gh api repos/<owner>/<repo>/contents/<path>?ref=<head sha>`, read-only; Azure DevOps `git show <remote>/<source>:<path>` in the checkout the diff came from). A point about a removed line links the target branch file and line and says it was removed in this pull request.

Percent-encode the branch and the path except unreserved characters and `/` (a space is `%20`, `#` is `%23`, `&` is `%26`, `+` is `%2B`). Strip `refs/heads/`. For a pull request from a fork, file and branch links use the fork (GitHub `headRepositoryOwner` and `headRepository`; Azure DevOps `forkSource.repository`).

Azure DevOps, with `<repo-url>` = `https://dev.azure.com/<org>/<project>/_git/<repo>` (or the `visualstudio.com` form the pull request uses):

| Link | URL |
| --- | --- |
| File and line | `<repo-url>?path=/<path>&version=GB<branch>&line=<n>&lineEnd=<n>&lineStartColumn=1&lineEndColumn=1` |
| File and lines | `<repo-url>?path=/<path>&version=GB<branch>&line=<a>&lineEnd=<b>&lineStartColumn=1&lineEndColumn=1` |
| Branch | `<repo-url>?version=GB<branch>` |
| PR overview | `<repo-url>/pullrequest/<n>` |

GitHub, with `<repo-url>` = `https://github.com/<owner>/<repo>`:

| Link | URL |
| --- | --- |
| File and line | `<repo-url>/blob/<branch>/<path>?plain=1#L<n>` |
| File and lines | `<repo-url>/blob/<branch>/<path>?plain=1#L<a>-L<b>` |
| Branch | `<repo-url>/tree/<branch>` |
| PR overview | `<repo-url>/pull/<n>` |

`?plain=1` makes the line anchor work on files GitHub renders (Markdown and others). It is always added.

Links point at the source branch, so they show the code the author is editing and keep working after a force-push. Lines can drift after new pushes, and a branch link stops opening after the branch is deleted; the pull request itself keeps its diff.

## Re-review

The same layout. After the opening, a `### Since last time` section: one bullet per earlier point, link first, with its status in the explanation ("This looks sorted now in `abc1234`.", "I think there's still a little left here: …", "This one went away with the rewrite."). Then new points under the normal sections. Links point at the branch as it is now. Earlier points are the points of the comment as posted, not the draft (1.67.0, [comment-as-posted.md](comment-as-posted.md) **Re-review**).

## Nothing to say

Verdict `Approve` in the chat, and a block of one plain line: `I've looked through the PR and run it through my checks, and I didn't find anything to change.`

## Example

```markdown
I've looked through the PR and run it through my checks. This is what I found:

### Blockers

- [Branch feat/orders-config-move](https://dev.azure.com/contoso/orders/_git/orders-api?version=GBfeat/orders-config-move)

  **Merge order:** As I understood it, the `feat/orders-config-move` branch should go into develop before any other orders-sync change. It has no PR yet, and this PR was built without it. Is that branch still planned to go in first? If so, could it get a PR and be merged first, and then develop merged into this branch so the two don't clash?

- [PR 42 overview](https://dev.azure.com/contoso/orders/_git/orders-api/pullrequest/42)

  **No required build:** I can't find any required build or check on the PR, so no green build or lint protects the merge. Could we add a build policy?

### Bugs

- [functions/orders-sync/store.py, line 401](https://dev.azure.com/contoso/orders/_git/orders-api?path=/functions/orders-sync/store.py&version=GBfeature/orders-retry-table&line=401&lineEnd=401&lineStartColumn=1&lineEndColumn=1)

  `RowKey` is random for every write. So if the supplier resends the same file, it adds a new row instead of an upsert. Maybe the key could be built from the file name and revision number?

### Tests to add with this PR

- [functions/orders-sync/store.py, line 401](https://dev.azure.com/contoso/orders/_git/orders-api?path=/functions/orders-sync/store.py&version=GBfeature/orders-retry-table&line=401&lineEnd=401&lineStartColumn=1&lineEndColumn=1)

  An idempotency test: the same file name and revision number twice should give one row.

### A question

- The new SQL table matches the design, but the develop README says this repo should be "Functions + Blob only". Do we want an explicit exception for orders-sync, or to drop that goal?
```

The same bug on GitHub: `[functions/orders-sync/store.py, line 401](https://github.com/contoso/orders-api/blob/feature/orders-retry-table/functions/orders-sync/store.py?plain=1#L401)`.
