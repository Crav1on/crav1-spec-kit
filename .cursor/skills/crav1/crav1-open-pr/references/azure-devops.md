# crav1-open-pr: azure devops

Read only when the pointer in `SKILL.md` sends you here. Moved word for word from `SKILL.md` in 1.71.0; the rules are unchanged.

### Azure DevOps (`az`)

Treat the remote as Azure DevOps when the URL matches `dev.azure.com` or `*.visualstudio.com` (HTTPS or SSH). Read org, project, and repository from that URL when you can:

| Shape | Org / project / repo |
| --- | --- |
| `https://dev.azure.com/<org>/<project>/_git/<repo>` | path segments |
| `https://<org>@dev.azure.com/<org>/<project>/_git/<repo>` | path segments (ignore the userinfo) |
| `https://<org>.visualstudio.com/<project>/_git/<repo>` | host label is the org |
| `git@ssh.dev.azure.com:v3/<org>/<project>/<repo>` | path after `v3/` |
| `git@vs-ssh.visualstudio.com:v3/<org>/<project>/<repo>` | path after `v3/` |
| `<org>@vs-ssh.visualstudio.com:v3/<org>/<project>/<repo>` | path after `v3/` |

`ssh://` URLs use the same path segments. Strip a trailing `.git`. Percent-decode project and repository when the URL encoded them. A collection segment such as `DefaultCollection` stays in the web URL; it is not the `--project` value.

Use `az repos pr` only when **all** of these are true:

1. `az` is on `PATH` (on Windows, `az.cmd` counts).
2. The azure-devops extension works or can be used. `az repos pr list -h` exits 0, or the first `az repos pr` call succeeds. Microsoft documents that this extension installs automatically the first time an `az repos pr` command runs (Azure CLI 2.30.0 or higher). If that first call still cannot run `az repos pr`, the extension is not usable.
3. The CLI is already authenticated for a non-interactive call. A list call for this remote that returns without an auth error counts. `az account show` exiting 0, or `AZURE_DEVOPS_EXT_PAT` already set, is a hint, not proof. A dialog box or a browser Microsoft sign-in is not a create path. Do not run `az login`, a device-code flow, or a web login. Do not create a token.

Prefer org, project, and repository parsed from the remote. Pass them on the command and pass `--detect false`:

- `--org` is the organization URL, for example `https://dev.azure.com/<org>` or `https://<org>.visualstudio.com`
- `--project` is the team project
- `--repository` is the repo name or id

`--detect` is documented as "Automatically detect organization" (`true` or `false`; default `true`). From a local Azure Repos checkout it reads **that** git remote and overrides `az devops configure` defaults. Command flags win over detection. Use `--detect true`, and omit only the flags you could not parse, **only** when the URL did not yield org, project, and repository **and** this command runs in a local checkout of that same remote. Otherwise do not use `--detect true`.

**Create** then uses the Azure DevOps steps. If `az` is missing, the extension is not usable, the CLI is not already authenticated, or list/create fails, print the Azure DevOps fallback below. Do not invent a URL.

### Azure DevOps (Create)

When **Host** says to use `az`, list open pull requests for this source → target **before** create. `--status active` is the open set, including drafts. Source is `<head>`. Target is `<base>`. Pass branch names (`dev`), not `refs/heads/...`.

Parsed org, project, and repository:

```text
az repos pr list --org <org-url> --project <project> --repository <repo> --source-branch <head> --target-branch <base> --status active --include-links --detect false --output json
```

Use the `--detect true` form from **Host** only in the case Host allows, and only for the flags you could not parse.

If the list is non-empty, print the web URL and stop. Do not run `az repos pr create`. Prefer `_links.web.href`. When the JSON has `pullRequestId` and no web link, print `https://dev.azure.com/<org>/<project>/_git/<repo>/pullrequest/<pullRequestId>` (or `https://<org>.visualstudio.com/...` when that is the organization host). That id came from the host.

If the list call fails, do not create. Print the Azure DevOps fallback from **Host**. Do not invent a URL. Do not start a sign-in.

If the list is empty, create one pull request.

Non-Windows: pass `--description` as one value (a HEREDOC is fine) so quotes and Markdown survive. Microsoft documents each `--description` value as one new line.

```text
az repos pr create --org <org-url> --project <project> --repository <repo> --source-branch <head> --target-branch <base> --title <title> --description <body> --detect false --output json
```

Windows (PowerShell calling `az.cmd`): do not pass the body on the command line. `cmd.exe` keeps only the text before the first newline.

1. Write the accepted body to a new temp file as UTF-8 without a BOM. A BOM shows up as a character at the start of the description. Non-ASCII (an en dash, for example) must survive. Windows PowerShell `Set-Content -Encoding utf8` writes a BOM. Do not use it.

```powershell
$path = Join-Path ([System.IO.Path]::GetTempPath()) ("az-pr-body-" + [guid]::NewGuid().ToString() + ".md")
$utf8NoBom = New-Object System.Text.UTF8Encoding $false
[System.IO.File]::WriteAllText($path, $body, $utf8NoBom)
```

2. Pass `--description "@<path>"` with the `@` file token quoted, so PowerShell does not treat `@` as a splat. Azure CLI loads that file and keeps every line.

```text
az repos pr create --org <org-url> --project <project> --repository <repo> --source-branch <head> --target-branch <base> --title <title> --description "@<path>" --detect false --output json
```

3. Delete the temp file after the create call returns, whether it succeeded or failed. Do not commit it. Do not leave it in the repo.

Quote any `--query` value that contains parentheses. `cmd.exe` treats an unquoted `(` as syntax.

Do not pass `--open`, `--auto-complete`, `--draft`, `--delete-source-branch`, `--reviewers`, `--optional-reviewers`, `--required-reviewers`, `--work-items`, `--transition-work-items`, `--squash`, `--merge-commit-message`, `--labels`, or `--bypass-policy` unless they asked for that in this chat. Do not set auto-complete, merge, draft, reviewers, work items, or delete-source-branch unless they asked.

On success, print the web URL the same way (`_links.web.href`, otherwise `/pullrequest/<pullRequestId>` from the id the command returned) and follow **After it exists**. A `url` field on that JSON counts as the host returning a URL; still print the web form when you can build it from that id.

If create fails because a pull request already exists, print that URL. Do not open a second.

If create fails for any other reason, print the Azure DevOps fallback from **Host**. Do not invent a URL. Do not start a sign-in.
