# crav1-what-do-we-know-about-this: answer sections

Read only when the pointer in `SKILL.md` sends you here. Moved word for word from `SKILL.md` in 1.86.5; the rules are unchanged.

## Answer sections

1. **Verdict** — one line. Example shape: finished code that is switched off, and the open item is a decision.
2. **What it is** and **Why it's in this state** — two short paragraphs. Use the words the docs already use.
3. **The decision** — when one is still open. Name where it is open (the file, the heading, or the question). Each option the docs already list gets one line for and one line against, then its own checkbox task list. Do not invent an option. When the options are not written, say that, and do not invent the lists.
4. **Either way** — tasks that apply whatever is decided. An `Ask <person>: …` line uses a person, or a role, the docs already name, plus the file and heading. Do not guess a person. Do not turn a role into a name. When a slice exists and this section is shown, the last task updates that slice’s `spec.md`. Those checkboxes stay in the chat. This command does not edit `tasks.md` or `spec.md`.
5. **Do not touch** — guardrails the docs already state. Each one has the date that note or ADR gives. When the note has no date, say the date is not written. Do not invent a date.
6. **Seen only live** — a setting or a change that no doc mentions. Each line says `Live read.` A fact the docs already state stays out of this section.
7. **Research marked stale** — a `Stale since` line under `## Research findings`, or a stale block on a note that section links to. Quote the mark. Name the path. This is not **Stale notes**. Do not clear the mark.
8. **Stale notes** — an older note that disagrees with a later note, or with a live read. Say which note is wrong and what to trust instead. A short note is not stale. A research mark is not this section.
9. **Tracked elsewhere** — work items, open pull requests, and branches. When the live read ran, this section stays, and `none` is a real line. Each line says `Live read.` When the user picked Skip, leave this section out.
10. **Source** — existing slice, found slice, or no slice (candidate). Then the files and the reads used.

**Unexplained** is for a code-only hit with no spec and no architecture note. What the code shows goes there. What the code does not say stays unexplained. Leave that heading out on every other case.

A line that is a guess ends with `(inference, not in the docs)`. A fact the file or the live read shows does not get that label.

Case 3 names the next command in **Source**. It does not run it.

A gap matching an open question (1.78.0): end `Next: /crav1-show-or-ask-open-questions ask research <its words>`, plus spec if ambiguous. One line per matching question, in its own words, never one line for several (1.90.4).

When the user picked Skip, **Source** includes one line: the live checks did not run, and why.
