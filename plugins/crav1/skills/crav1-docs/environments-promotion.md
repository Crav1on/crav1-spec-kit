# Promotion lines

`docs/environments/promotion.md` says which branch deploys to which environment, so status can show how far merged work has got (since 1.69.0). It sits next to [marks.md](environments-marks.md) and uses the same four-field shape, the same environment words and the same append rules. Examples use made-up names.

## Line

```text
<repo> | <branch, pattern or tag <pattern>> | <environment>[ (after <environment>)] | <source>
orders-api | develop | dev | pipeline orders-cd, stage DeployDev
orders-api | develop | test | pipeline orders-cd, stage DeployTest
orders-api | main | prod | pipeline orders-cd, stage DeployProd
orders-api | release/* | prod | marked by the user
orders-api | tag v* | prod | marked by the user
orders-api | hotfix | sandbox (after dev) | marked by the user
```

- **Second field.** A branch (`develop`), a branch pattern (`release/*`, every matching branch on disk), or `tag <pattern>` for a repo that releases by tag.
- **Environment.** One of `dev`, `test`, `stage`, `uat`, `qa`, `pre-prod`, `prod` (`development` is `dev`). Any other word must say its place in the chain, `sandbox (after dev)`. Without `(after …)` the line is shown as Unclear and not used.
- **Source.** `pipeline <name>, stage <stage>` (proposed by `/crav1-map-pipeline-environments` from Azure DevOps definitions) or `marked by the user` (written by hand, for example for GitHub Actions).
- Lines are appended, never rewritten. Several lines for one environment are all kept; reaching any one counts. The file and `docs/environments/` are created only when the first line is confirmed.

## The chain

Per repo, environments are ordered dev < test < stage, uat, qa < pre-prod < prod, with an `(after X)` environment right after X: `develop → dev, test; main → prod`. There is no separate chain format.

## What status shows

`/crav1-help` status, `/crav1-verify-build-against-spec`, `/crav1-tasks-ready-to-build` and `/crav1-merge-pr` add a line after the Branches line:

`Promotion: on the branch that deploys to test (develop); not yet on the branch that deploys to prod (main).`

- **What it names.** The furthest environment reached, then each later environment not yet reached, and the chain: `Promotion: on the branch that deploys to test (develop); not yet on the branch that deploys to prod (main). (chain: dev → test → prod)`.
- **Branch reach, not deployment proof.** An environment is reached when the work is contained in a branch its line names (the same merged tests as done). The wording is never "deployed to".
- **Release branches.** `on release/2026.11 (deploys to prod)` names the newest matching branch that contains the work. A fix made on a release branch, `(into release/2026.11)`, shows `not back on develop` until it reaches the base branch.
- **Tags.** `in tag v2.3.0 (deploys to prod)` names the newest matching tag that contains the work; with none, `not yet tagged`.
- **Done stays merged.** Promotion never blocks done and never writes a spec line.

## Pipeline runs (optional)

When a pipeline-sourced line is behind the Promotion line, the report ends with **Also check the latest pipeline runs?** The choice word `pipeline runs` runs it without asking; a headless run without the word gives the git answer and `Pipeline runs not checked. Add the word: pipeline runs.` It reads the latest successful Azure DevOps run per pipeline, read-only, and says for example `Promotion (pipeline runs): test, DeployTest succeeded 2026-10-18 at 63e334b, which contains the work; prod, no successful DeployProd run contains the work.` Hand-written lines keep the branch-reach answer (`pipeline runs: Azure DevOps only`). With `az` signed out it says `az has no login` and keeps the git answer.
