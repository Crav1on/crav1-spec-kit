# crav1-open-pr: draft

Read only when the pointer in `SKILL.md` sends you here. Moved word for word from `SKILL.md` in 1.71.0. The body template is format B since 1.176.0.

## Draft title and body

When base, head, and the checks are settled, write the draft into the user-visible reply **before** any choice UI.

**Title** (one line):

```text
<slug>: <short summary>
```

**Body** (format B, 1.176.0): a short fixed shape that always fits, on GitHub and on Azure DevOps. Four parts, in this order, and nothing else:

```markdown
<Summary: 2–3 sentences on what this branch delivers and why. No links.>

### Tasks
- T5 Orders CI/CD: infra Bicep for dev, test and prod. Adds the three environments and their settings.
- T6 Orders CI/CD: deploy pipeline with DEV, TEST and PROD stages. Deploys each stage after the one before passes.

### Verified
<1–2 lines: what was run or checked, where, the result and the date (YYYY-MM-DD).>

AB#52
```

**Summary.** From the spec H1 and acceptance, or the commit subjects, in plain words. It is not a heading.

**Tasks.** One line per task built on this branch: the `T#`, the full task name (the same name the ready check and the build map show, never cut with `...`), then one sentence on what it does. From `tasks.md`, `verify.md` and the commits. With no `T#` (work built outside the kit), one line per main change in the same form, without a number.

**Verified.** From `verify.md` on the head, the tests in the diff, or the checks named in commits or the user's message. One or two lines, never a list of every test. No source: write `Not verified on this branch yet.` and say so in the chat.

**Work item.** The last line, only when [references/work-item-mention.md](../../crav1-finalize-commit/branches/message-only/references/work-item-mention.md) resolves a mention for that slug (plugin: sibling `skills/crav1-finalize-commit/branches/message-only/references/work-item-mention.md`): `#<id>` on Azure Repos, `AB#<id>` on GitHub, or the file's full token. On Azure DevOps, only a line whose work item home matches this repo's `Work items go to` cell in `docs/system/repos.md` is mentioned. No mention: leave the line out. The hint from that reference, when it has one, is a single sentence after the draft, not inside the body. Do not pass `--work-items` or `--transition-work-items` because of it.

**Not in the body.** No links at all: no spec, plan, task list or verify link, nothing under `docs/specs/`, no code or file links, no `Full notes` link. No per-file detail, no Changes list, no walk or run recap, no risks, merge order, open-items or questions section. That detail lives in the commit messages. A missing rollback on an infra, pipeline or PROD change is said in the chat only: `No rollback stated; add one in your edit if you want it.`

**Slug.** It comes from `feat/<slug>` or `spec/<slug>`. Else (1.64.0) it is the spec whose `Synced at` lines, Match `Branch:` list or task `(branch: …)` parts name the head, in this repo or in the sibling spec repo found under **Base branch**; when several specs name it, leave the slug out of the title. If the head name has no slug and exactly one `docs/specs/<slug>/` folder changed vs base (not `_template/`), use that slug. If several changed, leave the slug out of the title. The slug's files are sources; the body never links them.

**Format.** Plain Markdown, English, no tables, no HTML, no closing line.

**The PR record.** This skill writes no PR note and no `## PR record`.

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
