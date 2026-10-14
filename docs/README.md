# CRAV1 Spec Kit docs

This is the index of every page in the kit's docs. Pick by what you want to do, or by who you are. The [README](../README.md) is the short landing page.

## Where next

| You want to | Go to |
| --- | --- |
| Install the kit | [Install](install.md) |
| Get going in fifteen minutes | [First 15 minutes](first-run.md) |
| Pick a way in | [The seven starter options](../README.md#the-seven-starter-options) |
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
- [From intake files to specs](from-intake.md)
- [From existing repos and a dump to specs](from-match.md)
- [From named repos to an architecture spec](from-repos.md)
- [From a named host](from-environment.md)
- [From a bug that already exists](from-fix-bug.md)

The core loop, after a starter:

- [From a draft spec to an accepted spec](from-draft-spec.md)
- [From a spec to a plan](from-spec-to-plan.md)
- [Build tasks](from-plan-to-build.md)
- [Verify and fix](from-verify.md)
- [From commit to merge](from-commit.md)

Once specs exist:

- [From new information to an existing spec](from-add.md)
- [From a later dump onto existing specs](from-match-dump.md)
- [From a code change onto existing specs](from-code.md)
- [From a meeting to specs](from-meeting.md)
- [Ask open questions](from-ask-open-questions.md)

Find your way:

- [Ask the kit for help](from-help.md): what to run next, in what order, and what a command does
- [Workflow routes](reference/workflow.md)
- [Tasks ready to build](from-tasks-ready-to-build.md): which tasks can be built now, and why the others cannot

Keep the picture current:

- [From the system notes](from-explain.md)
- [What's known about one thing](from-whats-known-about.md)
- [Keep the picture current](from-keep-current.md)
- [From Azure DevOps pipelines](from-pipeline-environments.md)
- [From a security review](from-security.md)

Testing and review:

- [From a built slice, exploratory test](from-exploratory-test.md)
- [From code that already exists, suggest tests](from-suggest-tests.md)
- [From a pull request review](from-review-pr.md)

Azure Boards:

- [Feature candidates](from-feature-candidates.md)
- [From specs to Azure Boards](from-specs-to-ado.md)
- [From tasks to Azure Boards](from-tasks-to-ado.md)
- [From Azure Boards to tasks](from-ado-to-tasks.md)
- [From Azure Boards to specs](from-ado-to-specs.md)

Install:

- [Installing and using the kit](install.md)
- [Cursor plugin quick start](../plugins/crav1/README.md)

### Reference

- [Skills reference](reference/skills.md). Every command and subagent, by lane, with one page each. Generated from [`skills.yaml`](reference/skills.yaml).
- [Guild routing](guild-routing.md). Which lane each command belongs to.
- [Environment marks](environments-marks.md). The line format of `docs/environments/marks.md`.
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
2. A starter walkthrough: [one sentence](from-nothing.md), [a pile of ideas](from-ideas.md), or [intake files](from-intake.md)
3. [From a draft spec to an accepted spec](from-draft-spec.md) and [Ask open questions](from-ask-open-questions.md)
4. [From new information to an existing spec](from-add.md), [From a meeting to specs](from-meeting.md), [From a later dump onto existing specs](from-match-dump.md)
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
