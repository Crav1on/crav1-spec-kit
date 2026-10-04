# Checks named on a task

Plan names the checks. It does not write test code. It does not invent product behavior. `/crav1-verify-spec` is the gate that says these named checks passed. Do not run that command from plan.

Each verify note names the kind, then the check or checks:

`(verify: <kind> — <named check>)`

A kind is one check or many, depending on what must be proved. Not one test per kind by default.

## Kinds

Always choose from these when they prove the task:

- **unit** — one piece, in process
- **system** — the whole path
- **browser** — someone uses the screen
- **integration** — the boundary where two parts meet (systems, services, or modules). Only when there is an edge. A system test is the whole path. An integration test is the boundary.

Name these only when the thing being built needs them:

- **contract** — two parts share a published API or message shape
- **load** or **speed** — only when the spec already says how fast or how big. Quote that limit. Do not invent a performance goal.
- **accessibility** — when someone uses the screen, named with the browser check. Do not add a browser check only to hold an accessibility check.
- **golden** or **property** — an algorithm with many inputs. That check is still a unit test.

## When the spec already requires them

- When the spec describes an algorithm, name several checks, including corner cases of the behavior the spec already states. That is part of the workflow, not optional. Do not invent a new rule to have a corner case.
- When the change touches behavior that already works, name regression tests that would fail if that old behavior broke. Do not invent old behavior.
- When two parts meet, name an integration test for that edge. Only when there is an edge.

## Kept security checks

Read `docs/system/security.md` when it exists, and a `## Security` section on the spec when it exists. Each kept finding has a Check line.

Map that check to a `T#`, or write “covered by T#” on the Trace row. A task that already proves the check is enough. Do not copy the check into acceptance criteria. Do not invent a product behavior the finding does not state. Do not run `/crav1-security-review`.

If the kept decision conflicts with a spec non-goal, stop and send it to `/crav1-tighten-spec`. Do not encode the conflict as a task.

## Stay out

Smoke after deploy, chaos, and fuzzing for its own sake stay out. A **property** check for an algorithm with many inputs stays; that is not fuzzing for its own sake.
