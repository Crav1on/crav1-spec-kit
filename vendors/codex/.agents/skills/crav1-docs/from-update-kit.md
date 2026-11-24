# Update the installed kit

Kit not in this project yet? [Install first](install.md) (Cursor and Claude Code; the slash commands match, the files do not). The first jump, before this command exists in the project, downloads the release asset.

```bash
curl -fsSL -o crav1-update-kit.py https://github.com/Crav1on/crav1-spec-kit/releases/latest/download/crav1-update-kit.py
PYTHONUTF8=1 python3 -X utf8 crav1-update-kit.py detect
```

On Windows PowerShell 5.1, `curl` is an alias for `Invoke-WebRequest`, so the curl flags fail. On Windows, `python3` is often missing. Use `python` or `py`.

```powershell
Invoke-WebRequest -Uri https://github.com/Crav1on/crav1-spec-kit/releases/latest/download/crav1-update-kit.py -OutFile crav1-update-kit.py
$env:PYTHONUTF8 = "1"
python -X utf8 crav1-update-kit.py detect
```

Use this in a consumer project when the installed kit should move to a published release. `$crav1-update-kit` takes an optional `to vX.Y.Z`. With no version, the target is the latest published release tag.

This is cross-cutting. It is not a starter option. It does not switch branches, and it does not start Specify, Plan, or Build.

## First prompt

```text
$crav1-update-kit

Update the kit in this consumer project.
```

A version looks like `$crav1-update-kit to v1.129.0`. `main`, a branch name, a commit, and a pull request number are refused in one line.

## Steps

| Phase | You | Agent |
| --- | --- | --- |
| Detect | — | Reads the installed version from `plugin.json` or the `Kit version:` line. Resolves the target tag. Refuses anything that is not a published release |
| Heads-up | Read which branch you are on | Shows the branch, that only this branch gets the new kit, and that other branches stay on the old kit until you merge this branch into them. Says merge develop into the branch, and never rebase. Suggests merging first or switching branch when this branch should not move. Warns about uncommitted changes. Writes nothing until you answer |
| Confirm | `yes, write and commit (Recommended)`, `write only`, or `stop` | A clash is on that same card. The recommendation keeps your edit. The free-text answer can say `path: keep` or `path: take` |
| Replace | — | Replaces kit files. Auto-merges edits that do not overlap. CRLF and LF compare equal, so a line-ending-only difference is an update, not a clash. The written file keeps the local line endings. Leaves specs, walk-progress, build-progress, plans, notes, and the build map alone. Updates a copied template only when it still matches the old kit apart from line endings |
| Migrate | `apply (Recommended)` or `leave` | Dry-runs the version steps for this jump, lists them, and writes them only after `apply` |
| Commit | — | On yes, one commit: `Update CRAV1 kit vA to vB`. Does not push unless you already said to push in this run |

A plugin install does not get that commit. The command compares the installed plugin with the latest release, tells you how to refresh it, and still offers the migration steps.

## After

```text
Run next: nothing needed now.
```

Reload the window so the new skills load. When files were written and not committed, the run adds one `Uncommitted:` line. See [How a run ends](reference/run-ending.md).

Reference page: [update-kit](reference/skills/crav1-update-kit.md)

Since 1.176.0 `$crav1-update-kit` also fixes a saved commit-style rule that is out of date. When `.cursor/rules/draft-commit-style.mdc` (or the gitlog rule, or the `.claude/rules/` copy) is the old release's copy, or still points at `crav1-draft-commit-message/`, it is rewritten from the current asset in the same yes, so agents stop looking for a skill that is gone. A rule you changed by hand is left and named.

## 1.198.0 changes

`update_kit.py available --vendor codex` prints one `Kit update available: <installed> -> <latest>` line, read-only, with a 5 second timeout and a 12 hour cache, and nothing when offline. `$crav1-build-walk` and `$crav1-tighten-and-plan-ready-to-build` show it at the start with `$crav1-update-kit` in Run next.

## 1.201.0 changes

`vendors.json` in the update-kit skill lists each host: the folders the kit owns, the frontmatter a skill needs, the command prefix, and extra files. Cursor and Claude Code rows reproduce the 1.200 allow-list, so a plan and an apply on an existing install match 1.200. Codex and Copilot are listed and are not installed.

`update_kit.py detect --vendor codex` adds `vendors`, the hosts whose marker file is present. `update_kit.py vendors --root . --vendor codex` lists each vendor's folder and skill count and writes nothing.

A script that prints Run next takes `--vendor`. The default stays `/`. `--vendor codex` prints `$crav1-`.

## 1.202.0 changes

`$crav1-update-kit` still installs only Cursor and Claude Code. The kit repo now also commits generated Codex and Copilot copies under `vendors/codex/` and `vendors/copilot/`. Update does not copy those trees into a product repo.
