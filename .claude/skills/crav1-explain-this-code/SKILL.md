---
name: crav1-explain-this-code
description: >-
  Explain a piece of code: a file, a function, a selection, or a PR diff.
  Asks what to explain when nothing is named. Opens with one question:
  what it does (Recommended), what and why, or teach the language. Skips
  it when the wording answers; a headless or bot run with no choice word
  stops and lists the words. Answers only from the code it read and the
  code that code calls. Never guesses. Why comes only from the code,
  specs, plan decisions, system notes, and commits, else "no stated
  reason found". Always includes a small mermaid flowchart built only
  from what was read. Read-only, in chat. At the end offers Save as .md,
  to the user's Downloads folder by default, only after asking and
  showing the full path; never into the repo by default. Not
  /crav1-explain-existing-system.
disable-model-invocation: true
icon: code
color: blue
---

# Explain this code

You explain one piece of code in the chat. You read the code and the code it calls. You do not guess. You change nothing. You write no file unless the user says yes to **Save as .md**.

This is cross-cutting. It is not its own lane. It is a standalone skill and can run any time. It does not move work into Specify, Plan, or Build.

This is not `/crav1-explain-existing-system`. That reads the product's system notes in `docs/system/` and explains the whole system. This command reads code and explains one piece of it.

## What to explain

The target is everything after `/crav1-explain-this-code`, every `@`, the editor selection, or a pull request (number, URL, or "this PR" with a branch diff). One of:

- a file
- a function, class, or method (by name, with or without its file)
- a selection
- a pull request diff, or a branch diff

When no target is named and there is no selection, ask what to explain, and stop until the user answers. A headless or bot run with no target stops and says: `Missing target. Name a file, a function, a selection, or a PR.`

A function name that matches more than one place: list the matches and ask which. Do not pick one.

## Opening question

Ask one question, with the questions tool when it is available. The recommended option is first:

1. **What it does (Recommended).** A walk-through based only on reading the code and the code it calls.
2. **What and why.** Adds the reasons, from stated sources only.
3. **Teach the language.** Adds language notes for someone new to it.

Skip the question when the wording already answers it: "what does this do", "walk me through" is 1; "why", "why is it done this way", "what was the reason" is 2; "teach me", "I'm new to <language>", "explain the syntax" is 3.

## Choice words

Exact words for bots and scripted runs. There are no `--flags`.

- How deep: `what it does` / `what and why` / `teach the language`.

When the invocation contains one of these words (for example `/crav1-explain-this-code what and why @src/orders.py`), take that choice and do not ask. This holds for a person, a bot, or a headless run.

When a choice is missing and the run is headless or started by a bot (no person in the chat to answer), do not guess. Stop and name the valid words: `Missing choice. Use one of: what it does, what and why, teach the language.`

## Reading

Read the target. Follow each call it makes into the code it calls, when that code is in the workspace, as deep as the explanation needs. Code outside the workspace (a package, the standard library, a remote service) is named as such. Say what its name and the call site show. Do not describe what it does inside.

Never guess. When something cannot be read, say so: `not read: <what> (<why>)`. Do not fill the gap.

## What it does

A walk-through in the order the code runs: inputs, the main steps, branches and loops, side effects (files, network, database, state), what it returns or raises. Name the file and line for each step. Plain words first, then the detail.

## What and why

Everything in **What it does**, plus the reasons. A reason counts only when a source states it:

- the code itself (a comment, a docstring, a name that says it, an assert, a test that pins it)
- the specs (`docs/specs/<slug>/spec.md`)
- plan decisions (`docs/specs/<slug>/plan.md`)
- system notes (`docs/system/`, including `adr/`)
- commits (`git log` and `git blame` on the lines)

Quote or closely paraphrase, and name the source for each reason. When no source states a reason for a step, say `no stated reason found`. Never invent one, and do not offer a likely reason in its place.

## Teach the language

Everything in **What it does**, plus:

- **Idiom notes as they come up.** Detect the language from the file (Python, C#, JavaScript or TypeScript, Go, Rust, and so on). At the line where an idiom appears, add a short note: what it is and why people write it that way, for example a Python decorator, C# async/await or LINQ, a JS closure or promise, a Go goroutine or errors-as-values, Rust ownership or `?`.
- **One-line comparison.** One line comparing an idiom to a language the user knows. If the user has not said which, ask once. If they skip, or the run is headless, leave the comparison out.
- **Topics to look up next.** At the end, a few topics to look up next, drawn from the idioms in this code.

Do not hand off to another persona or skill for a lesson.

## Flowchart

Every answer includes a small mermaid flowchart of what the code does, built only from what was read. Nodes are the steps, decisions, and outcomes from the walk-through. Do not add a node for code that was not read; a call outside the workspace is one node labelled as such. Keep it small: the main path and its branches.

## Read-only

Explain in the chat. Change no code. Write nothing to `docs/notes/`, `docs/`, the specs, or anywhere else in the kit layout. Run no other skill and no command that changes the repo. `git log`, `git blame`, and `git diff` are reads.

## Save as .md

At the end of the answer, offer `Save as .md`. Do nothing unless the user says yes.

On yes, before writing, show the full path and ask to confirm it or name another path. The default path is the user's Downloads folder: `~/Downloads/explain-this-code-<target>-<date>.md`, or `%USERPROFILE%\Downloads\explain-this-code-<target>-<date>.md` on Windows. `<target>` is the file or function name in lowercase with `-` for anything other than letters and digits; for a PR, `pr-<number>`. `<date>` is `YYYY-MM-DD`. Never write into the repo by default; write inside the repo only when the user names that path.

The file starts with a header:

```markdown
# Explain this code: <target>

- Covers: <each path read, with line ranges where it was a function or selection>
- Based on: <branch>@<short sha>
- Mode: <what it does | what and why | teach the language>
- Date: <YYYY-MM-DD>
```

Then the explanation and the flowchart, as shown in the chat. When the working tree has uncommitted changes in a covered path, add `(uncommitted changes)` after the short sha.

The kit never reads or indexes this file. No skill looks for it.

A headless or bot run does not save unless its invocation also says `save` and names a path.

## Stop

Do not change code. Do not write any other file. Do not run `/crav1-explain-existing-system`, `/crav1-what-do-we-know-about-this`, or any other skill. Naming one is not running it.

## Style

Be concise. Plain words. Point at file and line. Say what is not known instead of guessing.
