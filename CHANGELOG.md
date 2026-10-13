# Changelog

Notable changes to **CRAV1 Spec Kit** (`crav1`). Version matches `plugins/crav1/.cursor-plugin/plugin.json`.

## Unreleased

## 1.46.0 (2026-10-13)

### Kit

- New skill `/crav1-ado-to-tasks` (cross-cutting, later skill, not a starter). Pick a spec with task lines in `work-item.md`, or all. Every recorded task item is read back (State, title, description, acceptance, Assigned To, comments, history) and only what differs from the spec and `tasks.md` is shown, plus child items under the Feature that no task line records. Each difference is kept or dismissed, fresh every run; kept changes go in through `/crav1-add-to-spec`. A task Done in Azure Boards ticks its box only on a yes; a new child is added as a task and recorded in `work-item.md` only on a yes. It never writes a field back; reply comments are stripped and posted only on a yes.
- Work-item mentions (`work-item-mention.md`, used by `/crav1-draft-commit-message`, `/crav1-finalize-commit`, and `/crav1-open-pr`): task lines `Work item: <id> — task: T<n> …` were read as ordinary labelled lines, so a file with a Feature line and task lines asked between all of them and could mention only a task id. Task lines are now their own kind. The mention keeps the Feature id; a task id is added after it only when the change clearly implements one recorded task, the skill asks when unclear, and a task id is never the only mention. `/crav1-feature-candidates`, `/crav1-specs-to-ado`, and `/crav1-ado-to-specs` no longer treat task lines as Feature ids.
- `/crav1-tasks-to-ado` names `/crav1-ado-to-tasks` as the later read-back.
- `plugins/crav1/.cursor-plugin/plugin.json` is 1.46.0.

### Docs

- New walkthrough [From Azure Boards to tasks](docs/from-ado-to-tasks.md) and reference page, linked from the docs index, [From tasks to Azure Boards](docs/from-tasks-to-ado.md), the [data layout](docs/concepts/data-layout.md) (task lines and mentions), and guild routing.
- New walkthrough [From tasks to Azure Boards](docs/from-tasks-to-ado.md) for `/crav1-tasks-to-ado`, with a generic task example. Linked from the docs index, the skill's reference page, [From specs to Azure Boards](docs/from-specs-to-ado.md), the [data layout](docs/concepts/data-layout.md) (task lines in `work-item.md`), [Environment marks](docs/environments-marks.md) (the task type line), and the plugin README.

## 1.45.0 (2026-10-13)

### Kit

- New skill `/crav1-tasks-to-ado` (cross-cutting, later skill, not a starter). Pick one spec that already has a Feature id in `work-item.md`; every task in its `tasks.md` is listed and you pick by number or all. The child work item type is asked once and saved as `Azure Boards task type: <type>` in `docs/environments/marks.md`. Each task is previewed (Create or Update #id, only changed fields on an update) in the Feature layout: fuller title, State New, Iteration and Priority blank, slice and code repo tags, owner when stated, fuller description with decisions, quotes, names, and dates, open blockers or none recorded, and the verify line as acceptance. Paths, line numbers, spec references, and kit names are stripped; code repo names stay; the specs repo is never mentioned. Created only after a yes, as a child of the Feature, and recorded as `Work item: <id> — task: T<n> <short title>` in `work-item.md` (never in `tasks.md`). Uses the same `az` checks as `/crav1-specs-to-ado`, plus a new `references/child-items.md`.
- `/crav1-specs-to-ado` names `/crav1-tasks-to-ado` as the next step in its report and does not run it.
- `plugins/crav1/.cursor-plugin/plugin.json` is 1.45.0.

### Docs

- New reference page for `/crav1-tasks-to-ado`, the skills table, and guild routing updated.

## 1.44.0 (2026-10-13)

### Kit

- `/crav1-review-pr` comment style (agreed by Thomas and Rhea, 2026-10-12) for the paste-ready block, posted comments, and re-review replies: the user's own friendly first-person voice, the source kept vague ("me and my checks", never a tool, skill, or bot), a varied opening every time, soft wording with the same information, and the description read first so deliberate choices are acknowledged and moved to Follow-ups. The sections are now Blocker, Bugs, Tests to add with this PR, and Follow-ups (not for this PR), replacing blocking / should fix / nit. Each file links to the pull request files view (GitHub or Azure DevOps) with per-line remarks usable as inline comments. Posting on yes, the summary without the verdict line, the verdict options, and the re-review statuses are unchanged.
- `plugins/crav1/.cursor-plugin/plugin.json` is 1.44.0.

### Docs

- The review-pr reference page describes the comment style.

## 1.43.0 (2026-10-13)

### Kit

- Imported sources (`crav1-add-to-spec` `references/sources.md`, used by add-to-spec, intake, match, match-dump, and meeting): the transfer data policy is one shared policy for Cursor and Claude Code, written as both copies together and copied across when only one exists (conflicting copies: the user picks). Temporary files go to the system temp folder and are deleted even on failure. An image the kit cannot view is never guessed at: it is left out and flagged for Rhea or the user to check. New two-pass headless mode (questions to a temp file, answers on a second run). Partial extracts get a "Left out" list. Black-boxed PDF text is treated as redacted (`[redacted in source]`). Superseded versions are kept and marked "Superseded by"; only the newest is read. Source precedence: newest decided source wins, otherwise an open question, with a conflict pass after a multi-file intake. Plain uncontested facts are applied without asking and listed in the run summary. One folder per document. Ambiguous dates are never guessed. `.docx` tracked changes are accepted but flagged and comments listed with author and date. Exact duplicate images are stored once. New glossary terms are added freely; rewriting an existing row needs a yes.
- `/crav1-review-pr` ends with a paste-ready Markdown comment (verdict, findings by severity with file and line, suggested fix, no kit-internal details, English by default). After the user's yes it posts each finding as an inline comment on its line and a summary without the verdict line, then offers the verdict options (approve, comment, request changes). A re-review reads earlier findings from the pull request's threads and marks each Fixed (with the commit), Partly fixed, Still open, or No longer relevant, flags resolved-but-still-open threads, replies in existing threads, and resolves threads only after a yes.
- `/crav1-feature-candidates` uses the hand-made layout: titles that say what the work is, fixed labelled lines per candidate (Target date with source, Spec, Description, Open blockers/questions, Order/priority), and fuller descriptions with context, owners, related tasks, and dated quotes, with no invented facts.
- `/crav1-specs-to-ado` strips spec paths, `docs/sources/` folders, and spec references from the candidate text before the preview.
- `plugins/crav1/.cursor-plugin/plugin.json` is 1.43.0.

### Docs

- [Data policy](docs/concepts/data-policy.md): the shared policy and how imports handle the hard cases. Skill reference pages regenerated for review-pr, feature-candidates, and specs-to-ado.

## 1.42.0 (2026-10-11)

### Kit

- The always-on project instruction (`.cursor/rules/crav1.mdc`, the plugin copy, and the generated `.claude/CLAUDE.md`) is cut from about 5,150 words to about 650: standing rules plus pointers: the layout and `Synced at` rules, the seven starter options, the typical order, six standing rules that hold for every skill, and links to the skills reference and the data layout. The per-skill text it repeated already lives in each skill's `SKILL.md` and on its reference page.
- `/crav1-implement-task` and `/crav1-complete-task` now say in their own `SKILL.md` that they do not ask whether to run `/crav1-keep-current`. The project instruction said this before; the behavior is unchanged.
- [CONTRIBUTING.md](CONTRIBUTING.md) and the maintainer rule: a new skill is done only when it is documented (its `skills.yaml` entry and reference page, a walkthrough that links back, a docs index line for a new page, and a CHANGELOG entry). The maintainer rule also says the project instruction stays standing rules plus pointers.
- `plugins/crav1/.cursor-plugin/plugin.json` is 1.42.0.

### Docs

- The [README](README.md) is now a short landing page: what the kit is, the seven starter options with links to their reference pages and walkthroughs, a lane diagram, and one pointer to the docs index.
- New [docs index](docs/README.md), grouped by type (tutorial, how-to, reference, explanation) and by reader (spec writer, developer, guild bot, maintainer). It is the one map of every page. [docs/install.md](docs/install.md) and [docs/first-run.md](docs/first-run.md) point at it instead of keeping their own long lists.
- New [docs/concepts/](docs/concepts/): [the method](docs/concepts/method.md) (how the pieces fit together, the starting points, the working loop, setup, best practices, and minimal templates, moved from the README), [data layout](docs/concepts/data-layout.md) (every folder and file, who writes it, notes, sources, research stale marks, open question marks, `work-item.md`, and the spec sections the kit looks for), a [glossary](docs/concepts/glossary.md), and the [data policy](docs/concepts/data-policy.md) for personal data and secrets in imported sources.
- The README's per-skill paragraphs and its "already ships" list moved into a new `in_depth` field in [`docs/reference/skills.yaml`](docs/reference/skills.yaml), shown under Purpose on each skill page. The README's per-lane tables are gone; the [skills reference](docs/reference/skills.md) has them.
- [plugins/crav1/README.md](plugins/crav1/README.md) uses full GitHub links and points at the skills reference instead of its own per-skill list.
- The Skills row in [docs/install.md](docs/install.md) links to the skills reference instead of describing every command.
- Five walkthroughs for the core loop after a starter: [From a draft spec to an accepted spec](docs/from-draft-spec.md) (architecture-reviewer, tighten-spec, resolve-questions, feature-branch), [From a spec to a plan](docs/from-spec-to-plan.md) (plan-from-spec, review-plan, tighten-plan), [Build tasks](docs/from-plan-to-build.md) (implement-task, complete-task, complete-tasks, complete-features), [Verify and fix](docs/from-verify.md) (verify-spec, fix-from-verify, fix-live), and [From commit to merge](docs/from-commit.md) (draft-commit-message, finalize-commit, open-pr, merge-pr).
- New walkthrough [Ask open questions](docs/from-ask-open-questions.md) for `/crav1-ask-open-questions`, including the `Pending:` and `Asked:` marks it writes. Every skill except `/crav1-export-spec` (reference only) now has a walkthrough.
- [Feature candidates](docs/from-feature-candidates.md), [From specs to Azure Boards](docs/from-specs-to-ado.md), and [From Azure Boards to specs](docs/from-ado-to-specs.md) follow the same outline as the other walkthroughs: First prompt, Steps, What gets written, After.
- Every walkthrough links to the reference page of each skill it covers, and each reference page links to its walkthrough through the `walkthrough` field in `skills.yaml`. `scripts/gen-skill-docs.py --check` fails when a walkthrough does not link back.
- [From a meeting to specs](docs/from-meeting.md) no longer names specific meeting or chat tools.

## 1.41.0 (2026-10-11)

### Kit

- New data file [`docs/reference/skills.yaml`](docs/reference/skills.yaml) holds every skill and subagent: lane, group inside the lane, starter flag, use when, what it reads and writes, what it leaves alone, its exceptions, who calls it, what it calls, what you run next, its walkthrough, the release it first appeared in, and a first prompt. It was seeded from the behavior map and the README skills table and covers all 42 skills and 5 subagents.
- New generator `scripts/gen-skill-docs.py` writes [`docs/reference/skills.md`](docs/reference/skills.md) (one table grouped by lane, Starters, Specify, Plan, Build, and Cross-cutting, with the README phases as groups inside the lanes, plus a table of all five subagents) and one page per skill under `docs/reference/skills/`. Columns: Command (linked to its page), Starter, Use when, Reads, Writes (every side effect), You run next, Runs by itself, and Walkthrough. Each page has Purpose, Runs when, Reads, Writes, Does not, You run next / Runs by itself, Lane and group, Stage and since, First prompt, and Walkthrough.
- CI runs `scripts/gen-skill-docs.py --check` (generated pages match the YAML, every skill folder and subagent is in it, lanes match the guild-routing map) and the new `scripts/check-kit-docs.py` (every skill description in the three trees is within 1,024 characters, and `plugin.json` equals the newest CHANGELOG release heading). Both need PyYAML.
- The behavior map moved out of `.cursor/rules/kit-maintainer.mdc` into the reference. The maintainer rule now points at `docs/reference/` and says a new or changed skill updates `skills.yaml` and regenerates. `plugin.json` is 1.41.0 and follows the release tag from now on.

### Docs

- Stale claims fixed. `/crav1-meeting-to-specs` has four choices (keep, leave, dismiss, or note) and `/crav1-match-dump-to-specs` has four piles (belongs, already in, note, does not fit) in the README and [docs/install.md](docs/install.md). The README "already ships" list now has `/crav1-meeting-to-specs`, `/crav1-ask-open-questions`, `/crav1-feature-candidates`, `/crav1-specs-to-ado`, and `/crav1-ado-to-specs`. The README minimal plan template has `## Linter`, the same as `docs/specs/_template/plan.md`. The README layout block lists `docs/architecture/`, `docs/environments/`, `docs/notes/`, `docs/sources/`, `docs/research/`, and the extra files in a spec folder.
- The project instruction is no longer called short in the README, [docs/install.md](docs/install.md), the maintainer rule, or the catalog description.
- [docs/guild-routing.md](docs/guild-routing.md) sends the researcher's note to `docs/research/` with a line under `## Research findings`, the place every skill reads. The `docs/specs/<slug>/research.md` path is gone.
- The README skills table lists every side effect in Writes: worker code and commits for `/crav1-complete-task`, `/crav1-complete-tasks`, and `/crav1-complete-features`, the reply comment after a yes for `/crav1-ado-to-specs`, sources, stale marks, and answer links for the import skills, and the code read for a partial slice in `/crav1-tighten-spec`. The subagent table lists all five subagents.
- [plugins/crav1/README.md](plugins/crav1/README.md) lists the Plan skills under Plan, not Build, and names `/crav1-ask-open-questions` among the later skills. [docs/install.md](docs/install.md) and [docs/first-run.md](docs/first-run.md) link the walkthroughs they were missing.
- A specific git client is no longer named in the README, `AGENTS.md`, the plugin README, `from-ideas.md`, or `from-nothing.md`.
- Skill descriptions: `/crav1-complete-task`, `/crav1-complete-tasks`, and `/crav1-finalize-commit` use host-neutral wording. The six descriptions over 1,024 characters (add-to-spec, code-into-specs, keep-current, match-dump-to-specs, meeting-to-specs, repos-to-spec) are shortened with the same meaning. The plugin mirror and `.claude/` copies are regenerated.
- `plugins/crav1/.cursor-plugin/plugin.json` is at 1.40.0, so the line above about the version matching now holds. Its description and the catalog description cover the current kit.
- [CONTRIBUTING.md](CONTRIBUTING.md), [docs/install.md](docs/install.md), [docs/guild-routing.md](docs/guild-routing.md), and the README point at the skills reference instead of the behavior map.

## 1.40.0 (2026-10-11)

### Kit

- New cross-cutting skill `/crav1-ask-open-questions`. The user names a person, one spec, or a topic. It gathers the open questions on the specs for that selection. For a person, that includes questions routed via that person, for example a partner's questions that go through one contact. It drafts a mail, a meeting agenda, a chat message, or meeting questions to ask out loud in a standup, a call, or a longer meeting. Meeting questions lists every selected question, not a short cut, and has no agenda layout. The questions are numbered and grouped by topic in plain words, each with enough context to be answered. The draft never names a spec slug, a path, or a question id. The kit keeps which question came from which spec on the spec itself. The draft is in English, or in the language the user names. The personal-data and secrets check runs on the draft, the same as for other outbound text. Nothing is sent. It is a later skill. It is not a starter option.

- After the draft, the skill asks whether the questions were asked. Each option says what it does. Yes writes an `Asked:` line under each question, with the date, how, and who. No writes nothing. Pending writes a `Pending:` line with the date and who, for text copied now and sent later. On the next run, pending questions are shown first, for example `Drafted for Arvid on 2026-10-11 (mail), not marked as sent yet.` The user can mark them as sent, keep them pending, or drop the mark. They are not mixed silently into the new draft.

- When `/crav1-meeting-to-specs`, `/crav1-match-dump-to-specs`, or `/crav1-add-to-spec` import a mail, a transcript, minutes, or a chat, a clear answer to a spec open question is linked under that question with the quote and the source, and the question is marked answered. Meeting does not ask keep for it. Match-dump links it with the confirmed sort. An unclear or partial answer is shown as a possible answer and the question stays open. An answer that would change a spec line names `/crav1-resolve-questions`. An answer that settles a stale research point runs the existing research re-check. Matching works whether the question is asked, pending, or not marked.

- When the imported source shows a question being asked, the asked-on date is the mail's sent date, the meeting date, or the chat message's date. That replaces a pending mark, or a date from the user's yes. The user's yes date is used only when no source shows it. After a meeting, questions that got an answer are linked. The rest go back to open and keep their asked mark.

- `/crav1-resolve-questions` shows a linked answer with its source and offers it first. When the user picks an answer, the quote and source stay with the decision. The shared wording is [`.cursor/skills/crav1/crav1-add-to-spec/references/open-questions.md`](.cursor/skills/crav1/crav1-add-to-spec/references/open-questions.md).

### Docs

- [docs/guild-routing.md](docs/guild-routing.md) lists `/crav1-ask-open-questions` under Cross-cutting. The behavior map in [`.cursor/rules/kit-maintainer.mdc`](.cursor/rules/kit-maintainer.mdc), [`.cursor/rules/crav1.mdc`](.cursor/rules/crav1.mdc), [AGENTS.md](AGENTS.md), the README Runnable pieces table, [docs/install.md](docs/install.md), and [plugins/crav1/README.md](plugins/crav1/README.md) name the skill and the answer links.

## 1.39.0 (2026-10-11)

### Kit

- When an updated note comes back for a stale mark, the kit also reads that note's own open questions. That is the Open questions section, and any line the note marks as needing a source or a confirmation. A question whose answer lies outside the note's owner is written on each spec whose Research findings link to the note. The question names who has the fact when the note says so. A decision is marked as a decision. The same meaning already on the spec is not written again. A question the note's owner can still answer stays in the note. This runs whether or not the mark had open points, and also when the mark clears. The end-of-run summary lists every one of those questions. The kit does not ask the user. It does not send anything. It does not commit.

- An older stale mark with no per-point lines is not one point. The kit splits it into the hits it was made from: the contradiction and answered-question lines named in the note's stale block, the spec's stale line, and the run that wrote them when that run is visible. It judges each hit. When those hits cannot be found, it judges the whole update against the original quote, and the summary says the older mark had no points. It does not rewrite that mark as a count of points.

- An open question about a spec line names the real source of the suggested wording. When the wording is in the note's owner's revisit answer, the question says so and includes that answer's date. It uses the owner's name when the note or the answer names them. When the wording is in the note, the question names that section. It does not attribute to the note what is only in the answer. The spec line stays.

- The check still does not ask the user. It still routes an open point the same four ways, and it still numbers a follow-up draft. Nothing is sent. Nothing is committed. The shared wording is [`.cursor/skills/crav1/crav1-add-to-spec/references/research-stale.md`](.cursor/skills/crav1/crav1-add-to-spec/references/research-stale.md). No new skill.

### Docs

- The behavior map in [`.cursor/rules/kit-maintainer.mdc`](.cursor/rules/kit-maintainer.mdc) records the note's own open questions and the split of an older mark. [docs/guild-routing.md](docs/guild-routing.md) notes the same. No new skill.

## 1.38.0 (2026-10-11)

### Kit

- The revisit request no longer says the mark is cleared when an updated note comes back. The question asks the note's owner to say, per point, resolved, partly, or not addressed, and why when it is still open. Examples are a partner who still has to confirm, a fact that is not in public sources, and a decision. The status line says the kit checks the updated note against each listed point when it comes back to `docs/research/`.

- When an updated note is written to `docs/research/` for a note with a stale mark, or the user replaces the file and points `/crav1-add-to-spec` or `/crav1-keep-current` at it, the kit judges each listed point from the update's text. It does not ask the user. Copying the note in does not clear the mark. When every point is resolved, the kit removes the stale block and the spec's stale line, and records `Cleared <date>: updated note <path or commit>.` under Research findings, with one short line per point on how it was resolved. Otherwise the mark stays and is narrowed to `Stale since <date>, N of M points open: <points>.` Resolved points are recorded with the update that resolved them.

- Each open point is routed from the owner's own reason. Research that missed it or got it wrong gets a follow-up revisit draft in the chat, for those points only, numbered `Follow-up N of this mark`. From follow-up 3 the draft says the point has been open a while and suggests a conversation instead of another note. The kit does not decide that. A fact someone else has (a partner, a customer, a document not yet read) becomes an open question on the spec, naming who can answer when the update or the note says so. It is not sent back to the owner. A decision (cost, which option) becomes an open question marked as a decision. When the update does not say why, the kit asks the owner once who can answer it. Each open point names where it waits: `waiting for the note's owner` or `open question on <slug>, waiting for <who>`. A spec line the update says to change becomes an open question with the owner's suggested wording quoted. The kit does not rewrite the spec.

- When that open question is later answered, by `/crav1-resolve-questions` or by a new source through the impact check, the kit re-checks the point and clears it when settled. The mark clears when no point is open. Keep open leaves the point. The run ends with one short summary of what was cleared, narrowed, and routed where. Everything is written in the files. Drafts only. Nothing is sent. Nothing is committed. The shared wording is [`.cursor/skills/crav1/crav1-add-to-spec/references/research-stale.md`](.cursor/skills/crav1/crav1-add-to-spec/references/research-stale.md). No new skill.

### Docs

- The behavior map in [`.cursor/rules/kit-maintainer.mdc`](.cursor/rules/kit-maintainer.mdc) records that the clear does not ask the user, and that `/crav1-resolve-questions` may re-check a stale point. [docs/guild-routing.md](docs/guild-routing.md) notes the same. No new skill.

## 1.37.0 (2026-10-11)

### Kit

- After a quote is kept, the impact check also covers research. `/crav1-meeting-to-specs` does this through the `/crav1-add-to-spec` handoff and does not run the check a second time. `/crav1-add-to-spec`, `/crav1-match-dump-to-specs`, and `/crav1-code-into-specs` compare the quote with notes in `docs/research/` and with `## Research findings` on the specs it touches, including notes those findings link to. Two hits are listed. A clear contradiction of a research line. A quote that answers an open question in the note or the findings. The new quote is shown next to the research line or the question. An unclear case is not marked. It stays an open question on the spec, as today.

- The research is marked only after the user says yes. The note gets a blockquote below the title and the owner line: `> Stale since <date>: <one line on what changed>. Source: docs/sources/YYYY-MM-DD-<slug>/`, or the input's source line when the quote was not imported. The note's own text is not changed. The spec's Research findings get `Stale since <date>: <one line>. See <note path>.` The skills do not commit.

- After the mark, the kit offers to draft a short revisit request in the chat for the note's owner, taken from the note. The draft names the note path and the owner, what changed, what it contradicts, a question asking the owner to revisit and whether the recommendation still holds, and the status. The kit drafts only. It does not send the request or contact anyone. When the note names no owner, it says so and drafts without one.

- When an updated note is written to `docs/research/`, or the user replaces the file and runs `/crav1-add-to-spec` or `/crav1-keep-current` pointed at it, the kit sees the stale block and asks whether the update resolves it. Yes removes the block and the spec's stale line, and records `Cleared <date>: updated note <path or commit>.` under Research findings. No leaves the mark. The skills do not commit.

- `/crav1-explain`, `/crav1-whats-known-about`, and `/crav1-feature-candidates` show a stale note as stale. `/crav1-plan-from-spec` lists stale research findings under Risks and does not block. `/crav1-tighten-spec` may name the mark as an issue. The shared wording is [`.cursor/skills/crav1/crav1-add-to-spec/references/research-stale.md`](.cursor/skills/crav1/crav1-add-to-spec/references/research-stale.md). No new skill.

### Docs

- The behavior map in [`.cursor/rules/kit-maintainer.mdc`](.cursor/rules/kit-maintainer.mdc) records the research check, the mark, the revisit draft, and the clear. [docs/guild-routing.md](docs/guild-routing.md) notes the same. No new skill.

## 1.36.0 (2026-10-11)

### Kit

- `/crav1-meeting-to-specs` and `/crav1-match-dump-to-specs` offer Note next to keep, leave, and dismiss. The choice is `Note — keep it in the repo without tying it to a spec yet.` Note is the recommended answer when the item is worth keeping and is not a decision, a clarification, information, or an answer for an existing spec. Exploration with no feature yet, input that may feed several features, technical debt, and general information gathering are that case. A mail that maps SQL tables and views when no spec covers it is that case. Dismiss stays for a greeting, scheduling, and thanks. There is no question after Note about what kind of note it is. Meeting still asks one item at a time and does not add an accept-all question. Match-dump still confirms the sort once. The recommendation is on that sort. Both read `docs/notes/` first. An item already noted is shown as already noted and is not written again.

- A note lives in the product repo at `docs/notes/YYYY-MM-DD-<slug>.md`, with `docs/notes/index.md`. The file has a title, a date, the quote verbatim (`From <kind> <date>.` when there is a date), a `Source:` line to `docs/sources/YYYY-MM-DD-<slug>/` when the input was imported, and an empty `## Used by`. The index line is title, date, status (`open` or `absorbed`), and used by. The folder and the index are created when missing. The templates are [docs/notes/_template/note.md](docs/notes/_template/note.md) and [docs/notes/_template/index.md](docs/notes/_template/index.md), and the same files in the skill `assets/`. The skills do not commit.

- A note is not owned by one spec. `/crav1-add-to-spec` writes `Used by <slug>` when a spec quotes a note, and updates the index. Status stays open. Many specs can be listed. `Absorbed by <slug>` only when one spec clearly takes the whole note, and only after the user says yes. Then status is absorbed. Partial use never closes the note. `/crav1-spark-to-spec`, `/crav1-ideas-to-spec`, `/crav1-intake-to-specs`, `/crav1-match-to-specs`, and `/crav1-tighten-spec` do the same when they quote a note. `/crav1-feature-candidates` reads open notes as input, labelled as notes. A note is not a candidate by itself. No new skill.

### Docs

- The behavior map in [`.cursor/rules/kit-maintainer.mdc`](.cursor/rules/kit-maintainer.mdc) records the `docs/notes/` write, the Used by line, and the feature-candidates read. [docs/guild-routing.md](docs/guild-routing.md) notes the same. [README.md](README.md) names `docs/notes/` on the Writes cells that gained it. [docs/from-meeting.md](docs/from-meeting.md), [docs/from-match-dump.md](docs/from-match-dump.md), [docs/from-add.md](docs/from-add.md), and [docs/from-feature-candidates.md](docs/from-feature-candidates.md) name the same. No new skill.

## 1.35.0 (2026-10-10)

### Kit

- For a mail, each embedded image, inline or attached, is listed before the source folder is written. The same four options as a separate binary file apply to each image. The recommendation is convert to text when the image is a diagram, a table, or text that can be reproduced exactly, and compress otherwise. An image above about 10 MB still recommends leave it out. After the list, one question: accept all recommendations, go through them one by one with the recommendation shown, or change some by naming items. The transfer data policy `auto-accept` applies to these recommendations only when the rule text clearly covers them. The rule written today applies auto-accept to keep and redact. That line does not cover the four image options, so the question is still asked. Nothing is written to the source folder until every image has an answer. The skills do not commit. The shared reference is [`.cursor/skills/crav1/crav1-add-to-spec/references/sources.md`](.cursor/skills/crav1/crav1-add-to-spec/references/sources.md). No new skill.

- Convert to text removes that image part from the `.eml`, leaves a short placeholder that names the new file, and writes `<name>.md` in the same `docs/sources/YYYY-MM-DD-<slug>/` folder. The file has the image's text word for word, a Mermaid redraw for a diagram, and a markdown table for a table. The README notes the conversion and says the `.eml` is no longer the untouched original. Leave out removes the part, the placeholder says it was left out, and the README notes it. Compress replaces the part with the compressed image, with the same screenshot rules. Commit as-is leaves the part unchanged.

- The personal-data and secrets check also covers what is readable in an embedded image and in the converted text. A secret in an image is removed. Commit as-is is not available for that image.

### Docs

- The behavior map in [`.cursor/rules/kit-maintainer.mdc`](.cursor/rules/kit-maintainer.mdc) records the image ask on `/crav1-add-to-spec`, `/crav1-meeting-to-specs`, `/crav1-intake-to-specs`, `/crav1-match-to-specs`, and `/crav1-match-dump-to-specs`. [docs/guild-routing.md](docs/guild-routing.md) notes the same ask. [docs/from-meeting.md](docs/from-meeting.md) names it on a kept mail. No new skill.

## 1.34.0 (2026-10-10)

### Kit

- Imported sources recommend keep or redact before the files are written. Keep a work email of a person on From, To, or Cc, other than the sender, an office phone, and an office address. Redact a personal mobile, a private street address, and a private email. The sender's own email stays unflagged. An item the kit cannot place, such as a mobile that may be work or private, has no recommendation and is asked one at a time. Secrets are always redacted and are never a choice: connection strings, SAS tokens, API keys, passwords, private keys, and VPN configs. The list shows a secret by kind only, never the value. The same README note names the kind and does not paste the value.

- A note is shown once above the list. It is marked as not legal advice. Keeping a work mail as a project record fits, because a spec quote must trace to the source. Keep only what that trace needs. Where the repo is hosted matters. The client's or the employer's data and retention policy comes first. Removing something after it is pushed means rewriting git history.

- After the list, one question has three answers: accept all recommendations, go through them one by one with the recommendation shown on each, or change some by naming items to flip. Unplaced items are still asked one at a time, whatever is picked. Nothing is written until every flagged item has an answer. A redaction is noted in the README by kind, never by value. No unredacted copy is written. The skills do not commit.

- The first check with no rule asks once which types to check (personal data for now; the file allows more types later), whether to auto-accept the recommendations or review each run, and where the repo is hosted. It then offers to save that as the rule. Yes writes it. No uses the answers this run only. When the rule exists, the check applies it, shows one line naming the file and what it chose, shows the note once, and asks only about unplaced items, plus the accept question when the rule says review. The user changes it by editing or deleting the file. The skill never writes a secrets choice into it. Cursor: `.cursor/rules/crav1-transfer-data-policy.mdc`. Claude Code project: `.claude/rules/crav1-transfer-data-policy.md`. The template is [`.cursor/skills/crav1/crav1-add-to-spec/assets/crav1-transfer-data-policy.mdc`](.cursor/skills/crav1/crav1-add-to-spec/assets/crav1-transfer-data-policy.mdc). `/crav1-add-to-spec`, `/crav1-meeting-to-specs`, `/crav1-intake-to-specs`, `/crav1-match-to-specs`, and `/crav1-match-dump-to-specs` follow it. No new skill.

### Docs

- The behavior map in [`.cursor/rules/kit-maintainer.mdc`](.cursor/rules/kit-maintainer.mdc) records the rule write on those five skills. [docs/guild-routing.md](docs/guild-routing.md) notes the same check. [docs/install.md](docs/install.md) names the file a product repo may get, next to the commit-style rule. No new skill.

## 1.33.0 (2026-10-09)

### Kit

- `/crav1-specs-to-ado`, before the preview, reads the project's Feature fields. When the type has Acceptance Criteria (`Microsoft.VSTS.Common.AcceptanceCriteria`), the spec's checks go there. When it does not, as on Agile and Basic, the checks go in the Description as an Acceptance checks numbered list, that field is not sent, and the preview says so in one line. The same rule applies on Update, so a re-run moves checks that were stored off the form into the Description. A failed field read states the issue, suggests a fix, and offers a skip. It does not guess.

- After a Create, writing the new id into `docs/specs/<slug>/work-item.md` (with the milestone or slice label), or a row on the landscape “No spec yet in ADO” table when the item has no spec, is a required final step. The closing output names the file, says it is not committed yet, and names `/crav1-finalize-commit`. Without that file a later run offers Create again and would make a duplicate. If the write fails, the run says so and prints the line to add.

- `/crav1-ado-to-specs` reads the checks from Acceptance Criteria when the Feature type has that field, and from the Acceptance checks list in the Description when it does not, so a round trip that matches is not reported as a change. Discussion comments use api version `7.1-preview`. Current `az devops invoke` deletes `-preview` and parses the rest as a float, so `7.1-preview.4` fails. `7.1-preview` parses. No new skill.

### Docs

- The behavior map in [`.cursor/rules/kit-maintainer.mdc`](.cursor/rules/kit-maintainer.mdc) and [docs/guild-routing.md](docs/guild-routing.md) record the same three rules. [docs/from-specs-to-ado.md](docs/from-specs-to-ado.md) and [docs/from-ado-to-specs.md](docs/from-ado-to-specs.md) name them too. No new skill.

## 1.32.0 (2026-10-08)

### Kit

- `/crav1-tighten-spec`, when the slice is partial or `## In the code` names paths, reads the committed code on the repo and branch the spec names before wording issues, and treats that code as the current fact. It reads only that repo and branch. A different open checkout stops the run and names the right ones. A stub, for example a `.gitkeep` on `main`, is not the code. If the spec names no branch, it stops and asks which branch has the code. It does not assume `main` or the open checkout. After the user answers, that branch is the read. Writing the branch onto the spec is a yes or no, not a silent edit. A spec that is too thin for that read stops. Too thin means partial, status `done`, or `## In the code` without a repo or without paths, or neither marker on a spec that is not already a full spec with no code behind it. It names `/crav1-code-into-specs` when a change already landed on an existing spec, or `/crav1-match-to-specs` when the slice was never matched. It does not guess and it does not tighten. A disagreement between the tightened wording and the code is called out. The spec is not silently rewritten to match the code. A spec with no code behind it (match status `not in the code`, or a full spec that never claims existing code) skips the read and tightens as before. Finish the gap, add a verify test, and leave it are not choices here. Those belong to `/crav1-plan-from-spec`. No new skill. No version bump.

- `/crav1-plan-from-spec`, before any task is written, when the spec is partial or `## In the code` names paths, reads that same repo and branch and lists each built piece. Each choice says what it means and what it will do. Finish the gap: the code is partly there and v0 wants the rest; the task is that gap only; what already matches is not rebuilt. Add a verify test: the code stays as it is; the task checks what is already there; the feature does not change. Leave it: no task; the plan gets one line saying this piece was left as committed; a later run does not turn it into work unless the user says so. A piece that already matches v0 is not a choice. It is marked already there and gets no rebuild task. A disagreement, such as the spec says one environment and the code enables another, is its own line before any task exists, with the same three choices. The plan check and the plan reviewer treat `already there` and `left as committed` as not a missing task. No new skill. No version bump.

### Docs

- [docs/guild-routing.md](docs/guild-routing.md) and the behavior map in [`.cursor/rules/kit-maintainer.mdc`](.cursor/rules/kit-maintainer.mdc) record one line per skill: what it reads, what it writes, and what it leaves alone, plus one short exception line. [README.md](README.md), [plugins/crav1/README.md](plugins/crav1/README.md), [docs/first-run.md](docs/first-run.md), [docs/from-nothing.md](docs/from-nothing.md), and [docs/from-ideas.md](docs/from-ideas.md) name the same read. [AGENTS.md](AGENTS.md) and [`.cursor/rules/crav1.mdc`](.cursor/rules/crav1.mdc) name it too. The words stay host-generic. No new skill. No version bump.

## 1.31.0 (2026-10-08)

### Kit

- Cross-cutting skills `/crav1-feature-candidates`, `/crav1-specs-to-ado`, and `/crav1-ado-to-specs`. Feature candidates reads the landscape (the spec index, Ideas, Way of working, and code with no slice), `repos.md`, the glossary, every spec’s milestones, slices, open questions, and actions, plus `plan.md`, `tasks.md`, and `verify.md` where they exist, and `docs/research/` and `docs/sources/` with each fact labelled by where it came from. It also reads each `work-item.md` and the landscape “No spec yet in ADO” table. A dated milestone or slice is one candidate. An undated spec with open work is one candidate. A spec that holds only open questions is marked questions only, and the questions sit in the description. An item with no spec is marked no spec yet. A spec that is done or retired with nothing open is skipped. A recorded id is shown. A target date is given only when the docs state it, with its source. Dated rows are ordered by date. Undated rows are left for the user’s team to prioritize. The chat list is a numbered table and a short block per row. The skill writes nothing unless the user asks for a file. Specs to Azure Boards takes the org and project from `docs/environments/marks.md` or from the Azure DevOps URLs in `docs/system/repos.md`, checks `az` including the default install paths, and checks that the project has the Feature work item type. On a failure it states the issue, suggests a fix such as `az login`, and offers a skip. It runs feature candidates, the user picks by number or all, and it previews the Feature form: title, State New, Area default, Value area Business, Iteration and Priority blank, Target Date only when the spec states it, tags for the slice name and the code repos it touches, a description that stands alone, and acceptance criteria only from the spec’s checks. Nothing sent mentions the specs repo. `AB#` mentions already in code repos stay as they are. A preview is not edited in place. A change goes into the spec through `/crav1-add-to-spec`, then the preview is rebuilt. Create or update runs only after the user says yes, one at a time or all reviewed together. The new id is written to that spec’s `work-item.md` with its milestone or slice label, or to a “No spec yet in ADO” row (id, title, date) when the item has no spec. When a spec is made later, the id moves into that spec’s `work-item.md`. Azure Boards to specs reads the recorded ids, or only the ids the user names: State, Priority, Target Date, Iteration, Assigned To, comments, and history. It shows only what differs or is new. A missing id is missing, with no guessed match. The user keeps or dismisses each change. Dismissals start fresh each run. A kept change goes through `/crav1-add-to-spec`, labelled as coming from Azure Boards with the date and who changed it. An answer the user gives during the run goes into the spec first, labelled with the date as the user’s answer to the Azure Boards question. A no-spec-yet Feature suggests making the spec first. A reply comment is drafted from the spec only when the spec answers the question, shown as `Post comment on Feature <id>: <text>`, and posted only on yes. `work-item.md` holds several ids, one line each with a milestone or slice label. The old single-line format is still read. The commit mention picks the id for the slice being worked and asks if that is unclear. The offer that records an id the user already has points at `/crav1-specs-to-ado` for creating a Feature. Guild routing lists the three skills under Cross-cutting. No new lane. Walkthroughs: [docs/from-feature-candidates.md](docs/from-feature-candidates.md), [docs/from-specs-to-ado.md](docs/from-specs-to-ado.md), and [docs/from-ado-to-specs.md](docs/from-ado-to-specs.md). No version bump.

### Docs

- [docs/from-feature-candidates.md](docs/from-feature-candidates.md), [docs/from-specs-to-ado.md](docs/from-specs-to-ado.md), and [docs/from-ado-to-specs.md](docs/from-ado-to-specs.md) walk the three Azure Boards skills for Cursor and Claude Code. The slash commands are the same. [docs/guild-routing.md](docs/guild-routing.md) lists them under Cross-cutting. They may run from any lane. They do not move work into Specify, Plan, or Build. They are later skills. They are not starter options. [README.md](README.md), [docs/install.md](docs/install.md), [docs/first-run.md](docs/first-run.md), and [plugins/crav1/README.md](plugins/crav1/README.md) name the commands. The behavior map gains one line each. [docs/system/_template/landscape.md](docs/system/_template/landscape.md) gains `## No spec yet in ADO`. [docs/specs/_template/work-item.md](docs/specs/_template/work-item.md) holds one id per line. [docs/from-ideas.md](docs/from-ideas.md) points Feature creation at `/crav1-specs-to-ado`. No new lane. No version bump.

## 1.30.0 (2026-10-07)

### Kit

- Imported sources. A mail, a transcript, minutes, a chat, a screenshot, a diagram, or another original file that a skill quotes into a spec is stored in the target project at `docs/sources/YYYY-MM-DD-<slug>/`, with the original files and a `README.md`. The README says what it is, the sender or the participants, the date and the time, and how it was converted. Spec `Source:` and `Trace:` lines link to that folder, so every verbatim quote traces to its original. A mail is a `.eml` text file with its CRLF line endings kept. If the project's `.gitattributes` lacks `*.eml -text`, the skill asks once, yes or no, before adding that line. For every binary file the skill asks which of four options to use and recommends one from the file type: commit as-is; compress, then commit (for a screenshot: crop off taskbars and app bars, no sharpening, WebP, and show samples at q70, q85, and lossless so the user picks the quality); convert to text and commit that instead, keeping the original outside the repo (for a document: `transcript.md`, word for word, with speakers and timestamps, checked word for word against the original); or leave it out and only reference where the original lives (the recommendation above about 10 MB). Git LFS (Large File Storage) is a note only, never an option, because it needs repo setup the kit does not do. The README records which option was used. Before the files are written, phone numbers, street addresses, personal emails beyond the sender, and similar details, for example in a mail signature, are flagged. The user keeps or redacts each item. A redaction is noted in the README, because the file is then no longer the untouched original. The skills write the files and do not commit. The shared reference is [`.cursor/skills/crav1/crav1-add-to-spec/references/sources.md`](.cursor/skills/crav1/crav1-add-to-spec/references/sources.md). `/crav1-meeting-to-specs` and `/crav1-add-to-spec` follow it. `/crav1-match-dump-to-specs`, `/crav1-intake-to-specs`, and `/crav1-match-to-specs` follow it when they quote those files. A short fact typed for one spec, an environment-read fact, a test suggestion, and a quote of repository code are not imported sources. No new skill. No version bump.

### Docs

- [docs/from-meeting.md](docs/from-meeting.md), [docs/from-add.md](docs/from-add.md), [docs/from-match-dump.md](docs/from-match-dump.md), [docs/from-intake.md](docs/from-intake.md), and [docs/from-match.md](docs/from-match.md) name the imported-sources folder `docs/sources/YYYY-MM-DD-<slug>/`. The behavior map records the same write on `/crav1-meeting-to-specs`, `/crav1-add-to-spec`, `/crav1-match-dump-to-specs`, `/crav1-intake-to-specs`, and `/crav1-match-to-specs`. [docs/guild-routing.md](docs/guild-routing.md), [README.md](README.md), [docs/install.md](docs/install.md), and [plugins/crav1/README.md](plugins/crav1/README.md) name the same folder. The skills write the files and do not commit. No new skill. No version bump.

## 1.29.0 (2026-10-07)

### Kit

- `docs/system/repos.md` has a per-repo `Synced at` column, `<branch>@<short sha>, <date>`. A repo may list several branches, separated by `; `. Example: `main@abc1234, 2026-10-07; develop@def5678, 2026-10-06`. When `/crav1-keep-current`, `/crav1-repos-to-spec`, `/crav1-code-into-specs`, or `/crav1-intake-to-specs` and `/crav1-ideas-to-spec` (where they read repos) read a whole repo, they set that repo's column to the branch and commit they actually read. They touch only the repos they read. When a run reads only one slice, it does not touch the repo column. It writes or updates `Synced at: <repo> <branch>@<short sha>, <date>` in that slice's `spec.md`. A consumer measuring drift uses the older of the repo column and the slice line, and an empty value means unknown, so fall back to spec file commit dates. Skills that write `repos.md` include the column. `/crav1-spark-to-spec` leaves the cell empty and writes the slice line when it read that slice's code. `/crav1-match-to-specs` leaves the cell empty. `/crav1-add-to-spec` and `/crav1-match-dump-to-specs` keep an existing cell and do not set it. No new folder. No version bump.

### Docs

- [docs/system/_template/repos.md](docs/system/_template/repos.md) adds the `Synced at` column and the drift sentence. [docs/from-ideas.md](docs/from-ideas.md), [docs/from-intake.md](docs/from-intake.md), [docs/from-nothing.md](docs/from-nothing.md), [docs/from-code.md](docs/from-code.md), [docs/from-repos.md](docs/from-repos.md), and [docs/from-keep-current.md](docs/from-keep-current.md) name the same stamp. The behavior map records it on the skills that write it. No new folder. No version bump.

## 1.28.0 (2026-10-07)

### Kit

- `/crav1-review-pr` treats a pull request with no `plan.md` or `tasks.md` for its slug as built outside the kit. That is an info note, not a fix finding. It does not report a missing `verify.md`. It still checks spec fit, the pull request body against the diff, the required green linter, and secrets. Instead of `verify.md`, it reads the test results that pull request's own pipeline already recorded and reports, as an info note, which tests ran, whether they passed, and which changed files no test touches. It does not run tests and it does not ask to. When the pipeline shows no test run, the note names the tests the pull request includes and tells the user they can run them manually and then rerun the review. A rerun only sees results the pipeline recorded, so a local run shows up only if the user pastes its output. The note states that these are the pull request's own tests, not a check against the spec. An outside pull request ends with one line naming `/crav1-keep-current` as the next step after the pull request merges, to bring its changes into the spec and `docs/system/`. The skill does not run it. A pull request that has a plan keeps the full plan and `verify.md` checks. Walkthrough: [docs/from-review-pr.md](docs/from-review-pr.md). No new folder. No version bump.

## 1.27.0 (2026-10-07)

### Kit

- `/crav1-whats-known-about` derives the Azure DevOps org and project from Azure DevOps URLs in `docs/system/repos.md` when the git remote is not Azure Repos and `docs/environments/marks.md` does not name them. It then reads work items, open pull requests, and branches read-only, the same way as the existing live-read path. Every fact is tagged as a live read. Before it reports the Azure CLI `az` as not installed, it checks the default install paths on Windows (`C:\Program Files\Microsoft SDKs\Azure\CLI2\wbin\az.cmd` and `C:\Program Files (x86)\Microsoft SDKs\Azure\CLI2\wbin\az.cmd`), macOS (`/opt/homebrew/bin/az` and `/usr/local/bin/az`), and Linux (`/usr/bin/az` and `/usr/local/bin/az`). When one of those paths is there, it uses that path. No new folder. No version bump.

## 1.26.0 (2026-10-07)

### Kit

- `/crav1-explain` stays read-only. On every run it compares the feature index with the system picture: the slice's node in `docs/system/diagrams.md` and its line under `## How the parts connect`. Names match only by slug, spec title, or main resource name. At the end of the answer it lists each slice that is missing entirely or partly, one line per slice, including done and retired, and shows that status. It names `/crav1-keep-current` and does not run it. When the picture has nothing on the question, it quotes the first paragraph of the matching slice's spec, labelled as coming from the spec, and names `/crav1-whats-known-about`. When no spec matches either, it says so and names that skill. It does not run it. No new folder. No version bump.

- Some commands ask once at the end of a run, yes or no: "The system picture may now be out of date. Run `/crav1-keep-current`?" They do not run `/crav1-keep-current`. `/crav1-complete-features` asks when a slice is marked done or retired. `/crav1-fix-bug` and `/crav1-fix-live` ask when the fix changes how the parts connect. `/crav1-environment-read` asks after `docs/environments/marks.md` lines are added. `/crav1-add-to-spec` asks once at the end of a handoff from environment-read or suggest-tests-for-code, not once per item. `/crav1-implement-task` and `/crav1-complete-task` do not ask. Spark, ideas, intake, match, match-dump, code-into-specs, and repos-to-spec still update the picture in their own pass. No new folder. No version bump.

### Docs

- [docs/from-explain.md](docs/from-explain.md) names the feature-index check and the spec-paragraph fallback on `/crav1-explain`. [docs/from-keep-current.md](docs/from-keep-current.md) names who asks before `/crav1-keep-current` and who still updates the picture in their own pass. [docs/from-fix-bug.md](docs/from-fix-bug.md), [docs/from-environment.md](docs/from-environment.md), and [docs/from-add.md](docs/from-add.md) name the same yes or no question. The behavior map records one line per skill. [docs/guild-routing.md](docs/guild-routing.md), [README.md](README.md), [docs/install.md](docs/install.md), [AGENTS.md](AGENTS.md), and [plugins/crav1/README.md](plugins/crav1/README.md) name the same checks. No new folder. No version bump.

## 1.25.0 (2026-10-06)

### Kit

- `/crav1-meeting-to-specs` shows a build-state line on each item that matches an existing spec. The line is `State: <state>.` plus a short reason that names the evidence. It is in the item block and in the keep, leave, or dismiss question. The states are built, partly built, planned, and not built. `Fits: none` has no state line. Evidence is the matched slice’s `spec.md` (including `## Match`), `plan.md`, `tasks.md` checkboxes, and `verify.md` when present. When those do not settle it, one read-only look at the code that spec or plan points to. No codebase-wide search. A code-based or uncertain state is labeled `(inference, not in the docs)`. The line does not change the options. It is not written. It is not passed to `/crav1-add-to-spec` as quote text. That handoff does not write a `State:` line. The skill still writes nothing itself. No new folder. No version bump.

### Docs

- [docs/from-meeting.md](docs/from-meeting.md) names the build-state line on `/crav1-meeting-to-specs`. The behavior map line now includes that slice’s `plan.md`, `tasks.md`, `verify.md`, and a read-only look at the code that spec or plan points to when those files do not settle the state. [docs/guild-routing.md](docs/guild-routing.md), [README.md](README.md), [docs/install.md](docs/install.md), [docs/from-add.md](docs/from-add.md), and [plugins/crav1/README.md](plugins/crav1/README.md) name the same line. No new folder. No version bump.

## 1.24.0 (2026-10-06)

### Kit

- `/crav1-meeting-to-specs` takes minutes, a transcript, a Teams or Zoom export, an email, or a pasted Slack or Teams chat thread. The kind is `meeting`, `email`, or `chat`, from what the input shows. It does not guess. If the kind is not clear, it asks once per run, options only: meeting, email, or chat. The date comes from the input. It does not invent one. When the input shows no date, it asks once per run, options only: give a date, or skip. A date the user gives is used. Skip means no date. One kind and one date apply to every item. The `Source` line is `<kind> <date>`, or `<kind>`. A kept addition handed to `/crav1-add-to-spec` starts the quote with `From <kind> <date>.` when there is a date, otherwise `From <kind>.` Speaker and time stay when the input shows them. The skill still writes nothing itself. Dismissals still start fresh each run. No new skill. No new folder. No version bump.

### Docs

- [docs/from-meeting.md](docs/from-meeting.md) says an email or a chat thread is accepted, and the quote label follows the kind and the date. The behavior map line for `/crav1-meeting-to-specs` names that input. [docs/guild-routing.md](docs/guild-routing.md), [README.md](README.md), [docs/install.md](docs/install.md), [docs/first-run.md](docs/first-run.md), and [plugins/crav1/README.md](plugins/crav1/README.md) name the same input. No new folder. No version bump.

## 1.23.0 (2026-10-06)

### Kit

- Cross-cutting skill `/crav1-whats-known-about`. The user asks about one feature, slice, resource, or not-yet-feature. The answer comes from the specs first. It reads only. It writes nothing. An exact name match runs first, across spec titles, `tasks.md`, Match quotes, `docs/system/`, `docs/architecture/spec.md`, and `docs/environments/marks.md`. A sentence uses the key words, with spec titles and Match quotes weighted highest. One pass. It does not hunt the whole codebase. An `@` keeps the search inside that path. One slice that wins is the answer, and the path is named. Two or more close hits are listed, one line each, and it asks which. It does not guess. No slice: it says so, shows what the repo, the code, and the environment notes know, and presents a candidate slice. A code-only hit, with no spec and no architecture note, shows what the code says and fills in Unexplained. It names `/crav1-spark-to-spec`, `/crav1-ideas-to-spec`, or `/crav1-intake-to-specs` and does not run them. Pasted minutes or a long dump names `/crav1-meeting-to-specs` or `/crav1-match-dump-to-specs` and stops. After the repo part it runs read-only live checks: Azure resource settings and recent changes with `az`, and Azure DevOps work items, open pull requests, and branches that touch the thing. Each live fact is tagged as a live read. Production follows the `/crav1-environment-read` rule: shape and connections only, after the same yes or no. It never reads data. A failed live read shows one prompt with the issue, a fix when there is one, and Retry or Skip. Skip is the repo-only answer, with a line that the live checks did not run and why. A focus still runs the full read and shows only those sections. The chat answer follows `assets/answer.md`. Empty sections are left out. A guess is labeled `(inference, not in the docs)`. It may name one skill. It does not run another skill. It does not start Specify, Plan, or Build. It may run from any lane. It is a later skill. It is not a starter option. When the user asks for startup options, name only the seven. That ask names the list and does not run this command. The seven starter options stay unchanged. It is not `/crav1-explain`. Explain reads `docs/system/` and does not open a spec to answer the question. Guild routing lists it under Cross-cutting. No new lane. Walkthrough: [docs/from-whats-known-about.md](docs/from-whats-known-about.md). No version bump.

### Docs

- [docs/from-whats-known-about.md](docs/from-whats-known-about.md) walks `/crav1-whats-known-about` for Cursor and Claude Code. The slash command is the same. [docs/guild-routing.md](docs/guild-routing.md) lists the skill under Cross-cutting. It may run from any lane. It does not move work into Specify, Plan, or Build. It is a later skill. It is not one of the seven starter options. [docs/from-explain.md](docs/from-explain.md) points at it. [README.md](README.md), [docs/install.md](docs/install.md), [docs/first-run.md](docs/first-run.md), and [plugins/crav1/README.md](plugins/crav1/README.md) name the command. The behavior map gains one line. No new lane. No version bump.

## 1.22.0 (2026-10-05)

### Kit

- `/crav1-environment-read` can read a prod-only resource for shape and connections only, after one yes. Prod-only means the mark is production (name, group, tag, or `docs/environments/marks.md`) and no source on that same resource says non-prod or pre-prod. A different resource with a similar name is not a twin. The question is the same yes or no as pre-prod and shared-with-prod. A no lists them as not read, and a declined prod-only resource stays in Skipped. A yes reads names, types, setting keys, routes the settings already show, timers, links, and secret names. Never data. Never secret values. Never a row or a blob. Each Seen, System, Architecture, Match, and Links line says `Seen in <host> prod.` and `prod only`. Look-inside still never opens a production database or store. Naming production, prod, or live as the host still stops the read. No new skill. No new lane. No version bump.

## 1.21.0 (2026-10-05)

### Kit

- Cross-cutting skill `/crav1-meeting-to-specs`. Everything after the command, and every `@`, is the minutes or transcript (a file, a paste, or a Teams or Zoom export). If there is no pointer, it stops and asks. Options only. It does not guess. It extracts requirements, decisions, changes, open questions, and bugs. Each item is a quote. Speaker and time are included when the transcript shows them. Small talk and status chatter are dropped. It matches each item against existing `docs/specs/<slug>/` folders and skips `_template`. The cases are an addition to a named existing spec, a possible new feature, a bug, or unclear. When more than one existing spec could fit, every candidate stays listed. Nothing is dropped to keep the list short. The user takes items one at a time: keep, leave, or dismiss. Dismiss is for this run only. The next run starts fresh. It does not write a dismissals file and does not remember a dismiss across runs. A kept addition is handed to `/crav1-add-to-spec` for that slug, with a source label from the meeting and the date when it is known. The impact check still runs there. A kept new feature names `/crav1-spark-to-spec`, `/crav1-ideas-to-spec`, or `/crav1-intake-to-specs` and does not run it. A kept bug names `/crav1-fix-bug` and does not run it. An unclear keep asks which existing slug, or treats the item as a new feature. The skill writes nothing itself. It does not copy the transcript into the repo. It does not create a slug. It does not start Specify, Plan, or Build. It may run from any lane. It is a later skill. It is not a starter option. When the user asks for startup options, name only the seven. That ask names the list and does not run this command. The seven starter options stay unchanged. Guild routing lists it under Cross-cutting. No new lane. Walkthrough: [docs/from-meeting.md](docs/from-meeting.md). No version bump.

### Docs

- [docs/from-meeting.md](docs/from-meeting.md) walks `/crav1-meeting-to-specs` for Cursor and Claude Code. The slash command is the same. [docs/guild-routing.md](docs/guild-routing.md) lists the skill under Cross-cutting. It may run from any lane. It does not move work into Specify, Plan, or Build. It is a later skill. It is not one of the seven starter options. [README.md](README.md), [docs/install.md](docs/install.md), [docs/first-run.md](docs/first-run.md), and [plugins/crav1/README.md](plugins/crav1/README.md) name the command. The behavior map gains one line. `/crav1-add-to-spec` gains a handoff section, and its caller list includes this skill. No new lane. No version bump.

## 1.20.0 (2026-10-05)

### Kit

- `/crav1-environment-read` can look inside a database or storage after the first read, and before any section. It asks first. A no leaves them unopened. SQL reads metadata only: schemas, table and view names, columns and types, keys and relationships, stored procedure and function names, and SQL Agent jobs or other scheduled jobs and triggers when they can be reached. The line for a job or a trigger is source, target, and schedule. Storage reads structure only: accounts or buckets, containers, file shares, queues, table names, prefixes to depth 2, public or private access, lifecycle, versioning, soft delete, and what points at it, including storage triggers. It lists prefixes, not files. It never reads a row or a blob, and it never reports a file count or a size. It never prints a connection string, a key, or a secret. Production is never opened. Pre-prod and shared-with-prod follow the existing yes and stay shape and connections only. When the databases have no clear environment, it says there are no clear database environments, then asks whether the environments are in the same database, then whether to read the schema. Before that second question, and before the storage question, it says how to reach it and how much setup is needed. `sqlcmd` is optional. The skill does not install a tool, and it does not create a login, a firewall rule, a role, a SAS token, or a key. Missing access stops that look-inside and names the gap. A schema, a name, or a prefix is evidence only when the whole-word token rule matches. Facts join the sections that already exist and say they were seen in that environment. Readers: [references/sql.md](.cursor/skills/crav1/crav1-environment-read/references/sql.md) and [references/storage.md](.cursor/skills/crav1/crav1-environment-read/references/storage.md). No new skill. No new lane. No new output section. No version bump.

### Docs

- [docs/from-environment.md](docs/from-environment.md) walks the SQL and storage look-inside on `/crav1-environment-read`. [docs/install.md](docs/install.md) lists `sqlcmd` as optional. The skill does not install it. [docs/guild-routing.md](docs/guild-routing.md) stays cross-cutting. The behavior map stays one line plus one exception. [README.md](README.md) and [plugins/crav1/README.md](plugins/crav1/README.md) name the look-inside. No new skill. No new lane. No version bump.

## 1.19.0 (2026-10-05)

### Kit

- Cross-cutting skill `/crav1-pipeline-environments`. The user names Azure DevOps, the org, and the project. A pipeline name is optional. If any of those three is missing, it stops and asks. Options only. It does not guess. It reads pipeline definitions with `az pipelines` and `az devops` (list and show only, with the `azure-devops` extension). It does not run, queue, edit, approve, or trigger a pipeline. It does not read builds, logs, test runs, boards, or repo files beyond the pipeline definition. Secrets are not printed. The stage name gives the environment, with the same whole-word rule as `/crav1-environment-read`. A deploy step marks the resource it names. The resource group is context on that line and the rest of the group is not marked. One environment proposes a `pipeline <name>, stage <stage>` line. A resource deployed by both a non-prod stage and a production stage is one line per stage, because the marks format has no `shared` word. An unclear stage or an unresolved variable proposes no mark. Confirmed lines are appended to `docs/environments/marks.md`. The file is created only then. An existing line is never rewritten. It does not write `docs/system`, `docs/architecture/spec.md`, a feature spec, or `docs/architecture/left-out.md`. If `az` is missing, the extension is missing, or there is no login, the stop names which. It does not install or log in. It names `/crav1-environment-read` and does not run it. It is a later skill. It is not a starter option. The seven starter options stay unchanged. Guild routing lists it under Cross-cutting. No new lane. Walkthrough: [docs/from-pipeline-environments.md](docs/from-pipeline-environments.md). No version bump.

### Docs

- [docs/from-pipeline-environments.md](docs/from-pipeline-environments.md) walks `/crav1-pipeline-environments` for Cursor and Claude Code. The slash command is the same. [docs/guild-routing.md](docs/guild-routing.md) lists the skill under Cross-cutting. It is a later skill. It is not one of the seven starter options. [docs/environments-marks.md](docs/environments-marks.md) points at the skill. The marks format stays four fields. There is no `shared` word. [README.md](README.md), [docs/install.md](docs/install.md), [docs/first-run.md](docs/first-run.md), and [plugins/crav1/README.md](plugins/crav1/README.md) name the command. The behavior map gains one line. No new lane. No version bump.

## 1.18.0 (2026-10-05)

### Kit

- `/crav1-environment-read` reads every non-prod environment on the host the user named, in one pass. The user no longer picks dev or test. Naming production, prod, or live still stops the read. Seen lines keep their own environment (`Seen in Azure dev.`, `Seen in Azure test.`, and the same for stage, uat, qa, and pre-prod). Non-prod tokens are dev, development, test, testing, stage, staging, uat, and qa. Pre-prod is `preprod`, or the neighboring whole words `pre` then `prod` from `pre-prod` and `pre_prod`. `live` is production when it is a whole word. Pre-prod, and a resource marked both non-prod and production by different sources, are shape and connections only after one yes, and the mixed resource is labelled `shared with prod`. A resource whose only mark is production stays skipped. A fourth mark source is `docs/environments/marks.md` (format: [docs/environments-marks.md](docs/environments-marks.md)). The read appends only lines the user confirmed and never rewrites an existing line. Unmarked resources can be marked from shown evidence, strongest first, then from a group suggestion, then by the user per resource or per group. Triggers are connections and show the definition only. A missing CLI or login is named, with the install page and the login command. The skill does not install or log in, and it does not look inside databases or storage. `/crav1-pipeline-environments` appends the pipeline lines. This read does not run it. Guild routing stays cross-cutting. No new lane. No version bump.

### Docs

- [docs/from-environment.md](docs/from-environment.md) walks the host pass for `/crav1-environment-read`. [docs/environments-marks.md](docs/environments-marks.md) defines the `docs/environments/marks.md` line. [docs/guild-routing.md](docs/guild-routing.md) stays cross-cutting and says the user names the host. The behavior map says the skill appends confirmed marks and leaves the other files to their owners. [README.md](README.md), [docs/install.md](docs/install.md), [docs/first-run.md](docs/first-run.md), and [plugins/crav1/README.md](plugins/crav1/README.md) name the host pass. No new lane. No version bump.

## 1.17.0 (2026-10-05)

### Kit

- Cross-cutting skill `/crav1-suggest-tests-for-code`. The user points at code that already exists, one repo or one area, not the whole system. It reads that code and suggests tests for what that code can actually break. A function gets a few checks. A page gets a browser check. A boundary gets an integration check. It does not dump every test type. Every suggestion stays listed. Nothing is dropped to keep the list short. The user takes them one at a time: keep, leave, or dismiss. Dismiss means it is not offered again. A kept suggestion goes onto the existing spec through `/crav1-add-to-spec`. Plan turns it into a task. It does not write the tests, change the code, or start Specify, Plan, or Build. It does not move work into a lane. It may run from any lane. It is a later skill. It is not a starter option. When the user asks for startup options, name only the seven. That ask names the list and does not run this command. The seven starter options stay unchanged. Guild routing lists it under Cross-cutting. No new lane. No new folder beyond the skill’s own files. Walkthrough: [docs/from-suggest-tests.md](docs/from-suggest-tests.md). No version bump.

### Docs

- [docs/from-suggest-tests.md](docs/from-suggest-tests.md) walks `/crav1-suggest-tests-for-code` for Cursor and Claude Code. The slash command is the same. [docs/guild-routing.md](docs/guild-routing.md) lists the skill under Cross-cutting. It may run from any lane. It does not move work into Specify, Plan, or Build. It is a later skill. It is not one of the seven starter options. [README.md](README.md), [docs/install.md](docs/install.md), [docs/first-run.md](docs/first-run.md), and [plugins/crav1/README.md](plugins/crav1/README.md) name the command. The behavior map gains one line. No new lane. No version bump.

## 1.16.0 (2026-10-04)

### Kit

- Cross-cutting skill `/crav1-exploratory-test`. It runs after a build of a slice already exists. Pass one learns the slice by using it once. Pass two is no longer careful. It adds randomness: sometimes a double-click, a hover back and forth, repeating an action, or using the same control more than once. It follows what the last action showed. It lasts about as long as the first pass, long enough to provoke bugs, then it stops. That stop is named `matched the first pass`. It stops sooner when the user says stop. That stop is named `the user said stop`. It does not run forever. The user does not set a clock. It writes bugs to `docs/specs/<slug>/explore.md`. It does not write the checks the plan already named. It does not start Specify, Plan, or Build. It does not move work into a lane. A bug it finds is not sent to `/crav1-fix-bug` unless the user says so in that turn. It may run from any lane. It is a later skill. It is not a starter option. When the user asks for startup options, name only the seven. That ask names the list and does not run this command. Guild routing lists it under Cross-cutting. No new lane. Walkthrough: [docs/from-exploratory-test.md](docs/from-exploratory-test.md). No version bump.

### Docs

- [docs/from-exploratory-test.md](docs/from-exploratory-test.md) walks `/crav1-exploratory-test` for Cursor and Claude Code. The slash command is the same. [docs/guild-routing.md](docs/guild-routing.md) lists the skill under Cross-cutting. It may run from any lane, after a build of a slice already exists, and it does not move work into Specify, Plan, or Build. It is a later skill. It is not one of the seven starter options. [README.md](README.md), [docs/install.md](docs/install.md), [docs/first-run.md](docs/first-run.md), and [plugins/crav1/README.md](plugins/crav1/README.md) name the command. The behavior map gains one line. No new lane. No version bump.

## 1.15.0 (2026-10-04)

### Kit

- When the user asks for startup options, the kit names only these seven: `/crav1-spark-to-spec`, `/crav1-ideas-to-spec`, `/crav1-intake-to-specs`, `/crav1-match-to-specs`, `/crav1-repos-to-spec`, `/crav1-environment-read`, and `/crav1-fix-bug`. Every other skill is a later skill. That ask names the list. It does not run a skill and does not move work into a lane. Each starter still follows the rules it already has. `/crav1-repos-to-spec` still runs only when the user names repos. `/crav1-environment-read` still runs only when the user names the host and a dev or test environment. `/crav1-fix-bug` still runs only when the user names a real bug. The list is in [docs/guild-routing.md](docs/guild-routing.md), [docs/first-run.md](docs/first-run.md), [docs/install.md](docs/install.md), [README.md](README.md), and [plugins/crav1/README.md](plugins/crav1/README.md). No new skill. No new lane. No new folder. No version bump.

## 1.14.0 (2026-10-04)

### Kit

- `/crav1-environment-read` now has an AWS reader and a Google Cloud reader, beside the Azure reader. The user names the host and the environment. The environment is dev or test. Never production. The user names the environment, not the subscription, the account, or the project. Each reader lists only what that named environment actually has. A resource marked production is skipped and listed as skipped. A resource with no environment mark stops and is not read. Any other host still stops and says it has no reader. Azure DevOps, GitHub, and CI stay out. The skill still only reads. After a confirmed section, the owning skill adds only what is new. A fact is marked seen in that environment. Existing lines are not rewritten. Guild routing stays cross-cutting. No new skill. No new lane. No new folder. No version bump.

## 1.13.0 (2026-10-04)

### Kit

- Cross-cutting skill `/crav1-environment-read`. The user names the host and the environment at the start. Examples: Azure dev, Google Cloud test, AWS dev. It does not guess the host. It never reads production. Each host has its own reader. The reader lists only what that named environment actually has. A host with no reader stops and says so. It does not pretend to read it. It does not read Azure DevOps, GitHub, or CI. The user names the environment, not the subscription, the account, or the project. The reader takes only a resource whose name, group, or tag says dev or test. Anything marked production is skipped and listed as skipped. A resource with no environment mark stops and asks. It is not read. The skill only reads. It does not write `docs/system`, `docs/architecture/spec.md`, a feature spec, or `docs/architecture/left-out.md`. A fact is marked seen in that environment, not as something the code shows. It does not become a link unless the environment shows the connection. Confirmation is one section at a time, with its own question and answer, and nothing is dropped to keep a section short. After the user confirms a section, the skill that already owns the file adds only what is new. System facts go to `docs/system`. Architecture facts go to `docs/architecture/spec.md`. A slice Match already owns goes on that feature spec. A left-out line the environment now shows comes off `docs/architecture/left-out.md`. Lines that are already there are not rewritten. It does not start Specify, Plan, or Build. Guild routing lists it under Cross-cutting. No new lane. Walkthrough: [docs/from-environment.md](docs/from-environment.md). No version bump.

## 1.12.0 (2026-10-04)

### Kit

- `/crav1-repos-to-spec` confirms the read in sections before any file is written. One section per named repo for confirmed facts, one section for inferred guesses, one section for links, and one section for left-out. Each section has its own question and its own answer. Every item stays listed. A guess stays out until that section’s answer accepts it, and then it is accepted from a guess, not a code fact. A guess that stays left out is written to `docs/architecture/left-out.md`, beside `docs/architecture/spec.md`. Each line says the guess and that the code does not show it. It is not a confirmed fact and it is not a link. A later re-read reads that file and checks the code for every line. When the code shows the fact or a real link, the line comes off that file and is written as a fact or a link. The left-out answer can accept a line, keep it left out, or dismiss it. Dismiss means it is not offered again. A link is written only when the code shows it. If none is found, that section says so and does not offer a guessed link. Confirming a guess does not turn it into a link. Guild routing stays cross-cutting. No new skill. No new lane. No new folder. No version bump.

## 1.11.0 (2026-10-04)

### Kit

- `/crav1-repos-to-spec` no longer stops when a real note is already in `docs/system/`. When `docs/architecture/spec.md` is missing, it writes that file and leaves existing system notes as they are. When the architecture spec or those notes are already there, a later re-read adds only what is new and does not rewrite lines that are already there. A fact the code shows is confirmed. A guess stays out until the user confirms it. A link is written only when the code shows it. It does not design the next feature, write application code, or start Specify, Plan, or Build. Guild routing stays cross-cutting. No new skill. No new lane. No version bump.

## 1.10.0 (2026-10-04)

### Kit

- `/crav1-repos-to-spec` writes the architecture spec at `docs/architecture/spec.md`. The folder is `docs/architecture/`. The file is `spec.md`. Later architecture files can sit beside it. It stays out of `docs/system` and out of `docs/specs`. `docs/specs` stays one folder per feature slug. `docs/system` stays the short picture. This file stays the one the lanes can extend. Confirmed versus inferred, links, and the stop before Specify, Plan, and Build are unchanged. Guild routing stays cross-cutting. No new lane. No version bump.

### Docs

- [docs/from-repos.md](docs/from-repos.md) says the architecture spec from `/crav1-repos-to-spec` is `docs/architecture/spec.md`. The behavior map line for that skill names the same path. Guild routing stays cross-cutting. No new lane. No version bump.

## 1.9.0 (2026-10-04)

### Kit

- Cross-cutting skill `/crav1-repos-to-spec`. The user names one or more repos. It reads those repos and writes one architecture spec the lanes can extend (`docs/architecture/spec.md`) and the `docs/system/` notes `/crav1-explain` reads. A fact the code shows is confirmed. A guess stays out of the spec until the user confirms it. A link between repos is written only when the code shows it. If none is found, it says so. It does not invent links. It does not design the next feature, write application code, or start Specify, Plan, or Build. A later re-read that only adds what is new is not this command. It is not `/crav1-code-into-specs`. Guild routing adds it under Cross-cutting. No new lane. Walkthrough: [docs/from-repos.md](docs/from-repos.md). No version bump.

### Docs

- [docs/from-repos.md](docs/from-repos.md) walks `/crav1-repos-to-spec` for Cursor and Claude Code. The slash command is the same. [docs/guild-routing.md](docs/guild-routing.md) lists the skill under Cross-cutting. No new lane. [README.md](README.md), [docs/install.md](docs/install.md), [docs/first-run.md](docs/first-run.md), and [plugins/crav1/README.md](plugins/crav1/README.md) name the command. The behavior map gains one line. No version bump.

## 1.8.0 (2026-10-04)

### Kit

- Cross-cutting skills `/crav1-explain` and `/crav1-keep-current`. Explain reads the system notes spark, ideas, intake, or match already wrote (`docs/system/`). The first answer is a short TLDR. Longer goes one level deeper from the same notes. The user can point it at one part. A question about whether the system can do something is yes with a pointer, no, or that it is not written down. It does not guess, write a second document, teach, or start Specify, Plan, or Build. When the picture is older than the specs, it says so and names keep-current. It does not run it. Keep-current adds what is new to the short description, the diagram, and how the parts connect. It does not rewrite what is already there. It does not design the change and does not build it. It can run on its own. Spark, ideas, intake, match, match-dump, and code-into-specs run that same picture update in the pass that already appends a glossary row. Existing glossary rows are not rewritten. Guild routing adds both skills under Cross-cutting. No new lane. Walkthroughs: [docs/from-explain.md](docs/from-explain.md) and [docs/from-keep-current.md](docs/from-keep-current.md). No version bump.

### Docs

- [docs/from-explain.md](docs/from-explain.md) walks `/crav1-explain`. [docs/from-keep-current.md](docs/from-keep-current.md) walks `/crav1-keep-current`. [docs/guild-routing.md](docs/guild-routing.md) lists both under Cross-cutting. No new lane. [README.md](README.md), [docs/install.md](docs/install.md), [docs/first-run.md](docs/first-run.md), and [plugins/crav1/README.md](plugins/crav1/README.md) name the commands. The landscape starter gains `## How the parts connect`. The behavior map gains one line for each. No version bump.

- The behavior map in [`.cursor/rules/kit-maintainer.mdc`](.cursor/rules/kit-maintainer.mdc) records one line per skill on main: what it reads, what it writes, what it leaves alone, who calls it, and which skill or agent it calls. An agent is listed only when it runs a skill. The map covers main. Guild routing is unchanged. No version bump.

## 1.7.0 (2026-10-04)

### Kit

- Cross-cutting skill `/crav1-fix-bug` names one real bug the user already named. It runs only when that turn names one. If none is named, it stops. It does not go hunting. A real bug is a verify failure on work that is already shipping, or a defect that comes in from outside. A design gap found before Build stays in the spec. An unfinished task stays a task. A one-off flaky check is a note, unless it keeps blocking ship. It says where the bug was seen (verify, a report, or production), names the bug, points at the spec or the shipped behavior it breaks, and names the lane. A spec miss goes to Specify. A plan miss goes to Plan. A verify miss or a broken implementation goes to Build. It does not start that lane, edit code, open a pull request, or create an Azure Boards work item. It is not a lane and not a stretch of verify. When the user asks for startup options, it is one of the options in that list. It is an intake for a bug that already exists. It is not a skill that runs because a repo is new, and it is not started automatically. Spark, specify, plan, and verify do not run it. Guild routing lists it under Cross-cutting. No new lane. Walkthrough: [docs/from-fix-bug.md](docs/from-fix-bug.md). No version bump.

- The bundled commit-message style is named CRAV1 style. The rules are unchanged (hyphen bullets, a verb at the start of each line, no Conventional Commits prefixes). The file stays `references/style.md`. GitKraken remains the name of the app where a message is pasted. Skill replies and the docs use CRAV1 style for that choice. No version bump.

### Docs

- [docs/from-fix-bug.md](docs/from-fix-bug.md) walks `/crav1-fix-bug` for Cursor and Claude Code. The slash command is the same. [docs/guild-routing.md](docs/guild-routing.md) lists the skill under Cross-cutting and adds it to the startup options. It may run from any lane, only when the user names a real bug, and it does not move work into Specify, Plan, or Build. [README.md](README.md), [docs/install.md](docs/install.md), [docs/first-run.md](docs/first-run.md), and [plugins/crav1/README.md](plugins/crav1/README.md) name the command. No new lane. No version bump.

## 1.6.0 (2026-10-04)

### Kit

- Cross-cutting skill `/crav1-review-pr` reads one named open pull request and says whether it can ship. It runs only when that turn names the pull request (number or URL) or clearly asks to review it. Any open pull request, not only a feature branch. If none is named, it asks which one and stops. It does not pick the newest. It reads the diff. It does not edit code, the spec, or the plan. It does not run the tests, vote, post a comment, install a linter, change branch protection, or merge. Before it says ship, five checks have to hold: the diff matches the spec, the plan’s named files and checks are in the diff, `verify.md` is quoted when it is already on the branch (and said to be missing when it is not), the pull request body matches that scope, and a linter or checker covers the code in the diff and is required and green. Each miss is its own finding (what is off, what could happen, decision ship, fix, or drop). Any fix or drop means the review does not say ship. It names the lane and does not start it: a spec miss is Specify, a plan miss is Plan, a verify miss or a file the plan already named but the diff lacks or a red or missing linter is Build, and a body mismatch is a rewrite of that pull request body, not a new spec. Suggestions do not block ship, except a secret in the diff, which is a first-section fix. A clean review says so and stops. `/crav1-open-pr` may name it and does not run it. `/crav1-merge-pr` does not run it. A review is not a merge ask. Merge still stops on its own when a required host check is red. Spark, specify, and verify do not run it. Guild routing lists it under Cross-cutting. Walkthrough: [docs/from-review-pr.md](docs/from-review-pr.md). No version bump.

- `/crav1-plan-from-spec` says whether this repo has a linter or checker for the code the tasks will touch, in `plan.md` under `## Linter`. When it has one, the plan names the tool and the command, and Build is expected to leave that check green. When it does not, the plan says so and stops before Build. The user decides to add the linter or to go on without one. The plan skill does not install one. Specify stays yes/no acceptance and does not name the linter. `/crav1-review-plan` and `/crav1-tighten-plan` use the same rule when they check that a plan is complete. A missing linter note is a plan `P#`. A plan that already says none is complete on that point and still stops before Build until the user chooses. No new plan skill. No version bump.

### Docs

- [docs/from-review-pr.md](docs/from-review-pr.md) walks `/crav1-review-pr` for Cursor and Claude Code. The slash command is the same. [docs/guild-routing.md](docs/guild-routing.md) lists the skill under Cross-cutting. It may run from any lane, only when the user names a pull request, and it does not move work into Specify, Plan, or Build. [README.md](README.md), [docs/install.md](docs/install.md), [docs/first-run.md](docs/first-run.md), and [plugins/crav1/README.md](plugins/crav1/README.md) name the command. Plan pages say the plan names a linter before Build. No version bump.

## 1.5.0 (2026-10-04)

### Kit

- `/crav1-plan-from-spec` names the checks on each task verify note before any code. Kinds are unit, system, browser, and integration when two parts meet. Contract, load or speed, accessibility, and golden or property are named only when the thing being built needs them. An algorithm gets several checks, including corner cases. A change that touches behavior that already works names regression tests. Kept security checks in `docs/system/security.md` or a Security section map to a task, or the plan says which task already covers them. The plan does not invent product behavior, a performance goal, or test code. Smoke after deploy, chaos, and fuzzing for its own sake stay out. Specify stays a yes/no acceptance line and names unit, system, or browser only when that kind is already obvious from the source. It does not invent a test list. `/crav1-review-plan` and `/crav1-tighten-plan` use the same check rules. `/crav1-implement-task` writes the checks named on that verify note. `/crav1-verify-spec` is unchanged and remains the gate that says the named checks passed. No new skill. Guild routing is unchanged. No version bump.

### Docs

- [README.md](README.md) says acceptance stays yes or no, and that `/crav1-plan-from-spec` names the checks on each task verify note before code. The task starter matches that shape. Guild routing is unchanged.

## 1.4.0 (2026-10-04)

### Kit

- Cross-cutting skill `/crav1-security-review` asks whether the thing in front of it is secure, and only after architecture already exists (`docs/system/` or a spec that already describes the design). The same command covers the whole system, one existing spec, or the change in front of us. If the target is unclear, it asks with options only, one option per real target. Findings are risks and what should change (what is wrong, what could happen if it stays, the decision being asked), each marked confirmed or inferred, plus a plain-language check. One confirm, then it writes only the kept findings: `docs/system/security.md` for a system pass, or a Security section on that spec for a feature or a change. It does not invent an architecture, write exploit steps, plan, implement, or commit. Spark, plan, and verify do not run it. `/crav1-architecture-reviewer` may name it as an optional next step and does not run it. Guild routing lists it under Cross-cutting. Walkthrough: [docs/from-security.md](docs/from-security.md). No version bump.

### Docs

- [docs/from-security.md](docs/from-security.md) walks `/crav1-security-review` for Cursor and Claude Code. The slash command is the same. [docs/guild-routing.md](docs/guild-routing.md) lists the skill under Cross-cutting and says it sits after architecture exists, with the same command for the whole system, one spec, or one change. [README.md](README.md), [docs/install.md](docs/install.md), [docs/first-run.md](docs/first-run.md), and [plugins/crav1/README.md](plugins/crav1/README.md) name the command. There is no public Cursor Marketplace listing.

- User-facing pages name Cursor and Claude Code on the first screen. The slash commands are the same. The install is not. Cursor installs plugin `crav1` from this GitHub repo (team marketplace import or a local plugin). There is no public Cursor Marketplace listing. Claude Code has no plugin and no marketplace; copy `.claude/` into a repository you own, or into `~/.claude` for a client project. Cloning the kit does not install it into another product. [docs/install.md](docs/install.md) stays the file-location guide. Skill behavior is unchanged. No version bump.

## 1.3.0 (2026-10-02)

### Kit

- Specify skills that write or read `docs/system/` now treat `glossary.md` as part of the landscape, not a feature spec. `/crav1-spark-to-spec`, `/crav1-ideas-to-spec`, `/crav1-intake-to-specs`, and `/crav1-match-to-specs` seed it in the same pass as `landscape.md`, `repos.md`, and `diagrams.md` when `docs/system/` is missing, write only that file when the folder exists and the glossary is missing, and append only new rows when the file exists. `/crav1-match-dump-to-specs` and `/crav1-code-into-specs` do not seed `docs/system/`. They fill a missing `glossary.md` only when that folder already exists, from the dump or the landed change, and they append new rows when the file exists. `/crav1-add-to-spec` does not create a glossary and does not write a new row unless apply is chosen. A new row from the new information can be one listed edit. Existing glossary rows are not rewritten, reordered, or edited. Rows are words or abbreviations the source already uses. When that source already says the meaning, that text is used. When it does not, Meaning is `to be researched`. Ordinary English is skipped. No new slash command. Guild routing is unchanged. No version bump.

### Docs

- Walkthroughs that list system files now include `glossary.md`: [docs/from-nothing.md](docs/from-nothing.md), [docs/from-ideas.md](docs/from-ideas.md), [docs/from-intake.md](docs/from-intake.md), and [docs/from-match.md](docs/from-match.md). [docs/from-match-dump.md](docs/from-match-dump.md) and [docs/from-code.md](docs/from-code.md) say a missing glossary is a gap fill only when `docs/system/` already exists. The starter is [docs/system/_template/glossary.md](docs/system/_template/glossary.md).

## 1.2.0 (2026-10-02)

### Kit

- `/crav1-code-into-specs` sorts a code change that already landed onto specs that already exist. The change is a commit, a commit range, or the diff of the current branch against the default branch. If the user does not name one, it looks at git and asks with options only (recent commits, or the branch diff) and does not ask for a typed hash. No dump is required. It does not ask for a slug first. It shows three piles — belongs to this spec, already described there, or fits none — and writes what belongs only after that sort is confirmed. Quotes go into the matching `spec.md` files the same way `/crav1-add-to-spec` writes them. It does not create a slug. Leftovers stay listed. It does not invent a landscape from the diff, and it does not seed `docs/system/` when that folder is missing. It does not rewrite the landscape or other specs unless the user chooses apply. It does not plan, implement, or commit. It does not watch the repo. Guild routing lists it in Specify between `/crav1-match-dump-to-specs` and `/crav1-add-to-spec`. Those skills, and match, intake, spark, ideas, and tighten, are unchanged. Walkthrough: [docs/from-code.md](docs/from-code.md).

## 1.1.0 (2026-10-02)

### Kit

- `/crav1-match-dump-to-specs` sorts a later dump (notes, tickets, old docs, diagrams, screenshots) onto specs that already exist. It does not ask for a slug first. It shows three piles — belongs to this spec, already in that spec, or does not fit — and writes new bits only after that sort is confirmed. Quotes go into the matching `spec.md` files the same way `/crav1-add-to-spec` writes them. It does not create a slug. Leftovers stay listed. It does not seed `docs/system/` when that folder is missing, and it does not rewrite the landscape or other specs unless the user chooses apply. It does not plan, implement, or commit. Guild routing lists it in Specify between `/crav1-match-to-specs` and `/crav1-add-to-spec`. Those skills, and intake, spark, ideas, and tighten, are unchanged. Walkthrough: [docs/from-match-dump.md](docs/from-match-dump.md).

## 1.0.0

First release of the public-facing kit: the skills, dual install, and sync check on `main`, plus the product-name, first-run, contributing, and support docs shipped with this changelog. The GitHub repository stays private until the owner changes visibility. This changelog does not create a git tag.

### Kit

- MIT license. The copyright notice is in [LICENSE](LICENSE).
- Dual install, documented in [docs/install.md](docs/install.md):
  - Drop-in copy into a product repo: `.cursor/skills/crav1/`, `.cursor/agents/crav1-*.md`, `.cursor/agent-assets/crav1-*`, and `.cursor/rules/crav1.mdc`.
  - Cursor plugin at `plugins/crav1/` with catalog `.cursor-plugin/marketplace.json` (team marketplace or local plugin).
- Skill loop under `/crav1`: spark, ideas, or intake → spec → architecture review and tighten → resolve questions → plan → review-plan and tighten-plan → one task (`/crav1-implement-task`) or an isolated worker (`/crav1-complete-task`, `/crav1-complete-tasks`, serial `/crav1-complete-features`) → verify → fix-from-verify (and fix-live) → draft or finalize a commit message.
- Maintainer sync: edit `.cursor/`, then run `scripts/sync-crav1-plugin.sh`. GitHub Actions (`.github/workflows/drop-in-plugin-sync.yml`) fails the check when the drop-in tree and `plugins/crav1/` drift, and when `kit-maintainer.mdc` is present under the plugin.
- `/crav1-add-to-spec` adds new information to one existing `docs/specs/<slug>/spec.md`, then reports whether `docs/system/` or another spec has to change. It does not rewrite those other files unless the user chooses apply. It does not plan, implement, or commit. A not-started spec can keep taking information until planning. Guild routing gains this skill. `/crav1-match-to-specs`, `/crav1-intake-to-specs`, `/crav1-spark-to-spec`, `/crav1-ideas-to-spec`, and `/crav1-tighten-spec` are unchanged. Walkthrough: [docs/from-add.md](docs/from-add.md).
- `/crav1-match-to-specs` matches one or more repos that already make up a system, plus a dump, to `docs/system/` and one `docs/specs/<slug>/` per confirmed slice (`done`, `partial`, or `not in the code`). It asks where the spec files go before any map, uses one branch for the dump, and does not plan, implement, or commit. Not-started slices stay thin. Code with no slice is a landscape note. Guild routing gains this skill. `/crav1-intake-to-specs`, `/crav1-spark-to-spec`, and `/crav1-ideas-to-spec` are unchanged. Walkthrough: [docs/from-match.md](docs/from-match.md).
- `/crav1-spark-to-spec` and `/crav1-ideas-to-spec` seed a thin `docs/system/` when that folder is missing, including greenfield and brownfield, then write the spec, then add one landscape index row. Thin uses the same landscape, repos, diagram, and ADR templates as intake, filled from the repo in front of the agent. They do not run an intake interview, call `/crav1-intake-to-specs`, or respec the whole product. An existing `docs/system/` is not rewritten; only an index row is added, plus a repo and ADR row when a new repo is needed. Intake is unchanged and still writes `docs/system/`. Method docs say the layout always includes `docs/system/`. Guild routing lanes are unchanged.
- Claude Code drop-in beside the Cursor install. `.cursor/` stays the source. `scripts/sync-crav1-plugin.sh` still mirrors `plugins/crav1/` and now regenerates `.claude/` (`scripts/sync-crav1-claude.sh`). `scripts/sync-crav1-claude.sh --check` exits non-zero when the committed `.claude/` tree is stale, and the drop-in sync workflow runs that check. Skill names and guild routing are unchanged. No version bump, no release tag, no Claude Code marketplace. Kit commit `acdaa0d` is on main (PR #12). On Claude Code 2.1.286, in a private throwaway git repo, the generated `.claude/` drop-in was used for `/crav1-spark-to-spec`, `/crav1-plan-from-spec`, one implement task, and `/crav1-verify-spec`. The trial feature was a root `hello.txt` of exactly the five bytes `68 65 6c 6c 6f`. Verify passed. Nothing from that repo was pushed. Two frictions: a PowerShell byte-dump that uses a script block was blocked by Claude Code's permission check, and the same bytes were checked another way; the feature-branch skill wants a clean tree, and the branch was created with the kit files still untracked.
- `/crav1-spark-to-spec`, `/crav1-ideas-to-spec`, and `/crav1-intake-to-specs` offer once to write `docs/specs/<slug>/work-item.md` when they create a new spec folder and the git remote is Azure Repos (`dev.azure.com` or `*.visualstudio.com`, same detection as the work-item mention). The question is optional. An id (`52`, `#52`, or `AB#52`) writes one line, `Work item: <id>`. Intake asks once and lists the new slugs so the user can give an id per slug or skip. Skip writes nothing and does not ask again in that run. GitHub and other hosts are not asked. The skills do not create or look up a work item, do not call Azure DevOps or `az`, and do not pass `--work-items`. Shared steps: `crav1-draft-commit-message` `references/work-item-offer.md`.
- `/crav1-merge-pr` confirms an Azure DevOps merge commit by re-reading the pull request (`status` completed; the update response can still say `active`) and counting parents with `git rev-list --parents -n 1` on `lastMergeCommit.commitId`. It does not read `lastMergeCommit.parents`, which can be null. If git cannot see the commit, it GETs the commits API and counts the `parents` array, or it says the merge type could not be verified and does not claim a no-fast-forward merge. One parent still stops the skill.
- `/crav1-open-pr` on Windows writes the accepted Azure DevOps description to a temp file as UTF-8 without a BOM and passes `--description "@<file>"`, then deletes the file, so `cmd.exe` does not keep only the first line. Non-Windows still passes the body as one value. `--query` values that contain parentheses must be quoted for `cmd.exe`. `/crav1-merge-pr` does not pass a multi-line body to `az`.
- Cross-cutting skill `/crav1-merge-pr` merges one named pull request only when that turn explicitly asks (number or URL). Always a merge commit: GitHub `gh pr merge <n> --merge`; Azure Repos `az repos pr update --org <url> --id <n> --status completed --squash false --detect false` (a non-squash completion with no `mergeStrategy` is no-fast-forward). `az repos pr update` takes the id, not `--project`, `--repository`, or `--merge-strategy`. No squash, no rebase, no `--admin`, no `--bypass-policy`. A draft is marked ready only as part of that ask (`--draft false` on the same update command, without `--project` or `--repository`). After completion the skill reads the pull request again and requires `status` completed, then a two-parent commit via `git rev-list` (commits API if git cannot see it). If `az` is missing, the update fails, or a branch policy disallows `noFastForward`, the skill prints the REST PATCH (`status` completed, `completionOptions.mergeStrategy` `noFastForward`, `lastMergeSourceCommit` set to the source head) and the web UI steps, and does not run `az rest` to complete the pull request. A `keyring` crash (`module 'keyring' has no attribute 'core'`) or `TF400813` uses a Code Read & Write token in `AZURE_DEVOPS_EXT_PAT`; the skill does not print the token. After a confirmed merge it reports the merge commit hash and, when the tree is clean, fast-forwards local `main`. It does not delete a branch unless asked, and it does not change work-item links. `/crav1-open-pr` names it as a later explicit step and does not run it.
- Optional Azure Boards linking via `docs/specs/<slug>/work-item.md` (`Work item: <id>`). Spec skills may write that file when the user answers the Azure Repos offer. `/crav1-draft-commit-message` leaves the subject and description as drafted, then appends a blank line and the mention as the last description line (GitKraken paste includes it). `/crav1-finalize-commit` keeps that line through the HEAD check and the Cursor-attribution strip. `/crav1-open-pr` adds a `## Work item` section when the file resolves a mention, and its Spec section links that slug’s `spec.md`, `plan.md`, and `tasks.md`. The mention is `#<id>` on Azure Repos, `AB#<id>` on GitHub, and omitted on any other host unless the file already contains a full token. A missing file does not block. On Azure Repos only, the commit and pull-request skills print one hint. `/crav1-open-pr` still does not pass `--work-items`.
- Cross-cutting skill `/crav1-open-pr` pushes the change branch only after an explicit yes, then opens one pull request against the default branch. It does not commit, merge, force-push, or delete the branch. `/crav1-finalize-commit`, `/crav1-complete-task`, `/crav1-complete-tasks`, and `/crav1-complete-features` may name it as an optional next step; they do not run it. Workers stay no push / no PR.
- `/crav1-open-pr` creates an Azure DevOps pull request with `az repos pr create` when the remote is `dev.azure.com` or `*.visualstudio.com` and the Azure CLI is available. GitHub still uses `gh`. If `az` is missing, not logged in, or create fails, the skill prints commands and GitKraken GUI paste fields and does not claim a pull request was opened.
- Subagent files and `name:` values now end in `-agent` (`crav1-architecture-reviewer-agent`, `crav1-complete-task-agent`, `crav1-intake-slice-agent`, `crav1-plan-reviewer-agent`, `crav1-spec-reviewer-agent`) so the Cursor slash picker can tell them apart from skills. Skill commands stay `/crav1-architecture-reviewer` and `/crav1-complete-task`. Descriptions start with `Subagent.`

### Docs

- README leads with the product name **CRAV1 Spec Kit** (`crav1`) and keeps the spec-driven playbook.
- [docs/first-run.md](docs/first-run.md) — install through one task.
- [CONTRIBUTING.md](CONTRIBUTING.md) — consumers install from [docs/install.md](docs/install.md); contributors edit `.cursor/` and sync.
- [SUPPORT.md](SUPPORT.md) — GitHub Issues for a broken skill or install.
- [docs/install.md](docs/install.md) no longer says Claude Code is waiting on a trial.
- Plugin author name and marketplace owner name stay **Crav1**. There is no author email. Questions, bugs, and requests go to GitHub Issues on this repo ([SUPPORT.md](SUPPORT.md)). [LICENSE](LICENSE) is unchanged.
- [README.md](README.md), [docs/from-nothing.md](docs/from-nothing.md), [docs/from-ideas.md](docs/from-ideas.md), [docs/from-intake.md](docs/from-intake.md), and [docs/first-run.md](docs/first-run.md) describe the method (specs, `plan.md`, `tasks.md`, verify). Host file locations, slash-command install, and the note that each host’s plan UI is not `plan.md` are in [docs/install.md](docs/install.md). Guild routing is unchanged.
- [docs/from-ideas.md](docs/from-ideas.md), [docs/from-nothing.md](docs/from-nothing.md), and [docs/from-intake.md](docs/from-intake.md) describe the optional Azure Repos work-item offer when a spec folder is created. [AGENTS.md](AGENTS.md) and the README describe that offer, the merge-pr parent count, and the Windows `@file` description. Guild routing is unchanged.
- [docs/from-ideas.md](docs/from-ideas.md) documents the optional `docs/specs/<slug>/work-item.md` mention. Starter: [docs/specs/_template/work-item.md](docs/specs/_template/work-item.md).
- Guild routing map added: [docs/guild-routing.md](docs/guild-routing.md). Lanes are Specify, Plan, Build, and Cross-cutting for public reuse.
- [docs/guild-routing.md](docs/guild-routing.md) lists `/crav1-open-pr` under Cross-cutting.
- [docs/guild-routing.md](docs/guild-routing.md) lists `/crav1-merge-pr` under Cross-cutting (any lane, only on an explicit ask to merge a named pull request). Specify, Plan, and Build lane ownership is unchanged.
- Plugin author and marketplace owner display name is **Crav1**. The contact email is unchanged. [LICENSE](LICENSE) is unchanged.
- [docs/guild-routing.md](docs/guild-routing.md) adds Research as a cross-cutting helper (no slash command). A lane that must answer a technical question before Specify or Plan flags the process orchestrator or guild lead, who pauses that lane. The researcher writes `docs/specs/<slug>/research.md` (recommendation, trade-offs, confidence, link to the full study) and does not edit specs, plans, or code, or change the lane.
