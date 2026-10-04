---
name: crav1-repos-to-spec
description: >-
  Read one or more repos the user named. Write one architecture spec the
  lanes can extend (docs/architecture/spec.md) when that file is missing,
  and the docs/system/ notes /crav1-explain reads when those notes are
  missing. When a real system note is already there, leave it and write
  only the missing architecture spec. When the architecture spec or those
  notes are already there, a later re-read adds only what is new and does
  not rewrite lines that are already there. A fact the code shows is
  confirmed. A guess stays out of the spec until the user confirms it. A
  link between repos is written only when the code shows it. If none is
  found, say so. Do not invent links. Do not design the next feature,
  write application code, or start Specify, Plan, or Build. This is not
  /crav1-code-into-specs.
disable-model-invocation: true
icon: boxes
color: cyan
---

# Repos to spec

The user names one or more repos. You read those repos and write **one** architecture spec the lanes can extend (`docs/architecture/spec.md`). When that file is missing and a real system note is already in `docs/system/`, you write only the spec and leave the notes. When those notes are missing, you write them too.

Command: `/crav1-repos-to-spec`.

This is cross-cutting. It is not a lane. It is not a mode of Specify. It does not move work into Specify, Plan, or Build. It does not start those lanes.

This is not `/crav1-code-into-specs`. That command sorts a code change that already landed onto specs that already exist. This command reads the repos the user named and writes one architecture spec. Do not send this job to that command, and do not absorb its job.

This is not `/crav1-match-to-specs`. Match needs a dump and writes one spec per slice. This command has no dump and writes one architecture spec. This is not `/crav1-spark-to-spec`, `/crav1-ideas-to-spec`, or `/crav1-intake-to-specs`. Those specify a feature. This command does not design the next feature.

A later re-read is this command. It adds only what is new. It does not rewrite a line that is already there.

## Inputs

Everything after `/crav1-repos-to-spec`, and every `@`, is the pointer.

A named repo is a checkout they `@`-mentioned, a path they gave, or this checkout when they said this repo. A URL with no checkout is not a repo you can read. Ask them to point at a checkout. Do not clone. Do not invent a repo.

If they named no repo, stop. Ask them to name the repos. Do not pick the current checkout for them. Do not scan the workspace and choose.

## Where the files go

One named repo: that repo is the destination. Do not ask.

More than one named repo: ask where the files go before the read. Use the questions tool when it is available. Options only. Do not ask them to type a path.

1. One option per named repo, labeled with that repo’s name.
2. Last option: **A new clean repo**.

Stop until they pick. Do not read for facts yet. Do not write files.

**A new clean repo.** Create it only after they confirm the read, and only when you are about to write. `git init` a new directory. No remote. No application code. Name it with a short kebab the code already shows, or `architecture` when the code shows no name. Put it next to the named repos when those paths share a parent directory. Otherwise create it in the current workspace. Tell them the path you used. The named repos stay evidence. They are listed in `repos.md` on a pass that writes system notes, and are not given their own spec trees.

## What is already there

Check the destination before the read. Do not stop because a note is already in `docs/system/`. Do not stop because `docs/architecture/spec.md` is already there. Name which pass this is, then read.

A real note is a short description that is not the template sentence, a diagram that is not only the template sample, a connection line that is not the template intro, a repo row, a glossary row, an ADR, or a feature-index row with a slug. The template sentence `What this product/system is, in one short paragraph.` is not a short description. The template diagram `user[User] --> app[App]` with no other node is not a diagram of this system. A `docs/system/` that is missing, or that is only the untouched template, is not already written.

Three passes:

1. **First write.** `docs/architecture/spec.md` is missing, and `docs/system/` is missing or only the untouched template. Write the architecture spec and the system notes.
2. **Missing architecture spec.** `docs/architecture/spec.md` is missing, and a real note is already in `docs/system/`. Write only `docs/architecture/spec.md`. Leave every system note as it is. Do not add a line to those notes. Do not rewrite them.
3. **Later re-read.** `docs/architecture/spec.md` is already there. Add only what is new to that file. Do not rewrite a line that is already there. The same rule for system notes that are already there. When `docs/system/` is missing or only the untouched template, those notes are not already there, so this pass writes them and still only adds what is new to the architecture spec.

The architecture spec path is locked: `docs/architecture/spec.md`. It stays out of `docs/system` and out of `docs/specs`. Do not invent any other folder. Do not create `docs/specs/architecture/`.

Do not point this pass at `/crav1-explain`. Do not run it.

## Read (no files yet)

Read the named repos. On a later re-read, also read `docs/architecture/spec.md` and the real notes in `docs/system/` so you know which lines are already there. Then show two lists. Do not write files.

**Confirmed.** A fact the code shows. A reader can point at a file, a type, a route, a config key, or a dependency. Cite the path on every line. A fact with no path is not confirmed. On a later re-read, mark a fact that is already a line as already written. Keep it on the list. The write does not add it again.

**Inferred.** A guess. A purpose, a product story, or a “should” the code does not state. These stay out of the spec until the user confirms them. List them here so the user can accept or leave them.

A smaller fact beats a story. `this file defines Charge` stays confirmed when the file shows that name. `this service handles billing` is inferred unless the code states billing.

**Links.** A link is code in one named repo that reaches another named repo: a call, an import, a URL, a client, a queue, or a config entry. Cite the path. Write a link only when the code shows it. A comment, a README wish, or a similar name is not a link. Do not put a guessed link on the inferred list as something the user can accept into the link section. One named repo has no second repo to reach. Say only one repo was named. Do not invent a link inside that repo and call it a link between repos. If the search finds no link, say so in the confirmed list: no link between these repos is in the code. Do not invent a link. On a later re-read, mark a link that is already a line as already written.

Stop. They confirm or edit the lists. Do not write files. That confirmation is the only stop before writing. Do not open a feature interview, an architecture interview, or an export-format question.

Use the questions tool when it is available. Options only:

1. **Write the confirmed facts.** Every guess stays out.
2. **Write the confirmed facts and the guesses I name.** They name which inferred lines to accept.

If they edit the lists, the edit is the confirmation. Do not ask again. A confirmed fact they struck stays out. A guess they do not accept stays out. A guess they accept is written later as accepted from a guess, not as a fact the code shows. Confirming a guess does not turn it into a link. If they add a link the code does not show, do not write that link. Say the code does not show it.

## Branch

After they confirm, and after you create a new clean repo if they picked one. A repo with no commits skips the prompt. On a later re-read, when every confirmed fact and accepted guess is already a line in `docs/architecture/spec.md` and in the system notes this pass may edit, skip the branch. Write nothing. Say the files are current. A missing `docs/architecture/spec.md` is not current. Do not skip that write because the notes already state the facts.

Follow `/crav1-feature-branch` (drop-in: `.claude/skills/crav1-feature-branch/SKILL.md`; plugin: sibling `skills/crav1-feature-branch/SKILL.md`) in the **destination** repo. Slug: `architecture`. Specify options: `feat/architecture` first, then `spec/architecture`, stay, or other. Do not write files until that choice is done or skipped. Do not push. Do not open a pull request.

## Write

One spec: `docs/architecture/spec.md`, from this skill’s `assets/spec.md` (drop-in: `.claude/skills/crav1-repos-to-spec/assets/spec.md`; plugin: this skill’s `assets/spec.md`). The folder is `docs/architecture/`. The file is `spec.md`. Later architecture files can sit beside it. This file stays out of `docs/system` and out of `docs/specs`. `docs/specs` stays one folder per feature slug. `docs/system` stays the short picture. This file stays the one the lanes can extend. Do not create `docs/specs/architecture/`. Do not invent any other folder.

System notes, when this pass writes them, come from this skill’s `assets/system/` (same files as `docs/system/_template/`: `landscape.md`, `repos.md`, `diagrams.md`, `glossary.md`; an ADR file comes from `assets/system/adr.md` only when the table below says to write one). Drop-in: `.claude/skills/crav1-repos-to-spec/assets/system/`. Plugin: this skill’s `assets/system/`.

Source for every fill is the confirmed list, plus a guess only when they accepted it. An accepted guess is labeled accepted. It is not labeled confirmed.

A fact, link, guess, row, node, or edge that is already written is not new. Do not add it again. Do not reword the line that is already there.

### First write

`docs/architecture/spec.md` is missing, and the system notes are missing or only the untouched template. Write the architecture spec and the system notes. Replace the template fills.

| File | Fill |
| --- | --- |
| `spec.md` | The sections in `assets/spec.md`. Confirmed facts under **Confirmed** and under the repo heading, each with a path. Accepted guesses only under **Accepted from a guess**, each saying the code does not show it. Leave that section empty when they accepted none. Under **How the repos connect**, one line per link the code shows, with the path. When only one repo was named, the only line is `Only one repo was named.` When more than one repo was named and the code shows no link, the only line is `No link between these repos is in the code.` **Open questions** name what the code does not show. A guess they did not accept stays out of the file. |
| `landscape.md` | One short paragraph of what the code shows these repos are. Replace the template sentence. Under `## How the parts connect`, one line per link the code shows. When only one repo was named, one line: `Only one repo was named.` When more than one repo was named and the code shows no link, one line: `No link between these repos is in the code.` **v0** is the architecture the code already shows, in one line. Leave **Later** empty. Bulk assumptions are confirmed facts only. When the code states none, write `None the code states.` Constraints are only ones the code shows. When it shows none, write `None the code states.` Leave the feature index empty until the spec file exists, then one row: slug `architecture`, spec `docs/architecture/spec.md`, Repos column lists the destination and the named repos, Notes `architecture`. |
| `repos.md` | Every named repo, plus the destination when it is the new clean repo. Status `exists` when the checkout is a real repo. Put the URL when the checkout has one. The new clean repo stays without a remote. Boundaries only when the code shows one. |
| `diagrams.md` | One context diagram. Replace the sample. One heading, one sentence, one fence. Nodes are the named repos. An edge only when the code shows that link. When only one repo was named, one node and no edge, and the sentence says only one repo was named. When more than one repo was named and the code shows no link, draw the nodes and no edge, and the sentence says no link was found. Do not invent a user, a service, or a queue. |
| `glossary.md` | From `assets/system/glossary.md`. See the glossary rules below. |
| `adr/` | Only where the code shows a real choice, with real alternatives. Otherwise write no ADR. A guess is not an ADR. |

**Glossary.** `glossary.md` is part of the landscape, not a feature spec. Source is the code in the named repos. Do not invent terms, expansions, or definitions. Do not write TBD or to be decided. A row is only a word or abbreviation that code already uses. When that same code already says the expansion or meaning, put that text in Meaning. When the code never says what it means, set Meaning to `to be researched`. Skip ordinary English. A code identifier is not a row unless the code already treats that word as a term. Write the file even when it has no rows. An accepted guess does not add a row.

The picture is the short description, the context diagram, and `## How the parts connect`. This write fills those three from the confirmed list. Do not run `/crav1-keep-current`.

### Missing architecture spec

A real note is already in `docs/system/`, and `docs/architecture/spec.md` is missing. Write only that spec, using the `spec.md` row above. Leave every file under `docs/system/` as it is. Do not add a line. Do not rewrite a line. Do not fill a gap in those notes on this pass. Do not run `/crav1-keep-current`.

### Later re-read

`docs/architecture/spec.md` is already there. Add only what is new. Do not rewrite, reorder, or delete a line that is already there.

**Architecture spec.** Append a confirmed fact under **Confirmed** and under the repo heading when that fact is not already a line. Cite the path. A repo the user named that has no heading yet gets a new heading. Do not rewrite the lines under a heading that is already there. Append an accepted guess under **Accepted from a guess** when it is not already a line, and say the code does not show it. Append a link under **How the repos connect** when the code shows it and that link is not already a line. Cite the path. Do not invent a link. Leave an existing `Only one repo was named.` or `No link between these repos is in the code.` line as it is. Append an open question when the code does not show it and that question is not already a line. A guess they did not accept stays out. When nothing new belongs in the file, write no line. Say the architecture spec is current.

**System notes that are already there.** The same rule. Add only what is new. Do not rewrite a line that is already there.

- Short description: keep every sentence. When a confirmed fact is not already named there, add one sentence at the end. Do not rephrase a sentence that is already there.
- `## How the parts connect`: append one line per new link the code shows that is not already a line. Do not edit a line that is already there.
- Diagram: keep every existing node and edge. Append a node or an edge the code shows that the fence does not already show. Do not rename a node. Do not redraw the fence. Do not invent a user, a service, or a queue. When the fence is still the template sample, replace that sample. It is not a real diagram.
- `repos.md`: append a row for a named repo that is not already listed. Do not rewrite an existing row.
- `glossary.md`: append a new row only for a word the code already uses that is not already a row. Do not rewrite an existing row. The glossary rules above still apply. An accepted guess does not add a row.
- Feature index: when `docs/architecture/spec.md` exists and the architecture row is missing, append that one row. Do not rewrite other rows.
- `adr/`: do not rewrite an existing ADR. Write a new ADR only when the code shows a real choice, with real alternatives, that is not already an ADR. A guess is not an ADR.
- v0, bulk assumptions, and constraints: append a confirmed fact that is not already a line. Do not rewrite a line that is already there. Leave `None the code states.` in place.

When `docs/system/` is missing or only the untouched template, those notes are not already there. Write them with the first-write table. Still add only what is new to the architecture spec.

Do not run `/crav1-keep-current`. This pass is the add.

Do not write `plan.md`, `tasks.md`, `diagrams.md` inside the spec folder, `adr/` inside the spec folder, `export/`, `verify.md`, `fix-log.md`, `security.md`, or `work-item.md`. Do not read `work-item-offer.md`. Do not write application code. Do not design the next feature. No goals for a feature, no acceptance list for work to build, no “should”.

## Stop

Do not plan. Do not implement. Do not commit. Do not start Specify, Plan, or Build. Do not run `/crav1-spark-to-spec`, `/crav1-ideas-to-spec`, `/crav1-intake-to-specs`, `/crav1-match-to-specs`, `/crav1-code-into-specs`, `/crav1-plan-from-spec`, `/crav1-implement-task`, `/crav1-explain`, `/crav1-keep-current`, or `/crav1-finalize-commit`.

Output only:

- Which pass: first write, missing architecture spec, or later re-read
- Paths written. On a missing architecture spec, say the system notes were left as they are. On a later re-read, name each file that got a new line, or say that file is current
- Counts: confirmed facts written, guesses accepted, guesses left out
- Whether the code shows a link, or that no link was found
- Next: `/crav1-finalize-commit` when a file changed (no push). When nothing was written, name no command. Do not run it. The lanes can extend `docs/architecture/spec.md` in a later turn. Do not start that turn.

If they chose `spec/architecture`, say that branch is specify-only: no implement there.

## Hard rules

- No repo named: stop. Do not pick one.
- A fact the code shows is confirmed and cites a path.
- A guess stays out of the spec until the user confirms it. Then it is accepted from a guess, not a code fact.
- A link is written only when the code shows it. If none is found, say so. Do not invent a link.
- One architecture spec at `docs/architecture/spec.md`. That path is locked. Branch slug `architecture`. Do not create a second slug. Do not put this file under `docs/specs/` or `docs/system/`. Do not invent any other folder.
- When that file is missing and a real `docs/system/` note is already there, write only the architecture spec. Leave those notes as they are.
- When `docs/architecture/spec.md` is already there, a later re-read adds only what is new. Do not rewrite a line that is already there. The same rule for system notes that are already there.
- Do not design the next feature. Do not write application code. Do not start Specify, Plan, or Build.
- This is not `/crav1-code-into-specs`.

## Style

Be concise. Cite paths. Prefer the smaller fact. Do not fill a gap with an architecture you invented.
