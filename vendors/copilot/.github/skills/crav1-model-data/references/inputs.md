# Command inputs

Read this when you record. Do not read `scripts/model_run.py` to learn a field. The other flow file stays closed.

Run `scripts/model_run.py`. Pick the interpreter as `crav1-docs/reference/running-scripts.md` says. Content goes through a file. Inline flags are for short values only.

`--input <file.json>` and `--json <file.json>` are the same JSON file. Pass one of them. `--text-file` is the prose file. `--text` is the short inline form.

A hand edit is refused. Change an existing item with `revise`.

## discover

Flags: `--root <repo>`, optional `--scope`.

Example file: `references/inputs/discover.args`

## init

Flags: `--home`, `--name`, `--flow` (`manual` or `auto`), optional `--scope`.

Example file: `references/inputs/init.args`

## recommend

`--home` and `--input`. Fields:

- `recommendation`: `retain`, `targeted`, `redesign`, `held`, or `tie`
- `existing_meets_need`: true or false
- `documentation`: such as `poor` or `adequate`
- `decision_changing_gaps`: list of short labels
- `provisional`: true while a gap is open
- `best_fit`: the lean, or empty on a tie
- `alternatives`: list
- `assumptions`, `reason`, `binding`, `revisit`
- `axis`: the axis this recommendation is about
- `tie_excluded`: axes you are explicitly not leaning on
- `tie`: true on a genuine tie. Do not set `best_fit` unless `user_chose` is true
- `user_chose`: manual flow only, after the user picks. An open auto run rejects it

Example file: `references/inputs/recommend.json`

## example

`--kind` and `--input`. Add `--home` to store it on the model. Kinds:

- `history-window`: `retained_days`, `needed_days`, `claim` (`can-reconstruct`, `conditional`, or `met`), `other_source`, `other_source_days`, optional `other_source_from`, optional `narrative`. A can-reconstruct claim with another source and no `other_source_days` is an open question. A start date alone is not coverage.
- `double-count`: `operation` (`sum`), `rows` of `grain` and `amount`
- `schema-not-disproof`: `claim` (`unknown-feasibility` or `history-impossible`)
- `correction`: `correction_meaning`, optional `narrative`
- `views`: `area_obligations`, `platform_obligations`, `default_view` null, `promoted_to_platform_rule` false

Example files: `references/inputs/example-history-window.json`, `example-double-count.json`, `example-schema.json`, `example-correction.json`, `example-views.json`

## decide

`--home` and `--input`. Fields: `id`, `stage` (`business-model` or `physical-design`), `status` (`proposed`; auto physical detail uses `conditional`), `evidence`, `requirement`, `fit`, `outcome`, `scope`, `axis`, `sources`, `depends`, `conditional`, `implementable`, `grain`, `measure`, `short_source`, `body`.

An id that already exists is refused. Use `revise`.

Example file: `references/inputs/decide.json`

## question

`--home` and `--input`. Fields: `id`, `affects`, `provider`, `blocks`, `body`.

Example file: `references/inputs/question.json`

## diagram

Flags: `--home`, `--id`, `--kind` (`er` or `flow`), `--caption` or `--caption-file`, `--mermaid <file.mmd>`.

Example files: `references/inputs/diagram.args`, `references/inputs/diagram.mmd`

## transition

`--home`, `--kind` (`concise` or `none`), `--text-file` or a short `--text`.

Example file: `references/inputs/transition.txt`

## views

`--home` and `--input`. Same fields as the `views` example.

Example file: `references/inputs/views.json`

## confirm-scope

`--home` and `--yes`, only after the user says yes. An open auto run rejects it.

Example file: `references/inputs/confirm-scope.args`

## propose-scope

`--home` and `--scope` or `--scope-file`.

Example file: `references/inputs/propose-scope.txt`

## pin

`--home`, `--root`, `--source` (path inside the repo), `--decisions` (comma-separated ids).

Example file: `references/inputs/pin.args`

## drift

`--home` and `--root`. Read only.

Example file: `references/inputs/drift.args`

## note-drift

`--home` and `--root`. Marks affected proposed decisions. Does not change `confirmed.md`.

Example file: `references/inputs/note-drift.args`

## approve

`--home`, `--stage`, `--revision`, `--date` (`YYYY-MM-DD`), `--yes`. An open auto run rejects it.

Example file: `references/inputs/approve.args`

## auto-begin

`--home`, `--minutes`, `--passes`. Do not pass `--now`.

Example file: `references/inputs/auto-begin.args`

## auto-baseline

`--home`, `--fingerprint`, optional `--unresolved`, `--text-file` or a short `--text`, optional `--stage`. This does not use a correction pass. Do not pass `--now`.

Example file: `references/inputs/auto-baseline.txt`

## auto-pass

`--home`, `--fingerprint`, `--unresolved`, `--progress` (`yes` or `no`), `--text-file` or a short `--text`, optional `--stage`. The first call before a baseline is the baseline and does not use a pass. Do not pass `--now`.

Example file: `references/inputs/auto-pass.txt`

## auto-finish

`--home` and `--root`.

Example file: `references/inputs/auto-finish.args`

## feedback

`--home`, `--review` (the review directory), `--decision`, `--comment-file` or a short `--comment`.

Example file: `references/inputs/feedback.txt`

## revise

`--home`, `--id`, `--reason` or `--reason-file`, `--input`.

The JSON is the new content for that id. A decision uses the `decide` fields. An example uses the example fields plus `kind`. A question uses the `question` fields. A diagram uses `kind`, `caption`, and `mermaid`. The id must already exist. Status is set back to proposed, except a question, which stays open.

Example files: `references/inputs/revise-decision.json`, `references/inputs/revise-example.json`

## report

`--home` and `--kit <version>`. Do not pass `--now`. This writes a new review snapshot and does not change the model.

Example file: `references/inputs/report.args`

## link-line

`--name`. Prints the spec line. It does not write the spec.

Example file: `references/inputs/link-line.args`
