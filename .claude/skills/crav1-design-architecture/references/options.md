# How options are shown

Each option, same order every time, short:

```text
B  Retry queue owned by orders-api (Recommended)
   What changes: orders-api publishes a failed payment to a retry queue; a worker in
   orders-api retries with backoff. New: one queue, one worker. Diagram: one new box.
   Environments: can run in test first; prod keeps inline retry until stage 2.
   Cost: medium build (about 3-4 tasks), small run cost, one more thing to watch.
   Risks: a retry storm if payments is down; needs a dead-letter path.
   Fits drivers: checkout does not wait (yes), one team runs it (yes), try in test first (yes).
   Reverses: nothing accepted.
   Why: the only option that keeps checkout fast without a new team owning code,
   and it can be tried in test on the existing hosting.
```

- **What changes**: components, flows, data, hosting or environment impact, and which kit files would change at go-ahead.
- **Environments**: how dev, test and prod would differ and whether it fits current infrastructure. Leave it out only when the decision has no environment or hosting effect.
- **Cost**: build size in plain words with a task guess, run cost, people and operations burden. No invented numbers; an unknown cost says `unknown` and can become a `to-question`.
- **Risks**: what can go wrong and what the design bets on.
- **Fits drivers**: one word per driver: yes, partly, no.
- **Reverses**: any accepted ADR, constraint, approval item or current environment fact it would undo.

When 3 or more options are wide, print a short option by driver table in the same reply.

## The user's own ideas

- An idea becomes its own option, **Your idea**, in the same shape and scored on the same drivers.
- If it is better, it becomes the recommendation and the reason says so. If weaker, say on which drivers and why; it stays selectable as `choose-mine`.
- A hybrid gets its own row only when the parts really fit.
- An idea that is a requirement is routed to `/crav1-add-to-spec`. An idea for a different decision is parked on that decision.

## The decision card

Card: Which option settles this decision?
- **Option B (Recommended)** (`choose-b`): settle with option B and write its draft ADR in the design folder. Why: it fits the most drivers.
- **Option A** (`choose-a`): settle with option A and write its draft ADR in the design folder.
- **Your idea** (`choose-mine`): settle with your own option and write its draft ADR in the design folder.
- **Keep talking** (`discuss`): talk this decision through; nothing outside the design folder changes.
- **Add my idea** (`add-my-idea`): add your own option and score it on the same drivers.
- **Ask me first** (`ask-me`): answer up to three short questions, then see the options again.
- **Ask a person** (`to-question`): write an open question in the design folder naming who has the fact or decides.
- **Needs research** (`to-research`): write an open question in the design folder and name the research step.
- **Skip for now** (`skip-for-now`): move on; this decision stays open in the design.

Show `choose-c` when there is a third option. Order the options so the recommended one is first.
