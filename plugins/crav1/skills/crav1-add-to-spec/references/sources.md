# Imported sources

A mail, a transcript, minutes, a chat, a screenshot, a diagram, or another original file that a skill quotes into a spec is an imported source. The quote in the spec stays the words from that source. The original lives in the target project so every verbatim quote can be checked.

This file is the convention. `/crav1-add-to-spec` follow it. A skill that quotes the same kinds of files into a spec follows it too. Drop-in: `.cursor/skills/crav1/crav1-add-to-spec/references/sources.md`. Plugin, from this skill: `references/sources.md`. Plugin, from another skill: sibling `skills/crav1-add-to-spec/references/sources.md`.

Do not apply this file to a short fact the user typed for one spec, to a fact seen in an environment, to a test suggestion, or to a quote of repository code.

These skills write the files. They do not commit. They do not push. They do not open a pull request. The user commits.

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

## Mails

A mail goes in as a `.eml` text file. Keep the CRLF line endings. Do not convert them to LF. A paste that used LF is written with CRLF. The README says the paste was written with CRLF.

Read the project's `.gitattributes`. If that file does not already contain the line `*.eml -text`, ask the user once, before adding it. Yes or no. Use the questions tool when it is available. One question for the run, not once per mail.

The question is: Add `*.eml -text` to `.gitattributes` so Git keeps the CRLF line endings on mail files?

1. **Yes.** Add that line on its own line. Create `.gitattributes` only when the file is missing. Do not rewrite other lines.
2. **No.** Do not add the line. The README says `.gitattributes` was left as it was, so a later commit may change the line endings.

Do not add the line without that yes. When the line is already there, do not ask.

A mail follows this section. Each image inside the mail, inline or attached, also follows Images inside a mail. The binary section does not replace the mail. An attachment the user also supplied as its own file follows the binary section and lives in the same folder when it belongs to that mail. A non-image part stays in the `.eml`.

## Binary files

For every binary file the user hands over as its own file, ask which of these four options to use. One question per file. Options only. Use the questions tool when it is available. Name one recommendation in the question. The user picks. Do not pick for them.

An image inside a mail uses the list in Images inside a mail. Ask once for that list. The four options are the same.

1. **Commit as-is.** The file goes in the folder unchanged.
2. **Compress, then commit.** For a screenshot: crop off taskbars and app bars, no sharpening, WebP. Show samples at q70, q85, and lossless so the user picks the quality. Write only the picked file into the folder. This is the recommendation for a screenshot that is not above about 10 MB.
3. **Convert to text and commit that instead.** The original stays outside the repo. A `.docx` or a PDF transcript becomes `transcript.md`, word for word, with speakers and timestamps when the original has them. Check that text word for word against the original before the file is written. Do not invent a speaker or a timestamp. The README says where the original lives. This is the recommendation for a document that is not above about 10 MB.
4. **Leave it out and only reference where the original lives.** The folder does not contain the file. The README records that place. When the user already pointed at the file, that place is the reference. When they did not, ask where it lives. Do not guess. This is the recommendation when the file is above about 10 MB.

For any other binary under about 10 MB, the recommendation is commit as-is.

For an image inside a mail that is not above about 10 MB, the recommendation is convert to text when the image is a diagram, a table, or text that can be reproduced exactly. Otherwise the recommendation is compress. An image that is a diagram and a table is convert to text. Text that can be reproduced exactly means the whole image can be written again as words, a markdown table, or a Mermaid diagram. A photo or a screen that would drop part of the picture is compress.

When a file is above about 10 MB, recommend leave-it-out even when it is a screenshot, a document, or an image inside a mail. Still offer all four options. The size is the file as offered, or that image part, before a compress.

Git LFS (Large File Storage) is a note only. It is not an option. It needs repo setup the kit does not do.

The README records which option was used.

Screenshot samples: crop first, then encode three WebP files, q70, q85, and lossless. Do not sharpen. Show the three to the user with the quality named on each. Stop until the user picks one. Write only the picked file into the folder. Remove the other two. Do not leave the samples in the source folder. If no encoder is available, say so and ask the user to pick another of the four options. Do not install an encoder. An image inside a mail uses the same samples. The picked image replaces that part, as Images inside a mail says.

A text file that is already text, such as `.txt`, `.md`, or `.vtt`, is not a binary file. Store it unchanged. A `.docx` or a PDF is a document and gets the four options.

## Images inside a mail

A mail can hold images inline, or as attached image parts. List every one before the folder is written. Nothing is dropped to keep the list short. Read each image before the question. When a secret is readable in an image, commit as-is is not an option for that image. Secrets says what is written instead. A mail with no image skips this section.

Number each image. The line says inline or attached, the file name or content id when the mail has one, and a short line of what the image shows. The line ends with the recommendation from Binary files: `Recommendation: convert to text.`, `Recommendation: compress.`, or `Recommendation: leave it out.`

### One question for the images

After the list, one question when there is at least one image. Three answers. Use the questions tool when it is available. Stop until the user picks.

1. **Accept all recommendations.**
2. **Go through them one by one.** The recommendation is shown on each image. The four options are the answers.
3. **Change some.** The user names images and the option, for example convert 2, compress 4.

Accept all recommendations applies every listed recommendation.

Go through them one by one asks the four options for each image. One image at a time. Options only. Use the questions tool when it is available. The question shows the recommendation. Stop until the user picks.

Change some waits for the user to name the images and the option. The named option replaces the recommendation for that image. An image they do not name keeps its recommendation. When a number is not on the list, or the reply names an image and no option, ask again. Do not guess.

The transfer data policy `auto-accept` applies to keep and redact recommendations. Apply it to these image recommendations only when the rule text clearly covers them. The template says auto-accept applies the keep and redact recommendations. That line does not cover the four image options. Ask this question. A rule the user edited covers the image recommendations only when its own text says so, for example that auto-accept applies to embedded-image options. A keep and redact line is not that cover. Do not add an image choice to the rule. Do not rewrite the rule for this.

When the option is compress, the quality samples in Binary files still run. Accept all does not skip that pick. Stop until the user picks a quality. That pick is part of the answer.

Do not write the source folder until every image has an answer. The transfer data policy file may still be written when the user says yes, as Personal data says.

### What each option does to the part

1. **Commit as-is.** That image part stays in the `.eml` unchanged.
2. **Compress, then commit.** Replace that image part with the picked WebP. Same crop, no sharpening, and the same three samples as a screenshot. Keep the content id when the part had one. Set the type to `image/webp`. Keep the CRLF line endings. Do not write a second copy of the image next to the `.eml`. The README names the image and the quality. The `.eml` is then no longer the untouched original. The README says so.
3. **Convert to text.** Remove that image part from the `.eml`. Leave a short placeholder where the image was shown, naming the new file: `[Image converted to text: <name>.md]`. When the image was only an attachment, add that line at the end of the text body. Write `<name>.md` in the same `docs/sources/YYYY-MM-DD-<slug>/` folder. The name comes from the image file name. Lowercase. Hyphens. Do not put a person's name in the name. When the mail shows no file name, use a short name from what the image shows. When that name is already used in the folder, add the list number. The file holds the image's text word for word. A diagram is a Mermaid redraw. A table is a markdown table. An image that has both holds both. Check that text word for word against the image before the file is written. Do not invent a label, a word, or a box the image does not show. The README notes the conversion and names the file. The README says the `.eml` is no longer the untouched original.
4. **Leave it out.** Remove that image part from the `.eml`. Leave a short placeholder where the image was shown: `[Image left out: <name>]`. When the image was only an attachment, add that line at the end of the text body. Use the same name rules as convert to text. The folder does not contain that image. The README notes the leave-out and names the image. The README says the `.eml` is no longer the untouched original.

Put the placeholder where that image was shown. A mail with a plain part and an HTML part gets the placeholder in both. Do not ask where an image that lived only in the mail now lives. The `<name>.md` from convert to text is the file the folder stores.

Keep the CRLF line endings on the `.eml` after any of these edits. When every image is commit as-is, and no later section changes the file, the `.eml` stays the untouched original.

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

Number each item that has a recommendation. The line shows the text, the kind, and where it sits. The line ends with `Recommendation: keep.` or `Recommendation: redact.`

List each unplaced item after the numbers. The line shows the text, the kind, and where it sits. The line says there is no recommendation.

List secrets last. One line per kind. Do not number them. Do not show the value. The line says redacted.

### One question for the recommendations

Ask this question when there is at least one numbered item, and the rule or this run says review. One question. Three answers. Use the questions tool when it is available. Stop until the user picks.

1. **Accept all recommendations.**
2. **Go through them one by one.** The recommendation is shown on each item.
3. **Change some.** The user names items to flip, for example keep 3, redact 5.

Accept all recommendations applies every numbered recommendation.

Go through them one by one asks keep or redact for each numbered item. One item at a time. Options only. Use the questions tool when it is available. The question shows the recommendation. Stop until the user picks.

Change some waits for the user to name the items. The named choice replaces the recommendation for that item. An item they do not name keeps its recommendation. When a number is not on the list, or the reply does not name an item, ask again. Do not guess.

When the rule or this run says auto-accept, do not ask that question. Apply each numbered recommendation. That auto-accept covers these keep and redact lines. Images inside a mail says when it also covers an image recommendation.

Unplaced items are still asked one at a time, whatever was picked, including auto-accept. Options are keep and redact. There is no recommendation. Use the questions tool when it is available. Stop until the user picks.

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
