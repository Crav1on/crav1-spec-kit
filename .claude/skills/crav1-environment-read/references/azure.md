# Azure reader

`/crav1-environment-read` follows this reader when the user named Azure and an environment of dev or test. It lists only what that named environment actually has.

AWS follows [aws.md](aws.md). Google Cloud follows [google-cloud.md](google-cloud.md). Any other named host stops with no reader and does not use this file.

## Out of this reader

Do not read Azure DevOps, GitHub, or CI. Do not call `az repos`, `az pipelines`, `az boards`, `gh`, or a pipeline API. A project, a repo, a pipeline, or a board is not a resource this reader lists.

The user names the environment, not the subscription. Do not ask which subscription is dev or test. Do not treat a subscription name as an environment mark.

## Read-only

Use `az` only to list and show. If `az` is missing, or the login is not present, stop. Say the Azure reader cannot read. Do not invent a resource. Do not pretend the environment is empty.

Allowed:

- `az account list`
- `az resource list`
- `az resource show` for tags, or for a field on a resource this reader already took

Do not create, update, delete, deploy, start, stop, or set a resource. Do not print a secret, a key, or a password. A hostname in a setting can be a connection. The secret value is not a fact.

Scan every subscription the login can already see. Do not skip a subscription because its name says production or dev. The mark is on the resource.

List every resource. Do not filter them out in the query. The marks below decide what is taken, skipped, or unread.

## Mark

Look at the resource name, the resource group, and the tags. That look is the filter. Split name, group, tag key, and tag value on every character that is not a letter. Those words are the tokens.

| Named environment | Tokens that say it |
| --- | --- |
| dev | `dev`, `development` |
| test | `test`, `testing` |
| production | `prod`, `production` |

A token is the whole word. `device` is not `dev`. `protest`, `latest`, and `contest` are not `test`. `product` and `reproduce` are not `prod`.

- **Skipped.** Any production token on the name, the group, or a tag. List it as skipped: name, group, and the mark. Do not show the rest of the resource. Production wins when a dev or test token is also present.
- **Taken.** Not production, and a token says the named environment. The reader lists it. Cite the resource id.
- **No mark.** No dev, test, or production token on the name, the group, and the tags. Stop and ask, in the skill. Do not read that resource. Do not list it as seen. The subscription name is not a mark.

If `az resource list` omits tags, `az resource show --ids` may be used to read the tags only. If those tags still have no mark, stop. Do not read further properties on that resource.

## What a taken resource shows

For a taken resource, the fact is the resource id, the type, the name, and the group, plus the mark (name, group, or tag). Say `Seen in Azure dev.` or `Seen in Azure test.` Do not say the code shows it.

A connection is a field on that resource that names another resource id or a hostname. Cite the resource id and the field. A similar name is not a connection. Do not invent one. Do not read a skipped resource or an unmarked resource to look for a connection.

A setting that holds a secret is not copied. Say the setting exists only when the connection is a hostname or a resource id, and cite that, not the secret.
