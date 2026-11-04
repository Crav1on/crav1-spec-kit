# Imported sources: mails

Read only for a mail. [sources.md](sources.md) is the convention; its other sections still apply. Moved from `sources.md` in 1.71.1. Since 1.111.0 a mail is written as text.

## Mails

A mail is written as text, never as a mail file (1.111.0). Write `mail.md` in the source folder:

- A header block, one line each: `From`, `To`, `Cc`, `Date`, `Subject`, and `Message-ID` when the mail has one. Copy them as the mail shows them. A header the mail does not show says `not shown`.
- Then the text body word for word, the quoted thread kept. Use the plain text part. When the mail has only an HTML part, write its text without markup. Do not shorten, summarize, or reflow it.

The original mail file stays outside the repo. Do not copy it into the folder. Do not edit it. Do not write a script to edit, split, or re-encode a mail. Read the mail; write the text. The README names the original file name, the `Date`, and the `Message-ID`, and says the original is kept outside the repo. Do not write a local disk path. Write a location only when the user gives a shared one.

A pasted mail is also written as `mail.md`. The README says it was pasted and there was no original file.

The duplicate check matches a mail by its `Message-ID`. Without one, it matches `Date`, `Subject`, and `From`. An earlier import may be a `mail.md` or an older mail file; both count. Mail files already in a project stay as they are. Do not convert or remove them unless the user asks.

Personal data and Secrets apply to the text in `mail.md`: the headers, the body, the signature, and the quoted thread. A redaction edits `mail.md`.

A mail follows this section. Each image inside the mail, inline or attached, also follows Images inside a mail. An attachment that is not an image follows Binary files as its own file in the same folder. An attachment the user also supplied as its own file is that same file.

## Images inside a mail

A mail can hold images inline, or as attached image parts. List every one before the folder is written. Nothing is dropped to keep the list short. Read each image before the question. When a secret is readable in an image, commit as-is is not an option for that image. Secrets says what is written instead. A mail with no image skips this section.

Number each image. The line says inline or attached, the file name or content id when the mail has one, and a short line of what the image shows. The line ends with the recommendation from Binary files: `Recommendation: convert to text.`, `Recommendation: compress.`, or `Recommendation: leave it out.`

### One question for the images

After the list, one question when there is at least one image. Three answers. Use the questions tool when it is available. Stop until the user picks.

1. **Accept all recommendations.**
2. **Go through them one by one.** The recommendation is shown on each image. The four options are the answers; the recommended one comes first with ` (Recommended)`.
3. **Change some.** The user names images and the option, for example convert 2, compress 4.

Accept all recommendations applies every listed recommendation.

Go through them one by one asks the four options for each image. One image at a time. Options only. Use the questions tool when it is available. The recommended option comes first with ` (Recommended)` at the end of its label; the question text does not repeat it. Stop until the user picks.

Change some waits for the user to name the images and the option. The named option replaces the recommendation for that image. An image they do not name keeps its recommendation. When a number is not on the list, or the reply names an image and no option, ask again. Do not guess.

The transfer data policy `auto-accept` applies to keep and redact recommendations. Apply it to these image recommendations only when the rule text clearly covers them. The template says auto-accept applies the keep and redact recommendations. That line does not cover the four image options. Ask this question. A rule the user edited covers the image recommendations only when its own text says so, for example that auto-accept applies to embedded-image options. A keep and redact line is not that cover. Do not add an image choice to the rule. Do not rewrite the rule for this.

When the option is compress, the quality samples in Binary files still run. Accept all does not skip that pick. Stop until the user picks a quality. That pick is part of the answer.

Do not write the source folder until every image has an answer. The transfer data policy file may still be written when the user says yes, as Personal data says.

### What each option does to the image

Each image becomes its own file next to `mail.md`, or no file. `mail.md` gets a short placeholder where the image was shown. When the image was only an attachment, the placeholder goes at the end of the text body.

1. **Commit as-is.** Write the image file next to `mail.md`. Placeholder: `[Image: <file>]`.
2. **Compress, then commit.** Write the picked WebP next to `mail.md`. Same crop, no sharpening, and the same three samples as a screenshot. Placeholder: `[Image: <file>]`. The README names the image and the quality.
3. **Convert to text.** Write `<name>.md` next to `mail.md`. Placeholder: `[Image converted to text: <name>]`. The file holds the image's text word for word. A diagram is a Mermaid redraw. A table is a markdown table. An image that has both holds both. Check that text word for word against the image before the file is written. Do not invent a label, a word, or a box the image does not show.
4. **Leave it out.** No file. Placeholder: `[Image left out: <name>]`.

Names come from the image file name. Lowercase. Hyphens. Do not put a person's name in the name. When the mail shows no file name, use a short name from what the image shows. When that name is already used in the folder, add the list number. The README names each image and its option.
