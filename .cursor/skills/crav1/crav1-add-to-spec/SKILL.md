---
name: crav1-add-to-spec
description: >-
  Use when new information should go into existing specs (a fact, a dump, a
  landed code change, a meeting, a mail, or a chat). Sorts it into specs and
  notes, writes only after a confirmed sort, and reports whether docs/system/
  or another spec has to change. Does not create a slug, plan, implement, or
  commit.
disable-model-invocation: true
icon: file-plus
color: blue
---

# Add to spec

## Opening question (1.56.0)

Read `references/opening.md` ("Opening question (1.56.0)") only when no branch was named in the invocation.

## Choice words

Exact words for bots and scripted runs. There are no `--flags`.

- What you have: `fact` / `dump` / `code change` / `meeting` / `mail` / `chat`.
- Code change, every open branch: `branches` (`branches all`, `branches skip stale`); read `references/branches-sweep.md`.
- Once after updating to 1.84.0, 1.86.0 or 1.97.0: `migrate formats`; see **Merge-safe formats** below.
- After a PR: `all`. A PR ref alone (`pr71`, `#71`, as `references/scope.md` parses) means `code change`; `pr71 all` adds description and comments per `references/pr-comments.md`, and a record Point per new thread (`references/pr-record.md`, 1.97.0).
- After `/crav1-pr-status`: `pr<n> candidates` (or `pr<n> candidates 1,3`) takes only the record's `to spec` and `to decision` Points that are not yet `in spec`; read `references/pr-candidates.md` (1.100.0).

`mail` and `chat` run the dump branch. "This mail", "this email" or "this chat" picks that word.

When the invocation contains one of these words (for example `/crav1-add-to-spec fact`), take that choice and do not ask. This holds for a person, a bot, or a headless run.

When a choice is missing and the run is headless or started by a bot (no person in the chat to answer), do not guess. Stop and name the valid words, for example: `Missing choice. Use one of: fact, dump, code change, meeting, mail, chat.`

## Merge-safe formats (1.84.0)

Every `Synced at` line, open question, `**New:**` line, glossary row and PR record line (1.97.0) this skill writes follows `references/merge-safe.md`: one `Synced at` line per repo and branch, questions found by their words (`Q#` is display only), and new lines in sorted place, not at the end.

`migrate formats` rewrites every spec, `docs/system/repos.md` and (1.97.0) every PR note once, moving old review follow-ups notes into their PR notes' record. Run `python3 <this skill>/scripts/merge_safe_migrate.py --dry-run` from the repo root and show its list and diff. After one yes (headless: the word is the yes), run it without `--dry-run`. It checks nothing was lost before it writes; a `LOST` line means that file was left alone, so show it and stop. A second run says `already merge-safe`. Do not commit.

## From /crav1-read-environment

Read `references/handoffs-read-environment.md` ("From /crav1-read-environment") only when the call comes from /crav1-read-environment.

## From /crav1-suggest-tests-for-code

Read `references/handoffs-suggest-tests.md` ("From /crav1-suggest-tests-for-code") only when the call comes from /crav1-suggest-tests-for-code.

## From the push features branch of /crav1-ado-sync

Read `references/handoffs-ado-push.md` ("From the push features branch of /crav1-ado-sync") only when the call comes from the ado-sync push features branch.

## From the pull spec changes branch of /crav1-ado-sync

Read `references/handoffs-ado-pull.md` ("From the pull spec changes branch of /crav1-ado-sync") only when the call comes from the ado-sync pull spec changes branch.

## From the meeting branch of /crav1-add-to-spec

Read `references/handoffs-meeting.md` ("From the meeting branch of /crav1-add-to-spec") only when the call comes from the meeting branch.

## From an import: answer links and asked marks

Read `references/handoffs-import-answers.md` ("From an import: answer links and asked marks") only when the input answers an open question or shows one being asked.

## Picture offer

Read `references/handoffs-picture.md` ("Picture offer") only when the run ends and a picture could be offered.

## A fact

Read `references/fact.md` (Input, Target, Imported sources, Add to that spec.md, Notes, Impact, Stop, Style) only when the branch is a fact, or a handoff above says to run one of those sections. A dump follows `branches/dump/BRANCH.md`, a code change `branches/code-change/BRANCH.md`, and a meeting `branches/meeting/BRANCH.md`.

## Shared steps

Used by the fact path and the dump branch.

### Thin spec

A thin spec (match status `not in the code`, or only Match / What the dump says / In the code / Trace / Open questions) stays thin. Put the quote under the heading it belongs to. Add a heading only when their words are that content. Do not add Problem, Goals, Users and journeys, or Acceptance criteria to fill the file out. Do not add `## In the code` unless their words name code that is there.

### Research compare

Also compare the kept quote with research. Follow [references/research-stale.md](references/research-stale.md). Read [references/research-stale-mark.md](references/research-stale-mark.md) only on a hit. Read `docs/research/*.md` and `## Research findings` on the specs this quote touches, and the notes those findings link to. List a clear contradiction and an answered open question. An unclear case is not a hit. Ask before any new mark. Write the stale block and the findings line only after the user says yes. Then offer the revisit draft. The kit drafts only. It does not send it. It does not contact the note's owner. When the user pointed this command at an updated note in `docs/research/`, or this run writes one, follow the clear section, [references/research-stale-clear.md](references/research-stale-clear.md). Judge each listed point. An older mark with no point lines is not one point. Split it as that file says. Also route the note's own open questions when the answer lies outside the note's owner. That still runs when the mark clears. Do not ask the user whether the update resolves the mark. A kept quote that answers a point already waiting is re-checked there too. That re-check does not ask.
