---
name: crav1-2-show-sot
description: >-
  Read sot/ and answer what we know. Use when the user runs
  /crav1-2-show-sot with no word, none, facts, decisions, assumptions,
  or about-<topic>. Writes nothing.
---

# Show SoT

Read-only. This skill writes nothing and does not commit. The same words apply in Cursor, Claude Code, and Codex.

| Word | What it shows |
| --- | --- |
| (none) or `none` | the index, newest first |
| `facts` | cited facts and their quotes |
| `decisions` | the decision log, superseded entries marked |
| `assumptions` | open and closed assumptions |
| `about-<topic>` | passages and decisions that mention the topic |

A word in the invocation is taken. Do not ask. If the word is not one of these, run the engine anyway. It stops and lists the valid words. Print that list and stop. Do this in chat and in a headless run.

Run `python -X utf8 -m crav1_2 show-sot` and the word. `PYTHONPATH` is `~/.crav1-2/engine`, or `v2` in this kit repo. The project is the working directory. Add `repo <path>` only when it is somewhere else.

Print the `text` field. If it has a broken-pointer section, include it. Do not add a `Next:` line. Do not tell the user to edit a file. There is no card.
