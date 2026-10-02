# From existing repos and a dump to specs

Kit not in this project yet? [Install first](install.md). After a plugin install, the short command loop is [plugins/crav1/README.md](../plugins/crav1/README.md).

Use this when **one or more repos already make up a system**, and you have a **dump** (notes, tickets, old docs, diagrams, screenshots) to match against that code.

The repos are evidence of what exists. The dump is what to match. It is not a brief for a new product. You still do **not** start by coding.

This command is not [intake](from-intake.md), [a spark](from-nothing.md), or [a pile of ideas](from-ideas.md). It does not replace those commands. A new system, with code only as background, stays `/crav1-intake-to-specs`. One or two sentences stay `/crav1-spark-to-spec`. One unstructured pile for one feature stays `/crav1-ideas-to-spec`.

## First prompt

New chat. Strong reasoning model. Not the host plan UI yet.

`@` the repos and the dump. No required structure in the dump.

```text
/crav1-match-to-specs
@repo-a/
@repo-b/
@notes/old-spec.md
@tickets/

The repos are what exists. The dump is what to match.
Do not write code. Ask where the specs go, then map, and stop.
```

That slash command *is* the prompt.

## Steps

| Phase | You | Agent |
| --- | --- | --- |
| Where specs go | Pick one repo already in front of the command, or a new clean repo | Options only. Does not ask for a typed path. No files yet |
| Map | Confirm or edit slices, which repo each belongs to, and done / partial / not in the code | Reads the repos and the dump. Lists code no slice covers, on the side. Stops |
| Branch | Pick `feat/…` or `spec/…` (or stay) | `/crav1-feature-branch`, one branch for the dump (no push, no PR) |
| Landscape | — | `docs/system/` from the repos and the confirmed match, including `glossary.md`. An existing landscape is not rewritten; only gaps the match needs, including a missing glossary and new glossary rows. Existing glossary rows are not rewritten. A meaning the source does not state is `to be researched` |
| Slice specs | Wait | One `docs/specs/<slug>/` per confirmed slice, including not in the code |
| Index | — | One landscape row per slice, with match status |
| Stop | Glance, then `/crav1-finalize-commit` if this dump should be in git | Does not plan, implement, or commit |


The map confirmation is the only product stop before writing. Confirming the map accepts the facts left on it. Facts that were not confirmed stay labeled inferred.

A new clean repo is created only if that option was picked. Other repos are listed in `repos.md`. They do not get their own spec trees.

## What gets written

```text
docs/system/
  landscape.md
  repos.md
  diagrams.md
  glossary.md
  adr/
docs/specs/<slug>/
  spec.md
```

Human starter copies for the landscape are `docs/system/_template/` (same files as this skill’s `assets/` for landscape, repos, diagrams, glossary, and ADRs). The slice file starts from the skill’s `assets/spec.md`.

**Done** and **partial** specs record the match status, what the dump says, the repo paths that support the slice, what was read from the code versus what was only in the dump, and open questions. Normal spec sections appear only where the dump or the code supports them. The command does not invent acceptance criteria to make a slice look buildable.

**Not in the code** stays thin: what the dump says, that the code does not have it, open questions, and an empty trace. More information can be added later, until planning. This command does not add it.

Code that no slice covers is a note on the landscape, not a guessed spec. ADRs are written only where there was a real choice.

## After Index

If you are done with this dump:

```text
/crav1-finalize-commit
```

That puts `docs/system/` and the new spec slugs in git. No push. This command does not commit for you.

`/crav1-plan-from-spec` is only for a slice you choose to start. A slice that is not in the code is not planned by this command.
