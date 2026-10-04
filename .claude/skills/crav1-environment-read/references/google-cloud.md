# Google Cloud reader

`/crav1-environment-read` follows this reader when the user named Google Cloud and an environment of dev or test. GCP is Google Cloud. It lists only what that named environment actually has.

Azure follows [azure.md](azure.md). AWS follows [aws.md](aws.md). Any other named host stops with no reader and does not use this file.

## Out of this reader

Do not read Azure DevOps, GitHub, or CI. Do not call `gh`, a GitHub API, `az`, `az repos`, `az pipelines`, `az boards`, or a pipeline API. A repo, a pipeline, or a board is not a resource this reader lists. Leave those out of the list. They do not stop the read.

The user names the environment, not the project. Do not ask which project is dev or test. Do not treat a project id, name, or number as an environment mark.

## Read-only

Use `gcloud` only to list and show. If `gcloud` is missing, or the login is not present, stop. Say the Google Cloud reader cannot read. Do not invent a resource. Do not pretend the environment is empty.

Scan every project `gcloud projects list` already returns. Do not skip a project because its name says production or dev. The mark is on the resource. Do not enable an API. Do not create a project.

Allowed:

- `gcloud auth list`
- `gcloud projects list`
- `gcloud asset search-all-resources` for each of those projects, with no environment query
- `gcloud resource-manager tags bindings list` for tags only, when that search omits labels and tags
- One `gcloud` describe of a resource this reader already took, and only for a field that names another resource id or a hostname

Do not create, update, delete, deploy, start, stop, or set a resource. Do not print a secret, a key, or a password. A hostname in a setting can be a connection. The secret value is not a fact.

For each project, run `gcloud asset search-all-resources --scope=projects/PROJECT_ID --format=json`. Do not pass a query that filters on dev, test, or production. Follow the next page token until it is absent. The marks below decide what is taken, skipped, or unread.

If the asset search cannot run for a project the list already returned, stop. Say the Google Cloud reader cannot read. Do not skip that project. Do not pretend it is empty.

## Mark

Look at the resource name and the tags. Google Cloud has no resource group on the resource. The group contributes no token. Do not invent a group from the project, the folder, the organization, the region, or the zone.

The name is `displayName` when it is present, and the last segment of the full resource name. The tags are labels, tags, and network tags on that resource. Split name, tag key, and tag value on every character that is not a letter. Those words are the tokens.

| Named environment | Tokens that say it |
| --- | --- |
| dev | `dev`, `development` |
| test | `test`, `testing` |
| production | `prod`, `production` |

A token is the whole word. `device` is not `dev`. `protest`, `latest`, and `contest` are not `test`. `product` and `reproduce` are not `prod`.

- **Skipped.** Any production token on the name or a tag. List it as skipped: name, group, and the mark. The group on that line says none. Do not show the rest of the resource. Production wins when a dev or test token is also present.
- **Taken.** Not production, and a token says the named environment. The reader lists it. Cite the resource id (the full resource name).
- **No mark.** No dev, test, or production token on the name and the tags. Stop and ask, in the skill. Do not read that resource. Do not list it as seen. The project is not a mark. The folder, the organization, the region, and the zone are not marks.

If search omits labels and tags, `gcloud resource-manager tags bindings list --parent` may be used to read the tags only. If those tags still have no mark, stop. Do not read further properties on that resource.

## What a taken resource shows

For a taken resource, the fact is the resource id, the type, the name, and the group, plus the mark (name or tag). The group is none. Say `Seen in Google Cloud dev.` or `Seen in Google Cloud test.` Do not say the code shows it.

A connection is a field on that resource that names another resource id or a hostname. Cite the resource id and the field. Read it from the asset record when that field is already there. A similar name is not a connection. Do not invent one. Do not read a skipped resource or an unmarked resource to look for a connection.

A setting that holds a secret is not copied. Say the setting exists only when the connection is a hostname or a resource id, and cite that, not the secret.
