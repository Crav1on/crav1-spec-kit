# crav1-open-pr: fallback

Read only when the pointer in `SKILL.md` sends you here. Moved word for word from `SKILL.md` in 1.71.0; the rules are unchanged.

### Fallback (no URL)

After a successful `git push` (push path only), or instead of create (open-only path), print base ← head, the title and body they accepted, and the filled commands. On the open-only path, omit the `git push` line and say the remote branch must already exist.

GitHub, or a remote that is not Azure DevOps:

```text
git push -u <remote> <head>
gh pr create --base <base> --head <head> --title "<title>" --body "<body>"
```

Azure DevOps. Fill org, project, and repository from the remote when you have them. Name any you could not parse. Do not invent them. For `*.visualstudio.com`, `--org` is `https://<org>.visualstudio.com`.

```text
git push -u <remote> <head>
az repos pr list --org https://dev.azure.com/<org> --project <project> --repository <repo> --source-branch <head> --target-branch <base> --status active --include-links --detect false
az repos pr create --org https://dev.azure.com/<org> --project <project> --repository <repo> --source-branch <head> --target-branch <base> --title "<title>" --description "<body>" --detect false
```

On Windows, do not put a multi-line `<body>` on that create command. `cmd.exe` keeps only the first line. Write the accepted body to a temp file as UTF-8 without a BOM and pass `--description "@<file>"`, then delete the file. See **Create**. Quote any `--query` value that contains parentheses.

When org, project, and repository are known, also print the create-PR page they can open. This is not an opened pull request. URL-encode `<head>` and `<base>` (`/` as `%2F`):

```text
https://dev.azure.com/<org>/<project>/_git/<repo>/pullrequestcreate?sourceRef=<head>&targetRef=<base>
```

Use `https://<org>.visualstudio.com/...` when that is the host. Keep a collection segment from the remote when the web repo URL has one.

GitKraken stays **GUI paste only**: open a pull request from `<head>` into `<base>`. Paste the title and body. Do not merge. A later explicit ask to merge that named pull request is `/crav1-merge-pr`.

Do not run `gk ai pr create` or any other interactive `gk` pull-request create. Those commands wait for a confirmation prompt and fail in a non-interactive shell.

### No host create

When **Host** says not to call `gh` or `az`, print the fallback from that section. Do not claim a pull request was opened. Tell them that if one already exists for this head → base, they should use that URL and not open a second.
