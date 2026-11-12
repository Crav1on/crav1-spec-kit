# Drop-in overlay

Read this only when `writes_kit_files` is true. Fetch the installed tag and the target tag with `fetch`. Both must already have passed `resolve-target`. Do not fetch `main`, a branch, or a pull request.

Plan with `--old` and `--new` pointing at those trees. Show the heads-up card. On `yes` or `write only`, run `apply --yes`.

## What is replaced

Kit-owned paths only, for a host whose drop-in is already in the project. Do not create the other host's tree. The script's allow-list is the source of truth:

- the `crav1` skill tree, including bundled `crav1-docs`
- agent files whose names start with `crav1-`
- `crav1-*` agent-asset folders and `README.md` beside them
- the kit project instruction (`crav1.mdc`, or `CLAUDE.md` in the Claude Code drop-in)

A file the new release removed is deleted when the local copy still matches the old release. A file the project added inside a kit folder, and that neither release contains, is left in place and listed.

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

Never write these, even if a release tree contains them: a spec folder (`walk-progress.md`, `build-progress/`, `spec.md`, `plan.md`, `tasks.md`, `verify.md`, `work-item.md`, `build-map.md`), the rest of `docs/system/`, `docs/notes/`, `docs/playbooks/`, `docs/environments/`, `docs/research/`, `docs/sources/`, a product `AGENTS.md`, `kit-maintainer.mdc`, the draft-commit persist rules, and the transfer data policy. Do not run `sync-crav1-plugin.sh` or the other maintainer generators in the consumer project. The release already contains the generated docs and the Claude Code drop-in. A later `git merge` that conflicts on `walk-progress.md` version lines is `/crav1-finalize-commit` `references/pull.md` (1.139.0), not this replace. The same settle covers a `build-progress` file whose conflict is only hash lines (1.142.0).

## Commit

On `yes`, after apply and after the migration card when there is one, run `commit --yes --from-version <installed> --to-version <target>`. The message is `Update CRAV1 kit vA to vB`. The commit stages kit-owned paths and updated templates only. Project files stay unstaged, including a spec a migration just rewrote. On `write only`, do not commit.
