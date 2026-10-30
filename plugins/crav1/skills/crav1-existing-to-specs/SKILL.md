---
name: crav1-existing-to-specs
description: >-
  Use when the user names repos of a system that already exists and wants
  specs for it, optionally matched against a bundle of notes or old docs, or
  wants to recheck existing specs against the repos: code no spec covers and
  stale spec claims. Starter option. Does not write code, plan, or build.
disable-model-invocation: true
icon: search
color: yellow
---

# Existing system to specs

You read a system that already exists and write specs from what it shows. You do not write application code.

This replaces `/crav1-repos-to-spec` and `/crav1-match-to-specs` (1.56.0). Their rules are kept, unchanged, as the branches below. Follow the branch the answers pick, in full. It is a starter option and still runs only when the user names the repos.

## Recheck (1.108.0, preview)

When the invocation has `recheck` or `repos vs specs`, or the user asks what code no existing spec covers, follow only [branches/recheck/BRANCH.md](branches/recheck/BRANCH.md). Do not ask the opening questions and do not read the other branches.

## Opening questions

Ask one question at a time.

1. **What do you have?**
   - **Repos only.** The named repos are the whole input.
   - **Repos plus a bundle.** The repos, plus notes, tickets, old docs, diagrams, or screenshots to match to them.
2. **What should it write?**
   - **One spec.** The architecture spec the code shows (`docs/architecture/spec.md`, `left-out.md`, and the system notes when missing).
   - **System notes plus one spec per feature.** `docs/system/` and one spec per confirmed slice.

Which branch:

- Repos only, one spec: [branches/repos-only/BRANCH.md](branches/repos-only/BRANCH.md).
- Repos plus a bundle, system notes plus one spec per feature: [branches/repos-and-bundle/BRANCH.md](branches/repos-and-bundle/BRANCH.md).
- Repos only, system notes plus one spec per feature: [branches/repos-and-bundle/BRANCH.md](branches/repos-and-bundle/BRANCH.md) with no bundle; every slice comes from the code.
- Repos plus a bundle, one spec: [branches/repos-only/BRANCH.md](branches/repos-only/BRANCH.md), using the bundle only as context for the confirmations; nothing from the bundle becomes a fact unless the code shows it.

Skip a question the message already answers: no attached files means repos only; a dump or attachments means a bundle; "architecture spec" means one spec; "features" or "slices" means one spec per feature.

When the user names no repos, stop and ask for them. Do not read the open checkout on your own. Recheck is the one exception: it may take the repos from `docs/system/repos.md`.

## Choice words

Exact words for bots and scripted runs. There are no `--flags`.

- What to read: `repos only` / `repos and bundle`.
- What to write: `one spec` / `spec per feature`.
- Recheck existing specs against the repos: `recheck` / `repos vs specs`, optionally a repo, a path, and `since`.

When the invocation contains one of these words (for example `/crav1-existing-to-specs repos only`), take that choice and do not ask that question. This holds for a person, a bot, or a headless run.

When a choice is missing and the run is headless or started by a bot (no person in the chat to answer), do not guess. Stop and name the valid words, for example: `Missing choice. Use one of: repos only, repos and bundle.` Each question with no word stops the same way.

## After

Each branch ends with its own recap and next step.
