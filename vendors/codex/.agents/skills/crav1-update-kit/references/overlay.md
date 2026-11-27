# Drop-in overlay

Read this only when `writes_kit_files` is true. Fetch the installed tag and the target tag with `fetch`. Both must already have passed `resolve-target`. Do not fetch `main`, a branch, or a pull request.

`fetch` (1.190.0) clones into a short folder in the system temp folder when `--dest` is left out (`ck` plus the version digits), with `core.longpaths=true` and `core.autocrlf=false`, because a long clone path fails on Windows. It then checks that `git status` in the clone is clean. A failed clone or an incomplete checkout is refused with the reason and no plan is made; fetch again with a shorter `--dest`.

Plan with `--old` and `--new` pointing at those trees. Show the heads-up card. On `yes` or `write only`, run `apply --yes`.

## What is replaced

Kit-owned paths only, for each vendor in `.crav1/kit.json`. When that file is missing, the vendors are the ones whose marker files are present, and the same yes writes the file. A normal update does not create a vendor that is not selected. `add` and `remove` are [vendors.md](vendors.md). The script's allow-list is the source of truth:

- the `crav1` skill tree, including bundled `crav1-docs`
- agent files whose names start with `crav1-`
- `crav1-*` agent-asset folders and `README.md` beside them
- the kit project instruction (`crav1.mdc`, or `CLAUDE.md` in the Claude Code drop-in)

A file the new release removed is deleted when the local copy still matches the old release. A file the project added inside a kit folder, and that neither release contains, is left in place and listed.

The commit stages files the release trees ship (1.205.0). A name pattern is not the list. Pass `--old` and `--new` on `commit`, the same trees as the plan. A skill or agent whose name starts with `crav1-2-`, a `.crav1-2/` folder, and `sot/` are refused. They are not written, staged, or deleted.

## Three-way merge

Compare the old release, the local file, and the new release.

- The local file matches the old release: take the new file.
- The new release matches the old release: keep the local file.
- The two sides change different lines: merge them.
- The two sides change the same lines: a clash. Show both sides on the heads-up card. `keep` keeps the local side and still takes non-overlapping kit lines. `take` takes the kit side and still keeps non-overlapping local lines. A clash with no `keep` or `take` refuses to write.

CRLF and LF compare equal (1.132.0). A local file that matches the old release apart from line endings is a plain update, not a clash. A real edit on the same lines still clashes. The written file keeps that file's line endings. When the file has no clear style, `.gitattributes` `eol` is used, otherwise LF. `fetch` clones with `core.autocrlf=false`.

## Copied templates

`docs/specs/_template/` and `docs/system/_template/` are not merged line by line. A file that is already in the project and still matches the old release, apart from line endings, is replaced. A real edit is left alone and listed, including a template the project never copied. Do not add a template file the project does not already have. The written template keeps the local line endings.

## Left alone

Never write these, even if a release tree contains them: a spec folder (`walk-progress.md`, `build-progress/`, `spec.md`, `plan.md`, `tasks.md`, `verify.md`, `work-item.md`, `build-map.md`), the rest of `docs/system/`, `docs/notes/`, `docs/playbooks/`, `docs/environments/`, `docs/research/`, `docs/sources/`, a product `AGENTS.md`, `kit-maintainer.mdc`, the draft-commit persist rules (except the stale case below), and the transfer data policy. Do not run `sync-crav1-plugin.sh` or the other maintainer generators in the consumer project. The release already contains the generated docs and the Claude Code drop-in. A later `git merge` that conflicts on `walk-progress.md` version lines is `$crav1-finalize-commit` `references/pull.md` (1.139.0), not this replace. The same settle covers a `build-progress` file whose conflict is only hash lines (1.142.0).

## Persisted commit style (1.176.0)

A saved commit-style rule (`draft-commit-style` or `draft-commit-gitlog` in the repo's Cursor or Claude Code rules folder) is rewritten from the current message-only asset when it is stale: it is the old release's copy unchanged, or it names `crav1-draft-commit-message/`, a skill that no longer exists. It shows under `update` in the plan, so it is in the same yes. A stale rule whose asset is gone from the new release is listed under `delete` and the kit removes it in the same yes (1.178.0). The kit writes, removes and commits these rules itself, so a stale rule is never refused as a project file. A rule changed by hand is left and listed in `style_rules_left`; say which one and that it still points where it did. A rule under the home folder is not touched.

## Commit

On `yes, write and commit`, after apply and after the migration card when there is one, run `commit --yes --from-version <installed> --to-version <target> --old <old-release> --new <new-release>`. The message is `Update CRAV1 kit vA to vB`. The commit stages files those release trees ship, including an updated template that still matched the old release. Project files stay unstaged, including a spec a migration just rewrote, a `crav1-2-` skill or agent, `.crav1-2/`, and `sot/`. On `write only`, do not commit. When `repo_writes` is zero, do not run `commit` and do not offer it (1.208.0).

## Kit 2.0 flag (1.206.0)

When `.crav1/flags.local.json` is missing, say nothing about kit 2.0. When `kit2` is true, plan dry-runs `v2/install.py install dry-run` from the release in `--new`, and apply runs `install` at user level after the kit files are written. The result is one `kit2_line`. Counts under `files` stay the same. When those counts are empty and the dry-run is the only change, the card is `install-kit2` or `stop` (1.208.0). Apply's `ending_args` name that ending: `--not-updated --kit2` when no repo file was written. When `kit2` is false and `~/.crav1-2/installed.json` exists, that line offers `uninstall-kit2` (Recommended) or `keep-kit2`. A file that cannot be read is one plain line, and the update continues with no flags. Do not write the flag file during plan or apply. The words that write it are in [flags.md](flags.md).
