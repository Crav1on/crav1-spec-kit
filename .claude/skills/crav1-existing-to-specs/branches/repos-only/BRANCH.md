# Repos to spec

The user names one or more repos. You read those repos and write **one** architecture spec the lanes can extend (`docs/architecture/spec.md`). Guesses that stay left out are written to `docs/architecture/left-out.md` beside that spec. When that spec is missing and a real system note is already in `docs/system/`, you write the spec and the left-out file and leave the notes. When those notes are missing, you write them too.

Command: `/crav1-existing-to-specs`.

This command is a starter option. When the user asks for startup options, name only `/crav1-spark-to-spec`, `/crav1-ideas-to-spec`, `/crav1-bundle-to-specs`, `/crav1-existing-to-specs`, `/crav1-read-environment`, and `/crav1-fix-bug`. That ask names the list. It does not run this command and does not move work into a lane. Every other skill is a later skill. This command still runs only when the user names repos.

This is cross-cutting. It is not a lane. It is not a mode of Specify. It does not move work into Specify, Plan, or Build. It does not start those lanes.

This is not the code change branch of `/crav1-add-to-spec`. That command sorts a code change that already landed onto specs that already exist. This command reads the repos the user named and writes one architecture spec. Do not send this job to that command, and do not absorb its job.

This is not the repos and bundle branch of `/crav1-existing-to-specs`. That branch needs a dump and writes one spec per slice. This command has no dump and writes one architecture spec. This is not `/crav1-spark-to-spec`, `/crav1-ideas-to-spec`, or `/crav1-bundle-to-specs`. Those specify a feature. This command does not design the next feature.

A later re-read is this command. It adds only what is new to the architecture spec and the system notes. It does not rewrite a line that is already there. It also reads `docs/architecture/left-out.md` and can remove a line from that file when the code shows it, or when that section dismisses it.

## From /crav1-read-environment

When `/crav1-read-environment` hands a confirmed architecture section or a left-out line, run only this section, then stop. Do not run the repo read, the section interview, or the branch prompt. Do not start Specify, Plan, or Build.

An architecture section adds only what is new to `docs/architecture/spec.md` when that file is already there. Mark each new line `Seen in <host> <environment>.` When the line says `shared with prod`, `prod only`, or shape and connections only, keep that label. Do not mark it as a fact the code shows. A link is added only when that section says the environment shows the connection. Do not rewrite a line that is already there. If `docs/architecture/spec.md` is missing, write nothing. Do not create it from the environment.

A left-out line the environment now shows comes off `docs/architecture/left-out.md`. Do not rewrite a line that stays. Do not write the line back as a guess.

## Inputs

Everything after `/crav1-existing-to-specs`, and every `@`, is the pointer.

A named repo is a checkout they `@`-mentioned, a path they gave, or this checkout when they said this repo. A URL with no checkout is not a repo you can read. Ask them to point at a checkout. Do not clone. Do not invent a repo.

If they named no repo, stop. Ask them to name the repos. Do not pick the current checkout for them. Do not scan the workspace and choose.

## Where the files go

One named repo: that repo is the destination. Do not ask.

More than one named repo: ask where the files go before the read. Use the questions tool when it is available. Options only. Do not ask them to type a path.

1. One option per named repo, labeled with that repo’s name.
2. Last option: **A new clean repo**.

Stop until they pick. Do not read for facts yet. Do not write files.

**A new clean repo.** Create it only after every confirmation section has an answer, and only when you are about to write. `git init` a new directory. No remote. No application code. Name it with a short kebab the code already shows, or `architecture` when the code shows no name. Put it next to the named repos when those paths share a parent directory. Otherwise create it in the current workspace. Tell them the path you used. The named repos stay evidence. They are listed in `repos.md` on a pass that writes system notes, and are not given their own spec trees.

## What is already there

Read this skill's `branches/repos-only/references/already-there.md` now, before you go on.

## Read (no files yet)

Read this skill's `branches/repos-only/references/read.md` now, before you go on.

## Branch

After every section has an answer, and after you create a new clean repo if they picked one. A repo with no commits skips the prompt. On a later re-read, when every confirmed fact and accepted guess is already a line in `docs/architecture/spec.md` and in the system notes this pass may edit, and `docs/architecture/left-out.md` would not gain, lose, or move a line, skip the branch. Write nothing. Say the files are current. A missing `docs/architecture/spec.md` is not current. Do not skip that write because the notes already state the facts.

Follow `/crav1-create-feature-branch` (skill `crav1-create-feature-branch`, `SKILL.md`) in the **destination** repo. Slug: `architecture`. Specify options: `feat/architecture` first, then `spec/architecture`, stay, or other. Do not write files until that choice is done or skipped. Do not push. Do not open a pull request.

## Write

One spec: `docs/architecture/spec.md`, from this skill’s `assets/spec.md` (this skill's `branches/repos-only/assets/spec.md`). The folder is `docs/architecture/`. The file is `spec.md`. `docs/architecture/left-out.md` sits beside it, from this skill’s `assets/left-out.md` (same drop-in and plugin paths). Both stay out of `docs/system` and out of `docs/specs`. `docs/specs` stays one folder per feature slug. `docs/system` stays the short picture. `spec.md` stays the one the lanes can extend. Do not create `docs/specs/architecture/`. Do not invent any other folder. Do not put left-out guesses under a heading in `spec.md`.

System notes, when this pass writes them, come from this skill’s `assets/system/` (same files as `docs/system/_template/`: `landscape.md`, `repos.md`, `diagrams.md`, `glossary.md`; an ADR file comes from `assets/system/adr.md` only when the table below says to write one). Drop-in: this skill's `branches/repos-only/assets/system/`. Plugin: this skill’s `assets/system/`.

Source for every fill of `spec.md` is the confirmed facts the repo sections’ answers kept, plus a guess only when the inferred section or the left-out section accepts it. An accepted guess is labeled accepted. It is not labeled confirmed. A link comes only from the links section, and only when the code shows it. A guess that stays left out is written only to `docs/architecture/left-out.md`.

A fact, link, guess, row, node, or edge that is already written is not new. Do not add it again. Do not reword the line that is already there. That does not keep a left-out line the code now shows, or a line this answer accepts or dismisses.

### First write

Read this skill's `branches/repos-only/references/first-write.md` now, before you go on.

### Later re-read

Read this skill's `branches/repos-only/references/later-re-read.md` now, before you go on.

## Synced at

Read this skill's `branches/repos-only/references/synced-at.md` now, before you go on.

## Stop

Do not plan. Do not implement. Do not commit. Do not start Specify, Plan, or Build. Do not run `/crav1-spark-to-spec`, `/crav1-ideas-to-spec`, `/crav1-bundle-to-specs`, the repos and bundle branch of `/crav1-existing-to-specs`, the code change branch of `/crav1-add-to-spec`, `/crav1-plan-from-spec`, the implement step of `/crav1-build-tasks`, `/crav1-explain-existing-system`, `/crav1-refresh-system-notes`, or `/crav1-finalize-commit`.

Output only:

- Which pass: first write, missing architecture spec, or later re-read
- Paths written. On a missing architecture spec, say the system notes were left as they are, and name a `Synced at` line in `repos.md` when that was the exception. On a later re-read, name each file that got a new line or lost a left-out line, or say that file is current. Name each `Synced at` line in `repos.md` this run set.
- Counts: confirmed facts written, guesses accepted, guesses left out, guesses dismissed
- Whether the code shows a link, or that no link was found
- Next: `/crav1-finalize-commit` when a file changed (no push). When nothing was written, name no command. Do not run it. The lanes can extend `docs/architecture/spec.md` in a later turn. Do not start that turn.

If they chose `spec/architecture`, say that branch is specify-only: no implement there.

## Hard rules

- No repo named: stop. Do not pick one.
- A fact the code shows is confirmed and cites a path.
- A guess stays out of `spec.md` until the inferred section or the left-out section accepts it. Then it is accepted from a guess, not a code fact. Confirming a guess does not turn it into a link.
- A guess that stays left out is written to `docs/architecture/left-out.md`. Each line says the guess and that the code does not show it. It is not a confirmed fact and it is not a link. Do not put those lines under a heading in `spec.md`. Do not put them in `docs/system/` or `docs/specs/`.
- Dismiss means that line is not offered again. Keep it in `left-out.md` under `## Dismissed`.
- A later re-read reads `docs/architecture/left-out.md` and checks the code for every line there. When the code shows the fact, write it as a confirmed fact and remove the line. When the code shows a real link, write it as a link and remove the line. A similar name, a README wish, or a matching identifier the code does not call is not enough. When the code still does not show it, the line stays.
- A link is written only when the code shows it. If none is found, the links section says so and does not offer a guessed link. Do not invent a link.
- One architecture spec at `docs/architecture/spec.md`. Left-out guesses at `docs/architecture/left-out.md`. Those paths are locked. Branch slug `architecture`. Do not create a second slug. Do not put these files under `docs/specs/` or `docs/system/`. Do not invent any other folder.
- When `spec.md` is missing and a real `docs/system/` note is already there, write the architecture spec and the left-out file. Leave those notes as they are.
- When `docs/architecture/spec.md` is already there, a later re-read adds only what is new to that file and to system notes that are already there. Do not rewrite a line that is already there. `left-out.md` still loses a line when the code shows it or that section dismisses it.
- Do not design the next feature. Do not write application code. Do not start Specify, Plan, or Build.
- This is not the code change branch of `/crav1-add-to-spec`.

## Style

Be concise. Cite paths. Prefer the smaller fact. Do not fill a gap with an architecture you invented.
