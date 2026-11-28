# Sign-off, one screen at a time

Read this in step 5. The design step adds the items. The user records the yes with `/crav1-record-approval`. This skill never writes `Approved:`.

## The item

One `## Approval needed` item per screen in `spec.md`, written by `scripts/ui_screens.py sync --yes` through the same `add_item` code in skill `crav1-record-approval` `scripts/approval_needed.py` that plan and build use:

```text
- UI screen Orders list (S1): the product owner approves its layout, states and interactions in ui/design.md and ui/experience.md.
  - Person: the product owner
  - Holds: none (UI screen S1; the plan waits for this yes)
  - Screen: S1, version 3f0c9a1b2d4e, shape name=1a2b3c path=4d5e6f layout=7a8b9c states=0d1e2f interactions=3a4b5c checks=6d7e8f other=9a0b1c
```

- The item names the screen, its id, and both paths. `Holds: none (...)` because no task exists yet; the plan itself waits for the yes.
- `Screen:` is written by the script. It holds the screen's hashes, so a later run can tell a material change from a typo. Never type or edit it.
- The yes is `Approved: <person>, <source date>, <source>, "<quote>" (accepted by <recorder> <date>)` under that item, written by `/crav1-record-approval` with `--item "UI screen Orders list (S1)"` when the person has more than one item.

## What clears a yes

The script compares each screen with its `Screen:` mark and says which kind of change it found and why.

- **Material** (the yes is cleared): the screen's layout in `ui/design.md`, its states, its interactions, its checks, its other notes, its name, or its `Path:` or `Window:` line changed in words or in order. `sync --yes` appends `Cleared: <date>, material change: <why>` under the item and renames the item when the screen was renamed. The `Approved:` line stays in the file; one above the last `Cleared:` line no longer counts. The screen needs a new yes.
- **Not material** (the yes stays): only spelling, case, punctuation or spacing changed inside the screen, or the change is outside every screen section (the look, the tokens, `spec.md` prose). The script refreshes the `version` and writes no `Cleared:` line.
- **New screen**: its own item, on top of the yeses already recorded. Earlier screens stay approved, so a UI can be designed and signed off in steps.
- **Removed screen**: its item stays; the script says it is not in the files and the plan does not cover it.

Say each `sync` line to the user before the closing yes, in plain words, for example `Orders list (S1): material change (the states changed). Its yes is cleared; it needs a new yes.`

## What the plan does with it

`/crav1-plan-from-spec` and the walk's plan step run `ui_screens.py gate`. With no signed-off screen in a UI slice they stop before writing `plan.md` or `tasks.md` and name `/crav1-design-ui` and `/crav1-record-approval` as Run next. With some screens signed off, the plan covers only those; the others are named as waiting. Each check of a signed-off screen is traced into `tasks.md` as `(verify: ui — <named check>) (spec: ui/experience.md S1-C1)`.

## Who warns

`/crav1-add-to-spec` and the walk run `ui_screens.py touches` or `status` and warn when a change touches a signed-off screen. They do not clear the yes; this skill does, on its next run.
