# Azure DevOps reader

`/crav1-pipeline-environments` follows this file when the user named Azure DevOps. The skill’s Start, Cases, and Sections decide what is asked and what is appended. This file is the command list and the deploy inputs.

## Out of this reader

Do not read builds, runs, logs, test runs, boards, wikis, or artifacts. Do not call `az pipelines runs`, `az pipelines build`, `az pipelines release` except `az pipelines release definition list` and `az pipelines release definition show`, `az boards`, `az repos`, or `az artifacts`.

Do not queue, run, approve, edit, or trigger a pipeline. Do not pass `--open`.

A cloud resource is not read. Do not call `az resource`, `az webapp`, `az group`, or a host reader from `/crav1-environment-read`.

## CLI

If `az` is not on the path, stop. Say `az` is not installed. Point at `https://learn.microsoft.com/cli/azure/install-azure-cli`. Do not install it. Do not name the extension or the login in that same stop.

If `az` is on the path and `az extension show --name azure-devops` fails, stop. Say the `azure-devops` extension is not installed. The install command is `az extension add --name azure-devops`. Point at `https://learn.microsoft.com/azure/devops/cli/`. Do not install it.

If `az` runs and `az account show` fails because there is no login, stop. Say `az` has no login. The login command is `az login`. Also name `az devops configure --defaults`. Do not log in. Do not run configure.

If a later call is rejected for login, stop. Say the Azure DevOps login is missing. The same two commands. Do not print a token. Do not ask for a PAT.

Pass `--detect false` on every `az pipelines` and `az devops` call. Do not let the git remote choose the org.

The org URL is `https://dev.azure.com/<org>` unless the user already gave the full URL.

## Allowed commands

List and show only. `az devops invoke` is GET only.

- `az account show` for the login check
- `az extension show --name azure-devops` for the extension check
- `az devops project list --org <url> --detect false` when the project is missing and the org is named
- `az pipelines list --org <url> --project <project> --detect false`
- `az pipelines show --id <id> --org <url> --project <project> --detect false`
- `az pipelines release definition list --org <url> --project <project> --detect false`
- `az pipelines release definition show --id <id> --org <url> --project <project> --detect false`
- `az pipelines variable-group list --org <url> --project <project> --detect false`
- `az pipelines variable-group show --group-id <id> --org <url> --project <project> --detect false`
- `az devops service-endpoint list --org <url> --project <project> --detect false`
- `az devops service-endpoint show --id <id> --org <url> --project <project> --detect false`
- `az devops invoke --http-method GET` for a pipeline definition, the YAML file that definition names, or a pipeline YAML file that definition’s YAML includes with `template:` or `extends:`

If `az pipelines list` or `az pipelines release definition list` fails, stop. Say the pipeline list failed.

## YAML file

`az pipelines show` names the YAML path. When the body is not in that show, GET the file with `az devops invoke`:

- area `git`, resource `items`
- route parameters `project` and `repositoryId` from the definition
- query parameters `path` set to that YAML path, and `includeContent=true`
- `--http-method GET`
- `--api-version 7.1`

Read only that path, plus a `template:` or `extends:` path inside it. Do not list the repository. Do not read a Bicep file, an ARM file, a Terraform file, or a script file. A missing file means that part is not read.

Do not send POST, PUT, PATCH, or DELETE.

## Variables

Follow a variable only when the value is plain.

- A value written on the pipeline, stage, or job `variables:` block.
- A parameter default written in that YAML.
- A variable group value from `az pipelines variable-group show` whose `isSecret` is not true. `--group-id` is the id from `az pipelines variable-group list`. Do not pass a second id flag. If `isSecret` is true, ignore any value in the response.

Do not follow a secret. Do not print it. Do not print the variable group JSON. A Key Vault link, a missing name, a cycle, or a runtime expression (`$[ ]`) is unresolved. The target is unclear. No mark is proposed.

Do not print a plain value that is a connection string, a key, or a password. An app name or a resource id inside a plain value can still be the target.

## Service connection

Match the task input to `az devops service-endpoint list` by name, then `az devops service-endpoint show` for that id.

Read the subscription id and the subscription name when those fields are shown. Put them on the section item. Do not put them in a new marks field.

Do not print `authorization`, a service principal key, a password, or the endpoint JSON.

When the endpoint shows no subscription, the subscription is not shown. The resource the step names can still be marked.

## Deploy inputs

A deploy step is one of these tasks. Other tasks contribute no target. A start, stop, or swap task contributes no target.

Use the input the task shows. The first marks field is the resource id when an input shows one, otherwise the app or resource name. The second field is the resource group, or `-` when the step shows none.

| Task | Resource | Group | Service connection input |
| --- | --- | --- | --- |
| `AzureWebApp` | `appName` | `resourceGroupName` | `azureSubscription` |
| `AzureWebAppContainer` | `appName` | `resourceGroupName` | `azureSubscription` |
| `AzureRmWebAppDeployment` | `WebAppName` | `ResourceGroupName` | `ConnectedServiceName` |
| `AzureFunctionApp` | `appName` | `resourceGroupName` | `azureSubscription` |
| `AzureFunctionAppContainer` | `appName` | `resourceGroupName` | `azureSubscription` |
| `AzureResourceManagerTemplateDeployment` | a resource id or app name in the inputs | `resourceGroupName` | `azureResourceManagerConnection` |
| `AzureResourceGroupDeployment` | a resource id or app name in the inputs | `resourceGroupName` | `azureSubscription` or `ConnectedServiceName` |
| `AzureContainerApps` | `containerAppName` | `resourceGroup` | `azureSubscription` |
| `AzureStaticWebApp` | the app name input when the task shows one. `app_location` is a path, not the resource. Do not read `azure_static_web_apps_api_token` | `resourceGroupName` when present | `azureSubscription` when present |
| `SqlAzureDacpacDeployment` | `DatabaseName` on `ServerName` | `ResourceGroupName` when present | `AzureSubscription` or the connection input the task shows |

`AzureResourceManagerTemplateDeployment` and `AzureResourceGroupDeployment` often name only the group. That group is context. It is not a mark, unless an input also names an app or a resource id.

`AzureCLI` and `AzurePowerShell` count only when the inline script text shows an app name or a resource id as a plain value. Do not open `scriptPath` or `ScriptPath`. A target that lives only in that file is unresolved.

A Kubernetes or Helm task counts only when an input shows an Azure resource id or an app name. Do not invent a cluster id from the service connection name.

A slot input is not a separate resource and not the environment. The stage name is the environment.
