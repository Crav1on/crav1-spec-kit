# From a later dump onto existing specs

Kit not in this project yet? [Install first](install.md). After a plugin install, the short command loop is [plugins/crav1/README.md](../plugins/crav1/README.md).

Use this when **specs already exist** under `docs/specs/` and there is a **new dump** (notes, tickets, old docs, diagrams, screenshots) to sort onto them.

Size is not a limit. One dump may be a lot about one slug, or it may cover many slugs.

[Match](from-match.md) creates the folders from repos plus a dump. [Add](from-add.md) takes information already aimed at one named spec. This command is the later dump. It does not replace [intake](from-intake.md), [a spark](from-nothing.md), or [a pile of ideas](from-ideas.md). It does not write application code.

A not-started spec (match status `not in the code`, or a thin spec) can keep taking information until planning. Adding information does not start planning and does not write `plan.md` or `tasks.md`.

## First prompt

New chat. Strong reasoning model. Not the host plan UI yet.

`@` the dump. Do not name a slug first. No required structure in the dump.

```text
/crav1-match-dump-to-specs
@notes/later-dump.md
@tickets/
@sketches/flow.png

The specs already exist. Sort this dump onto them.
Do not write code. Do not plan.
```

That slash command *is* the prompt.

## Steps

| Phase | You | Agent |
| --- | --- | --- |
| Specs | — | Reads `docs/specs/<slug>/` (skips `_template`). Does not ask for a slug. A hint in the dump that names a slug is evidence for the sort |
| Sort | Confirm or edit the three piles | Belongs to this spec, already in that spec, or does not fit any of them. Stops |
| Write | — | Quotes the new bits into the matching `spec.md` files. Labels what is new versus what was already there. Inferred stays inferred. Does not invent acceptance, architecture, or tasks |
| Impact | If other files are affected, pick apply or leave them alone | Reads `docs/system/` and the other specs. Lists each proposed edit in one line. Does not edit those files until apply |
| Stop | Glance, then `/crav1-finalize-commit` if a changed file should be in git | Does not plan, implement, or commit |

No spec folders under `docs/specs/` (other than `_template`): the command stops and points at spark, ideas, intake, or match. It does not create a slug.

The sort confirmation is the only stop before writing. Confirming the sort accepts the facts left on it. Facts that were not confirmed stay labeled inferred.

A hint about where something belongs is evidence. It is not a requirement. If the dump names a slug, that slug is used. If it does not, the sort matches by what the dump says.

Match status stays as it is unless the new information itself says the status changed.

Anything that fits none of the existing specs is listed and left alone. The command does not create a spec for that pile. If you say to create one, it points at spark, ideas, intake, or match. It does not write that folder.

## What gets written

The matching `docs/specs/<slug>/spec.md` files, for bits that were new.

`docs/system/` and other specs change only when apply is picked. Each of those edits was listed in one line (file and what would change). Leaving them alone writes nothing outside the specs that received new quotes.

No `plan.md`. No `tasks.md`. No application code. A missing `docs/system/` is not seeded here. A missing `glossary.md` is a gap fill only when `docs/system/` already exists. The does-not-fit pile is not a new spec folder.

## After

If a file changed and those edits should be in git:

```text
/crav1-finalize-commit
```

That puts the spec edits (and any applied edits) in git. No push. This command does not commit for you.

`/crav1-plan-from-spec` is only for a slice you choose to start. This command does not run it.
