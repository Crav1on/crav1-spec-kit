# AWS reader

`/crav1-environment-read` follows this reader when the user named AWS. Amazon Web Services is AWS. It lists what that account actually has. The skill’s Marks, marks.md, Evidence, Pre-prod, shared, and prod-only, Group suggestion, and Leftovers sections decide what is taken, skipped, shared, pre-prod, prod-only, or not read. One pass reads every non-prod environment. Production data is never read. A prod-only resource is shape and connections only after the one yes.

Azure follows [azure.md](azure.md). Google Cloud follows [google-cloud.md](google-cloud.md). Any other named host stops with no reader and does not use this file.

## Out of this reader

Do not read Azure DevOps, GitHub, or CI. Do not call `gh`, a GitHub API, `az`, `az repos`, `az pipelines`, `az boards`, or a pipeline API. A repo, a pipeline, or a board is not a resource this reader lists. Leave those out of the list. They do not stop the read.

The user names the host, not the account. Do not ask which account is dev or test. Do not treat an account id, alias, or name as an environment mark.

This reader lists a database and a bucket. It does not open them. Schema and storage structure are a later step, in [sql.md](sql.md) and [storage.md](storage.md), and only when the user says yes. Do not list tables, columns, prefixes, or objects in this pass.

## CLI

If `aws` is not on the path, stop. Say `aws` is not installed. Point at `https://docs.aws.amazon.com/cli/latest/userguide/getting-started-install.html`. Do not install it.

If `aws` runs and `aws sts get-caller-identity` fails because there is no login, stop. Say `aws` has no login. The login command is `aws sso login` or `aws configure`. Do not log in.

Do not invent a resource. Do not pretend the host is empty.

## Read-only

Use `aws` only to list and show. The account is the one `aws sts get-caller-identity` already returns. Do not assume a role. Do not switch profile. Do not call `aws organizations` to open another account.

Do not create, update, delete, deploy, start, stop, or set a resource. Do not create an index or a view. Do not print a secret, a key, a password, or a payload. A hostname in a setting can be a connection. The secret value is not a fact.

A region with no index is not a failure. Search the aggregator view with query `*`. If the CLI rejects that, use an empty query string. Do not put an environment word in the query. Paginate until the next token is absent. The marks in the skill decide what is taken, read for shape, skipped, or unread.

If no aggregator view is already there, stop. Say the AWS reader cannot read the whole account. Do not treat one region as the whole account. Do not invent a resource.

Allowed:

- `aws sts get-caller-identity`
- `aws ec2 describe-regions` and `aws resource-explorer-2 list-indexes`, only to find an aggregator index the login already has
- `aws resource-explorer-2 list-views` and `aws resource-explorer-2 search` on that aggregator view
- `aws resource-groups list-groups` and `aws resource-groups list-group-resources`
- `aws resourcegroupstaggingapi get-resources` for tags, when search omits them
- `aws cloudcontrol get-resource` for a connection field, or a private endpoint, VPC, or subnet id used as evidence, on a resource the skill allows
- `aws events list-rules` and `aws events list-targets-by-rule` for an EventBridge rule this reader is allowed to read. Use the region on that rule. Show the pattern or schedule and the target. Do not show an input transformer secret
- `aws s3api get-bucket-notification-configuration` for a bucket this reader is allowed to read. Show the event type and the topic, queue, or function. Do not show a secret
- `aws lambda list-event-source-mappings` for a function this reader is allowed to read. Show the source, the function, and the state. Do not show a payload
- `aws cloudformation list-stacks` and `aws cloudformation list-stack-resources` for evidence. Use a stack that still exists. Do not describe parameters

If the resource search fails, stop. Say the AWS reader cannot list resources. If a CloudFormation command fails, that evidence is absent. Do not stop the read for that.

An empty group list means no resource has a group mark. If the resource groups list cannot be read, stop. Say the AWS reader cannot read. Do not assume the group is empty.

## Mark

Look at the resource name, the group, and the tags. That look is the filter, together with `docs/environments/marks.md` and the evidence in the skill. The name is the last segment of the ARN. The group is an AWS resource group the resource belongs to. The account and the region are not a group. The tags are the resource tags. Split name, group, tag key, and tag value on every character that is not a letter. Compare tokens without regard to case. Those words are the tokens.

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

If search omits tags, `aws resourcegroupstaggingapi get-resources` may be used to read the tags only. If those tags still have no mark, the resource is unmarked until evidence or the user marks it. Do not read further properties on that resource, except the private endpoint, VPC, or subnet id when testing connection evidence. On AWS the VNet is a VPC.

## What a taken resource shows

For a taken non-prod resource, the fact is the resource id (the ARN), the type, the name, and the group, plus every mark source. Say `Seen in AWS dev.` or the environment the mark table names (`test`, `stage`, `uat`, `qa`). One resource can carry more than one of those sentences. Do not say the code shows it.

A pre-prod, shared, or prod-only resource is shown only after the user said yes. The fact is the name, the type, setting keys, routes the settings already show, timers, links, and secret names. A setting value is shown only when it is a resource id or a hostname. Say `Seen in AWS pre-prod.` or `Seen in AWS <environment>.` plus `shared with prod`. A prod-only line says `Seen in AWS prod.` plus `prod only`. Say `Shape and connections only.` Never data. Never secret values. Never row or blob contents. Do not open a database or a bucket for a prod-only resource. The list and the settings already shown are the shape.

A connection is a field on that resource that names another resource id or a hostname. Cite the resource id and the field. A similar name is not a connection. Do not invent one. Do not read a prod-only resource for a connection before the yes, except the connection fields the skill allows when testing whether production also connects to an unmarked resource.

A setting that holds a secret is not copied. Cite the secret name. Do not cite the secret value. A hostname or a resource id in a setting is a connection. Cite that, not the secret.

## Triggers

Triggers are connections. They appear in the Links section. Show the definition only: what starts the work, what it runs, and the schedule when it has one. Never a payload. Never a secret. List these when the resource is one this reader is allowed to read:

- EventBridge rules. The event pattern or the schedule expression, and each target.
- S3 notifications. The event type, and the topic, queue, or function.
- Lambda event source mappings. The source, the function, and the state.

An EventBridge schedule expression is the schedule. Do not call a second scheduler API.
