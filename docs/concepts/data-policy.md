# Data policy for imported sources

When a skill quotes an imported source into a spec (a mail, a transcript, minutes, a chat, a screenshot, a diagram, or another original file), it keeps the original in the product repo under `docs/sources/` so every quote can be checked. Before it writes those files, it checks them for personal data and secrets. This page explains that check in plain words. The full rules, which the skills follow, are in the add-to-spec reference [sources.md](../../.cursor/skills/crav1/crav1-add-to-spec/references/sources.md).

The skills that import a source are `/crav1-add-to-spec`, `/crav1-meeting-to-specs`, `/crav1-match-dump-to-specs`, `/crav1-intake-to-specs`, and `/crav1-match-to-specs`. `/crav1-ask-open-questions` uses the same policy for its drafts.

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

## Related

- [Data layout](data-layout.md) for the source folder and its `README.md`.
- [Glossary](glossary.md).
