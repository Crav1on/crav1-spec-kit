# Explain this code

Kit not in this project yet? [Install first](install.md) (Cursor and Claude Code; the slash commands match, the files do not).

Use this when you want **one piece of code explained**: a file, a function, a selection, or a pull request diff. `/crav1-explain-this-code` reads that code and the code it calls, and explains it in the chat. It never guesses. It changes nothing.

The whole system, from the notes in `docs/system/`, is [from the system notes](from-explain-existing-system.md) (`/crav1-explain-existing-system`). This command reads code, not the notes.

This is cross-cutting. It is not its own lane. It can run any time and does not start Specify, Plan, or Build.

## First prompt

```text
/crav1-explain-this-code what it does
@src/orders/service.py
```

No target named and nothing selected: it asks what to explain.

## The opening question

It asks one question. The recommended option is first. It skips the question when your wording already answers it ("why is this done this way" is what and why).

| Option | Choice word | What you get |
| --- | --- | --- |
| What it does (Recommended) | `what it does` | A walk-through in run order, from reading the code and the code it calls, with file and line. |
| What and why | `what and why` | Adds reasons, only from the code itself, specs, plan decisions, system notes, and commits. A step with no stated reason says `no stated reason found`. |
| Teach the language | `teach the language` | Adds idiom notes as they come up (language detected from the file), a one-line comparison to a language you know (it asks; skip is fine), and a few topics to look up next. |

A headless or bot run with no choice word stops and lists the three words.

Every answer includes a small mermaid flowchart of what the code does, built only from what was read.

## Save as .md

Nothing is written to `docs/` or anywhere in the kit layout. At the end it offers `Save as .md`. On yes it shows the full path and asks first. The default is your Downloads folder (`~/Downloads`, or `%USERPROFILE%\Downloads` on Windows) as `explain-this-code-<target>-<date>.md`. Name another path to save elsewhere. It never writes into the repo unless you name a path there.

The file opens with a header naming the paths it covers and the commit it was based on (`<branch>@<short sha>`). The kit never reads or indexes it.

## What it reads and writes

- Reads: the named code, the workspace code it calls, and for what and why also `docs/specs/`, plans, `docs/system/`, `git log`, and `git blame`.
- Writes: nothing, except the saved .md when you say yes.
- Leaves alone: code, specs, `docs/`, and the kit layout.

Reference page: [explain this code](reference/skills/crav1-explain-this-code.md)
