# Reports: common rules

Read with exactly one `reports/<type>-<depth>.md`, only when the message has a `report-*` word (1.104.0).

## Before writing

1. Run the same match as the free-form answer. Two or more close hits: list them and ask. No hit: say so and stop; do not write a report about nothing.
2. Live reads: the ones `references/live-reads.md` describes, plus any read-only source the host already has for the topic (for example the pull request on its forge). When a source needs a sign-in, a permission, or a tool that is not there, ask first, one prompt: what it is, why the report wants it, **Allow** or **Skip**. Never sign in, mint a token, or install a tool on your own. Production stays shape and connections only, after the same yes or no as `/crav1-read-environment`. Never data, never a secret value.
3. Label every line that needs it: a fact from a live source ends `Live read.`; a guess ends `(inference, not in the docs)`. A fact from a file names the file.

## Diagrams

Visual first. Draw a Mermaid diagram wherever a picture explains faster than prose (`flowchart`, `sequenceDiagram`, `gitGraph`, `stateDiagram-v2`, `erDiagram`), and skip it where it does not. Draw only the diagrams the report file lists for this depth; C4 only when that file says so. Each diagram gets one plain sentence under it saying what to look at. Node names come from the docs; an invented node is labelled as inference.

## The file

- Name: `<topic-slug>-report-<type>-<depth>-<YYYY-MM-DD>.md`.
- Where: the user's Downloads folder when you can write there; otherwise the system temp folder. Never inside the project, and never commit it.
- First lines: the title, then `Report: report-<type>-<depth> · <date> · kit <version>`, then the Verdict.
- Leave out a section that has nothing under it. Do not print placeholders.

## In chat

Always: the Verdict line, then a link to the file (or attach it), then the folder it went to and why when it is not Downloads. Never leave the report only on disk.
