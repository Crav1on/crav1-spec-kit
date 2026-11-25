# Add or remove a vendor

Read this when the user says `add <vendor>` or `remove <vendor>`. A plain update does not read this page. Read [heads-up.md](heads-up.md) first, every run.

Codex is installed by this release. Copilot is listed and is not installed yet. An unknown name is refused in one line.

The vendor list is `.crav1/kit.json`:

```json
{"schema": 1, "vendors": ["claude", "codex"]}
```

`detect` prints `vendors` and `vendors_from` (`kit.json` or `inferred`). A missing file means the installable vendors whose marker files are present. The same yes writes the file. The version is not stored in it.

## Add

`add codex` uses the installed release, so the other vendors stay as they are. Fetch that tag, not the latest, unless the user named a version (`add codex to vX.Y.Z`).

```text
update_kit.py plan --add codex --new <release-tree> --root . --vendor copilot
```

The old side is empty, so every kit file is an add. A file that is already there and differs is a clash, with the same `local` and `kit` sides as any other clash. Show the counts, at most 10 sample paths, and every clash.

The card question is `Add Codex on <branch>?` The choices stay `yes, write and commit (Recommended)`, `write only`, and `stop`. A clash on that same card is `keep` or `take`.

On yes:

```text
update_kit.py apply --add codex --new <release-tree> --yes --root . --vendor copilot
```

It writes that vendor's files and `.crav1/kit.json` only. Then, when they chose the commit:

```text
update_kit.py commit --yes --add codex --to-version <version> --root . --vendor copilot
```

The message is `Add CRAV1 kit vendor codex vX.Y.Z`. One commit. It does not push.

A second apply that finds the same files changes nothing.

## Remove

`remove codex` deletes kit-owned files that still match the installed release. A local edit is a clash (`keep` leaves it, `take` deletes it). A file the release does not contain stays. Other vendors' folders stay.

```text
update_kit.py plan --remove codex --old <release-tree> --root . --vendor copilot
update_kit.py apply --remove codex --old <release-tree> --yes --root . --vendor copilot
update_kit.py commit --yes --remove codex --to-version <version> --root . --vendor copilot
```

The message is `Remove CRAV1 kit vendor codex vX.Y.Z`.

## Left alone

Never write `AGENTS.md`, `.github/copilot-instructions.md`, a spec, a plan, a task list, or a note. A skill folder that does not start with `crav1-` is a project file.

## Ending

Print `update_kit.py ending --vendor copilot`. Run next comes first. When the vendor is Codex, add one line after the reload line: `Restart Codex so the new skills load.` Commands in that copy use the Codex prefix.
