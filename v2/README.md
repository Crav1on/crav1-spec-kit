# CRAV1 kit 2.0 (alpha)

This folder is the kit 2.0 skeleton on `main`, next to 1.x. Nothing here is released. 1.x is not version-bumped. The 1.x doc check skips this folder so a 2.0 file is not treated as a 1.x workflow copy.

The engine is Python 3.10 or newer, standard library only. It appends `.crav1-2/events.jsonl`, folds that log into state, and rebuilds `sot/index.md`, `sot/facts.md`, `sot/decisions.md`, and `sot/assumptions.md`. A note page (`sot/<YYYY-MM-DD-slug>/note.md`) is rendered with passage anchors when the log carries the passage text. The engine does not commit.

`/crav1-2-link-to-spec` is not in this build.

## /crav1-2-add-to-sot

Capture one source as one note. Words: `mail`, `chat`, `meeting`, `session`, `document`, `fact`, `from-sources`, `this-session`, and `dry-run`. Kind words combine into one note. A word in the invocation is taken as given. A missing word stops and lists those words.

The engine checks the source-extractor JSON, assigns passage ids (`p-001` upward), copies originals after secret redaction (the value is dropped, the kind is kept), appends one `note.added` event, and rebuilds the views. `from-sources` writes a thin note that points at `docs/sources/<folder>/` and copies nothing. `dry-run` prints the note and the events and writes nothing.

## this-session

`/crav1-2-add-to-sot this-session` reads the current chat. The skill text is the same in Cursor, Claude Code, and Codex. One card (`keep-all`, `pick-some`, `stop`) comes before anything is written. `keep-all` is recommended only when a quote was checked against a session file.

Where a session file exists, each quote is checked and a miss is marked unverified. Claude Code reads `~/.claude/projects/<encoded-repo>/*.jsonl`. Codex reads `~/.codex/sessions/` and `~/.codex/archived_sessions/` when the file names this repo. Cursor has no readable session file, and the note says the quotes were not checked.

An answer is matched to an open question by the question's words and recorded as `answer.matched`. The question stays open. A second run with the same session id adds only new passages (`note.extended`). A parked run resumes from `.crav1-2/sessions/<id>.json`.

## /crav1-2-show-sot

Read-only. Words: `none` (or no word) for the index, `facts`, `decisions`, `assumptions`, and `about-<topic>`. It writes nothing. A broken pointer is reported in the reply, not written into the view.

## Try it

Use a scratch home and a scratch project. `--home` is a test hook, not a product option. The words are `install`, `uninstall`, `status`, and `dry-run`.

```bash
mkdir -p /tmp/crav1-2-home /tmp/scratch-repo
python v2/install.py --home /tmp/crav1-2-home install
PYTHONPATH=v2 python -m crav1_2 init repo /tmp/scratch-repo
PYTHONPATH=v2 python -m crav1_2 add-to-sot fact dry-run repo /tmp/scratch-repo <<'JSON'
{"title":"One fact","date":"2026-11-26","extractor":{"passages":[{"kind":"fact","who":"person A","quote":"The feed stays on the current channel."}]}}
JSON
PYTHONPATH=v2 python -m crav1_2 show-sot repo /tmp/scratch-repo
python v2/install.py --home /tmp/crav1-2-home status
python v2/install.py --home /tmp/crav1-2-home uninstall
```

`append` reads one JSON object, or one object per line, from stdin. `rebuild-views` rewrites the generated pages. `lint` checks ids, pointers, a single origin kind, and MUST on an assumption item. `check-lines before after` reports whether a shared spec's 1.x lines changed.

User-level files:

- Cursor plugin id `crav1-2`: `~/.cursor/plugins/local/crav1-2/`
- Claude Code: `~/.claude/skills/crav1-2-*/` and `~/.claude/agents/crav1-2-*.md` (never `CLAUDE.md`)
- Engine: `~/.crav1-2/engine/`
- Record: `~/.crav1-2/installed.json`

Codex is skipped. 1.x 1.204.0 installs Codex into the project `.agents/skills/` tree and has no matching user-level path.

Install refuses when an installed 1.x kit is older than 1.205.0. If no 1.x install is found, install continues and says so. Uninstall deletes only listed files whose bytes still match. A changed file is listed and left in place. A project's `sot/` and `.crav1-2/` event log are never part of that list.

## Tests

From the repository root:

```bash
python -m unittest discover -s v2/tests -v
```
