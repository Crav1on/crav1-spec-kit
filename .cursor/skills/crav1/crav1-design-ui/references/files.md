# The two UI files

Read this when you write or change `ui/design.md` or `ui/experience.md`. Both live in the slice folder, `docs/specs/<slug>/ui/`. Start from this skill's `assets/design.md` and `assets/experience.md`. Keep what is already there; add and change only what the user asked for.

The written Markdown is the source of truth. A picture, a Salt block, a Mermaid block, or the HTML mock that disagrees with the text loses. Fix the picture to match the text, never the other way round.

## Screens and their ids

- One `### <name> (S<n>)` heading per screen or window, in `ui/experience.md`, for example `### Orders list (S1)`. The same heading in `ui/design.md` holds that screen's layout.
- The id stays when the name changes. A new screen takes the next free number. Never reuse the id of a removed screen.
- The `## Screens` table at the top of `ui/experience.md` lists every screen with its path or window and one line on what it is for.
- A `Path:` line (a route such as `/orders`) or a `Window:` line (a desktop window such as `Order editor`) sits under the heading.
- A name with `<` or `>` is a template placeholder. The script ignores it.

## ui/experience.md: behaviour

Under each screen:

- `#### States`: at least **Empty**, **Loading**, **Error**, and **Full of data**, one bullet each, saying what the user sees. Add the slice's own states, for example `Offline`, `Read-only`, `Saving`, `Conflict`, `No permission`. A state the spec does not need is not invented.
- `#### Interactions`: the ones that apply. **Click**, **Keyboard** (tab order, shortcuts, Enter and Escape), **Zoom** and **Pan** (a canvas, a map, a chart), **Resize** (narrow and wide), **Dock** (windows that dock or undock). Leave out the ones that do not apply.
- `#### Flow`, optional: a Mermaid state or flow diagram, when step 3 picked Mermaid.
- `#### Checks`: the UI acceptance checks. Each is a yes/no line a stranger could mark by looking at the running screen, ending with its id:

  ```text
  - [ ] With no orders, the list shows "No orders yet" and a New order button. (S1-C1)
  ```

  Not `looks good`, not `is fast`, not `is intuitive`. A check names what is on the screen, what happens after an action, or what a keyboard key does. Each state and each interaction you wrote gets at least one check. Ids are per screen: `S1-C1`, `S1-C2`, then `S2-C1`.

## ui/design.md: the look

- `## Look`: two or three sentences on the feel and the density, and what the eye lands on first.
- `## Tokens`: one fenced `yaml` block in the DESIGN.md style, with `colors`, `typography`, `spacing`, and `radius`, then one short line per group on when it is used. Tokens live here. There is no separate tokens file. Reuse the product's existing tokens when the code or `docs/system/` names them.
- `## Visual`: the visual type and its one-line reason, and the mock path or `none`.
- `## Screens`: per screen, `### <name> (S<n>)` and `#### Layout`, the regions top to bottom and left to right, plus a Salt block when Salt was chosen.

## What a run changes

A sign-off is per screen. Changing the layout, the states, the interactions, the checks, the name or the path of a screen that already has its yes clears that yes when `sync --yes` runs. A typo fix, a case or punctuation change, a change to the look or the tokens, or a change outside the screen sections keeps it. Say which kind of change you made before the closing yes. Step 5 of this skill's `SKILL.md` checks it with the script.
