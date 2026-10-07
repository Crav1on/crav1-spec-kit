# From named repos to an architecture spec

Kit not in this project yet? [Install first](install.md) (Cursor and Claude Code; the slash commands match, the files do not). After a Cursor plugin install, the short command loop is [plugins/crav1/README.md](../plugins/crav1/README.md). Claude Code has no plugin.

Use this when the user names **one or more repos** and wants the architecture the code shows written down. This command is a starter option. Asking for startup options names it and does not run it. It still runs only when the user names repos.

This is cross-cutting. It is not a lane. It is not a mode of Specify. It writes one architecture spec the lanes can extend (`docs/architecture/spec.md`) when that file is missing. It writes the system notes under `docs/system/` that [explain](from-explain.md) reads when those notes are missing. When a real system note is already there, it leaves those notes and writes the missing architecture spec and `docs/architecture/left-out.md`. When the architecture spec or those notes are already there, a later re-read adds only what is new and does not rewrite lines that are already there, and removes a left-out line when the code shows it. It does not design the next feature. It does not write application code. It does not start Specify, Plan, or Build.

A fact the code shows is confirmed. Before any file is written, the confirmation stays in sections: one per named repo for confirmed facts, one for inferred guesses, one for links, and one for left-out. Each section has its own question and its own answer. Every item stays listed. A guess stays out until that section’s answer accepts it. A guess that stays left out is written to `docs/architecture/left-out.md`, beside the architecture spec. A later re-read checks every line in that file against the code. When the code shows it, the line comes off that file. The left-out answer can accept a line, keep it left out, or dismiss it. Dismiss means it is not offered again. A link between repos is written only when the code shows it. If none is found, that section says so and does not offer a guessed link. It does not invent links. Confirming a guess does not turn it into a link.

This is not [a code change onto existing specs](from-code.md) (`/crav1-code-into-specs`). That command sorts a change that already landed. This command reads the repos. Repos plus a dump stay [match](from-match.md). A feature sentence stays [a spark](from-nothing.md).

## First prompt

New chat. Strong reasoning model. Not the host plan UI.

Name the repos in this message.

```text
/crav1-repos-to-spec
@repo-a/
@repo-b/

Read these repos. Write one architecture spec and the system notes.
A guess stays out until I confirm it. Do not invent a link. Do not write code.
```

That slash command *is* the prompt.

If the message names no repo, the command stops. It does not pick a checkout.

## Steps

| Phase | You | Agent |
| --- | --- | --- |
| Repos | Named one or more checkouts | Stops when none was named. Does not clone. Does not pick a repo |
| Where | One repo is the destination. Several repos: pick one of them, or a new clean repo | Options only. No typed path. No files yet |
| Already there | — | Does not stop because notes or the architecture spec are already written. Missing spec and real notes: write `docs/architecture/spec.md` and `docs/architecture/left-out.md`, and leave the notes. Spec already there: a later re-read adds only what is new and checks `left-out.md` |
| Read | Answer one question per section | Sections stay separate: one per named repo, inferred guesses, links, and left-out. Every item stays listed. A fact cites a path. A guess stays out until that section accepts it. A link only when the code shows it. If none is found, that section says so and does not offer a guessed link. Left out can accept a line, keep it, or dismiss it. A fact already written is marked and is not added again |
| Branch | Pick `feat/architecture` or `spec/architecture` (or stay) | `/crav1-feature-branch` in the destination (no push, no pull request). On a later re-read, skips the branch when the confirmed list adds no new line. A missing architecture spec is still written |
| Write | Glance | Missing `docs/architecture/spec.md` is written there. Guesses that stay left out go to `docs/architecture/left-out.md` beside it. System notes are written when they are missing. Existing notes stay when the spec is the missing file. A later re-read appends only new spec lines and removes a left-out line when the code shows it. An accepted guess is labeled accepted. A link the code does not show is not written |
| Stop | `/crav1-finalize-commit` if a file changed | Does not plan, implement, or commit. Does not start Specify, Plan, or Build |

## What gets written

One spec: `docs/architecture/spec.md`. Starter: the skill’s `assets/spec.md`.

Guesses that stay left out: `docs/architecture/left-out.md`, beside that spec. Starter: the skill’s `assets/left-out.md`. Each line says the guess and that the code does not show it. It is not a confirmed fact and not a link.

The folder is `docs/architecture/`. The spec file is `spec.md`. `left-out.md` sits beside it. Both stay out of `docs/system` and out of `docs/specs`. `docs/specs` stays one folder per feature slug. `docs/system` stays the short picture. `spec.md` stays the one the lanes can extend. Do not put left-out guesses under a heading in `spec.md`.

System notes, the same files explain reads: `docs/system/landscape.md`, `repos.md`, `diagrams.md`, `glossary.md`, and an ADR only when the code shows a real choice. Starters: [docs/system/_template/](system/_template/).

A meaning the code does not state is `to be researched` on a glossary row. A later re-read appends a new row and does not rewrite a row that is already there. The first write is the one that creates the file. When real notes are already there and the architecture spec is missing, this command does not edit those notes except the `Synced at` cell of a repo it read, and only when `repos.md` already exists. A whole-repo read sets that cell to `<branch>@<short sha>, <date>`. A repo may list several branches, separated by `; `. Example: `main@abc1234, 2026-10-07; develop@def5678, 2026-10-06`. It touches only the repos it read.

No `plan.md`. No `tasks.md`. No application code. No `security.md`. No `work-item.md`.

The picture is the short description, the diagram, and how the parts connect. The first write fills those three from the confirmed facts. A later re-read adds only what is new and does not rewrite a line that is already there. When real notes are already there and the architecture spec is missing, the picture stays as it is. This command does not run `/crav1-keep-current`.

## After

If a file changed:

```text
/crav1-finalize-commit
```

That puts the spec and the notes in git. No push. This command does not commit for you.

The lanes can extend `docs/architecture/spec.md` in a later turn. This command does not start that turn.
