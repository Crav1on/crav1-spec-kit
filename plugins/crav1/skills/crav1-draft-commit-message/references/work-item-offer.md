# Work item offer

Optional, once, when a spec skill creates a new spec folder. Read this from `/crav1-spark-to-spec`, `/crav1-ideas-to-spec`, and `/crav1-intake-to-specs` at the end of the turn that created the folder. Commit and pull-request skills do not read this file. They only read an existing `work-item.md` via [work-item-mention.md](work-item-mention.md).

Creating the work item in Azure Boards is out of scope. Do not create a work item. Do not look one up. Do not call an Azure DevOps API. Do not run `az`. Do not pass `--work-items` or `--transition-work-items`.

## When to ask

Ask only when all of these are true:

1. This turn created one or more new `docs/specs/<slug>/` folders (the directory did not exist before this turn). Extending an existing folder does not count.
2. That slug has no `docs/specs/<slug>/work-item.md` yet.
3. The git remotes are Azure Repos, using the same rule as [work-item-mention.md](work-item-mention.md) **Remote prefix**. Use `git remote -v` fetch URLs. Azure Repos shapes are `dev.azure.com` and `*.visualstudio.com` (HTTPS or SSH), the same shapes as `/crav1-open-pr`. Ask only when there is one Azure Repos remote, or every remote is Azure Repos.

Do not ask when:

- The host is GitHub (`github.com`), any other host, there is no remote, or the remotes are mixed.
- The slug already has `work-item.md`.
- This command already asked, including when the user skipped or did not answer.

On GitHub or any other host that is not Azure Repos, never ask.

## Question

One question. Optional. Non-blocking. The spec files are already written. In the same turn, state that creating the work item in Azure Boards is out of scope and that this only records an id the user already has.

The question must accept a free-text id. If a questions tool cannot take that id, ask in the reply. Skip is a valid answer.

One new slug:

```text
Optional: link an Azure Boards work item to <slug>? Reply with the id, or skip.
```

Several new slugs (intake, or any run that created more than one folder that still lacks the file). One question lists every such slug. Do not ask once per slug.

```text
Optional: link an Azure Boards work item to these new specs (<slug-a>, <slug-b>)? Reply with an id per slug, or skip.
```

If the user skips or does not answer, write nothing and do not ask again in this run.

The turn that created the folders asks, then waits. The next message in this command is the answer. An id writes the file. Skip, or a message with no id, writes nothing. Do not ask a second time. Do not commit.

## What counts as an id

| Reply | File line |
| --- | --- |
| Digits (`52`) | `Work item: 52` |
| `#` plus digits (`#52`) | `Work item: #52` |
| `AB#` plus digits (`AB#52`; any letter case on `AB`) | `Work item: AB#52` |
| The same forms after a `Work item:` label | That id, in the form above |

Surrounding whitespace does not matter. Write `AB#` in uppercase so [work-item-mention.md](work-item-mention.md) can parse the line.

A single slug may be a bare id, or the slug plus the id (`<slug>: 52`). A different slug name writes nothing.

For several slugs, each id must name its slug (`billing: 52`, `catalog #18`). A slug with no id in the reply is a skip for that slug. One bare id with several slugs does not apply to all of them. Do not guess. Do not ask again.

Anything else (including "skip", "no", or a sentence that is not an id) writes nothing for that slug.

## File

Path: `docs/specs/<slug>/work-item.md`.

The file is that single line and a trailing newline. Do not copy `docs/specs/_template/work-item.md`. Do not add the HTML comment. Do not put the id in `tasks.md`.

After writing, stop. These skills do not commit.

## Who asks

The parent asks. `/crav1-intake-to-specs` asks after Index, once, for every new slug folder that still has no `work-item.md`. Slice workers do not ask and do not write `work-item.md`.
