# Work item mention

Optional Azure Boards link for one spec slug. Read this from `/crav1-draft-commit-message`, `/crav1-finalize-commit`, and `/crav1-open-pr`.

The id lives only in `docs/specs/<slug>/work-item.md`. Do not store it in `tasks.md` (workers parse `T#` rows and skills rewrite that file). Do not create a work item, do not call an Azure DevOps API, do not ask for an id, and do not add a git hook.

A missing file never blocks a commit, a pull request, or a worker. Do not fail a worker status for this.

Starter comment (humans copy from here; skills do not scaffold this file): `docs/specs/_template/work-item.md`.

## Slug

1. Branch `feat/<slug>` or `spec/<slug>`: slug is the remainder of the branch name.
2. Otherwise, when exactly one `docs/specs/<slug>/` folder is in the intended commit (draft) or changed vs the pull-request base (open PR), excluding `_template/`, use that slug.
3. Otherwise there is no slug. Do not pick one. No mention. No hint.

## File

Path: `docs/specs/<slug>/work-item.md`.

Ignore HTML comments, including the sample `Work item: 52` inside `docs/specs/_template/work-item.md`. Read the first non-empty line outside comments.

| Line | Result |
| --- | --- |
| `Work item: 52` | Numeric id `52`. Prefix comes from the remote. |
| `Work item: AB#52` or `Work item: #52` | That token, verbatim. |
| A line that is only `AB#52` or `#52` | That token, verbatim. |
| Anything else, or no such line | No mention. |

The label `Work item:` is case-insensitive. Surrounding whitespace does not matter. Digits are the id. `AB#` plus digits, or `#` plus digits, is a full token.

A full token is an override: use it on every host, including a host that would otherwise get no mention.

## Remote prefix

Use `git remote -v` fetch URLs. Same Azure Repos shapes as `/crav1-open-pr` (HTTPS or SSH): `dev.azure.com`, `*.visualstudio.com`. GitHub is a host of `github.com`.

| Remotes | Numeric id |
| --- | --- |
| One Azure Repos remote, or every remote is Azure Repos | `#<id>` |
| One GitHub (`github.com`) remote, or every remote is GitHub | `AB#<id>` |
| No remote, a non-matching host, or mixed hosts | No mention |

Do not treat other hostnames as GitHub. Do not ask which remote to use.

When the numeric id has no prefix, print one non-blocking line only if a slug was resolved, the file has that numeric id, and the remotes do not agree on a prefix: No work-item mention: git remotes do not agree on Azure Repos vs GitHub. Not required.

When a full token was used, skip that line.

## No mention

| Situation | What to print |
| --- | --- |
| No file, and the prefix table chooses Azure Repos | One line: Optional: add docs/specs/<slug>/work-item.md with a Work item: <id> line to mention an Azure Boards work item. Not required. |
| No file, any other host (or no slug) | Nothing |
| File exists and no line matched | One line: `docs/specs/<slug>/work-item.md has no usable work-item line, so no mention was added. Not required.` |
| Numeric id on a host with no prefix | Nothing, except the mixed-remote line above |

The hint sits after the commit paste blocks, or after the pull-request draft. It is not part of the Summary, Description, pull-request title, or pull-request body.

## Commit message

Subject and the drafted description stay as generated. Do not put the mention in the subject. Do not copy a trailing `#<id>` or `AB#<id>` line from `git log` into the description; this step adds the current slug’s mention once.

When a mention is resolved, append one blank line, then the mention as the **last line** of the Description (the GitKraken description, and the `git commit` body). When the description already ends with that same line, do not append it again.

`/crav1-finalize-commit` commits that Description as the body. The HEAD check expects the mention still last. The Cursor-attribution amend writes the same Summary and Description back, mention included. Do not treat `#<id>` or `AB#<id>` as a Cursor trailer.

## Pull request body

`/crav1-open-pr` adds this section only when a mention is resolved, after Verify:

```markdown
## Work item

#52
```

The line is the resolved mention (`#<id>`, `AB#<id>`, or the verbatim token). Omit the section when there is no mention. Do not pass `--work-items` or `--transition-work-items`.
