---
name: crav1-design-ui
description: >-
  Use when an accepted spec has a user-facing UI and its screens should be
  designed before the plan: look, layout, tokens, states, interactions, and
  UI checks. Writes ui/design.md, ui/experience.md, one visual, and one
  sign-off item per screen. Does not write code or commit.
disable-model-invocation: true
icon: layout
color: purple
---

# Design the UI

You design the user-facing screens of one slice with the user, after `spec.md` is accepted and before the plan. You write two Markdown files in the slice folder, one visual, and one `## Approval needed` item per screen. A named person's yes on each screen is recorded later with `/crav1-record-approval`. The plan covers only screens with that yes.

Command: `/crav1-design-ui`. It sits in Specify, next to `/crav1-plan-from-spec`. It is a later skill, not a starter option. When the user asks for startup options, name only `/crav1-spark-to-spec`, `/crav1-ideas-to-spec`, `/crav1-bundle-to-specs`, `/crav1-existing-to-specs`, `/crav1-read-environment`, and `/crav1-fix-bug`. `/crav1-tighten-and-plan-ready-to-build` opens this skill on its own when the slice has a UI.

**The written Markdown is the source of truth.** `ui/design.md` is the visual file: look, layout, colours, fonts, and the tokens. `ui/experience.md` is the behaviour file: the screens and windows, their states, their interactions, and the UI acceptance checks. When a picture, a Salt block, a Mermaid block, or the HTML mock disagrees with the Markdown text, the Markdown text wins. Say so when you see the disagreement, and fix the picture.

## Choice words (1.211.0)

Exact words, no flags. A word in the invocation takes that choice without asking.

- `with-mock`: also write the throwaway HTML mock under `ui/mock/`.
- `skip-mock`: no HTML mock this run. The visual is PlantUML Salt, Mermaid, or text art inside the Markdown.

With no word, the visual card in step 3 asks. A run with no person in the chat (a bot or a scheduled job) writes nothing. It prints the status from step 1 and stops. When no word was given it says `Missing choice. Use one of: with-mock, skip-mock.`

## Find the spec

The spec folder is the user's @-mention, or the one folder `<interpreter> -X utf8 <skill crav1-tasks-ready-to-build>/scripts/resolve_spec.py "<query>" --root docs/specs` prints, as `crav1-docs/reference/running-scripts.md` says. Several matches: list them and stop. No name: ask which slug.

## Route first

Run `<interpreter> -X utf8 scripts/ui_screens.py status --root <spec-folder>`. Pick the interpreter as `crav1-docs/reference/running-scripts.md` says. It writes nothing. Read its `ui` value:

- **`no`**: the slice clearly has no user-facing UI, or `spec.md` already says `UI: none`. Say `No UI step: <why>.` in one line, write nothing, and end with Run next `/crav1-plan-from-spec <slug>`.
- **`unclear`**: the spec names a screen, a button, a dashboard or a click, and there are no `ui/` files and no `UI: none` line. Ask once:

Card: Does this slice have a user-facing UI to design before the plan?
- **Design the UI (Recommended)** (`design`): write the screens, their states, interactions and checks, then one sign-off item per screen before the plan.
- **Skip, there is no user-facing surface** (`no-ui`): add one `UI: none` line with the reason to spec.md, so the plan and the walk do not ask again.

  On `no-ui`, show the line `UI: none (<reason in a few words>)` under the spec title, write it after the closing yes, and end with Run next `/crav1-plan-from-spec <slug>`. That line is the only write on that path.
- **`yes`**: `ui/` names screens already. Show one line per screen from `screens`: its label, its state (`approved`, `waiting`, `changed`, `new`, `removed`), and its `why`. A `changed` screen had a material change and its yes is cleared; a `minor` change kept the yes. Then go on with the screens the user wants to change or add.

A `binaries` list that is not empty: name each file and stop before any write. Screenshots are never stored in the repo. Read [references/feedback.md](references/feedback.md).

## Steps

1. **Read.** `spec.md` (users, journeys, acceptance, non-goals, constraints), `docs/system/` notes that name UI patterns, existing `ui/` files, and, when `## In the code` names paths, the existing screens, components and theme in that code. Existing UI patterns win over new ones unless the spec says otherwise. A requirement the spec does not state is not designed here: name it and route it to `/crav1-add-to-spec <slug> <text>` at the end.
2. **Screens and states.** Read [references/files.md](references/files.md). List the screens and windows the journeys need, each `### <name> (S<n>)`, with its path or window. For each screen write at least the empty, loading, error and full-of-data states, plus the slice's own states, the interactions that apply (click, keyboard, zoom, pan, resize, dock), and the UI acceptance checks as yes/no lines a stranger could mark, each with its id `(S<n>-C<n>)`. Write the look, the layout per screen, and the tokens in `ui/design.md`. Start from this skill's `assets/design.md` and `assets/experience.md` (the same files as `docs/specs/_template/ui/`).
3. **One visual, always.** Read [references/visuals.md](references/visuals.md). Suggest one visual type with a one-line reason: the HTML mock when zoom, docking, motion or a clickable flow matter; PlantUML Salt for a static layout; Mermaid for flows and states. The user confirms it, changes it, or adds another type. Text art only when none of those can be rendered. A choice word already given answers this card.
4. **Feedback.** The user may answer with text or attach screenshots. Read [references/feedback.md](references/feedback.md) when a screenshot is attached. You look at it only to understand the feedback. What it shows is written as text in `ui/experience.md` or `ui/design.md`, and that text is what gets approved.
5. **Sign-off items.** Read [references/sign-off.md](references/sign-off.md). Run `<interpreter> -X utf8 scripts/ui_screens.py sync --root <spec-folder> --person "<who>"` without `--yes` and show its `actions` lines: a new screen gets its own item, a material change clears that screen's yes and says why, a typo or non-UI edit keeps it and says why. The person is the one the spec names as signing off the UI; when none is named, ask for that value in the same batch as the visual card.
6. **One closing yes.** Show the files you will write, the visual, and the `sync` lines, then one yes card for all of them. On yes write the Markdown, the mock when chosen, then run the same `sync` command with `--yes`. That is the only write to `spec.md`.

## Hard rules

- **Refuse application code.** No components, styles, routes, or a scaffold. The HTML mock is throwaway: it lives only under `ui/mock/`, is never shipped, is never copied into the app, and is not a plan input.
- Never write `Approved:`. The yes is recorded with `/crav1-record-approval` as an `Approved:` line on that screen's item. There is no second approval syntax.
- No binary file under `docs/specs/`: no screenshot, no exported image, no PDF. Salt, Mermaid, text art and the HTML mock are text.
- No screenshot or pixel comparison. Build checks the written UI checks, traced into `tasks.md` as `(verify: ui — <named check>) (spec: ui/experience.md S<n>-C<n>)`.
- Leave `plan.md`, `tasks.md`, `verify.md`, code and `docs/system/` alone. In `spec.md` write only the screen items, their `Screen:` and `Cleared:` marks through `ui_screens.py sync --yes`, and the `UI: none` line on the skip path. Do not edit requirements.
- Do not commit, push, or open a pull request.
- When `/crav1-design-architecture` also applies to the slice, this step runs first; the architecture design may then read `ui/`.

## Run ending (1.122.0)

End as [run-ending.md](../crav1-docs/reference/run-ending.md) says. After the items are written: Run next with the label `Record each screen's yes, since the screens are written and wait for sign-off:` above `/crav1-record-approval` alone in its code span. When every screen already has its yes and nothing material changed: `Write the plan for the signed-off screens:` above `/crav1-plan-from-spec <slug>`. Add the `Uncommitted:` line when files changed.
