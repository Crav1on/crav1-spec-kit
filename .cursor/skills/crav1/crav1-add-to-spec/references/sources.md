# Imported sources

A mail, a transcript, minutes, a chat, a screenshot, a diagram, or another original file that a skill quotes into a spec is an imported source. The quote in the spec stays the words from that source. The original lives in the target project so every verbatim quote can be checked.

This file is the convention. `/crav1-add-to-spec` and `/crav1-meeting-to-specs` follow it. A skill that quotes the same kinds of files into a spec follows it too. Drop-in: `.cursor/skills/crav1/crav1-add-to-spec/references/sources.md`. Plugin, from this skill: `references/sources.md`. Plugin, from another skill: sibling `skills/crav1-add-to-spec/references/sources.md`.

Do not apply this file to a short fact the user typed for one spec, to a fact seen in an environment, to a test suggestion, or to a quote of repository code.

These skills write the files. They do not commit. They do not push. They do not open a pull request. The user commits.

## Folder

Each imported source is one folder:

`docs/sources/YYYY-MM-DD-<slug>/`

`YYYY-MM-DD` is the date of the source. Use the date the skill already has. Do not invent a date. When the user skipped the date, the folder is `docs/sources/undated-<slug>/`.

`<slug>` is a short name of that source, taken from the subject, the title, or the file name. Lowercase. Hyphens. Do not put a person's name in the slug. One source, one folder. A second source on the same day gets its own slug. Do not put two sources in one folder.

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
- A redaction, when one was made, including a secret. Name the kind that was removed. Do not paste the removed value. Say the file is then no longer the untouched original.

Do not invent a sender, a participant, a date, or a time. When the source does not show one, say it is not shown.

## Mails

A mail goes in as a `.eml` text file. Keep the CRLF line endings. Do not convert them to LF. A paste that used LF is written with CRLF. The README says the paste was written with CRLF.

Read the project's `.gitattributes`. If that file does not already contain the line `*.eml -text`, ask the user once, before adding it. Yes or no. Use the questions tool when it is available. One question for the run, not once per mail.

The question is: Add `*.eml -text` to `.gitattributes` so Git keeps the CRLF line endings on mail files?

1. **Yes.** Add that line on its own line. Create `.gitattributes` only when the file is missing. Do not rewrite other lines.
2. **No.** Do not add the line. The README says `.gitattributes` was left as it was, so a later commit may change the line endings.

Do not add the line without that yes. When the line is already there, do not ask.

A mail follows this section. The binary section does not replace it. An attachment the user also supplied as its own file follows the binary section and lives in the same folder when it belongs to that mail.

## Binary files

For every binary file, ask which of these four options to use. One question per file. Options only. Use the questions tool when it is available. Name one recommendation in the question. The user picks. Do not pick for them.

1. **Commit as-is.** The file goes in the folder unchanged.
2. **Compress, then commit.** For a screenshot: crop off taskbars and app bars, no sharpening, WebP. Show samples at q70, q85, and lossless so the user picks the quality. Write only the picked file into the folder. This is the recommendation for a screenshot that is not above about 10 MB.
3. **Convert to text and commit that instead.** The original stays outside the repo. A `.docx` or a PDF transcript becomes `transcript.md`, word for word, with speakers and timestamps when the original has them. Check that text word for word against the original before the file is written. Do not invent a speaker or a timestamp. The README says where the original lives. This is the recommendation for a document that is not above about 10 MB.
4. **Leave it out and only reference where the original lives.** The folder does not contain the file. The README records that place. When the user already pointed at the file, that place is the reference. When they did not, ask where it lives. Do not guess. This is the recommendation when the file is above about 10 MB.

For any other binary under about 10 MB, the recommendation is commit as-is.

When a file is above about 10 MB, recommend leave-it-out even when it is a screenshot or a document. Still offer all four options. The size is the file as offered, before a compress.

Git LFS (Large File Storage) is a note only. It is not an option. It needs repo setup the kit does not do.

The README records which option was used.

Screenshot samples: crop first, then encode three WebP files, q70, q85, and lossless. Do not sharpen. Show the three to the user with the quality named on each. Stop until the user picks one. Write only the picked file into the folder. Remove the other two. Do not leave the samples in the source folder. If no encoder is available, say so and ask the user to pick another of the four options. Do not install an encoder.

A text file that is already text, such as `.txt`, `.md`, or `.vtt`, is not a binary file. Store it unchanged. A `.docx` or a PDF is a document and gets the four options.

## Personal data

Before the files are written, check the source, and check the quote that will be written into the spec. Flag every item below. Flag a detail that is readable in a screenshot, including when it sits in a mail signature. Nothing is dropped to keep the list short.

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

Secrets are always redacted. They are never a choice. They are never stored in the rule. Check for them even when the rule does not list personal data.

The kinds are:

- connection strings
- SAS tokens
- API keys
- passwords
- private keys
- VPN configs

Show each secret in the list by kind only. Do not show the value. Do not ask keep or redact. Remove it from the file that will be written, and from the quote. Note it in the README by kind, not by value.

### Transfer data policy

The rule is once per repo. Read the file for the host that is running. Cursor: `.cursor/rules/crav1-transfer-data-policy.mdc`. Claude Code project: `.claude/rules/crav1-transfer-data-policy.md`. Do not read or write a user-level file. The user changes the rule by editing or deleting that file.

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

When the rule or this run says auto-accept, do not ask that question. Apply each numbered recommendation.

Unplaced items are still asked one at a time, whatever was picked, including auto-accept. Options are keep and redact. There is no recommendation. Use the questions tool when it is available. Stop until the user picks.

When there is no numbered item, do not ask the three-answer question. Ask the unplaced items. A secret is not a question.

**Keep.** That text stays.

**Redact.** Remove that item from the file that will be written, and from the quote. Note the redaction in the README, by kind, not by pasting the value. The file is then no longer the untouched original. The README says so.

Do not write the source files until every flagged item has an answer. A secret is already answered by this section. The rule file may be written when the user says yes, before the source files. Do not write an unredacted copy into the repo. When a screenshot will be compressed, the samples are the redacted image. The user commits later. A redacted value is not in the file they will commit. Do not commit.

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
