# crav1-open-pr: draft

Read only when the pointer in `SKILL.md` sends you here. Moved word for word from `SKILL.md` in 1.71.0. The body template is format A since 1.98.0.

## Draft title and body

When base, head, and the checks are settled, write the draft into the user-visible reply **before** any choice UI.

**Title** (one line):

```text
<slug>: <short summary>
```

**Body** (format A, 1.98.0): a 1–2 line summary, then `###` sections in this order. Leave out a section with nothing in it, heading included.

```markdown
<Summary: 1–2 lines. What changes and the main reason. No links.>

### Changes
**<Area, e.g. Infra>**
- [<path>, lines <a>–<b>](<head-commit link>)

  **<Short title>:** <What changed>. <Why, when a source gives it>.

### Verified
- <The check written out: what was run or compared, where, the result and the date (YYYY-MM-DD).>

### Risks and rollback
- <What could go wrong in which environment, and how to undo it.>

### Merge order
- [PR <n>](<pr link>) or [Branch <name>](<branch link>)

  <Merge before or after it, and why.>

### Not in this PR
- [<path>, line <n>](<head-commit link>)

  **<Short title>:** <What is deliberately left out, and when it comes.>

### Questions for reviewers
- [<path>, line <n>](<head-commit link>)

  **<Short title>:** <One question.>

### Work item
AB#52
```

**Summary.** From the spec H1 and acceptance, or the commit subjects. It is not a heading.

**Changes.** One bullet per change a reviewer should look at, not one per file. Group under bold area labels (Infra, Pipelines, Code, Tests, Docs) only when there are 2 or more areas. At most about 8 bullets; past that, combine smaller changes in one bullet with several links. Each bullet starts with its link, then a blank line and an indented paragraph: a bold short title, then what and why in 1–3 sentences. More places in the same file go in brackets after the first link, as `/crav1-review-pr` does. The why comes only from the spec, a plan task, a commit message or a code comment. With no source, write only the what. Never invent a reason.

**Links.** Line numbers are the right-hand lines of `git diff --unified=0 <base-ref>...<head>` hunks. Links are pinned to the head commit (`git rev-parse <head>`, full SHA), so they keep working after the branch is deleted. Use the link forms and encoding of `crav1-review-pr` `references/comment-layout.md` **Links** (drop-in: `.claude/skills/crav1-review-pr/references/comment-layout.md`; plugin: sibling `skills/crav1-review-pr/references/comment-layout.md`) with the commit in place of the branch:

- Azure DevOps file and lines: `<repo-url>?path=/<path>&version=GC<sha>&line=<a>&lineEnd=<b>&lineStartColumn=1&lineEndColumn=1`
- GitHub file and lines: `<repo-url>/blob/<sha>/<path>?plain=1#L<a>-L<b>` (one line: `#L<n>`)

Branch and PR overview links keep the review-pr forms. The repo URL comes from the remote. No remote: plain `<path>, lines <a>–<b>` text, no link.

**No spec in the body.** No Spec section and no link to `spec.md`, `plan.md`, `tasks.md`, `verify.md` or anything else under `docs/specs/`. Readers of the pull request should not need the spec. Use what it says in the sections above, in plain words.

**Verified.** Write the result out: from `verify.md` when it exists on the head (what was checked, pass or fail, its date), test files in the diff, and live checks named in commits, notes or the user's message, each with its date and where it ran. No source: leave the section out and say in the chat `Nothing verified on this branch.`

**Risks and rollback.** From plan.md risks, commit messages or the user. When the diff touches infra, pipelines or a PROD deploy and no source says how to undo it, say in the chat only, never in the body: `No rollback stated; add one in your edit if you want it.` It rides on the draft prompt; it is not an extra question.

**Merge order.** From the spec's other unmerged work branches (1.64.0; Match `Branch:` lines and task `(branch: …)` parts), the PR note's `Order` lines when a note exists, and the user's words.

**Not in this PR.** From the spec's out-of-scope lines, open tasks of this slug, and code comments in the diff that defer work.

**Questions for reviewers.** Only the spec's open questions marked for review, or what the user adds in an edit. Never invented.

**Slug.** It comes from `feat/<slug>` or `spec/<slug>`. Else (1.64.0) it is the spec whose `Synced at` lines, Match `Branch:` list or task `(branch: …)` parts name the head, in this repo or in the sibling spec repo found under **Base branch**; when several specs name it, read each and leave the slug out of the title. If the head name has no slug and exactly one `docs/specs/<slug>/` folder changed vs base (not `_template/`), use that slug. If several changed, leave the slug out of the title. The slug's files are sources for the sections; the body never links them.

**Work item** is included only when [references/work-item-mention.md](../../crav1-finalize-commit/branches/message-only/references/work-item-mention.md) resolves a mention for that slug (plugin: sibling `skills/crav1-finalize-commit/branches/message-only/references/work-item-mention.md`). The section body is that one mention line (`#<id>` on Azure Repos, `AB#<id>` on GitHub, or the file’s full token), last in the body. On Azure DevOps, only a line whose work item home matches this repo's `Work items go to` cell in `docs/system/repos.md` is mentioned, as that reference says. Omit the section when there is no mention. The hint from that reference, when it has one, is a single sentence after the draft, not inside the body.

The section is Markdown in the description. Do not pass `--work-items` or `--transition-work-items` because of it. The ban in **Create** stays as written. Host order and fallbacks stay as written.

**Format.** Plain Markdown, English, no tables, no HTML, no closing line. Aim for 120–350 words; the summary and Changes must stand on their own.

**The PR record.** This skill writes no PR note and no `## PR record`. The next `/crav1-pr-status` run reads the body's Merge order, Questions for reviewers and Not in this PR sections.

Show base, head, remote, title, and body. Say they can edit any of those before you act.

**Then** offer the choices (questions tool when available). Put the actual title and body in the question prompt, for example:

```text
Base: <base>
Head: <head>
Title: <one line>

Body:
<the draft>

What next?
```

Options, **in this order**:

| Id | Choice | What it does |
| --- | --- | --- |
| `push` | Push and open PR | `git push -u <remote> <head>` (no force), then open one pull request. **Always list this first.** |
| `open` | Open PR only | Remote already has this head. Do not push. Open one pull request for that remote head. |
| `stop` | Stop | No push. No pull request. They can still copy the draft. |

Never call the questions tool before the title and body are in the reply. If they named `push` or `open` before any draft existed, ignore it, draft, show the text, then offer the choices.

If they edit the title, body, base, or head: apply only that edit, re-run the checks when base or head changed, show the new draft, **then** the same three choices (`push` still first). Do not push in the edit turn unless they pick `push` or `open` **after** seeing the new draft.
