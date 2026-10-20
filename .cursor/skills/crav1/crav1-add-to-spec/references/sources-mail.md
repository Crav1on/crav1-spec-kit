# Imported sources: mails

Read only for a mail. [sources.md](sources.md) is the convention; its other sections still apply. Moved word for word from `sources.md` in 1.71.1; the rules are unchanged.

## Mails

A mail goes in as a `.eml` text file. Keep the CRLF line endings. Do not convert them to LF. A paste that used LF is written with CRLF. The README says the paste was written with CRLF.

Read the project's `.gitattributes`. If that file does not already contain the line `*.eml -text`, ask the user once, before adding it. Yes or no. Use the questions tool when it is available. One question for the run, not once per mail.

The question is: Add `*.eml -text` to `.gitattributes` so Git keeps the CRLF line endings on mail files?

1. **Yes.** Add that line on its own line. Create `.gitattributes` only when the file is missing. Do not rewrite other lines.
2. **No.** Do not add the line. The README says `.gitattributes` was left as it was, so a later commit may change the line endings.

Do not add the line without that yes. When the line is already there, do not ask.

A mail follows this section. Each image inside the mail, inline or attached, also follows Images inside a mail. The binary section does not replace the mail. An attachment the user also supplied as its own file follows the binary section and lives in the same folder when it belongs to that mail. A non-image part stays in the `.eml`.

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

### What each option does to the part

1. **Commit as-is.** That image part stays in the `.eml` unchanged.
2. **Compress, then commit.** Replace that image part with the picked WebP. Same crop, no sharpening, and the same three samples as a screenshot. Keep the content id when the part had one. Set the type to `image/webp`. Keep the CRLF line endings. Do not write a second copy of the image next to the `.eml`. The README names the image and the quality. The `.eml` is then no longer the untouched original. The README says so.
3. **Convert to text.** Remove that image part from the `.eml`. Leave a short placeholder where the image was shown, naming the new file: `[Image converted to text: <name>.md]`. When the image was only an attachment, add that line at the end of the text body. Write `<name>.md` in the same `docs/sources/YYYY-MM-DD-<slug>/` folder. The name comes from the image file name. Lowercase. Hyphens. Do not put a person's name in the name. When the mail shows no file name, use a short name from what the image shows. When that name is already used in the folder, add the list number. The file holds the image's text word for word. A diagram is a Mermaid redraw. A table is a markdown table. An image that has both holds both. Check that text word for word against the image before the file is written. Do not invent a label, a word, or a box the image does not show. The README notes the conversion and names the file. The README says the `.eml` is no longer the untouched original.
4. **Leave it out.** Remove that image part from the `.eml`. Leave a short placeholder where the image was shown: `[Image left out: <name>]`. When the image was only an attachment, add that line at the end of the text body. Use the same name rules as convert to text. The folder does not contain that image. The README notes the leave-out and names the image. The README says the `.eml` is no longer the untouched original.

Put the placeholder where that image was shown. A mail with a plain part and an HTML part gets the placeholder in both. Do not ask where an image that lived only in the mail now lives. The `<name>.md` from convert to text is the file the folder stores.

Keep the CRLF line endings on the `.eml` after any of these edits. When every image is commit as-is, and no later section changes the file, the `.eml` stays the untouched original.
