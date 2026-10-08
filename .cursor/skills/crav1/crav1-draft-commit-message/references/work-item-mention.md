# Work item mention

Optional Azure Boards link for one spec slug. Read this from `/crav1-draft-commit-message`, `/crav1-finalize-commit`, and `/crav1-open-pr`.

The id lives only in `docs/specs/<slug>/work-item.md`. Do not store it in `tasks.md` (workers parse `T#` rows and skills rewrite that file). Do not create a work item, do not call an Azure DevOps API, and do not add a git hook.

`/crav1-draft-commit-message`, `/crav1-finalize-commit`, and `/crav1-open-pr` do not ask for a new id. They only read the file. When several lines are recorded and the slice is unclear, they ask which recorded line to mention. `/crav1-spark-to-spec`, `/crav1-ideas-to-spec`, and `/crav1-intake-to-specs` may write a line when they create a new spec folder on Azure Repos and the user replies with an id. That offer is [work-item-offer.md](work-item-offer.md). Creating a Feature is `/crav1-specs-to-ado`. These skills do not create one. `/crav1-specs-to-ado` writes a line after the user says yes.

A missing file never blocks a commit, a pull request, or a worker. Do not fail a worker status for this.

Starter comment (humans may copy from here): `docs/specs/_template/work-item.md`. Spec skills do not copy that comment into a slug. When the user answers the offer, they write one line per id, `Work item: <id>`, or `Work item: <id> — <label>` when they named a milestone or slice, and nothing else.

## Slug

1. Branch `feat/<slug>` or `spec/<slug>`: slug is the remainder of the branch name.
2. Otherwise, when exactly one `docs/specs/<slug>/` folder is in the intended commit (draft) or changed vs the pull-request base (open PR), excluding `_template/`, use that slug.
3. Otherwise there is no slug. Do not pick one. No mention. No hint.

## File

Path: `docs/specs/<slug>/work-item.md`.

Ignore HTML comments, including the sample lines inside `docs/specs/_template/work-item.md`. Read every non-empty line outside comments. A file with one unlabeled line is the old format. Keep reading it.

| Line | Result |
| --- | --- |
| `Work item: 52` | Numeric id `52`. No milestone or slice label. Prefix comes from the remote. |
| `Work item: 52 — October billing` | Numeric id `52`. Label `October billing`. |
| `Work item: AB#52` or `Work item: #52` | That token, verbatim. No label. |
| `Work item: AB#52 — catalog` or `Work item: #52 — catalog` | That token, verbatim. Label `catalog`. |
| A line that is only `AB#52` or `#52` | That token, verbatim. No label. |
| Anything else | That line is not a mention. Other lines are still read. |

The label `Work item:` is case-insensitive. Surrounding whitespace does not matter. Digits are the id. `AB#` plus digits, or `#` plus digits, is a full token.

The milestone or slice label is the text after the first ` — ` (space, em dash, space) or ` - ` (space, hyphen, space) that follows the id token. The writer uses the em dash. The reader accepts both. A line with no separator has no label.

A full token is an override: use it on every host, including a host that would otherwise get no mention.

## Which line

**One usable line.** Use it. A missing label does not ask. This is the old single-line format.

**Several usable lines.** The mention is the line whose label matches the slice being worked.

The slice being worked is the first of these that this turn already shows:

1. The user named a milestone or slice in this turn.
2. The intended commit (draft) or the pull-request diff (open PR) touches one milestone or slice heading in that spec, or one `tasks.md` row whose text is that label.
3. The slug was resolved from the branch, and the branch name has text after that slug (`feat/<slug>-<rest>` or `spec/<slug>-<rest>`) that matches one label. When the branch name is exactly `feat/<slug>` or `spec/<slug>`, this step does not apply.

A match is the whole label and that name, compared without regard to case. A partial overlap is not a match. One match uses that id.

**Unclear.** Zero matches, or more than one, asks. Options only. Use the questions tool when it is available. One option per usable line, showing the id and the label, or `no label` when the line has none. Last option: **No mention.** Stop until the user picks. Do not guess. Do not put a mention in the draft until they pick. **No mention** means this commit or this pull request has no mention. Do not write `work-item.md` from that answer.

A file whose every line fails the table uses the “no usable line” hint below. A file that parses some lines ignores the rest.

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
