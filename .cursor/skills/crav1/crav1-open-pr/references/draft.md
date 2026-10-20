# crav1-open-pr: draft

Read only when the pointer in `SKILL.md` sends you here. Moved word for word from `SKILL.md` in 1.71.0; the rules are unchanged.

## Draft title and body

When base, head, and the checks are settled, write the draft into the user-visible reply **before** any choice UI.

**Title** (one line):

```text
<slug>: <short summary>
```

**Body:**

```markdown
## What / why

<Two to four sentences from spec.md or the commits on base..head. Do not invent scope.>

## Spec

- [spec.md](docs/specs/<slug>/spec.md)
- [plan.md](docs/specs/<slug>/plan.md)
- [tasks.md](docs/specs/<slug>/tasks.md)

## Verify

<One line from verify.md when that file exists (pass, fail, or missing). Otherwise: No verify.md on this branch.> <When the spec has other unmerged work branches (1.64.0): This spec also has unmerged branches: <branch>, <branch>.>
```

When a work-item mention is resolved, add this section after Verify. The body of the section is the mention line only:

```markdown
## Work item

AB#52
```

**Spec** lists only files that exist on the head. Omit **Spec** when none of `spec.md`, `plan.md`, and `tasks.md` exist under `docs/specs/<slug>/`. Slug comes from `feat/<slug>` or `spec/<slug>`. Else (1.64.0) it is the spec whose `Synced at` entries, Match `Branch:` list or task `(branch: …)` parts name the head, in this repo or in the sibling spec repo found under **Base branch**; when several specs name it, list each under **Spec** and leave the slug out of the title. If the head name has no slug and exactly one `docs/specs/<slug>/` folder changed vs base (not `_template/`), use that slug. If several changed, leave the slug out of the title and omit **Spec** rather than picking one.

**Work item** is included only when [references/work-item-mention.md](../../crav1-finalize-commit/branches/message-only/references/work-item-mention.md) resolves a mention for that slug (plugin: sibling `skills/crav1-finalize-commit/branches/message-only/references/work-item-mention.md`). The section body is that one mention line (`#<id>` on Azure Repos, `AB#<id>` on GitHub, or the file’s full token). On Azure DevOps, only a line whose work item home matches this repo's `Work items go to` cell in `docs/system/repos.md` is mentioned, as that reference says. Omit the section when there is no mention. The hint from that reference, when it has one, is a single sentence after the draft, not inside the body.

The section is Markdown in the description. Do not pass `--work-items` or `--transition-work-items` because of it. The ban in **Create** stays as written. Host order and fallbacks stay as written.

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
