# Google Cloud reader

`/crav1-environment-read` follows this reader when the user named Google Cloud. GCP is Google Cloud. It lists what those projects actually have. The skill’s Marks, marks.md, Evidence, Pre-prod, shared, and prod-only, Group suggestion, and Leftovers sections decide what is taken, skipped, shared, pre-prod, prod-only, or not read. One pass reads every non-prod environment. Production data is never read. A prod-only resource is shape and connections only after the one yes.

Azure follows [azure.md](azure.md). AWS follows [aws.md](aws.md). Any other named host stops with no reader and does not use this file.

## Out of this reader

Do not read Azure DevOps, GitHub, or CI. Do not call `gh`, a GitHub API, `az`, `az repos`, `az pipelines`, `az boards`, or a pipeline API. A repo, a pipeline, or a board is not a resource this reader lists. Leave those out of the list. They do not stop the read.

The user names the host, not the project. Do not ask which project is dev or test. Do not treat a project id, name, or number as an environment mark.

This reader lists a database and a bucket. It does not open them. Schema and storage structure are a later step, in [sql.md](sql.md) and [storage.md](storage.md), and only when the user says yes. Do not list tables, columns, prefixes, or objects in this pass.

## CLI

If `gcloud` is not on the path, stop. Say `gcloud` is not installed. Point at `https://cloud.google.com/sdk/docs/install`. Do not install it.

If `gcloud` runs and `gcloud auth list` shows no active account, stop. Say `gcloud` has no login. The login command is `gcloud auth login`. Do not log in.

Do not invent a resource. Do not pretend the host is empty.

## Read-only

Use `gcloud` only to list and show. Scan every project `gcloud projects list` already returns. Do not skip a project because its name says production or dev. The mark is on the resource. Do not enable an API. Do not create a project.

Do not create, update, delete, deploy, start, stop, or set a resource. Do not print a secret, a key, a password, or a payload. A hostname in a setting can be a connection. The secret value is not a fact.

For each project, run `gcloud asset search-all-resources --scope=projects/PROJECT_ID --format=json`. Do not pass a query that filters on an environment word. Follow the next page token until it is absent. The marks in the skill decide what is taken, read for shape, skipped, or unread.

If the asset search cannot run for a project the list already returned, stop. Say the Google Cloud reader cannot read. Do not skip that project. Do not pretend it is empty.

Allowed:

- `gcloud auth list`
- `gcloud projects list`
- `gcloud asset search-all-resources` for each of those projects, with no environment query
- `gcloud resource-manager tags bindings list` for tags only, when that search omits labels and tags
- One `gcloud` describe of a resource this reader is allowed to read, and only for a field that names another resource id or a hostname, for a private endpoint, VPC, or subnet id used as evidence, or for an event trigger on a function this reader is allowed to read
- `gcloud pubsub subscriptions list` or describe, for a subscription this reader is allowed to read. Show the topic, the subscription, and the push endpoint. Do not show push authentication
- `gcloud scheduler jobs list` or describe, for a job this reader is allowed to read. Show the schedule and the target. Do not show a header that holds a secret
- `gcloud eventarc triggers list` or describe, for a trigger this reader is allowed to read. Show the event type, the source, and the destination
- `gcloud deployment-manager deployments list` and `gcloud deployment-manager resources list` for evidence. If the command fails or the API is disabled, that evidence is absent. Do not enable the API

There is no other read-only deployment-history equivalent this reader uses. Infrastructure Manager is not a second source.

## Mark

Look at the resource name and the tags. Google Cloud has no resource group on the resource. The group contributes no token. Do not invent a group from the project, the folder, the organization, the region, or the zone. The group suggestion in the skill does not apply.

The name is `displayName` when it is present, and the last segment of the full resource name. The tags are labels, tags, and network tags on that resource. Split name, tag key, and tag value on every character that is not a letter. Compare tokens without regard to case. Those words are the tokens. A marks line uses `-` in the group field.

| Tokens | Class | Environment on the Seen line |
| --- | --- | --- |
| `dev`, `development` | non-prod | dev |
| `test`, `testing` | non-prod | test |
| `stage`, `staging` | non-prod | stage |
| `uat` | non-prod | uat |
| `qa` | non-prod | qa |
| `preprod`, or the neighboring tokens `pre` then `prod` | pre-prod | pre-prod |
| `prod`, `production`, `live` | production | prod, when the resource is prod-only and the user said yes |

A token is the whole word. `device` is not `dev`. `protest`, `latest`, and `contest` are not `test`. `backstage` and `staged` are not `stage`. `equation` and `equator` are not `uat`. `qatar` and `equal` are not `qa`. `product` and `reproduce` are not `prod`. `preprod` is pre-prod. `pre-prod` and `pre_prod` are the neighboring tokens `pre` then `prod`, and that pair is pre-prod. The `prod` in the pair is not production. `pre-production` is production, because the whole word is `production`. `live` is production. `alive`, `lives`, `liveness`, `deliver`, `livestock`, and `livestream` are not `live`.

Classification, disagreement, pre-prod, shared, prod-only, evidence, and leftovers are in the skill. Follow those. Do not apply an older rule that a production token always wins across sources. A resource whose only mark is production is prod-only. It is not skipped until the user says no, or the read stops before the shape question.

If search omits labels and tags, `gcloud resource-manager tags bindings list --parent` may be used to read the tags only. If those tags still have no mark, the resource is unmarked until evidence or the user marks it. Do not read further properties on that resource, except the private endpoint, VPC, or subnet id when testing connection evidence.

## What a taken resource shows

For a taken non-prod resource, the fact is the resource id (the full resource name), the type, the name, and the group, plus every mark source. The group is none. Say `Seen in Google Cloud dev.` or the environment the mark table names (`test`, `stage`, `uat`, `qa`). One resource can carry more than one of those sentences. Do not say the code shows it.

A pre-prod, shared, or prod-only resource is shown only after the user said yes. The fact is the name, the type, setting keys, routes the settings already show, timers, links, and secret names. A setting value is shown only when it is a resource id or a hostname. Say `Seen in Google Cloud pre-prod.` or `Seen in Google Cloud <environment>.` plus `shared with prod`. A prod-only line says `Seen in Google Cloud prod.` plus `prod only`. Say `Shape and connections only.` Never data. Never secret values. Never row or blob contents. Do not open a database or a bucket for a prod-only resource. The list and the settings already shown are the shape.

A connection is a field on that resource that names another resource id or a hostname. Cite the resource id and the field. Read it from the asset record when that field is already there. A similar name is not a connection. Do not invent one. Do not read a prod-only resource for a connection before the yes, except the connection fields the skill allows when testing whether production also connects to an unmarked resource.

A setting that holds a secret is not copied. Cite the secret name. Do not cite the secret value. A hostname or a resource id in a setting is a connection. Cite that, not the secret.

## Triggers

Triggers are connections. They appear in the Links section. Show the definition only: what starts the work, what it runs, and the schedule when it has one. Never a payload. Never a secret. List these when the resource is one this reader is allowed to read:

- Pub/Sub subscriptions. The topic, the subscription, and the push endpoint when it has one.
- Cloud Scheduler jobs. The schedule and the target.
- Eventarc triggers. The event type, the source, and the destination.
- A function event trigger, when describe shows one. The event type and the resource it listens to. That is the function equivalent of a binding. Do not show the function’s environment variables.
