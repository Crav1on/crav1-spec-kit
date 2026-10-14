---
name: crav1-existing-to-specs
description: >-
  Turn a system that already exists into specs. Opens with two questions:
  repos only, or repos plus a bundle of notes, tickets, old docs,
  diagrams, or screenshots to match; and one spec (the architecture spec)
  or system notes plus one spec per feature. Skips a question the message
  already answers. Repos are evidence of what exists. A fact the code
  shows is confirmed; a guess stays out until accepted. Does not write
  application code or start Specify, Plan, or Build. Starter option.
  Replaces repos-to-spec and match-to-specs (their rules are kept as
  branches).
disable-model-invocation: true
icon: search
color: yellow
---

# Existing system to specs

You read a system that already exists and write specs from what it shows. You do not write application code.

This replaces `/crav1-repos-to-spec` and `/crav1-match-to-specs` (1.56.0). Their rules are kept, unchanged, as the branches below. Follow the branch the answers pick, in full. It is a starter option and still runs only when the user names the repos.

## Opening questions

Ask one question at a time, with the questions tool when it is available.

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

Skip a question the message already answers: no attached files means repos only; a dump or attachments means a bundle; "architecture spec" means one spec; "features" or "slices" means one spec per feature. An alias (`/crav1-repos-to-spec`, `/crav1-match-to-specs`) arrives with both answers already made (repos only and one spec; or repos plus a bundle and one spec per feature).

When the user names no repos, stop and ask for them. Do not read the open checkout on your own.

## After

Each branch ends with its own recap and next step.
