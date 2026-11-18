# Script inputs

Run `<interpreter> scripts/design_run.py [--root <specs repo>] [--headless] <move> ...`, where the interpreter is `py -3` on Windows and `python3` elsewhere (`crav1-docs/reference/running-scripts.md`). Exit 2 means refused; the reason is on stderr and nothing was written.

- `create --topic <topic> [--builds-on <base>] --input goal.json`: `ask`, `end_goal`, `drivers`, `constraints`, `criteria`, `design`, `design_title`, `decisions` (titles). With `--builds-on` it also returns `branch_from`, `git` (the branch commands), `update_from_base` and `fixed`.
- `change-goal --topic --input change.json --reason "<why>" [--yes]`: any of `ask`, `end_goal`, `drivers`, `constraints`, `criteria`, `decisions` (the new order; a missing one is dropped), `renames` (`{old: new}`), `drop_reasons` (`{title: reason}`), `reopen` (titles). Without `--yes` it writes nothing and returns `old`, `new`, `changes`, `flagged`, `dropped`. Never with `--headless`.
- `revisit --topic <linked topic> --decision "<words>" --reason "<why>"`: marks the base topic's decision reopened and returns its `ending`.
- `status [--topic]`, `resume --topic [--design]`, `park --topic [--design]`, `review --topic [--design]`.
- `add-decision --topic --title "<decision>"`.
- `lean --topic --decision "<words>" --input lean.json`: `options` (each `name`), `recommended`, `leaning`, `drivers`, `ideas`.
- `settle --topic --decision "<words>" --input settle.json [--revisit-yes]`: `chosen`, `options` (each `name`, `good`, `bad`, `not_chosen`, `yours`), `why`, `drivers`, `context`, `adr_title`, `deciders`, `end_state`, `diagram` (Mermaid), `sources` (paths a resume should watch), `reverses`, `scores`.
- `question --topic --text "<question> (who)" [--decision] [--kind research --research <topic>] [--stage]`; `answer --topic --question "<words>" --text "<answer>"`; `skip --topic --decision "<words>"`.
- `fan-out --topic --name <name> --mode copy|blank [--title]`.
- `stage --topic --input stages.json`: `stages`, each `name`, `reason`, optional `waits_on`.
- `compare --topic [--input]`: `scores` as `{design: {criterion: yes|partly|no}}`.
- `compare-topics --topics <a> <b> --asked --input`: `criteria`, `scores`.
- `go-ahead --topic [--design] [--slice <slug>] [--accept-findings] [--base-merged]`.
- `ending --topic --input state.json`: `phase` (`design`, `go-ahead`, `merged`), `parked`, `open`, `slices`, `no_slice`, `routed_requirement`, `research_topic`, `question_open`, `waiting`, `uncommitted`, `reason`.

Decisions and questions are found by their words, never by number.
