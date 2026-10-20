# CRAV1 Spec Kit docs

This is the index of every page in the kit's docs. Pick by what you want to do, or by who you are. The [README](../README.md) is the short landing page.

## Where next

| You want to | Go to |
| --- | --- |
| Install the kit | [Install](install.md) |
| Get going in fifteen minutes | [First 15 minutes](first-run.md) |
| Pick a way in | [The six starter options](../README.md#the-six-starter-options) |
| Go from a draft spec to a merged change | [The core loop](#how-to-walkthroughs): accept the spec, plan, build, verify, commit and merge |
| Do one thing step by step | [Walkthroughs](#how-to-walkthroughs) |
| Look up one command | [Skills reference](reference/skills.md) |
| Understand the method | [The method](concepts/method.md) |
| Know which file the kit writes | [Data layout](concepts/data-layout.md) |
| Route work to a lane | [Guild routing](guild-routing.md) |
| Change the kit itself | [Contributing](../CONTRIBUTING.md) |
| Report a problem | [Support](../SUPPORT.md) |

## By type

### Tutorial

- [First 15 minutes](first-run.md). Install, then one starter, then one task.

### How-to (walkthroughs)

Most walkthroughs share one outline: first prompt, steps, what gets written, and what to run after.

Starters:

- [From one sentence to a spec](from-nothing.md)
- [From a pile of ideas to a spec](from-ideas.md)
- [From intake files to specs](from-bundle-to-specs.md)
- [From existing repos and a dump to specs](from-existing-to-specs-with-bundle.md)
- [From named repos to an architecture spec](from-existing-to-specs-repos-only.md)
- [From a named host](from-read-environment.md)
- [From a bug that already exists](from-fix-bug.md)

The core loop, after a starter:

- [From a draft spec to an accepted spec](from-draft-spec.md)
- [From a spec to a plan](from-spec-to-plan.md)
- [Build tasks](from-plan-to-build.md)
- [Verify and fix](from-verify.md)
- [From commit to merge](from-commit.md)

Once specs exist:

- [From new information to an existing spec](from-add.md)
- [From a later dump onto existing specs](from-add-to-spec-dump.md)
- [From a code change onto existing specs](from-add-to-spec-code-change.md)
- [From a meeting to specs](from-add-to-spec-meeting.md)
- [Ask open questions](from-show-or-ask-open-questions.md)

Find your way:

- [Ask the kit for help](from-help.md): what to run next, in what order, and what a command does
- [Workflow routes](reference/workflow.md)
- [Tasks ready to build](from-tasks-ready-to-build.md): which tasks can be built now, and why the others cannot

Keep the picture current:

- [From the system notes](from-explain-existing-system.md)
- [Explain this code](from-explain-this-code.md): one file, function, selection, or PR diff, from reading the code
- [Retire, merge, park, or convert a spec](from-retire-spec.md): take one spec out of the work, or un-park it
- [What's known about one thing](from-what-do-we-know-about-this.md)
- [Keep the picture current](from-refresh-system-notes.md)
- [From Azure DevOps pipelines](from-map-pipeline-environments.md)
- [From a security review](from-review-security.md)

Testing and review:

- [From a built slice, exploratory test](from-run-exploratory-test.md)
- [From code that already exists, suggest tests](from-suggest-tests.md)
- [From a pull request review](from-review-pr.md)

Azure Boards:

- [Feature candidates](from-ado-sync-suggest-features.md)
- [From specs to Azure Boards](from-ado-sync-push-features.md)
- [From tasks to Azure Boards](from-ado-sync-push-tasks.md)
- [From Azure Boards to tasks](from-ado-sync-pull-tasks.md)
- [From Azure Boards to specs](from-ado-sync-pull-spec-changes.md)

Install:

- [Installing and using the kit](install.md)
- [Cursor plugin quick start](../plugins/crav1/README.md)

### Reference

- [Skills reference](reference/skills.md). Every command and subagent, by lane, with one page each. Generated from [`skills.yaml`](reference/skills.yaml).
- [Guild routing](guild-routing.md). Which lane each command belongs to.
- [Environment marks](environments-marks.md). The line format of `docs/environments/marks.md`.
- [Promotion lines](environments-promotion.md). The line format of `docs/environments/promotion.md` and the `Promotion:` status line (1.69.0).
- [Changelog](../CHANGELOG.md).

### Explanation

- [The method](concepts/method.md). How the pieces fit together, the starting points, the working loop, setup, best practices, and minimal templates.
- [Data layout](concepts/data-layout.md). Every folder and file the kit writes, who writes it, and the marks and spec sections it relies on.
- [Data policy](concepts/data-policy.md). Personal data and secrets in imported sources, and the once-per-repo transfer data policy.
- [Glossary](concepts/glossary.md). Words and abbreviations.

## By reader

### Spec writer

You turn ideas, meetings, and dumps into specs and keep them current.

1. [First 15 minutes](first-run.md)
2. A starter walkthrough: [one sentence](from-nothing.md), [a pile of ideas](from-ideas.md), or [intake files](from-bundle-to-specs.md)
3. [From a draft spec to an accepted spec](from-draft-spec.md) and [Ask open questions](from-show-or-ask-open-questions.md)
4. [From new information to an existing spec](from-add.md), [From a meeting to specs](from-add-to-spec-meeting.md), [From a later dump onto existing specs](from-add-to-spec-dump.md)
5. [Data layout](concepts/data-layout.md) and [Data policy](concepts/data-policy.md)
6. The Specify lane in the [skills reference](reference/skills.md#specify)

### Developer

You plan, build, verify, and ship one spec at a time.

1. [Install](install.md)
2. The working loop in [The method](concepts/method.md#the-working-loop-once-a-spec-exists)
3. [From a spec to a plan](from-spec-to-plan.md), [Build tasks](from-plan-to-build.md), [Verify and fix](from-verify.md), [From commit to merge](from-commit.md)
4. The Plan and Build lanes in the [skills reference](reference/skills.md#plan)
5. [From a pull request review](from-review-pr.md), [From a bug that already exists](from-fix-bug.md)

### Guild bot

You route kit work between agents.

1. [Guild routing](guild-routing.md)
2. [Skills reference](reference/skills.md), and its data file [`skills.yaml`](reference/skills.yaml)
3. [Data layout](concepts/data-layout.md)
4. [Glossary](concepts/glossary.md)

### Maintainer

You change the kit itself.

1. [Contributing](../CONTRIBUTING.md)
2. [Agent instructions for this repo](../AGENTS.md)
3. [`skills.yaml`](reference/skills.yaml) and the generator `scripts/gen-skill-docs.py`
4. [Changelog](../CHANGELOG.md)

## Renamed skills (1.56.0)

The old names were removed in 1.58.0 and no longer run. Use the new name, with the choice word where one is listed. `/crav1-help <old name>` answers with the new name.

| Old name | Now | Choice word to use |
| --- | --- | --- |
| `/crav1-implement-task` | [`/crav1-build-tasks`](reference/skills/crav1-build-tasks.md) | `one task` |
| `/crav1-complete-task` | [`/crav1-build-tasks`](reference/skills/crav1-build-tasks.md) | `one task` |
| `/crav1-complete-tasks` | [`/crav1-build-tasks`](reference/skills/crav1-build-tasks.md) | `range or all tasks` |
| `/crav1-complete-features` | [`/crav1-build-features`](reference/skills/crav1-build-features.md) | — |
| `/crav1-verify-spec` | [`/crav1-verify-build-against-spec`](reference/skills/crav1-verify-build-against-spec.md) | — |
| `/crav1-fix-from-verify` | [`/crav1-fix-build-gaps`](reference/skills/crav1-fix-build-gaps.md) | `verify gaps` |
| `/crav1-fix-live` | [`/crav1-fix-build-gaps`](reference/skills/crav1-fix-build-gaps.md) | `live gaps` |
| `/crav1-match-dump-to-specs` | [`/crav1-add-to-spec`](reference/skills/crav1-add-to-spec.md) | `dump` |
| `/crav1-code-into-specs` | [`/crav1-add-to-spec`](reference/skills/crav1-add-to-spec.md) | `code change` |
| `/crav1-meeting-to-specs` | [`/crav1-add-to-spec`](reference/skills/crav1-add-to-spec.md) | `meeting` |
| `/crav1-feature-candidates` | [`/crav1-ado-sync`](reference/skills/crav1-ado-sync.md) | `suggest features` |
| `/crav1-specs-to-ado` | [`/crav1-ado-sync`](reference/skills/crav1-ado-sync.md) | `push features` |
| `/crav1-tasks-to-ado` | [`/crav1-ado-sync`](reference/skills/crav1-ado-sync.md) | `push tasks` |
| `/crav1-ado-to-tasks` | [`/crav1-ado-sync`](reference/skills/crav1-ado-sync.md) | `pull tasks` |
| `/crav1-ado-to-specs` | [`/crav1-ado-sync`](reference/skills/crav1-ado-sync.md) | `pull spec changes` |
| `/crav1-match-to-specs` | [`/crav1-existing-to-specs`](reference/skills/crav1-existing-to-specs.md) | `repos and bundle` |
| `/crav1-repos-to-spec` | [`/crav1-existing-to-specs`](reference/skills/crav1-existing-to-specs.md) | `repos only, one spec` |
| `/crav1-intake-to-specs` | [`/crav1-bundle-to-specs`](reference/skills/crav1-bundle-to-specs.md) | — |
| `/crav1-architecture-reviewer` | [`/crav1-review-architecture`](reference/skills/crav1-review-architecture.md) | — |
| `/crav1-resolve-questions` | [`/crav1-resolve-open-questions`](reference/skills/crav1-resolve-open-questions.md) | — |
| `/crav1-ask-open-questions` | [`/crav1-show-or-ask-open-questions`](reference/skills/crav1-show-or-ask-open-questions.md) | `ask` |
| `/crav1-draft-commit-message` | [`/crav1-finalize-commit`](reference/skills/crav1-finalize-commit.md) | `message only` |
| `/crav1-explain` | [`/crav1-explain-existing-system`](reference/skills/crav1-explain-existing-system.md) | — |
| `/crav1-whats-known-about` | [`/crav1-what-do-we-know-about-this`](reference/skills/crav1-what-do-we-know-about-this.md) | — |
| `/crav1-keep-current` | [`/crav1-refresh-system-notes`](reference/skills/crav1-refresh-system-notes.md) | — |
| `/crav1-pipeline-environments` | [`/crav1-map-pipeline-environments`](reference/skills/crav1-map-pipeline-environments.md) | — |
| `/crav1-security-review` | [`/crav1-review-security`](reference/skills/crav1-review-security.md) | — |
| `/crav1-environment-read` | [`/crav1-read-environment`](reference/skills/crav1-read-environment.md) | — |
| `/crav1-exploratory-test` | [`/crav1-run-exploratory-test`](reference/skills/crav1-run-exploratory-test.md) | — |
| `/crav1-feature-branch` | [`/crav1-create-feature-branch`](reference/skills/crav1-create-feature-branch.md) | — |
