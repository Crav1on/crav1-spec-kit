# Fixed checks (1.95.0)

Every review, pull request or `branch`, runs every check below and shows one line per check, in this order, even when it is clean. A check that cannot apply says `n/a` and why in a few words. Findings from a check still go in their usual section (first section, suggestions, bugs, tests, questions); the line here names them by id. Anything else you notice comes after, as today.

Format: `<check>: ok`, `<check>: <ids>` (for example `B1, Q2`), or `<check>: n/a (<reason>)`.

1. **Spec and plan match.** Each change maps to the spec's acceptance and the plan's tasks; code the plan did not name is a first-section finding.
2. **Tests.** Each changed behavior has a test, or a test to add is listed.
3. **Secrets.** No secret in the diff (first section, decision **fix**).
4. **Infrastructure access per environment.** For each environment the change deploys to (TEST, PROD and any other the repo names), the identities, roles, Key Vault or other access the code needs exist in that environment's infrastructure code. A gap in one environment is a question or a bug.
5. **Environment parity.** Settings, packages and smoke checks that differ between environments are deliberate; an unexplained difference is a question.
6. **Spec wording a bug touches.** When a bug or fix contradicts or changes what the spec, its research or its notes say, name the line and suggest the wording fix (lane: Specify).
7. **Merge order.** Against the other open or unmerged branches the spec names (Match `Branch:` lines, task `(branch: …)` parts, `Synced at`) and the base: whether any touches the same files, and whether one must merge first. Read-only git on the refs on disk; a remote not fetched says so.
