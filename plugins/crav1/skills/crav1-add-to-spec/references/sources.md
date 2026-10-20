# Imported sources

A mail, a transcript, minutes, a chat, a screenshot, a diagram, or another original file that a skill quotes into a spec is an imported source. The quote in the spec stays the words from that source. The original lives in the target project so every verbatim quote can be checked.

This file is the convention. `/crav1-add-to-spec` follow it. A skill that quotes the same kinds of files into a spec follows it too. Drop-in: `.cursor/skills/crav1/crav1-add-to-spec/references/sources.md`. Plugin, from this skill: `references/sources.md`. Plugin, from another skill: sibling `skills/crav1-add-to-spec/references/sources.md`.

Do not apply this file to a short fact the user typed for one spec, to a fact seen in an environment, to a test suggestion, or to a quote of repository code.

These skills write the files. They do not commit. They do not push. They do not open a pull request. The user commits.

Kind sections live in their own files. A mail follows [sources-mail.md](sources-mail.md) (**Mails**, **Images inside a mail**). A binary file handed over as its own file, and each image inside a mail, follows [sources-binary.md](sources-binary.md) (**Binary files**). A paste, or a text file that is already text, needs neither. Moved word for word from `sources.md` in 1.71.1; the rules are unchanged.

## Folder

Each imported source is one folder:

`docs/sources/YYYY-MM-DD-<slug>/`

`YYYY-MM-DD` is the date of the source. Use the date the skill already has. Do not invent a date. When the user skipped the date, the folder is `docs/sources/undated-<slug>/`.

`<slug>` is a short name of that source, taken from the subject, the title, or the file name. Lowercase. Hyphens. Do not put a person's name in the slug. One source, one folder. A second source on the same day gets its own slug. Do not put two sources in one folder. An intake of several documents writes one folder per document, `docs/sources/YYYY-MM-DD-<doc-slug>/`, each with its own README, its own Left out list, its own Superseded by line, and its own images.

A mail and the files that belong to that same mail are one source. A meeting and a screenshot of that same meeting are one source when the user presented them together. When it is unclear whether two files are one source, ask once. Options only. Use the questions tool when it is available. The options are one folder, or one folder per file. Stop until the user picks.

The folder holds the original files, unchanged, except where a later section of this file changes a file, plus `README.md`.

A paste of a mail, a transcript, minutes, or a chat, with no file, is still a source. Write the pasted words as a text file in the folder. A pasted mail is a `.eml` file. The README says it was pasted and there was no original file.

Write the folder once, before the first verbatim quote from that source is written into a spec. Later quotes from the same source reuse the folder. Do not ask the questions below again for a folder this run already wrote. Do not write the folder when no quote from that source will be written.

## README

`README.md` in that folder states:

- What it is: mail, transcript, minutes, chat, screenshot, diagram, or the kind the file is.
- The sender, or the participants, as the source shows them.
- The date and the time, as the source shows them.
- How it was converted: as-is, compressed and the quality, converted to text, or left out.
- Where the original lives, when the file was left out, or converted and the original stays outside the repo.
- For a mail, each image that was converted, compressed, or left out. Name the image and the option. When any image changed, say the `.eml` is no longer the untouched original.
- **Left out**, when the import took only part of the document: one line per skipped section or page range, with a short reason. Then nobody mistakes the extract for the whole document.
- **Superseded by**, when a newer version of this document was imported: a link to the newer folder. See Versions and conflicts.
- For a `.docx`, the tracked changes and the comments. See Word files.
- A redaction, when one was made, including a secret. Name the kind that was removed. Do not paste the removed value. Say the file is then no longer the untouched original.

Do not invent a sender, a participant, a date, or a time. When the source does not show one, say it is not shown.

## Reading the document

### Temporary files

Extract images and other temporary files into a new folder in the system temp folder (for example `mktemp -d`, or `%TEMP%` on Windows), never inside the repo. Delete that folder at the end of the run, also when the run fails or stops early. Write only the picked files into `docs/sources/`.

### An image the kit cannot view

When the kit cannot see an image (for example a headless `-p` run, where images cannot be read), say so. Never guess what it shows from its type, its order, or its size. Leave the image out with the placeholder `[Image left out: <name>, not viewed]`. The README and the run summary list it, and tell Rhea or the user to check it before deciding keep or leave.

### Black-boxed text

Text under a black box in a PDF is redacted, even when it can still be extracted. Never copy it into a file, a quote, or the chat. Mark the spot `[redacted in source]`.

### Word files

Read a `.docx` as if every tracked change were accepted, and flag each change in the README (what changed, who, and when, as the file shows). List each comment in the README with its author and date. A change or a comment that affects a spec becomes an open question in that spec.

### Dates

Never guess an ambiguous date such as `03/04`. Keep it as the source wrote it and add an open question that asks which date is meant. Fill it in only once answered. When the context settles it (the document's locale, a weekday next to it), apply it the normal way.

### Duplicate images

Detect exact duplicates (same bytes) across a document and across the documents of one intake. Store each image once. The README lists every place it appears. Ask the keep-or-leave question once per image.

## Versions and conflicts

### Superseded versions

When an import brings a newer version of a document already imported, or an older one, mark the older folder's README `Superseded by: docs/sources/<newer>/`. Keep the old folder. Read only the newest version for specs.

### Source precedence

When sources disagree, the newest source that records a decision wins. When no source settles it, write an open question. After an intake of several files, run one conflict pass across them before the specs are final.

### Plain facts

A plain uncontested fact, such as a date or a name that no source contradicts, is applied without asking. List every one in the run summary. A fact that changes a decision, or that conflicts with text already in the spec, is still asked.

### Glossary

Add a new glossary term without asking. Before rewriting an existing row, show the old and the new definition side by side with the source, and wait for the user's yes.

## Headless runs (two-pass)

A run with no window (for example `-p`) cannot stop to ask. Run it in two passes:

1. **Pass 1** does everything that needs no answer, writes every question to a file in the system temp folder, names that file, and stops. It writes nothing to `docs/sources/` or a spec that depends on an answer.
2. **Pass 2** is pointed at that file with the answers filled in, applies them, and finishes.

When the file is gone at pass 2 (temp was cleaned), ask the questions again with a new pass 1.

## Personal data

Before the files are written, check the source, and check the quote that will be written into the spec. Flag every item below. Flag a detail that is readable in a screenshot, in an embedded image in a mail (inline or attached), and in text that a convert-to-text will write, including when it sits in a mail signature. Nothing is dropped to keep the list short.

Flag these:

- a work email address of a person in the thread, on From, To, or Cc, other than the sender
- a private email
- an email the kit cannot place as work or private
- an office phone
- a personal mobile number
- a phone the kit cannot place, such as a mobile that may be work or private
- an office address
- a private street address
- a street address the kit cannot place
- a similar detail the kit can place as work or private, or cannot place

The sender's own email address is the sender. Do not flag that address.

A work email is a work address of a person on From, To, or Cc. Recommend keep. A private email is one the source shows as private. Recommend redact. An email the kit cannot place has no recommendation.

An office phone is a number the source shows as an office phone, a switchboard, or a work desk phone. Recommend keep. A personal mobile is a number the source shows as a personal or private mobile, including the sender's mobile in a signature next to the office phone. Recommend redact. A mobile the source does not settle as work or private has no recommendation. A phone the kit cannot place has no recommendation.

An office address is a workplace or company address. Recommend keep. A private street address is a home or other private address. Recommend redact. A street address the kit cannot place has no recommendation.

A similar detail follows the same three outcomes. Recommend keep when it is a work contact detail. Recommend redact when it is private. No recommendation when the kit cannot place it.

### Secrets

Secrets are always redacted. They are never a choice. They are never stored in the rule. Check for them even when the rule does not list personal data. Check what is readable in an embedded image and in text that a convert-to-text will write. A secret in an image is removed from the file that will be written. Commit as-is is not available for that image. Leave it out removes the part. Compress or convert to text writes the image or the text with the secret removed.

The kinds are:

- connection strings
- SAS tokens
- API keys
- passwords
- private keys
- VPN configs

Show each secret in the list by kind only. Do not show the value. Do not ask keep or redact. Remove it from the file that will be written, and from the quote. Note it in the README by kind, not by value.

### Transfer data policy

The rule is once per repo and one shared policy for Cursor and Claude Code. It has two copies. Cursor: `.cursor/rules/crav1-transfer-data-policy.mdc`. Claude Code project: `.claude/rules/crav1-transfer-data-policy.md`. Read the copy for the host that is running. When only one copy exists, use it and write the other copy from it with the same words. When the kit writes the rule, it writes both copies together. When both exist and differ, say so and ask the user which one wins. Do not merge them. Then write the other copy from the one they picked. Do not read or write a user-level file. The user changes the rule by editing or deleting that file.

The template is this skill's `assets/crav1-transfer-data-policy.mdc` (drop-in: `.cursor/skills/crav1/crav1-add-to-spec/assets/crav1-transfer-data-policy.mdc`; plugin: this skill's `assets/crav1-transfer-data-policy.mdc`).

The file lists types, one per line. This version checks personal data. A later type can be added as its own line. It lists `auto-accept` or `review`. It lists where the repo is hosted, in the user's words. It does not list a secrets choice.

When the file exists and those three parts are present, apply it. Show one line that names the file and what it chose: the types, auto-accept or review, and where the repo is hosted. Do not ask the setup questions.

When the file is missing a type, a recommendation, or the hosted line, or the recommendation is not `auto-accept` or `review`, say what is missing. Do not guess. Ask the setup questions for this run. Do not rewrite the file unless the user says yes to save.

When no rule exists, and the check found a flagged item or a secret, ask the setup questions once for the run. A later source in that run uses the same answers. Do not ask them again in that run. Use the questions tool when it is available, except for the hosted question. Stop until the user answers.

1. **Which types should this check cover?** The only option this version offers is personal data. The rule stores one type per line, so a later type can be added.
2. **Apply the recommendations automatically, or review them on each run?** The options are auto-accept the recommendations, and review each run.
3. **Where is this repo hosted?** Free text. Not options. Do not invent a place. The note uses this answer.
4. **Save these answers as the transfer data policy for this repo?** Yes or no. Yes writes the file from the template. Replace `- <type>` with one line per chosen type. This version writes `- personal data` when the user picks that type. Replace `<auto-accept or review>` with `auto-accept` or `review`. Replace `<where this repo is hosted>` with the user's words. Do not leave the angle-bracket placeholders. Do not add a secret, a phone number, or an email address. No uses the answers this run only and does not write the file.

When nothing is flagged and there is no secret, say so in one line and continue. Do not ask the setup questions. Do not show the note.

### The note and the list

When there is a flagged item or a secret, show this note once, above the list. Mark it as not legal advice. Replace `<hosted>` with the hosted words from the rule, or from the answer this run. Do not leave the placeholder.

This is not legal advice. Keeping a work mail as a project record fits, because a spec quote must trace to the source. Keep only what that trace needs. Where the repo is hosted matters. This repo is hosted at <hosted>. The client's or the employer's data and retention policy comes first. Removing something after it is pushed means rewriting git history.

Then show the list.

Number each item that has a recommendation. The line shows the text, the kind, and where it sits. The line ends with `Recommended: keep.` or `Recommended: redact.`

List each unplaced item after the numbers. The line shows the text, the kind, and where it sits. The line says there is no recommendation.

List secrets last. One line per kind. Do not number them. Do not show the value. The line says redacted.

### One question for the recommendations

Ask this question when there is at least one numbered item, and the rule or this run says review. One question. Three answers. Use the questions tool when it is available. Stop until the user picks.

1. **Accept all recommendations.**
2. **Go through them one by one.** The recommendation is shown on each item, and in its question as the first option with ` (Recommended)`.
3. **Change some.** The user names items to flip, for example keep 3, redact 5.

Accept all recommendations applies every numbered recommendation.

Go through them one by one asks keep or redact for each numbered item. One item at a time. Options only. Use the questions tool when it is available. The recommended choice is the first option, labelled ` (Recommended)`, for example `Redact (Recommended)`, then the other. Stop until the user picks.

Change some waits for the user to name the items. The named choice replaces the recommendation for that item. An item they do not name keeps its recommendation. When a number is not on the list, or the reply does not name an item, ask again. Do not guess.

When the rule or this run says auto-accept, do not ask that question. Apply each numbered recommendation. That auto-accept covers these keep and redact lines. Images inside a mail says when it also covers an image recommendation.

Unplaced items are still asked, whatever was picked, including auto-accept, all in one questions call (1.70.0), one question per item. Options are keep and redact. There is no recommendation. Use the questions tool when it is available. Stop until the user picks.

When there is no numbered item, do not ask the three-answer question. Ask the unplaced items. A secret is not a question.

**Keep.** That text stays.

**Redact.** Remove that item from the file that will be written, and from the quote. Note the redaction in the README, by kind, not by pasting the value. The file is then no longer the untouched original. The README says so.

A detail that is readable only in an image follows the same keep or redact. When that image will be compressed, the samples are the redacted image. When that image will be converted to text, the redact removes the item from `<name>.md` and from the quote. When the option for that image is commit as-is, a redact cannot leave the image unchanged. Say so and ask the user to pick compress, convert to text, or leave it out for that image. Do not edit an as-is image.

Do not write the source files until every flagged item has an answer and every image inside a mail has an answer. A secret is already answered by this section. The rule file may be written when the user says yes, before the source files. Do not write an unredacted copy into the repo. When a screenshot or an embedded image will be compressed, the samples are the redacted image. The user commits later. A redacted value is not in the file they will commit. Do not commit.

## Spec lines

Every verbatim quote that comes from an imported source links to that folder. A close paraphrase a skill already allows links to that folder too. The link does not change the words that skill already writes.

On the quote:

`Source: docs/sources/YYYY-MM-DD-<slug>/`

Under `## Trace`, one line for this pass:

`Trace: docs/sources/YYYY-MM-DD-<slug>/ — <what this pass marked new, already there, and inferred>.`

When the quote comes from an imported source and `## Trace` is missing, create `## Trace` and that one line. A quote that is not from an imported source does not create `## Trace` only for a trace line.

The quote label the skill already uses stays. A meeting handoff still starts the quote with `From <kind> <date>.` when there is a date, otherwise `From <kind>.` The `Source:` line is the folder, in addition to that label.

A `Source:` line in a chat list, before the folder exists, stays `<kind> <date>`, or `<kind>`. After the folder is written, the spec lines use the folder path.

## Do not commit

Write the folder, the README, a `.gitattributes` line only after a yes, the transfer data policy only after a yes, and the spec lines. Do not commit. Do not push. Do not open a pull request. Name `/crav1-finalize-commit` when a file changed. Do not run it.
