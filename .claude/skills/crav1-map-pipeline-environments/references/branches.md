# crav1-map-pipeline-environments: branches

Read only when the pointer in `SKILL.md` sends you here. Moved word for word from `SKILL.md` in 1.71.0; the rules are unchanged.

## promotion.md (1.69.0)

Path: `docs/environments/promotion.md`, next to marks.md. Same four-field shape, the same environment words, and the same append rules: `<repo> | <branch, pattern or tag <pattern>> | <environment>[ (after <environment>)] | pipeline <name>, stage <stage>`. Example: `orders-api | develop | test | pipeline orders-cd, stage DeployTest`. The branch facts come from the definitions only, as `references/azure-devops.md` says under **Branches**. Create the file (and `docs/environments/`) only when at least one line is confirmed. Never rewrite a line; already there means the same repo, branch field and environment word. This command proposes known environment words only; an `(after …)` position is written by hand. The format is in `docs/environments-promotion.md`.
