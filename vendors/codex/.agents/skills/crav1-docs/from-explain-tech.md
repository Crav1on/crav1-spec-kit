# Explain a technology

Kit not in this project yet? [Install first](install.md) (Cursor and Claude Code; the slash commands match, the files do not).

Use this when you want **one technology explained** in the context of your specs, for example Private Link or Service Bus. `$crav1-explain-tech` finds where the specs, plans, tasks, design topics and ADRs mention it and explains it in the chat. It changes nothing unless you ask it to save.

One piece of code is [explain this code](from-explain-this-code.md). Everything known about one feature is `$crav1-what-do-we-know-about-this`.

This is cross-cutting. It is not its own lane. It can run any time and does not start Specify, Plan, or Build.

## First prompt

```text
$crav1-explain-tech Service Bus
```

Add `in <spec>` to look in one spec, one design topic or `architecture` only: `$crav1-explain-tech Private Link in orders-api`.

## The short answer

About 150 to 250 words, always in the same order:

1. What it is.
2. How it works, in two or three sentences.
3. Where it shows up, with links to the exact files and sections in your specs.
4. Why it is used, or why it would fit.
5. The main tradeoff.
6. One alternative.

Then Run next. When the specs never mention the technology, the answer says so plainly, explains it in general terms, gives no spec link, and names research as the next step. When a fact is missing, it names who has it: an ADR's deciders, an owner line, or the people under the spec's Approval needed.

## Deeper

`$crav1-explain-tech deeper Service Bus` gives a longer answer with the same sections expanded, plus how the technology fits with the rest of the spec: what it connects to, what depends on it, and which decisions and open questions touch it. Still read-only.

## Save

Nothing is written unless you ask. Say `save` (`$crav1-explain-tech save Service Bus in orders-api`), or answer yes on the card at the end. The short explanation and its links go under `## Technology notes` in the spec's `notes.md`, as a dated entry; the file is created when it is missing. Commit it with `$crav1-finalize-commit`.

## After

The ending is a Run next: explain it deeper, save it, ask for research when the specs do not mention it, or commit a saved note. See [How a run ends](reference/run-ending.md).

Reference page: [explain a technology](reference/skills/crav1-explain-tech.md)
