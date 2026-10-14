# Data policy for imported sources

When a skill quotes an imported source into a spec (a mail, a transcript, minutes, a chat, a screenshot, a diagram, or another original file), it keeps the original in the product repo under `docs/sources/` so every quote can be checked. Before it writes those files, it checks them for personal data and secrets. This page explains that check in plain words. The full rules, which the skills follow, are in the add-to-spec reference [sources.md](../../.cursor/skills/crav1/crav1-add-to-spec/references/sources.md).

The skills that import a source are `/crav1-add-to-spec`, `/crav1-bundle-to-specs`, and `/crav1-existing-to-specs`. `/crav1-show-or-ask-open-questions` uses the same policy for its drafts.

This is not legal advice. The client's or the employer's data and retention policy comes first.

## What is checked

The check covers the source file, the quote that will go into the spec, text readable in a screenshot or an embedded image, and text in a mail signature. Nothing is dropped to keep the list short.

| Kind | Recommendation |
| --- | --- |
| Work email of a person on From, To, or Cc (not the sender) | Keep |
| Private email | Redact |
| Email the kit cannot place as work or private | None. You choose |
| Office phone, switchboard, or work desk phone | Keep |
| Personal or private mobile, including a mobile in a signature next to the office phone | Redact |
| Phone the kit cannot place | None. You choose |
| Office or company address | Keep |
| Home or other private address | Redact |
| Address the kit cannot place | None. You choose |
| A similar detail | Keep when it is a work contact detail, redact when private, none when it cannot be placed |

The sender's own address is not flagged.

## Secrets

Secrets are always redacted. They are never a choice and never stored in the policy. The kinds are connection strings, shared access signature (SAS) tokens, application programming interface (API) keys, passwords, private keys, and virtual private network (VPN) configs. A secret is listed by kind only, never by value, removed from the file and the quote, and noted by kind in the source folder's `README.md`.

## The once-per-repo policy

The first time a check finds something, the skill asks four questions for the run:

1. Which types should this check cover? This version offers personal data.
2. Apply the recommendations automatically, or review them on each run?
3. Where is this repo hosted? Free text, in your words.
4. Save these answers as the transfer data policy for this repo?

On yes, it writes a project rule from the template [`crav1-transfer-data-policy.mdc`](../../.cursor/skills/crav1/crav1-add-to-spec/assets/crav1-transfer-data-policy.mdc). On Cursor that is `.cursor/rules/crav1-transfer-data-policy.mdc`. On Claude Code it is `.claude/rules/crav1-transfer-data-policy.md`. A later run reads it, shows one line with what it chose, and does not ask again. The kit never writes a user-level policy.

To change the policy, edit that file. To get the questions again, delete it.

## What you see on a run

When something is flagged, the skill shows a short note once, marked as not legal advice, naming where the repo is hosted. Then it lists the items: numbered items with a recommendation, then the items it cannot place, then secrets by kind.

With `review`, it asks one question: accept all, go through them one by one, or change some. With `auto-accept`, it applies the keep and redact recommendations. Items with no recommendation are always asked one at a time.

A redact removes the item from the file and the quote and notes the redaction in the `README.md` by kind. The file is then no longer the untouched original, and the README says so. No file is written until every flagged item has an answer, and no unredacted copy is written to the repo.

Removing something after it is pushed means rewriting git history, so the check runs before anything is written. The skills do not commit. You do.

## One policy for Cursor and Claude Code

The transfer data policy is one shared policy with two copies: `.cursor/rules/crav1-transfer-data-policy.mdc` and `.claude/rules/crav1-transfer-data-policy.md`. The kit writes both copies together. When only one exists, it copies it across with the same words. When a repo has two copies that disagree, the kit says so and you pick which one wins; it does not merge them.

## How imports handle hard cases

- **Temporary files** go to a new folder in the system temp folder, outside the repo, and are deleted at the end even when the run fails.
- **Images the kit cannot view** (for example in a headless `-p` run) are never guessed at. The kit says so, leaves the image out, and asks Rhea or you to check it before keep or leave.
- **Headless two-pass mode.** Pass 1 writes its questions to a file in the system temp folder and stops. You answer them, and pass 2 reads the answers and finishes. If the file is gone, the questions are asked again.
- **Partial extracts** get a "Left out" list in the source README: each skipped section or page with a reason.
- **Black-boxed PDF text** is treated as redacted: never copied, marked `[redacted in source]`.
- **Superseded versions** are kept, marked "Superseded by" with a link to the newer one; only the newest is read for specs.
- **Source precedence:** the newest source that records a decision wins; otherwise it becomes an open question. A multi-file intake ends with one conflict pass.
- **Plain uncontested facts** (a date, a name) are applied without asking and listed in the run summary. Decision changes and conflicts are still asked.
- **One folder per document:** `docs/sources/YYYY-MM-DD-<doc-slug>/`, each with its own README.
- **Ambiguous dates** such as `03/04` are kept as written and become an open question, unless the locale or a weekday settles them.
- **Word files** are read with tracked changes accepted but flagged; comments are listed with author and date; spec-relevant ones become open questions.
- **Duplicate images** are stored once, with every place they appear listed, and asked about once.
- **Glossary:** new terms are added freely; rewriting an existing row shows old and new with the source and waits for your yes.

The full rules are in [sources.md](../../.cursor/skills/crav1/crav1-add-to-spec/references/sources.md).

## Related

- [Data layout](data-layout.md) for the source folder and its `README.md`.
- [Glossary](glossary.md).
