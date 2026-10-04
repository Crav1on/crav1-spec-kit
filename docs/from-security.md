# From a security review

Kit not in this project yet? [Install first](install.md) (Cursor and Claude Code; the slash commands match, the files do not). After a Cursor plugin install, the short command loop is [plugins/crav1/README.md](../plugins/crav1/README.md). Claude Code has no plugin.

Use this when **architecture already exists** and you want to know whether the thing in front of you is secure.

Architecture is `docs/system/` when that folder already describes the design, or a spec that already describes the design. This command does not invent an architecture. [Spark](from-nothing.md), [ideas](from-ideas.md), [intake](from-intake.md), and [match](from-match.md) create that design. This command does not replace them.

This is not `/crav1-architecture-reviewer`. Architecture review critiques design hunches. This command asks whether the thing in front of it is secure. It is cross-cutting. It is not its own lane. Spark, plan, and verify do not run it.

Same command, three targets: the whole system, one existing spec, or the change in front of you.

## First prompt

New chat. Strong reasoning model. Not the host plan UI yet.

Name the target when one is already known.

Whole system:

```text
/crav1-security-review
@docs/system/

Review the whole system. Do not write code. Do not plan.
```

One spec:

```text
/crav1-security-review
@docs/specs/<slug>/

Review this spec. Do not write code. Do not plan.
```

The change in front of you:

```text
/crav1-security-review

Review the change on this branch. Do not write code. Do not plan.
```

That slash command *is* the prompt.

If the message does not name a target, and more than one real target is in front of the command, it asks with options only. One option per real target: the whole system when `docs/system/` describes the design, one option per spec that describes the design, and the change when a change is already in front of you. It does not ask for a typed path.

## Steps

| Phase | You | Agent |
| --- | --- | --- |
| Architecture | — | Stops when `docs/system/` and every spec are missing a design. Points at the command that creates it. Does not invent an architecture |
| Target | Named the system, one spec, or the change, or pick from the options | Options only when the target was not named. One option per real target. No typed path |
| Findings | Read the list | Trust, data, attack surface, and code only where the code is a security decision. Each finding is three lines: what is wrong, what could happen if it stays, and the decision being asked. Marked confirmed or inferred. A plain-language check is a suggestion |
| Confirm | Keep the list, or edit it | One confirm. An edited list is the confirmation. Does not ask again. Does not write before that reply |
| Write | — | Kept findings only. `docs/system/security.md` for a system pass. A Security section on that spec for a feature or a change |
| Stop | Glance, then `/crav1-finalize-commit` if a file changed | Does not plan, implement, or commit. Names that command only. Does not run it |

No design in front of the command: it stops and points at spark, ideas, intake, or match.

Findings are risks and what should change. No exploit steps, no payloads, no attack procedures. The check is a suggestion (for example, a stranger cannot call this without a login). The command does not write test code, run tests, or invent acceptance criteria, a plan, or tasks. Specify, plan, and build pick the checks up later.

## What gets written

A system pass writes `docs/system/security.md`. Starter: [docs/system/_template/security.md](system/_template/security.md).

A feature or a change writes a `## Security` section on that spec. Other sections stay as they are.

Dropped findings are not written. An empty review writes nothing.

No `plan.md`. No `tasks.md`. No acceptance criteria. No application code. A missing `docs/system/` is not seeded here. A missing spec is not created here.

## After

If a file changed:

```text
/crav1-finalize-commit
```

That puts the security notes in git. No push. This command does not commit for you. It does not run plan, implement, or verify.
