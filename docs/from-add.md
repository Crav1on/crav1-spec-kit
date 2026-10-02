# From new information to an existing spec

Kit not in this project yet? [Install first](install.md). After a plugin install, the short command loop is [plugins/crav1/README.md](../plugins/crav1/README.md).

Use this when **one spec already exists** and there is **new information** for that spec.

`/crav1-tighten-spec` stays for mushy wording. This command is for new information. [Match](from-match.md) creates the folders. This command updates one that already exists. It does not replace [intake](from-intake.md), [a spark](from-nothing.md), or [a pile of ideas](from-ideas.md). It does not write application code.

A not-started spec (match status `not in the code`, or a thin spec) can keep taking information until planning. Adding information does not start planning and does not write `plan.md` or `tasks.md`.

## First prompt

New chat. Strong reasoning model. Not the host plan UI yet.

Name the spec when one folder is the target. Paste the new information in the same message.

```text
/crav1-add-to-spec
@docs/specs/<slug>/

<the new information, in your words>

Add this to that spec. Do not write code. Do not plan.
```

That slash command *is* the prompt.

## Steps

| Phase | You | Agent |
| --- | --- | --- |
| Target | Named one `docs/specs/<slug>/`, or pick from the options | Options only when the target was not named, or more than one existing spec could fit. One option per spec folder. Does not ask for a typed slug. Does not create a slug |
| Add | — | Quotes the new information in that `spec.md`. Labels what is new versus what was already there. Inferred stays inferred. Does not invent acceptance, architecture, or tasks |
| Impact | If other files are affected, pick apply or leave them alone | Reads `docs/system/` and the other specs. Lists each proposed edit in one line. Does not edit those files until apply |
| Stop | Glance, then `/crav1-finalize-commit` if a changed file should be in git | Does not plan, implement, or commit |

No spec folders under `docs/specs/` (other than `_template`): the command stops and points at spark, ideas, intake, or match.

Match status stays as it is unless the new information itself says the status changed.

## What gets written

The target `docs/specs/<slug>/spec.md`, unless the new words were already there.

`docs/system/` and other specs change only when apply is picked. Each of those edits was listed in one line (file and what would change). Leaving them alone writes nothing outside the target spec.

No `plan.md`. No `tasks.md`. No application code. A missing `docs/system/` is not seeded here. This command does not create `glossary.md`. When that file already exists, a missing row that the new information defines can be one of the listed edits.

## After

If a file changed:

```text
/crav1-finalize-commit
```

That puts the spec (and any applied edits) in git. No push. This command does not commit for you.

`/crav1-plan-from-spec` is only when you say you want to start planning this slug. This command does not run it.
