# Imported sources

A mail, a transcript, minutes, a chat, a screenshot, a diagram, or another original file that a skill quotes into a spec is an imported source. The quote in the spec stays the words from that source. The original lives in the target project so every verbatim quote can be checked.

This file is the convention. `/crav1-add-to-spec` follow it. A skill that quotes the same kinds of files into a spec follows it too. Drop-in: `.cursor/skills/crav1/crav1-add-to-spec/references/sources.md`. Plugin, from this skill: `references/sources.md`. Plugin, from another skill: sibling `skills/crav1-add-to-spec/references/sources.md`.

Do not apply this file to a short fact the user typed for one spec, to a fact seen in an environment, to a test suggestion, or to a quote of repository code.

These skills write the files. They do not commit. They do not push. They do not open a pull request. The user commits.

Kind sections live in their own files. A mail follows [sources-mail.md](sources-mail.md) (**Mails**, **Images inside a mail**). A binary file handed over as its own file, and each image inside a mail, follows [sources-binary.md](sources-binary.md) (**Binary files**). A paste, or a text file that is already text, needs neither. Moved word for word from `sources.md` in 1.71.1; the rules are unchanged.

Rare and flagged sections live in their own files. When the check below flags an item or finds a secret, follow [sources-flagged.md](sources-flagged.md) (**Transfer data policy**, **The note and the list**, **One question for the recommendations**). A PDF with black-boxed text, a `.docx`, an ambiguous date, a newer or older version, sources that disagree, and a run with no window follow [sources-rare.md](sources-rare.md) (**Reading the document**, **Versions and conflicts**, **Headless runs (two-pass)**). Temporary files, an image the kit cannot view, and duplicate images are in [sources-binary.md](sources-binary.md). Moved word for word from `sources.md` in 1.71.2; the rules are unchanged.

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
