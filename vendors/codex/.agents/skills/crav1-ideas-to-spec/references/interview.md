# crav1-ideas-to-spec: interview

Read only when the pointer in `SKILL.md` sends you here. Moved word for word from `SKILL.md` in 1.71.0; the rules are unchanged.

## Architecture interview (still no spec files)

Ask **at most 7** technical questions. Prefer options, not essays. Cover only what the bundle actually implies:

- System boundary: what is in-process vs external
- Data: source of truth, ownership, retention
- Control flow: sync vs async, who waits
- Auth/trust: who is allowed to do the risky thing
- Failure: timeout, retry, idempotency, what the user sees
- Constraints they already stated (language, cloud, offline, existing repo)
- What must **not** change if a codebase exists

Then offer **2–3 architecture options** at the same abstraction level (not “use Redis vs not” mixed with “monolith vs 12 microservices”). For each: one-line shape, one good, one bad.

Do **not** pick a winner unless they already did. List which hunches would become ADRs vs which are implementation details (those stay out of requirements).

Stop again.
