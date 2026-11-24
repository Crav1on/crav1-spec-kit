# crav1-map-pipeline-environments: cli

Read only when the pointer in `SKILL.md` sends you here. Moved word for word from `SKILL.md` in 1.71.0; the rules are unchanged.

## CLI

Follow [references/azure-devops.md](azure-devops.md). Use `az pipelines` and `az devops` to list and show only. Pass `--detect false` on every call. The org is `https://dev.azure.com/<org>` unless they already gave the full URL.

If the CLI cannot read, stop before any pipeline list. Name exactly what is missing. Do not invent a pipeline. Do not install. Do not log in. Do not run `az devops configure`.

- **`az` is not installed.** Say `az` is not installed. Point at `https://learn.microsoft.com/cli/azure/install-azure-cli`. This skill does not install it. Do not also name the extension or the login.
- **The `azure-devops` extension is not installed.** Say the `azure-devops` extension is not installed. The install command is `az extension add --name azure-devops`. Point at `https://learn.microsoft.com/azure/devops/cli/`. This skill does not install it. Do not also ask them to log in.
- **`az` has no login.** Say `az` has no login. The login command is `az login`. Also name `az devops configure --defaults`. This skill does not log in and does not run configure.
- **Azure DevOps rejects the login.** Say the Azure DevOps login is missing. The same two commands. Do not print a token. Do not ask for a PAT.

The command is not installed when it is not on the path. The extension is missing when `az extension show --name azure-devops` fails. The login is missing when `az` is installed and `az account show` fails. Check in that order. A later Azure DevOps call that fails on login, after those checks passed, uses the Azure DevOps login stop.

A failed pipeline list stops the read. Say the pipeline list failed. Do not invent a pipeline.
