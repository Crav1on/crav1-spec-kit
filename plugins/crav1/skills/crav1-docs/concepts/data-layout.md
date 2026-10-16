# Data layout

This page lists every folder and file the kit reads or writes in a product repo, and which command writes it. It also lists the marks the kit adds inside those files, and the spec sections the kit looks for by name. What each command does in full is in the [skills reference](../reference/skills.md). Words used here are in the [glossary](glossary.md).

The kit writes files. It does not commit, push, or open a pull request unless you ask for that in the same turn. The commit and pull request skills do that, one step at a time.

## The tree

A layout that works without extra command-line tools:

```text
docs/system/
  _template/
  landscape.md       # short description, how the parts connect, v0 vs later, bulk A#s, feature index
  repos.md           # named repos (proposed until a URL exists), Synced at and Work items go to per repo
  diagrams.md        # context diagram; /crav1-refresh-system-notes adds what is new
  glossary.md        # words the source already uses; not a feature spec
  security.md        # kept risks after /crav1-review-security (system pass); not seeded by spark
  adr/
docs/architecture/
  spec.md            # one architecture spec from /crav1-existing-to-specs
  left-out.md        # guesses that stay left out
docs/environments/
  marks.md           # confirmed environment lines from read-environment or map-pipeline-environments
docs/notes/
  index.md           # generated: one row per month
  YYYY-MM/           # month of the source date (1.61.0)
    index.md         # generated: one row per note
    YYYY-MM-DD-<slug>.md  # one full input (fact, dump, code change, meeting) and its source
    review-pr-<n>-follow-ups.md  # follow-ups from /crav1-review-pr, one note per pull request
docs/sources/
  YYYY-MM-DD-<slug>/ # an imported mail, transcript, chat, screenshot, or other original
docs/research/
  <topic>.md         # research notes; a spec's ## Research findings links to them
docs/specs/
  _template/
    spec.md          # what / why / acceptance
    plan.md          # how / constraints / files / linter
    tasks.md         # ordered, testable slices
    verify.md        # acceptance matrix after implementation
    fix-log.md       # one gap from verify-build-against-spec, fix + re-proof
    live-fix.md      # legacy; new incidents go in fix-log.md
    work-item.md     # optional Azure Boards id starter (comment only)
  <change-id>/
    spec.md
    plan.md
    tasks.md
    verify.md
    fix-log.md
    diagrams.md      # ideas-to-spec and tighten-spec
    adr/             # slice decisions
    export/          # EARS, BDD, OpenSpec, YAML, JSON, or BMAD copies
    notes.md         # optional, from ideas-to-spec
    explore.md       # bugs from /crav1-run-exploratory-test
    work-item.md     # Azure Boards ids, one per line
```

`/crav1-plan-from-spec` writes `plan.md` and `tasks.md` into that folder so teammates see them.

## Who writes what

| Path | What it holds | Written by | Read by (examples) |
| --- | --- | --- | --- |
| `docs/system/landscape.md` | Short description, `## How the parts connect`, v0 vs later, bulk assumptions, `## Feature index`, and optionally `## Ideas`, `## Way of working`, `## Code with no slice`, `## No spec yet in ADO` | Seeded thin by `/crav1-spark-to-spec` and `/crav1-ideas-to-spec` when missing; written by `/crav1-bundle-to-specs` and `/crav1-existing-to-specs`; one index row per new spec; new lines by `/crav1-refresh-system-notes`; system notes by `/crav1-existing-to-specs` when missing; a "No spec yet in ADO" row by `/crav1-ado-sync` | `/crav1-explain-existing-system`, `/crav1-what-do-we-know-about-this`, `/crav1-ado-sync`, `/crav1-build-features` |
| `docs/system/repos.md` | Named repos and a `Synced at` cell per repo | The same commands that seed the landscape; `/crav1-refresh-system-notes`, `/crav1-existing-to-specs`, `/crav1-add-to-spec`, and, where they read repos, `/crav1-bundle-to-specs` and `/crav1-ideas-to-spec` update `Synced at` for a whole repo they read. A one-slice read writes a `Synced at` line in that slice’s `spec.md` instead | `/crav1-explain-existing-system`, `/crav1-plan-from-spec` |
| `docs/system/diagrams.md` | The context diagram | Seeded with the landscape; new nodes by `/crav1-refresh-system-notes` and the same pass in spark, ideas, intake, match, match-dump, and add-to-spec | `/crav1-explain-existing-system` |
| `docs/system/glossary.md` | Words the source already uses | Filled when missing and appended to by spark, ideas, intake, match, match-dump, and add-to-spec. Existing rows are not rewritten. A meaning the source does not state is `to be researched` | Every skill that writes a spec |
| `docs/system/security.md` | Kept risks from a system pass | `/crav1-review-security` | `/crav1-review-security`, `/crav1-plan-from-spec`, `/crav1-tighten-plan`, `/crav1-explain-existing-system` |
| `docs/system/adr/` | Cross-cutting decisions | `/crav1-bundle-to-specs`, `/crav1-ideas-to-spec`, and `/crav1-existing-to-specs`, only for a choice that had real alternatives | Plan, explain-existing-system, security review |
| `docs/architecture/spec.md` | One architecture spec from code | `/crav1-existing-to-specs`, when missing | The lanes that extend it |
| `docs/architecture/left-out.md` | Guesses that stay left out, under `## Left out`, and `## Dismissed` lines | `/crav1-existing-to-specs` | `/crav1-existing-to-specs` on a re-read, `/crav1-read-environment` |
| `docs/environments/marks.md` | One confirmed line per resource and environment | `/crav1-read-environment` and `/crav1-map-pipeline-environments`, appending only confirmed lines; `/crav1-ado-sync` appends one `Azure Boards task type:` line | `/crav1-read-environment`, `/crav1-what-do-we-know-about-this`. Line format: [Environment marks](../environments-marks.md) |
| `docs/specs/<slug>/plan.md`, `tasks.md` readiness marks | `Reviewed:` in `plan.md`, `(after: T#)` on task lines, `Blocks:` under spec open questions | `/crav1-review-plan`, `/crav1-tighten-plan`, `/crav1-plan-from-spec`, `/crav1-resolve-open-questions` | `/crav1-tasks-ready-to-build` |
| `docs/notes/YYYY-MM/` | One note per input with the full input and its source, by source date; generated `index.md` per month and a top `index.md` | `/crav1-add-to-spec` for every input (1.61.0); `/crav1-review-pr` for its follow-ups note; `/crav1-retire-spec` convert to note. Indexes: `notes_index.py` only |
| `docs/sources/YYYY-MM-DD-<slug>/` | The original of an imported mail, transcript, minutes, chat, screenshot, or diagram, plus a `README.md` | `/crav1-add-to-spec`, `/crav1-bundle-to-specs`, `/crav1-existing-to-specs` | Anyone checking a quote. See [Data policy](data-policy.md) |
| `docs/research/<topic>.md` | A short research note with the recommendation, trade-offs, confidence, and a link to the full study | The researcher (no slash command; see [guild routing](../guild-routing.md)). Skills only add or clear a stale mark | add, match-dump, add-to-spec, meeting, refresh-system-notes, explain-existing-system, what-do-we-know-about-this, ado-sync |
| `docs/specs/<slug>/spec.md` | What and why, acceptance, open questions | spark, ideas, intake (through `crav1-bundle-slice-agent`), match; then tighten-spec, resolve-open-questions, add-to-spec, match-dump, add-to-spec, and review-security | Every later lane |
| `docs/specs/<slug>/plan.md`, `tasks.md` | How, constraints, files, linter; ordered testable tasks | `/crav1-plan-from-spec`, `/crav1-tighten-plan`; `[x]` on a task row by implement and build-tasks | Build, verify, review |
| `docs/specs/<slug>/verify.md` | The acceptance matrix | `/crav1-verify-build-against-spec`; one row by `/crav1-fix-build-gaps` | `/crav1-open-pr`, `/crav1-review-pr` |
| `docs/specs/<slug>/fix-log.md` | One gap from verify, the fix, and the re-proof | `/crav1-fix-build-gaps` | Verify, review |
| `docs/specs/<slug>/live-fix.md` | Legacy. New incidents go in `fix-log.md` | Nothing new | Read when present |
| `docs/specs/<slug>/diagrams.md`, `adr/`, `export/`, `notes.md` | Slice diagrams, slice decisions, export copies, idea notes | `/crav1-ideas-to-spec`; `/crav1-tighten-spec` for a named diagram or ADR; `/crav1-export-spec` and plan for `export/` | Architecture review, plan |
| `docs/specs/<slug>/explore.md` | Bugs found by exploratory testing | `/crav1-run-exploratory-test` | `/crav1-fix-bug` when you say so |
| `docs/specs/<slug>/work-item.md` | Azure Boards ids, one per line | spark, ideas, and intake after an opt-in on Azure Repos; `/crav1-ado-sync` (task lines `Work item: <id> — task: T<n> <title>`) after a yes, and `/crav1-ado-sync` for an added task | Commit and pull request skills, `/crav1-ado-sync` |
| Transfer data policy rule | The once-per-repo answers for the personal-data check | Any skill that imports a source, after a yes. See [Data policy](data-policy.md) | The same skills |
| Commit-style rule | The commit style chosen for later commits | `/crav1-finalize-commit`, and build-tasks when onward is chosen | The commit skills |

The host file names for the two rules are in [install](../install.md) and on the skill pages.

## Notes

Since 1.61.0 every `/crav1-add-to-spec` input (fact, dump, code change, meeting) becomes **one note** that holds the full input and its source. A fact's note holds the fact plus the passage around it. Each matching spec gets only its own short points, each followed by `Full source: docs/notes/YYYY-MM/<file>.md`. Notes are never absorbed; `used_by` grows as specs take points. There is no Note choice and no "never used" flag. The rule is `crav1-add-to-spec` `references/notes.md`.

Each note is `docs/notes/YYYY-MM/YYYY-MM-DD-<slug>.md`. The date and the month folder are the **source date** (meeting date, mail sent date, commit date). The note also records `imported`. A source with no date is filed under the import date with `source_date: none`, and the run says so. The shape is `docs/notes/_template/note.md`:

```text
---
title: Title
kind: fact | dump | code change | meeting | email | chat | review-pr | converted spec
source: <mail subject, sender, sent date | meeting date and title | file path | commit sha>
source_date: YYYY-MM-DD
imported: YYYY-MM-DD
source_folder: docs/sources/YYYY-MM-DD-slug/
used_by: []
waiting_for: []
---
# Title

Source date: YYYY-MM-DD. Imported: YYYY-MM-DD.

<the full input, verbatim>
```

**Generated indexes.** `docs/notes/index.md` (one row per month) and `docs/notes/YYYY-MM/index.md` (title, date, kind, source, used by, waiting for) are built from the front matter by `notes_index.py` in the `crav1-add-to-spec` skill folder (`scripts/notes_index.py`). `--check` fails when an index is stale, so a product repo can run it in CI. No skill edits an index by hand. Lookups for a spec follow its `Full source:` links; matching new input and the duplicate check read the indexes.

**Duplicate check.** The same source again (the same mail, meeting date and title, file, or commit) is not written twice: the run says `already imported on <date> as <note>` and offers reuse (for specs that took nothing yet) or skip. The same point from a different source adds the new note as a second source on the existing spec line. A disagreement is written as a `**Conflict:**` line for the user to decide, never an overwrite.

**Parked specs.** A parked spec gets nothing written; its slug goes in the note's `waiting_for` until `/crav1-retire-spec` un-parks it.

**Older notes.** Notes from before 1.61.0 (flat in `docs/notes/`, no front matter, maybe `Absorbed by`) are still read; `Absorbed by` counts as used by. `/crav1-refresh-system-notes` recommends `notes_index.py migrate-dry-run` first (prints planned moves, source fills, and link rewrites; writes nothing), then the one-time move, `notes_index.py migrate` (1.62.0). It files notes by source date, fills `source` and `source_folder` from each note's `Source:` line (empty when there is none, never guessed; `/crav1-add-to-spec` uses these for its already-imported check), rewrites every markdown link to a moved note anywhere in the repo with correct relative paths and lists each changed file, and rebuilds the indexes. Re-running is safe. Old spec lines keep their source lines; nothing is backfilled. `/crav1-bundle-to-specs`, `/crav1-ideas-to-spec`, `/crav1-spark-to-spec`, `/crav1-tighten-spec`, and `/crav1-existing-to-specs` add their slug to `used_by` when they quote a note; `/crav1-ado-sync`, `/crav1-help`, and `/crav1-show-or-ask-open-questions` read the month folders and the generated indexes.

### Review follow-ups note

`/crav1-review-pr` does not post follow-ups to the pull request or put them in the paste-ready comment. When a review has at least one, it writes `docs/notes/YYYY-MM/review-pr-<n>-follow-ups.md` (month of the review date) in the same note format, where `<n>` is the pull request number. When two repos in the specs repo have the same pull request number, the file is `review-pr-<repo>-<n>-follow-ups.md`. The title is `Follow-ups from PR <n> (<repo>)`, front matter `kind: review-pr`, and each follow-up keeps its file and line. The indexes are regenerated. A re-review updates the same note where it is: it sets `imported` to the review date, adds new follow-ups, and marks addressed ones `(done in <short sha>)` without removing a line. A review with no follow-ups writes no note. See [From a pull request review](../from-review-pr.md#follow-ups).

## Sources

Each imported source is one folder, `docs/sources/YYYY-MM-DD-<slug>/`. The date is the date of the source. When the date is unknown, the folder is `docs/sources/undated-<slug>/`. The slug is short, lowercase, with hyphens, and never a person's name. The folder holds the original files and a `README.md`. A pasted mail, transcript, or chat with no file is still a source and is written as a text file. The full convention is the add-to-spec reference [sources.md](../../.cursor/skills/crav1/crav1-add-to-spec/references/sources.md). The personal-data part is summarized in [Data policy](data-policy.md).

A quote in a spec from an imported source carries `Source: docs/sources/YYYY-MM-DD-<slug>/`. Under `## Trace`, each pass adds one line: `Trace: docs/sources/YYYY-MM-DD-<slug>/ — <what this pass marked new, already there, and inferred>.`

## Research and stale marks

When a kept quote changes what a research note says, the skill asks before it marks the note stale. On yes, it adds one blockquote below the note's title and owner line:

```text
> Stale since <date>: <one line on what changed>. Source: docs/sources/YYYY-MM-DD-<slug>/
```

On each spec the quote was written into, or that links to that note, it adds under `## Research findings`:

```text
Stale since <date>: <one line>. See <note path>.
Point: <short label>. <the research line or the question, quoted>.
```

There is one `Point:` line per hit. When the note is updated, `/crav1-refresh-system-notes` or `/crav1-add-to-spec` checks each point and clears, narrows, or routes it. `/crav1-explain-existing-system`, `/crav1-what-do-we-know-about-this`, and `/crav1-ado-sync` show a stale note as stale and do not clear it. The full rules are in [research-stale.md](../../.cursor/skills/crav1/crav1-add-to-spec/references/research-stale.md).

## Open question marks

Under each item in a spec's `## Open questions`, the kit can add four kinds of lines:

```text
- <question>
  - Pending: drafted <date> for <who>, <channel>. Not marked as sent yet. Question <n> of that draft.
  - Asked: <date>, <channel> to <who>. Question <n>. Date from <the user's yes | email <date> | meeting <date> | chat <date>>.
  - Answered: <date>, <who>, <kind>: "<quote>" Source: docs/sources/YYYY-MM-DD-<slug>/
  - Blocks: T2, T4
```

`Blocks:` names the tasks that wait on a kept-open question. `/crav1-resolve-open-questions` writes it after a keep-open pick, and `/crav1-plan-from-spec` writes it for a kept-open question it parks as a risk. Without a `Blocks:` line, a kept-open question blocks the whole slice for [`/crav1-tasks-ready-to-build`](../from-tasks-ready-to-build.md). See [Readiness marks](#readiness-marks).

`/crav1-show-or-ask-open-questions` writes `Pending:` or `Asked:` after you say whether the draft was sent. `/crav1-add-to-spec` write `Answered:` when a kept quote clearly answers that question. `/crav1-resolve-open-questions` then walks the question with you. The full format is in [open-questions.md](../../.cursor/skills/crav1/crav1-add-to-spec/references/open-questions.md).

## Readiness marks

[`/crav1-tasks-ready-to-build`](../from-tasks-ready-to-build.md) reads three optional marks. Each is written only by the skills named here; the reader writes nothing:

| Mark | Where | Written by | Meaning |
| --- | --- | --- | --- |
| `Reviewed: <date>, P# open: <n>` | `plan.md`, under the `# Plan:` title | `/crav1-review-plan` writes it; `/crav1-tighten-plan` lowers `<n>` as `P#`s are fixed | The plan was reviewed, and how many reviewer findings are still open |
| `(after: T1, T3)` | End of a task line in `tasks.md` | `/crav1-plan-from-spec` | The task needs those tasks done first |
| `Blocks: T2, T4` | Under a kept-open question in `spec.md` | `/crav1-resolve-open-questions`, `/crav1-plan-from-spec` | The question blocks only those tasks |

When a mark is missing, the reader falls back and labels the reason **inferred**:

- No `Reviewed:` line: the task can still be ready, with a warning to run `/crav1-review-plan`.
- No `(after: …)`: every earlier unticked task blocks it.
- A kept-open question, or a plan Risk that says do not implement until resolved, with no `Blocks:` line: it blocks the whole slice.

A ticked task is Done only when `verify.md` lists it as verified. Otherwise it shows as Needs verify.

## Work item homes

Each implementation repo has its own work item home: the Azure DevOps (ADO) project its work items go to. The home is the `Work items go to` cell for that repo in `docs/system/repos.md`:

```text
ADO: <org>/<project>
```

- The specs repo itself never has a home. Its cell stays empty.
- Skills that write `repos.md` add the column when it is missing and leave new cells empty. The first Azure Boards skill that needs a home asks once per repo, with the repo's own ADO project marked as the suggestion, and writes the cell after the answer. A later run reads the cell and does not ask again. To change a home, edit the row.
- A task goes to the home of the repo it touches. A Feature goes to the homes of its spec's repos: one Feature per home, each holding only its own repos' tasks. Features in the same org are linked as related. Features in different orgs mention each other in the description.
- `Jira: <project>` is reserved for later. Nothing reads or sends to Jira yet, so a repo with a `Jira:` cell is treated as having no home.

## Work item file

`docs/specs/<slug>/work-item.md` is optional and only for Azure Boards linking. One id per line, optionally with the milestone or slice it belongs to:

```text
Work item: 52 (ADO: contoso/bc-operations)
Work item: 81 — October billing (ADO: contoso/bc-operations)
```

Each id line ends with its [work item home](#work-item-homes), `(ADO: <org>/<project>)`. An older line without the tag is read as the org and project in `docs/environments/marks.md`, and the next skill that writes the file adds the tag. One spec may record one Feature per home, and a Feature line and its task lines share a home.

The commit and pull request skills turn the id into a mention from the git remote: `#52` on Azure Repos, `AB#52` on GitHub. Any other host adds no mention. Leave the ids out of `tasks.md`. Task lines (`Work item: <id> — task: T<n> <title>`) record the child work items of the Feature. The mention keeps the Feature id; a commit that clearly implements one recorded task adds that task's id too, and the commit skills ask when it is unclear. A task id is never the only mention. Nothing blocks when the file is missing. The template comment is [`docs/specs/_template/work-item.md`](../specs/_template/work-item.md).

## Spec sections the kit looks for

The kit finds these headings by name. Keep the names when you edit by hand.

| Heading | Where | What reads or writes it |
| --- | --- | --- |
| `## Acceptance criteria` | `spec.md` | Yes or no lines. Plan maps each to a task. Verify checks them |
| `## Open questions` | `spec.md` | Tighten-spec, resolve-open-questions, show-or-ask-open-questions; the marks above |
| `## Assumptions`, `## Constraints` | `spec.md` | Written by intake and ideas; read by resolve-open-questions and plan |
| `## Repos` | `spec.md` | Written by intake for a one-repo feature |
| `## Match` | `spec.md` | Match status: done, partial, not in the code, or retired. Read by plan, tighten-spec, explain-existing-system, build-features |
| `## In the code` | `spec.md` | Paths of code that already exists. Plan and tighten-spec read that code first |
| `## Research findings` | `spec.md` | Links to `docs/research/` notes and stale marks |
| `## Trace` | `spec.md`, `plan.md` | Source trace lines on the spec; acceptance to task map on the plan |
| `## Security` | `spec.md` | Kept findings from `/crav1-review-security` on one spec |
| `## Dismissed test suggestions` | `spec.md` | Suggestions dismissed in `/crav1-suggest-tests-for-code`. Not acceptance and not a task |
| `## Linter` | `plan.md` | The linter or checker the build must leave green, or a line that there is none |
| `## Left as committed` | `plan.md` | Built pieces you chose to leave. Not offered again unless you say so |
| `## How the parts connect`, `## Feature index` | `docs/system/landscape.md` | The picture. Refresh-system-notes adds lines. Explain-existing-system compares them |
| `## Left out`, `## Dismissed` | `docs/architecture/left-out.md` | Existing-to-specs and read-environment |
| `used_by` | front matter of a note in `docs/notes/YYYY-MM/` | Which specs took points from the note (older notes: `## Used by`) |

## Renamed skills (1.56.0)

The files above did not move. Only the skills that write them were renamed. The old names were removed in 1.58.0; the [renamed skills](../README.md#renamed-skills-1560) table maps each old name to the new one. A merged skill keeps each old skill's rules in `.cursor/skills/crav1/<skill>/branches/<id>/BRANCH.md`.
