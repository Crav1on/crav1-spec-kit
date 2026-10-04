---
name: crav1-security-review
description: >-
  Ask whether the thing in front of you is secure, after architecture
  already exists (docs/system/ or a spec that already describes the design).
  Same command for the whole system, one existing spec, or the change in
  front of us. Findings are risks and what should change. One confirm, then
  write only the kept findings. Does not invent an architecture. Does not
  plan, implement, or commit. Not a mode of /crav1-architecture-reviewer.
disable-model-invocation: true
icon: lock
color: red
---

# Security review

You ask whether the thing in front of you is secure. You write only the findings they keep. You do not write application code. You do not plan, implement, or commit.

This is cross-cutting. It is not its own lane. It is not a mode of `/crav1-architecture-reviewer`. Architecture review critiques design hunches. This skill asks whether the thing in front of it is secure. Do not send this job to that command, and do not absorb its job.

Other skills do not run this one. Do not run it from spark, plan, or verify.

## When architecture is missing

Run only when architecture already exists: `docs/system/` describes the design, or a spec already describes the design. If that is missing, stop. Point at the skill that creates it. Do not invent an architecture. Do not seed `docs/system/`. Do not create a slug. Do not write `security.md` or a Security section to fill the gap.

A spec describes the design when `docs/specs/<slug>/spec.md` (skip `_template`) already states how the thing is shaped: users and journeys, constraints, decisions, diagrams, ADRs, or an approach the file already wrote. A file that is only a title, only open questions, or only a match status with no design, does not.

`docs/system/` describes the design when `landscape.md`, `diagrams.md`, or `adr/` already states what the system is. An empty folder, or a glossary alone, does not.

Point at one command when what they brought makes it obvious. Do not run it.

- One or two sentences, no design yet: `/crav1-spark-to-spec`
- A pile of ideas, no design yet: `/crav1-ideas-to-spec`
- Mixed files or several features, no design yet: `/crav1-intake-to-specs`
- Repos plus a dump, no design yet: `/crav1-match-to-specs`
- A spec folder exists and does not describe the design: `/crav1-add-to-spec` when they already have the information, otherwise spark or ideas for a new slug unless they said extend
- They picked the change, specs exist, and no spec describes that change: `/crav1-code-into-specs`

If they brought none of those, name the four commands that create the architecture (spark, ideas, intake, match) and stop.

## Target

Same command, three targets:

1. **The whole system** — only when `docs/system/` describes the design. Writes `docs/system/security.md`.
2. **One existing spec** — a `docs/specs/<slug>/` whose `spec.md` describes the design. Writes a Security section on that spec.
3. **The change in front of us** — a commit, a commit range, the diff of the current branch against the default branch, or uncommitted work, when that change is already in front of you. Writes a Security section on the spec that change belongs to.

Everything after `/crav1-security-review`, and every `@`, is the pointer.

If they named one real target, that is the target. Do not ask. If they named none and exactly one real target is in front of you, that target is the target. Do not ask.

A named target is one of these:

- The whole system, the landscape, or `@docs/system/` when that folder describes the design.
- One existing spec folder, or `@` of that folder or its `spec.md`, when that spec describes the design.
- The change, when they named a commit, a range, this branch, this diff, or the uncommitted work.

If the target is unclear, ask with options only. Use the questions tool when it is available. One option per real target already in front of you. No typed path. No typed slug. Stop until they pick.

Offer only targets that are real:

- **The whole system** — when `docs/system/` describes the design. Label it `docs/system/`.
- **One option per spec** that describes the design. Label it `docs/specs/<slug>/` and the title line of that `spec.md` when it has one. Skip `_template`. Skip a spec that does not describe the design.
- **The change in front of us** — one option, when a change is already in front of you: they named a commit or range, the current branch differs from the default branch, or the worktree has a diff. Label it with the branch name, the commit subject, or “uncommitted changes”. If that diff is empty and they named no change, do not offer it.

Default branch: the branch `origin/HEAD` points at, or `main` when that is the default you can see. Do not ask them to type a hash or a path.

When the target is the change and it belongs to one spec that describes the design, that spec is where the Security section goes. If it belongs to more than one such spec, ask with options only before findings. One option per spec the change actually touches. If it belongs to none, stop and point at `/crav1-code-into-specs` when spec folders exist, otherwise the command that creates the architecture. Do not invent a spec.

## Read

Read the target. Do not write files yet.

- **System:** `docs/system/` (`landscape.md`, `repos.md`, `diagrams.md`, `glossary.md`, `adr/`, and `security.md` when it exists) and the specs that describe trust, data, or attack surface of that system.
- **One spec:** that `spec.md`, plus `diagrams.md` and `adr/` in that folder when they exist.
- **Change:** the diff and its messages, plus the spec the change belongs to.

Look at trust, data, and attack surface. Look at code only where the code is a security decision: who is trusted, what data is stored or sent, or what is reachable, when the design or the change already shows that decision. Do not scan the repo for vulnerabilities. Do not invent an architecture from the code. A path the design does not mention stays out, unless this target is the change and that path is in the change and is itself a security decision.

## Findings (no writes yet)

Show the findings first. If the sources support no risk, say so. Do not invent a finding. Do not write a file. Do not ask for a confirm. Stop.

Otherwise each finding is three lines, then a check. Mark each **confirmed** or **inferred**.

- **Confirmed** — the design, the spec, or the code already shows it.
- **Inferred** — a connection you drew. The source did not state it. Not an accepted fact until they keep it.

Shape (one finding, one block). Number `S1`, `S2`, … Continue after the highest `S#` already in the file you would write.

```text
S1 — confirmed
What is wrong: <one line>
If it stays: <one line, what could happen>
Decision: <one line, the decision being asked>
Check: <one line a stranger could observe>
```

A check names a plain-language proof the risk is gone, for example: a stranger cannot call this without a login. Do not paste that example onto a finding it does not fit.

Findings are risks and what should change. The decision line is that change, as a decision, not a patch.

No exploit steps, no payloads, no attack procedures, no request samples, and no commands that would carry the risk out.

The check is a plain-language proof the risk is gone. Suggest only. Do not write test code. Do not run tests. Do not invent acceptance criteria, a plan, or tasks. Specify, plan, and build pick the checks up later. Do not add the check under Acceptance criteria. Do not write `plan.md`, `tasks.md`, or `verify.md`.

## One confirm

Stop. They keep the list, or they edit it. An edited list is the confirmation. Do not ask again. Do not write files before that reply.

A finding they struck is dropped. Do not write it. Wording they changed is the wording you write. A finding you never showed stays out.

## Write only the kept findings

Write in this chat. Do not launch a worker.

**System pass:** `docs/system/security.md`. File shape: this skill’s `assets/security.md` (same file as `docs/system/_template/security.md`; drop-in: `.claude/skills/crav1-security-review/assets/security.md`; plugin: this skill’s `assets/security.md`). When the file is missing, write that header, then the kept findings under `## Findings`. When the file exists, append kept findings that are not already there. Do not rewrite findings already in the file. Do not replace the file with the template.

**Feature or change:** a Security section on that spec. Section shape: this skill’s `assets/security-section.md` (drop-in: `.claude/skills/crav1-security-review/assets/security-section.md`; plugin: this skill’s `assets/security-section.md`). When `## Security` is missing, add that heading and its intro, then the kept findings. When it exists, append kept findings that are not already there. Do not rewrite other sections. Do not replace `spec.md` with the section file. Do not add Problem, Goals, Acceptance criteria, or tasks to fill the file out.

Each kept finding is written in the same four lines you showed, under `### S# — confirmed` or `### S# — inferred`. Keep their numbers.

A system pass writes only `docs/system/security.md`. A feature or a change writes only that spec’s Security section. Do not write the other file in the same pass.

If they drop every finding, write nothing.

Do not write `plan.md`, `tasks.md`, `diagrams.md`, `adr/`, `export/`, `verify.md`, `fix-log.md`, or `work-item.md`. Do not edit acceptance criteria. Do not commit.

## Stop

Do not plan. Do not implement. Do not commit. Do not run tests. Do not run `/crav1-plan-from-spec`, `/crav1-verify-spec`, `/crav1-tighten-spec`, or `/crav1-finalize-commit`.

Output only:

- Target (system, `docs/specs/<slug>/`, or the change and the spec it wrote)
- Kept findings, or that nothing was kept
- File written, or that nothing was written
- Next: `/crav1-finalize-commit` when a file changed (no push). When nothing was written, name no command. Do not run it.

## Style

Be concise. Prefer the smaller finding. Mark inferred as inferred. Do not fill gaps with an architecture you invented.
