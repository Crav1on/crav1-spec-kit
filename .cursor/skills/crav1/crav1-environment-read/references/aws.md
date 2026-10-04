# AWS reader

`/crav1-environment-read` follows this reader when the user named AWS and an environment of dev or test. Amazon Web Services is AWS. It lists only what that named environment actually has.

Azure follows [azure.md](azure.md). Google Cloud follows [google-cloud.md](google-cloud.md). Any other named host stops with no reader and does not use this file.

## Out of this reader

Do not read Azure DevOps, GitHub, or CI. Do not call `gh`, a GitHub API, `az`, `az repos`, `az pipelines`, `az boards`, or a pipeline API. A repo, a pipeline, or a board is not a resource this reader lists. Leave those out of the list. They do not stop the read.

The user names the environment, not the account. Do not ask which account is dev or test. Do not treat an account id, alias, or name as an environment mark.

## Read-only

Use `aws` only to list and show. If `aws` is missing, or the login is not present, stop. Say the AWS reader cannot read. Do not invent a resource. Do not pretend the environment is empty.

The account is the one `aws sts get-caller-identity` already returns. Do not assume a role. Do not switch profile. Do not call `aws organizations` to open another account.

Allowed:

- `aws sts get-caller-identity`
- `aws ec2 describe-regions` and `aws resource-explorer-2 list-indexes`, only to find an aggregator index the login already has
- `aws resource-explorer-2 list-views` and `aws resource-explorer-2 search` on that aggregator view
- `aws resource-groups list-groups` and `aws resource-groups list-group-resources`
- `aws resourcegroupstaggingapi get-resources` for tags, when search omits them
- `aws cloudcontrol get-resource` for a field on a resource this reader already took

Do not create, update, delete, deploy, start, stop, or set a resource. Do not create an index or a view. Do not print a secret, a key, or a password. A hostname in a setting can be a connection. The secret value is not a fact.

A region with no index is not a failure. Search the aggregator view with query `*`. If the CLI rejects that, use an empty query string. Do not put dev, test, or production in the query. Paginate until the next token is absent. The marks below decide what is taken, skipped, or unread.

If no aggregator view is already there, stop. Say the AWS reader cannot read the whole account. Do not treat one region as the whole account. Do not invent a resource.

## Mark

Look at the resource name, the group, and the tags. That look is the filter. The name is the last segment of the ARN. The group is an AWS resource group the resource belongs to. The tags are the resource tags. Split name, group, tag key, and tag value on every character that is not a letter. Those words are the tokens.

| Named environment | Tokens that say it |
| --- | --- |
| dev | `dev`, `development` |
| test | `test`, `testing` |
| production | `prod`, `production` |

A token is the whole word. `device` is not `dev`. `protest`, `latest`, and `contest` are not `test`. `product` and `reproduce` are not `prod`.

- **Skipped.** Any production token on the name, the group, or a tag. List it as skipped: name, group, and the mark. Do not show the rest of the resource. Production wins when a dev or test token is also present.
- **Taken.** Not production, and a token says the named environment. The reader lists it. Cite the resource id (the ARN).
- **No mark.** No dev, test, or production token on the name, the group, and the tags. Stop and ask, in the skill. Do not read that resource. Do not list it as seen. The account is not a mark. The region is not a mark.

If search omits tags, `aws resourcegroupstaggingapi get-resources` may be used to read the tags only. If those tags still have no mark, stop. Do not read further properties on that resource.

An empty group list means no resource has a group mark. If the resource groups list cannot be read, stop. Say the AWS reader cannot read. Do not assume the group is empty.

## What a taken resource shows

For a taken resource, the fact is the resource id, the type, the name, and the group, plus the mark (name, group, or tag). Say `Seen in AWS dev.` or `Seen in AWS test.` Do not say the code shows it.

A connection is a field on that resource that names another resource id or a hostname. Cite the resource id and the field. A similar name is not a connection. Do not invent one. Do not read a skipped resource or an unmarked resource to look for a connection.

A setting that holds a secret is not copied. Say the setting exists only when the connection is a hostname or a resource id, and cite that, not the secret.
