# Early-access flags

Read this when the user says `flags-list`, `flags-on`, or `flags-off`. A plain update does not read this page. With no `.crav1/flags.local.json`, do not mention kit 2.0.

The file is per repo and stays on this machine. The kit writes it. The words are the way to change it.

## Words

| Word | What it does |
| --- | --- |
| `flags-list` | Shows the registry and which flags are on. Writes nothing |
| `flags-on <flag> [<flag> ...]` | Turns each named flag on. Example: `flags-on kit2` |
| `flags-off <flag> [<flag> ...]` | Turns each named flag off |

One command may name several flags. A name the registry does not know is refused in one line that names the known flags. Names that are known are still applied. A flag already in the file that the registry does not know is kept and reported. It is not an error.

The script is `scripts/update_kit.py --vendor copilot` in this skill, for example `flags-on kit2 --root <project>`. `--home` is a test hook. Do not pass it for a person.

Each command shows the change. It writes only `.crav1/flags.local.json` and `.crav1/.gitignore`. The ignore file lists `flags.local.json`. An existing `*` line stays. The project's `.gitignore` is not changed.

A file that cannot be read is one plain line: `Flags file .crav1/flags.local.json is not readable; continuing with no flags.` The command then continues with no flags stored. An update that hits that file prints the same line and continues as if no flags were set.

## Registry

Known flags live in `scripts/flags.py` as `REGISTRY`. Each entry has a one-line description and a status of `experimental` or `beta`.

| Flag | Status | What it does |
| --- | --- | --- |
| `kit2` | experimental | On an update, install kit 2.0 at user level from the newest published `v2.0.0-*` pre-release, through `v2/install.py`. Off, when `~/.crav1-2/installed.json` exists, offer uninstall |

## kit2 on an update

After `flags-on kit2`, continue the normal update on this branch (detect, plan, apply). `plan` and `apply` fetch the newest published `v2.0.0-*` pre-release and run `v2/install.py` from that tag. The script does that fetch. Do not clone it yourself. When the lookup or the fetch fails, they use the bundled tree in `--new` and the line says a newer 2.0 may exist. Never pipe or redirect the `plan` or `apply` output (`| python -c`, `| head`, `>`). Read it directly.

The plan is a dry run of that install (`install dry-run`). Apply runs `install` after the kit files are written. The result is one `kit2_line`. It names the version that will be installed and the version installed now. When the installed engine already equals that version and `repo_writes` is 0, `card` is null. Do not show an install card. The counts under `files` stay the same. Say the line once.

When `kit2` is false and `~/.crav1-2/installed.json` exists, the same line is the offer. Ask one card. Do not uninstall on the update yes.

Uninstall kit 2.0? It removes only the files listed in the install record.

- `uninstall-kit2` (Recommended). Removes only those listed files.
- `keep-kit2`. Leaves the user-level install in place.

On `uninstall-kit2`, run `uninstall-kit2 --yes --new <release> --root <project>`. On `keep-kit2`, leave the install.

With no flag file, skip this section. Print nothing about kit 2.0.

## Run ending

A flag-only reply that did not change kit files ends with `update_kit.py ending --root <project> --not-updated --vendor copilot`. Run next comes first. When the same run also updated the kit, use the usual ending.
