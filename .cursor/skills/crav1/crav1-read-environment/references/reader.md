# crav1-read-environment: reader

Read only when the pointer in `SKILL.md` sends you here. Moved word for word from `SKILL.md` in 1.71.0; the rules are unchanged.

## Reader

Each host has its own reader. The reader lists what that host actually has, then the marks decide what is taken, skipped, shared, pre-prod, prod-only, or not read. A host with no reader stops. Say this host has no reader. Do not pretend to read it. Do not borrow another host’s reader.

This build has three readers.

- **Azure** — [references/azure.md](azure.md) (drop-in: `.cursor/skills/crav1/crav1-read-environment/references/azure.md`; plugin: this skill’s `references/azure.md`).
- **AWS** — [references/aws.md](aws.md) (drop-in: `.cursor/skills/crav1/crav1-read-environment/references/aws.md`; plugin: this skill’s `references/aws.md`). Amazon Web Services is AWS.
- **Google Cloud** — [references/google-cloud.md](google-cloud.md) (drop-in: `.cursor/skills/crav1/crav1-read-environment/references/google-cloud.md`; plugin: this skill’s `references/google-cloud.md`). GCP is Google Cloud.

Check the host name before any read.

- **GitHub, CI, Azure DevOps, or Azure Pipelines** — stop. This skill does not read them. Do not pretend to. Do not treat Azure DevOps as Azure.
- **Azure** — follow the Azure reader. The host name is Azure, not Azure DevOps. The user names the host, not the subscription.
- **AWS** — follow the AWS reader. The user names the host, not the account.
- **Google Cloud** — follow the Google Cloud reader. The user names the host, not the project.
- **Any other named host** — stop. This host has no reader.

If the CLI is missing, or the login is not present, stop before any resource list. Name exactly what is missing. Do not invent a resource. Do not install the CLI. Do not log in.

- **`az` is not installed.** Say `az` is not installed. Point at `https://learn.microsoft.com/cli/azure/install-azure-cli`. This skill does not install it.
- **`az` has no login.** Say `az` has no login. The login command is `az login`. This skill does not log in.
- **`aws` is not installed.** Say `aws` is not installed. Point at `https://docs.aws.amazon.com/cli/latest/userguide/getting-started-install.html`. This skill does not install it.
- **`aws` has no login.** Say `aws` has no login. The login command is `aws sso login` or `aws configure`. This skill does not log in.
- **`gcloud` is not installed.** Say `gcloud` is not installed. Point at `https://cloud.google.com/sdk/docs/install`. This skill does not install it.
- **`gcloud` has no login.** Say `gcloud` has no login. The login command is `gcloud auth login`. This skill does not log in.

The command is not installed when it is not on the path. The login is missing when the command runs and the reader’s identity check fails. If both are true, name the missing CLI. Do not also ask them to log in to a CLI that is not installed.

A failed resource list stops the read. Say the reader cannot list resources. An optional evidence command that fails means that evidence is absent. It does not stop the read.
