# From a code change onto existing specs

Kit not in this project yet? [Install first](install.md) (Cursor and Claude Code; the slash commands match, the files do not). After a Cursor plugin install, the short command loop is [plugins/crav1/README.md](../plugins/crav1/README.md). Claude Code has no plugin.

Use this when **specs already exist** under `docs/specs/` and a **code change already landed** without a spec, plan, or build.

The change is a commit, a commit range, or the diff of the current branch against the default branch. No dump is required.

[Match](from-existing-to-specs-with-bundle.md) creates the folders from repos plus a dump. [Match-dump](from-add-to-spec-dump.md) sorts a later dump onto specs that already exist. [Add](from-add.md) takes information already aimed at one named spec. This command starts from the change. It does not replace [intake](from-bundle-to-specs.md), [a spark](from-nothing.md), or [a pile of ideas](from-ideas.md). It is not [from the repos](from-existing-to-specs-repos-only.md) (`/crav1-existing-to-specs`), which reads the repos the user named and writes one architecture spec. It does not write application code. It does not watch the repo. It runs only when someone points it at a change.

A not-started spec (match status `not in the code`, or a thin spec) can keep taking information until planning. Adding what the change does does not start planning and does not write `plan.md` or `tasks.md`.

## First prompt

New chat. Strong reasoning model. Not the host plan UI yet.

Name the change when one is already known. Do not name a slug first. Do not paste a dump.

```text
/crav1-add-to-spec

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

No spec folders under `docs/specs/` (other than `_template`): the command stops and points at `/crav1-existing-to-specs`. It does not invent a landscape from the diff. It does not create a slug.

The sort confirmation is the only stop before writing. Confirming the sort accepts the facts left on it. Facts that were not confirmed stay labeled inferred.

Match status stays as it is unless the change itself says the status changed.

Anything that fits none of the existing specs is listed and left alone. The command does not create a spec for that pile. If you say to create one, it points at spark, ideas, intake, or match. It does not write that folder.

## What gets written

The matching `docs/specs/<slug>/spec.md` files, for what the change does that was not already described there.

Other `docs/system/` files and other specs change only when apply is picked. Each of those edits was listed in one line (file and what would change). Leaving them alone writes nothing outside the specs that received new quotes, except the glossary gap below.

No `plan.md`. No `tasks.md`. No application code. A missing `docs/system/` is not seeded here. A missing `glossary.md` is a gap fill only when `docs/system/` already exists. When that file exists, only new rows are appended. Existing rows are not rewritten. A meaning the change does not state is `to be researched`. When `docs/system/` already exists, that same pass adds what is new to the short description, the diagram, and how the parts connect. It does not rewrite what is already there. A whole-repo read sets that repo's `Synced at` cell. A one-slice read writes `Synced at: <repo> <branch>@<short sha>, <date>` on that slice's `spec.md` and does not touch the column. That stamp is not an apply option. The pile that fits none of the specs is not a new spec folder.

## One spec, several branches (1.64.0)

The work for one spec often sits on several branches, and sometimes in another repo. In this example the specs live in `orders-specs`, the code in the sibling checkout `../orders-api`, whose default branch is `main` but whose work merges into `develop`. Three branches carry the `orders` spec: `feature/orders-openapi` (1 commit), `feat/orders-retry` (2) and `feature/orders-export` (3).

```text
/crav1-add-to-spec code change orders-api feature/orders-openapi
```

- **Which checkout.** `orders-api` is read from `../orders-api`, read-only. When it isn't there, the kit asks for the path (options only). A headless run stops with `No checkout found for orders-api. Name its path.`
- **Fork point.** The branch diff starts where the branch split off, not at `main`: `Branch diff of feature/orders-openapi from develop (split at 00344be): 1 commit.` Measured from `main` it would be every commit on develop too. The report shows the age of each remote copy it read; nothing is fetched.
- **Branch list (1.67.1).** A one-slice read of a work branch also adds it to the spec's Match `Branch:` list, for example `- Branch: orders-api feat/orders-retry; orders-api feature/orders-openapi`. Base branches are never added, and existing entries and their markers stay.
- **Merges into.** Because the parent is `develop`, not the default branch, the kit asks once: `Work in orders-api merges into develop. Record that in repos.md?` A yes writes `develop` in the `Merges into` column. A headless run doesn't ask and writes nothing.
- **Synced at.** The spec's line gains one entry per branch: `Synced at: orders-api feature/orders-openapi@85d4561, 2026-10-19; feat/orders-retry@155b5c4, 2026-10-19`. A new read of a branch replaces only that entry.
- **No double import.** The note lists the commits it imported: `commits: [85d4561]`. Running the same branch again says `already imported`. A rebased or cherry-picked copy of an imported commit is `same change as <sha> in <note>` (matched by `git patch-id`). Only new commits are imported. When the branch was force-pushed since the last read, the run says `branch rewritten since last read` and carries on. A squash merge is recognised only through a merged PR on GitHub (`gh`) or Azure DevOps (`az`); anywhere else it is listed as `may already be in <note>` for you to keep or drop.
- **One note, several specs.** When the change feeds two specs, one note serves both (`used_by` lists both).

`/crav1-tighten-spec`, `/crav1-plan-from-spec`, `/crav1-help status`, `/crav1-tasks-ready-to-build`, `/crav1-verify-build-against-spec`, `/crav1-open-pr` and `/crav1-merge-pr` then read all three branches. The other skills that write a slice `Synced at` line (`/crav1-spark-to-spec`, `/crav1-ideas-to-spec`, `/crav1-bundle-to-specs`, `/crav1-refresh-system-notes`) keep the other branches' entries too, and `/crav1-existing-to-specs` templates carry the `Merges into` column.

## From a pull request (1.65.0)

A code change can be a pull request: `/crav1-add-to-spec code change orders-api PR 71`, or its URL. The change is its commits, read from the code repo's checkout. The pull request's title and description are saved as the PR note (`docs/notes/YYYY-MM/YYYY-MM-DD-pr-orders-api-71.md`, by its created date, `kind: pull request`), or reused when it exists, after the personal-data and secrets check. The code-change note links it with `pr_note:`, and a spec point taken from the description gets `Full source:` with the PR note's path.

Given a branch instead, it also writes the PR note when a signed-in `gh` or `az` host shows exactly one pull request for that branch. Otherwise it writes none and says why in one line, for example `no PR note: 2 PRs for feat/orders-retry; name one as PR <n>`. It never asks, and never stops because of it.

## After

If a file changed and those edits should be in git:

```text
/crav1-finalize-commit
```

That puts the spec edits (and any applied edits) in git. No push. This command does not commit for you. It points at that command only when those spec edits should be committed.

`/crav1-plan-from-spec` is only for a slice you choose to start. This command does not run it.

Reference page: [add-to-spec](reference/skills/crav1-add-to-spec.md)
