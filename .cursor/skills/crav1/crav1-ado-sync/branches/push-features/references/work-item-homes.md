# Work item homes

The specs repo is the source of truth. It is not tied to any tracker. Each implementation repo has its own **work item home**, where the work items for that repo's work go. One home can hold one or many repos, in any combination.

Read by `/crav1-ado-sync`, `/crav1-ado-sync`, `/crav1-what-do-we-know-about-this`, `/crav1-open-pr` (Azure DevOps part, through `work-item-mention.md`), and the skills that write `docs/system/repos.md`.

## Where the home is written

`docs/system/repos.md` has a column **Work items go to**, one cell per implementation repo:

```text
ADO: <org>/<project>
```

`Jira: <project>` is reserved for later. Nothing reads or sends to Jira yet. When a cell starts with `Jira:`, say Jira is not supported yet and treat that repo as having no home this run. Do not ask again.

- Never a home for the repo that holds the specs. Leave its cell empty.
- Written only after the user answers the question below. Never filled in silently, never guessed, never copied from another row without the answer saying so.
- A skill that writes `repos.md` adds the column when it is missing and leaves new cells empty. It does not ask for homes. The first skill that needs a home asks.
- Changes happen only by editing the row. A later run reads the cell and does not ask again.

## Ask (first time a repo's home is needed)

Ask once per repo with an empty cell, when a skill needs that repo's home. Use the questions tool when it is available. Options:

1. **The ADO project the repo lives in** (from its Azure DevOps URL in `repos.md`), marked `(Suggested)`. When the repo has no Azure DevOps URL, the project line in `docs/environments/marks.md` is the suggestion. When neither exists, there is no suggestion.
2. **Every other ADO project `az` can read** in that org (`az devops project list --organization <org-url> --detect false -o json`). When the list cannot be read, say so in one line and offer only the others.
3. **Same for all <N> new repos.** Only when more than one repo needs an answer in this run. Applies the picked home to every repo in this run with an empty cell.
4. **Type it.** `ADO: <org>/<project>`.

Write the cell right after the answer. Do not rewrite other cells or rows.

A run with no window uses the two-pass questions file from the imported-sources convention (drop-in: `.cursor/skills/crav1/crav1-add-to-spec/references/sources-rare.md` → **Headless runs (two-pass)**; plugin: sibling `skills/crav1-add-to-spec/references/sources-rare.md`). Pass 1 writes the question and sends nothing for that repo.

## Which home a task or a Feature goes to

- **A task** goes to the home of the repo it touches: the code repos the task or the plan names for it, else the slice's repos.
  - No clear repo: ask once for that task. Suggest the spec's main repo (the first code repo the spec or plan names).
  - Several repos in different homes: ask. Suggest splitting the task into one task per repo (through `/crav1-add-to-spec`), or picking one repo's home.
  - Several repos in one home: that home.
- **A Feature** goes to the homes of its spec's repos. When those repos are in several homes, it becomes one Feature in each home. Each one holds only the tasks of its own repos, its tags name only its own repos, and each is previewed and sent only on its own yes.
  - Same org: link them to each other with a `System.LinkTypes.Related` relation after both exist.
  - Different orgs: no link. Mention the other Feature in the Description in plain text: `Also tracked in <org>/<project> as Feature <id>.`

## Recorded ids

Every `work-item.md` id line ends with its home:

```text
Work item: 52 — October billing (ADO: contoso/orders)
Work item: 1234 — task: T3 Short title (ADO: contoso/orders)
```

- An older line without `(ADO: …)` is read as the org and project in `docs/environments/marks.md`, else the single pair the Azure DevOps URLs in `repos.md` name.
- The next time a skill writes that `work-item.md`, it adds the tag to those older lines without asking. Change nothing else on them.
- One spec may record one Feature per home. A Feature line and its task lines share a home.

## Reading an id back

Read each id in its own home. When it is not found there, report it as **moved or missing** with its recorded home. Ask before searching other projects: **Search the other projects `az` can read**, or **Leave it**. Never search on your own. Never match on the title. When a search finds it, show where, and ask before rewriting the home on that line.

## marks.md

`docs/environments/marks.md` keeps the Azure DevOps org. Its project line is only a fallback suggestion for the question above, and the home for older id lines. Task type and done state are kept per home:

```text
Azure Boards task type (<project>): <type>
Azure Boards task done state (<project>): <state>
```

An older line without `(<project>)` is read as the line for the marks.md project. A new home asks its own type once.

## Unchanged

Nothing goes to Azure Boards without a yes. Iteration and Priority stay blank. Code repo names stay in the text, paths and line numbers are stripped, and the specs repo is never mentioned. The State handling of the push tasks branch of `/crav1-ado-sync` is unchanged.
