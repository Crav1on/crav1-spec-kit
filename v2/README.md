# CRAV1 kit 2.0 (alpha)

This folder is the kit 2.0 skeleton on `main`, next to 1.x. Nothing here is released. The 1.x doc check skips this folder so a 2.0 file is not treated as a 1.x workflow copy. A repo turns it on with `flags-on kit2`.

The engine is Python 3.10 or newer, standard library only. It appends `.crav1-2/events.jsonl`, folds that log into state, and rebuilds `sot/index.md`, `sot/facts.md`, `sot/decisions.md`, and `sot/assumptions.md`. A note page (`sot/<YYYY-MM-DD-slug>/note.md`) is rendered with passage anchors when the log carries the passage text. The engine does not commit.

Phase 1 is complete in this alpha: add-to-sot, show-sot, and link-to-spec. Nothing here is released.

## /crav1-2-add-to-sot

Capture one source as one note. Words: `mail`, `chat`, `meeting`, `session`, `document`, `fact`, `from-sources`, `this-session`, and `dry-run`. Kind words combine into one note. A word in the invocation is taken as given. A missing word stops and lists those words.

The engine checks the source-extractor JSON, assigns passage ids (`p-001` upward), copies originals after secret redaction (the value is dropped, the kind is kept), appends one `note.added` event, and rebuilds the views. A mail file passed as `source` (or as a `.eml` word) is copied the same way, so the note points back at it. A passage time may be `HH:MM` or `YYYY-MM-DD HH:MM` with an optional zone, and the note shows that full value. The Added line uses the engine's clock and `git config user.name` (or the name the skill passes), never a speaker. Quotes keep the names in the source; only secret values are removed. `from-sources` writes a thin note that points at `docs/sources/<folder>/` and copies nothing. `dry-run` prints the note and the events and writes nothing. When the note does not already hold a matched answer, the ending suggests the matching `/crav1-add-to-spec` command and does not run it.

## this-session

`/crav1-2-add-to-sot this-session` reads the current chat. The skill text is the same in Cursor, Claude Code, and Codex. One card (`keep-all`, `pick-some`, `stop`) comes before anything is written. `keep-all` is recommended only when a quote was checked against a session file.

Where a session file exists, each quote is checked and a miss is marked unverified. Claude Code reads `~/.claude/projects/<encoded-repo>/*.jsonl`. Codex reads `~/.codex/sessions/` and `~/.codex/archived_sessions/` when the file names this repo. Cursor has no readable session file, and the note says the quotes were not checked.

An answer is matched to an open question by the question's words and recorded as `answer.matched`. The question stays open. A second run with the same session id adds only new passages (`note.extended`). A parked run resumes from `.crav1-2/sessions/<id>.json`.

## /crav1-2-link-to-spec

Link notes that have not been read against one 1.x spec. Words: none (every unread note), `note-<id>` (one note, for example `note-2026-11-25-outbound-channel`), `dry-run`, `resume`, and `park`.

The engine writes the finder inputs (notes, spec, decisions, tasks) to files and returns their paths. The spec file keeps the sections the note's topics touch, plus open questions. The gap-finder agent returns JSON. A finder item's `note` is the id `YYYY-MM-DD-slug`; a `note-` prefix is accepted and dropped. The engine checks the JSON, builds the cards, and ranks them. Each affected item is `covered`, `silent`, `conflicting`, or `vague`, with cited passages, impact and uncertainty from 1 to 3, what it holds, and proposed text. A high-impact gap is its own card. Low-impact gaps that do not say MUST share one assumption card (`accept-all`, `change-some`, `skip`). MUST is never written as an assumption. Questions that `answer.matched` already recorded share one card: "These N open questions have answers in the SoT", with `close-all`, `pick-some`, or `skip`. Closing a question writes one decision and an `Answered:` line on that 1.x question.

Each card has 2 to 4 hyphen-only options. Each option names its impact and its undo, and `skip` is always available. A recommendation is present only when a fact is cited. Otherwise the card names the missing fact and who could give it.

Write-back adds only `crav1-2:item` lines, each with one origin tag (`[src:]`, `[dec:]`, or `[asm:]`) and a pointer. No 1.x line is edited. `dry-run` prints the cards and the proposed items and writes nothing. When every item is covered and there is no card, the ending is `Run next: nothing needed; the spec already covers this note.`, including on `dry-run`. `park` and `resume` use the session file, including from a fresh chat. The ending starts with `Run next:` and has at most one `Also recorded:` line.

## /crav1-2-show-sot

Read-only. Words: `none` (or no word) for the index, `facts`, `decisions`, `assumptions`, and `about-<topic>`. It writes nothing. A broken pointer is reported in the reply, not written into the view.

## Try it

On a project that already has kit 1.x, this is the path:

```text
/crav1-update-kit flags-on kit2
```

Then update the kit. The update installs kit 2.0 at user level from that same release. `flags-list` shows the flag. `flags-off kit2` turns it off. When kit 2.0 is installed, the update offers `uninstall-kit2` (listed files only) or `keep-kit2`.

The scratch commands below try the engine in a temp project. `--home` is a test hook, not a product option. The update runs this install script. `flags-on kit2` only records the flag.

```bash
mkdir -p /tmp/crav1-2-home /tmp/scratch-repo/docs/specs/partner-b-feed
python v2/install.py --home /tmp/crav1-2-home install
PYTHONPATH=v2 python -m crav1_2 init repo /tmp/scratch-repo
cat > /tmp/scratch-repo/docs/specs/partner-b-feed/spec.md <<'MD'
# Partner B feed

## Constraints
- The feed to partner B runs over the existing secure channel.

## Open questions
- Who gets the certificate-expiry alert, and how early?
  - Blocks: none
MD
PYTHONPATH=v2 python -m crav1_2 add-to-sot fact repo /tmp/scratch-repo <<'JSON'
{"title":"Outbound channel","slug":"outbound-channel","date":"2026-11-25","extractor":{"passages":[{"kind":"fact","who":"person A","quote":"Agreed long term, likely before go-live, not in this slice."}]}}
JSON
PYTHONPATH=v2 python -m crav1_2 link-to-spec partner-b-feed dry-run repo /tmp/scratch-repo <<'JSON'
{"finder":{"items":[{"status":"silent","note":"2026-11-25-outbound-channel","passages":["p-001"],"impact":2,"uncertainty":1,"holds":[],"section":"Constraints","text":"The outbound messaging channel is agreed long term and is not built in this slice.","who":"person A"}]}}
JSON
PYTHONPATH=v2 python -m crav1_2 show-sot repo /tmp/scratch-repo
python v2/install.py --home /tmp/crav1-2-home status
python v2/install.py --home /tmp/crav1-2-home uninstall
```

`dry-run` prints the card and the proposed item and writes nothing. Drop `dry-run` to open the card, then send the card word (`add-pointer`, `skip`, and the rest) with `{}` on stdin. `add-to-sot this-session` records answers without closing questions. `link-to-spec` then offers `close-all`, `pick-some`, or `skip`.

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
