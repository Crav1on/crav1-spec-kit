# Azure reader

`/crav1-environment-read` follows this reader when the user named Azure. It lists what Azure actually has. The skill’s Marks, marks.md, Evidence, Pre-prod, shared, and prod-only, Group suggestion, and Leftovers sections decide what is taken, skipped, shared, pre-prod, prod-only, or not read. One pass reads every non-prod environment. Production data is never read. A prod-only resource is shape and connections only after the one yes.

AWS follows [aws.md](aws.md). Google Cloud follows [google-cloud.md](google-cloud.md). Any other named host stops with no reader and does not use this file.

## Out of this reader

Do not read Azure DevOps, GitHub, or CI. Do not call `az repos`, `az pipelines`, `az boards`, `gh`, or a pipeline API. A project, a repo, a pipeline, or a board is not a resource this reader lists.

The user names the host, not the subscription. Do not ask which subscription is dev or test. Do not treat a subscription name as an environment mark.

This reader lists a database and a storage account. It does not open them. Schema and storage structure are a later step, in [sql.md](sql.md) and [storage.md](storage.md), and only when the user says yes. Do not list tables, columns, containers, prefixes, or blobs in this pass.

## CLI

If `az` is not on the path, stop. Say `az` is not installed. Point at `https://learn.microsoft.com/cli/azure/install-azure-cli`. Do not install it.

If `az` runs and `az account show` fails because there is no login, stop. Say `az` has no login. The login command is `az login`. Do not log in.

Do not invent a resource. Do not pretend the host is empty.

## Read-only

Use `az` only to list and show. Do not create, update, delete, deploy, start, stop, or set a resource. Do not print a secret, a key, a password, a connection string, or a payload. A hostname in a setting can be a connection. The secret value is not a fact.

Scan every subscription the login can already see. Do not skip a subscription because its name says production or dev. The mark is on the resource.

List every resource. Do not filter them out in the query. The marks in the skill decide what is taken, read for shape, skipped, or unread.

Allowed:

- `az account show` for the login check, and `az account list`
- `az resource list`
- `az resource show` for tags, for a connection field, for a private endpoint, VNet, or subnet id used as evidence, or for a trigger definition on a resource this reader is allowed to read
- `az eventgrid event-subscription list` for a resource this reader is allowed to read, including a subscription whose source is a storage account
- `az functionapp function list` and `az functionapp function show` for bindings on a function app this reader is allowed to read
- `az datafactory trigger list` and `az datafactory trigger show` for a factory this reader is allowed to read
- `az logic workflow show` for the trigger object only, on a workflow this reader is allowed to read. Do not list runs
- `az servicebus topic subscription list` and `az eventhubs eventhub consumer-group list` on a namespace this reader is allowed to read. Do not list messages or events. Do not list keys
- `az deployment group list` for a resource group the resource list already showed, and `az deployment operation group list` for the target resource id only. Do not print the request, the response, or outputs

If `az resource list` fails, stop. Say the Azure reader cannot list resources. If a deployment command fails, that evidence is absent. Do not stop the read for that.

## Mark

Look at the resource name, the resource group, and the tags. That look is the filter, together with `docs/environments/marks.md` and the evidence in the skill. Split name, group, tag key, and tag value on every character that is not a letter. Compare tokens without regard to case. Those words are the tokens.

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

Classification, disagreement, pre-prod, shared, prod-only, evidence, the group suggestion, and leftovers are in the skill. Follow those. Do not apply an older rule that a production token always wins across sources. A resource whose only mark is production is prod-only. It is not skipped until the user says no, or the read stops before the shape question.

If `az resource list` omits tags, `az resource show --ids` may be used to read the tags only. If those tags still have no mark, the resource is unmarked until evidence or the user marks it. Do not read further properties on that resource, except the private endpoint, VNet, or subnet id when testing connection evidence.

## What a taken resource shows

For a taken non-prod resource, the fact is the resource id, the type, the name, and the group, plus every mark source. Say `Seen in Azure dev.` or the environment the mark table names (`test`, `stage`, `uat`, `qa`). One resource can carry more than one of those sentences. Do not say the code shows it.

A pre-prod, shared, or prod-only resource is shown only after the user said yes. The fact is the name, the type, setting keys, routes the settings already show, timers, links, and secret names. A setting value is shown only when it is a resource id or a hostname. Say `Seen in Azure pre-prod.` or `Seen in Azure <environment>.` plus `shared with prod`. A prod-only line says `Seen in Azure prod.` plus `prod only`. Say `Shape and connections only.` Never data. Never secret values. Never row or blob contents. Do not open a database or a storage account for a prod-only resource. The list and the settings already shown are the shape.

A connection is a field on that resource that names another resource id or a hostname. Cite the resource id and the field. A similar name is not a connection. Do not invent one. Do not read a prod-only resource for a connection before the yes, except the connection fields the skill allows when testing whether production also connects to an unmarked resource.

A setting that holds a secret is not copied. Cite the secret name. Do not cite the secret value. A hostname or a resource id in a setting is a connection. Cite that, not the secret.

## Triggers

Triggers are connections. They appear in the Links section. Show the definition only: what starts the work, what it runs, and the schedule when it has one. Never a payload. Never a secret. List these when the resource is one this reader is allowed to read:

- Event Grid subscriptions, including a subscription on storage. Source, target endpoint, and included event types.
- Function triggers and bindings: blob, queue, timer, Service Bus, Event Hub, and HTTP. Binding type, direction, the queue, blob path, topic, or schedule, and the function.
- Data Factory triggers: schedule, tumbling window, and storage event. Trigger type, schedule, and pipeline.
- Logic App triggers. Trigger kind, recurrence or event source, and the workflow. Do not list runs.
- Service Bus consumers and Event Hub consumers. Subscription or consumer group, and the topic or hub. Do not list messages or events.
