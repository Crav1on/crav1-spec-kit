# Worker status

Read only when `SKILL.md` says STATUS is not `done`, or the user says `skip-slug` or `stop`. Do not open this file when every worker returns `done`. The rules are unchanged.

| STATUS | Orchestrator |
| --- | --- |
| `needs_fix` | Ask `fix` / `skip-slug` / `stop`. `fix` → same `T#` worker `resume: fix`. |
| `needs_ready` | Ask them to refresh the live host, then `ready` / `skip-slug` / `stop`. `ready` → `resume: ready`. |
| `needs_dependency` | Show the BLOCKER line at the top. Ask start / skip / `skip-slug` / stop. `start` → `resume: dependency-start`; `skip` → `resume: dependency-skip`. Headless: two-pass questions file. |
| `blocked` / `failed` | Slug `blocked`. **End the board.** Do not start the next slug. |
| User `skip-slug` | Mark skipped. Switch to next slug (if any). |
| User `stop` | End the board. |

Do not skip a blocked slug unless they `skip-slug`.
