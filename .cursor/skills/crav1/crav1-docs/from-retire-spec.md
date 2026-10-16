# Retire, merge, park, or convert a spec

Kit not in this project yet? [Install first](install.md) (Cursor and Claude Code; the slash commands match, the files do not).

Use this when a spec should **stop counting as work**: it is done or dead, it belongs in another spec, it should wait, or it was only ever reference knowledge. `/crav1-retire-spec` handles one spec at a time. It always shows a summary of every change and waits for your yes. It never deletes anything: a spec that moves leaves a one-line `Moved:` pointer at its old path.

This is cross-cutting. It is not its own lane. It can run any time and does not start Specify, Plan, or Build.

## First prompt

```text
/crav1-retire-spec retire
docs/specs/<slug>/
```

No spec named: it asks which, one option per spec.

## The opening question

It asks one question and a one-line reason. The recommended option is first. It skips the question when your wording already answers it.

| Option | Choice word | What happens |
| --- | --- | --- |
| Retire (Recommended) | `retire` | Moves to `docs/specs/retired/<slug>/` with `Retired: date, reason`. The feature-index row is removed. Links to it are listed for you to fix. Every skill skips `docs/specs/retired/`. |
| Merge | `merge` | Moves content, open questions, and decisions into a target spec, marked `(from <slug>)`. Name the target, or it suggests only real fits, each with a reason (shared feature area, overlapping requirements, same system in landscape, links), best first. When nothing fits it says `no good merge fit found` and offers park, retire, or convert to note. The source moves to `docs/specs/retired/`. |
| Park | `park` | Stays in place with `Parked: date, reason`. Plan, build, and ado-sync push skip it. Help and open questions list it as parked. |
| Convert to note | `convert to note` | Becomes `docs/notes/<date>-<slug>.md` with a `Source:` line and an index row, plus one line under `## How the parts connect` in landscape. The feature-index row is removed. A converted note has no research owner, so no revisit request. |

A headless or bot run with no choice word stops and lists the four words.

## Parked specs and new input

While a spec is parked, `/crav1-add-to-spec` writes nothing into it. When input matches it, the **full input** is saved once as a note that says `Waiting for <slug> (parked)`. Active specs that match still get their points, plus a link to that full note, and are added to its `Used by`. The note is never marked absorbed: it stays the shared full source. Help shows how many notes wait for each parked spec, and open questions shows them as `waiting for parked <slug>`, not as open work.

## Un-park

```text
/crav1-retire-spec un-park docs/specs/<slug>/
```

It re-reads each waiting note in full and suggests what fits the spec now, including points that already went to other specs. After your yes it removes the `Parked:` line, adds the chosen points, and adds the spec to each note's `Used by`.

## What it reads and writes

- Reads: the named spec, the other specs, `docs/system/landscape.md`, and `docs/notes/`.
- Writes, after a yes: the moved spec and its pointer, the feature index, and for merge or convert the target spec or the note, its index row, and the landscape line.
- Leaves alone: every other spec, and inbound links (listed, not rewritten). Never deletes.

Reference page: [retire spec](reference/skills/crav1-retire-spec.md)
