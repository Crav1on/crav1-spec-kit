# Script inputs

Run `<interpreter> scripts/design_run.py [--root <specs repo>] [--headless] <move> ...`, where the interpreter is `py -3` on Windows and `python3` elsewhere (`crav1-docs/reference/running-scripts.md`). Exit 2 means refused; the reason is on stderr and nothing was written. Write input files under `docs/architecture/designs/<topic>/inputs/`; an input file outside the specs repo is refused. `create` and `change-goal` refuse unknown keys by name; a `notes` key (text, a list or an object) is saved to the topic's `notes.md` with `note`.

- `create --topic <topic> [--builds-on <base>] --input goal.json`: `ask`, `end_goal`, `drivers`, `constraints`, `criteria`, `design`, `design_title`, `decisions` (titles in order, or `{"title": ..., "detail": true}` for a detail decision), `notes`. It creates `design/<topic>` when it is missing (from `design/<base>` with `--builds-on`), refuses with `git switch` when that branch exists and is not checked out, and returns `branch_state`. With `--builds-on` it also returns `branch_from`, `git` (the branch commands), `update_from_base` and `fixed`.
- `change-goal --topic --input change.json --reason "<why>" [--yes]`: any of `ask`, `end_goal`, `drivers`, `constraints`, `criteria`, `decisions` (the new order; a missing one is dropped), `renames` (`{old: new}`), `drop_reasons` (`{title: reason}`), `reopen` (titles). Without `--yes` it writes nothing and returns `old`, `new`, `changes`, `flagged`, `dropped`. Never with `--headless`.
- `revisit --topic <linked topic> --decision "<words>" --reason "<why>"`: marks the base topic's decision reopened and returns its `ending`.
- `status [--topic]`, `resume --topic [--design]`, `park --topic [--design]`, `review --topic [--design]`.
- `add-decision --topic --title "<decision>" [--detail]`: added at the end of the stored order.
- `note --topic --title "<title>" [--kind scan|vision|scope|answers|goal|other] (--text "..." | --input note.json)`: `text` (a string) or `items` (a list); appends to `notes.md` in the topic folder.
- `small-fix --topic [--design] --text "<fix>"`: lists a change with no design choice under `## Small fixes`.
- `lean --topic --decision "<words>" --input lean.json`: `options` (each `name`), `recommended`, `leaning`, `drivers`, `ideas`. `drivers` names drivers already listed, by their short name; a short name that matches the start of a listed driver is not added again, and only a truly new driver is appended. The names are kept on the decision as `Drivers:`.
- `settle --topic --decision "<words>" --input settle.json [--revisit-yes]`: `chosen`, `options` (each `name`, `good`, `bad`, `not_chosen`, `yours`), `why`, `drivers`, `context`, `adr_title`, `deciders`, `end_state`, `diagram` (Mermaid), `sources` (paths a resume should watch), `reverses`, `scores`.
- `question --topic --text "<question> (who)" [--decision] [--kind research --research <topic>] [--stage]`; `answer --topic --question "<words>" --text "<answer>"`; `skip --topic --decision "<words>"`.
- `fan-out --topic --name <name> --mode copy|blank [--title]`.
- `stage --topic --input stages.json`: `stages`, each `name`, `reason`, optional `waits_on`.
- `compare --topic [--input]`: `scores` as `{design: {criterion: yes|partly|no}}`.
- `compare-topics --topics <a> <b> --asked --input`: `criteria`, `scores`.
- `go-ahead --topic [--design] [--slice <slug>] [--accept-findings] [--base-merged]`.
- `ending --topic --input state.json`: `phase` (`design`, `go-ahead`, `merged`), `parked` and `open` and `no_slice` and `routed_requirement` and `question_open` (true or false), `slices` (a list of slugs), `research_topic` and `reason` (text), `waiting` (text for one line, or a list for one `Waiting:` line per item), `uncommitted` (a count, a list of paths, true for the topic folder, or a short text).

Decisions and questions are found by their words, never by number.
