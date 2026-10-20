# Imported sources: binary files

Read only for a binary file handed over as its own file, an image inside a mail, or any image or temporary file the import extracts. [sources.md](sources.md) is the convention; its other sections still apply. Moved word for word from `sources.md` in 1.71.1; the rules are unchanged.

## Binary files

For every binary file the user hands over as its own file, ask which of these four options to use. One question per file. Options only. Use the questions tool when it is available. Mark the recommended option: list it first and end its label with ` (Recommended)`; the others keep the order below. Do not also write the recommendation in the question text. The user picks. Do not pick for them.

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

## Reading the document

Moved word for word from `sources.md` in 1.71.2.

### Temporary files

Extract images and other temporary files into a new folder in the system temp folder (for example `mktemp -d`, or `%TEMP%` on Windows), never inside the repo. Delete that folder at the end of the run, also when the run fails or stops early. Write only the picked files into `docs/sources/`.

### An image the kit cannot view

When the kit cannot see an image (for example a headless `-p` run, where images cannot be read), say so. Never guess what it shows from its type, its order, or its size. Leave the image out with the placeholder `[Image left out: <name>, not viewed]`. The README and the run summary list it, and tell Rhea or the user to check it before deciding keep or leave.

### Duplicate images

Detect exact duplicates (same bytes) across a document and across the documents of one intake. Store each image once. The README lists every place it appears. Ask the keep-or-leave question once per image.
