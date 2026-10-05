# Environment marks

`/crav1-environment-read` reads `docs/environments/marks.md` in the project repo after the resource name, the group, and the tags. It creates that folder and file only when the user has confirmed at least one mark. It appends those lines. It never rewrites an existing line.

`/crav1-pipeline-environments` appends a confirmed pipeline line to that same file. The walkthrough is [from-pipeline-environments.md](from-pipeline-environments.md). `/crav1-environment-read` does not run that command. It uses a pipeline line that is already there.

## Line

Four fields, separated by ` | ` (space, pipe, space). The source is everything after the third separator.

```text
<resource-id-or-name> | <group> | <environment> | <source>
```

- The first field is the resource id or the resource name. An id is the Azure resource id, the AWS ARN, or the full Google Cloud resource name.
- The second field is the group. Use `-` when the host has no group. Google Cloud uses `-`.
- The third field is one environment word: `dev`, `development`, `test`, `testing`, `stage`, `staging`, `uat`, `qa`, `pre-prod`, `preprod`, `prod`, `production`, or `live`.
- The source is one of:
  - `pipeline <name>, stage <stage>`
  - `marked by the user`
  - `marked by the user, suggested by group`

There is no `shared` word. A resource that a non-prod stage and a production stage both deploy is two lines, one per stage. `/crav1-environment-read` treats those two lines as shared with prod. A pipeline line names the resource the step names. The group on that line is context. The line does not mark every resource in the group.

A blank line is ignored. A line that starts with `#` is ignored.

```text
/subscriptions/00000000-0000-0000-0000-000000000000/resourceGroups/rg-app/providers/Microsoft.Web/sites/app-api | rg-app | dev | pipeline web, stage Dev
app-api | rg-app | test | marked by the user
app-db | rg-app | dev | marked by the user, suggested by group
arn:aws:lambda:eu-west-1:123456789012:function:orders | app-group | stage | pipeline orders, stage Staging
//pubsub.googleapis.com/projects/demo/topics/orders | - | uat | marked by the user
```

The read matches an id, or a name plus group. A similar name does not match. Compare without regard to case. If a name and group match more than one resource, that line is not used.

`development` is dev, `testing` is test, and `staging` is stage. `pre-prod` and `preprod` are pre-prod. `production` and `live` are production. A line that says production, and another source that says a non-prod environment, makes the resource shared with prod. A production line with no non-prod or pre-prod source makes the resource prod-only. `/crav1-environment-read` can read that resource for shape and connections only, after one yes. A no leaves it skipped.

## Who writes a line

This file is the only file `/crav1-environment-read` writes.

- The user accepts a group suggestion: `marked by the user, suggested by group`.
- The user marks a leftover, per resource or per group: `marked by the user`.
- `/crav1-pipeline-environments` after the user confirms a stage: `pipeline <name>, stage <stage>`. One line per stage. This read does not write that line. It uses one that is already there.

A mark from a connection, a deployment name, or infrastructure code is cited on the Seen line. It is not copied into this file.
