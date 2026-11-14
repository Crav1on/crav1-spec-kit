# crav1-open-pr: GitHub

Read only when the pointer in `SKILL.md` sends you here.

## GitHub (Create)

Moved word for word from `SKILL.md` in 1.158.0; the rules are unchanged. `<interpreter> -X utf8 scripts/pr_common.py find --branch <head> --base <base>` runs the same list and sums it up.

When **Host** says to use `gh`:

```text
gh pr list --head <head> --base <base> --state open --json number,url
```

If the list is non-empty, follow **Existing pull request**. Do not run `gh pr create`.

Otherwise:

```text
gh pr create --base <base> --head <head> --title <title> --body <body>
```

Pass the body with a HEREDOC or `--body-file` so quotes survive. Do not pass `--draft`, `--reviewer`, `--label`, `--assignee`, or `--milestone` unless they asked for that in this chat.

If create fails because a pull request already exists, follow **Existing pull request**. Do not open a second.

On success, follow **After it exists**.
