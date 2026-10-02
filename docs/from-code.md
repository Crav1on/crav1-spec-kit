# From a code change onto existing specs

Kit not in this project yet? [Install first](install.md) (Cursor and Claude Code; the slash commands match, the files do not). After a Cursor plugin install, the short command loop is [plugins/crav1/README.md](../plugins/crav1/README.md). Claude Code has no plugin.

Use this when **specs already exist** under `docs/specs/` and a **code change already landed** without a spec, plan, or build.

The change is a commit, a commit range, or the diff of the current branch against the default branch. No dump is required.

[Match](from-match.md) creates the folders from repos plus a dump. [Match-dump](from-match-dump.md) sorts a later dump onto specs that already exist. [Add](from-add.md) takes information already aimed at one named spec. This command starts from the change. It does not replace [intake](from-intake.md), [a spark](from-nothing.md), or [a pile of ideas](from-ideas.md). It does not write application code. It does not watch the repo. It runs only when someone points it at a change.

A not-started spec (match status `not in the code`, or a thin spec) can keep taking information until planning. Adding what the change does does not start planning and does not write `plan.md` or `tasks.md`.

## First prompt

New chat. Strong reasoning model. Not the host plan UI yet.

Name the change when one is already known. Do not name a slug first. Do not paste a dump.

```text
/crav1-code-into-specs

The specs already exist. Sort this change onto them.
Do not write code. Do not plan.
```

That slash command *is* the prompt.

If the message names a commit, a commit range, or the branch diff, that is the change. If it does not, the command looks at git and asks with options only: recent commits, or the diff of the current branch against the default branch. It does not ask for a typed hash.

## Steps

| Phase | You | Agent |
| --- | --- | --- |
| Change | Named a commit, a range, or the branch diff, or pick from the options | Options only when the change was not named. Recent commits, or the branch diff. Does not ask for a typed hash |
| Specs | — | Reads `docs/specs/<slug>/` (skips `_template`). Does not ask for a slug |
| Sort | Confirm or edit the three piles | Belongs to this spec, already described there, or fits none of them. Stops |
| Write | — | Quotes what the change does into the matching `spec.md` files. Labels what is new versus what was already there. Inferred stays inferred. Does not invent acceptance, architecture, or tasks |
| Impact | If other files are affected, pick apply or leave them alone | Reads `docs/system/` and the other specs. Lists each proposed edit in one line. Does not edit those files until apply |
| Stop | Glance, then `/crav1-finalize-commit` only if those spec edits should be committed | Does not plan, implement, or commit |

No spec folders under `docs/specs/` (other than `_template`): the command stops and points at `/crav1-match-to-specs`. It does not invent a landscape from the diff. It does not create a slug.

The sort confirmation is the only stop before writing. Confirming the sort accepts the facts left on it. Facts that were not confirmed stay labeled inferred.

Match status stays as it is unless the change itself says the status changed.

Anything that fits none of the existing specs is listed and left alone. The command does not create a spec for that pile. If you say to create one, it points at spark, ideas, intake, or match. It does not write that folder.

## What gets written

The matching `docs/specs/<slug>/spec.md` files, for what the change does that was not already described there.

Other `docs/system/` files and other specs change only when apply is picked. Each of those edits was listed in one line (file and what would change). Leaving them alone writes nothing outside the specs that received new quotes, except the glossary gap below.

No `plan.md`. No `tasks.md`. No application code. A missing `docs/system/` is not seeded here. A missing `glossary.md` is a gap fill only when `docs/system/` already exists. When that file exists, only new rows are appended. Existing rows are not rewritten. A meaning the change does not state is `to be researched`. The pile that fits none of the specs is not a new spec folder.

## After

If a file changed and those edits should be in git:

```text
/crav1-finalize-commit
```

That puts the spec edits (and any applied edits) in git. No push. This command does not commit for you. It points at that command only when those spec edits should be committed.

`/crav1-plan-from-spec` is only for a slice you choose to start. This command does not run it.
