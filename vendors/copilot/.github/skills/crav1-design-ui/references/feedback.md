# Feedback and screenshots

Read this when the user attaches a screenshot, or when `status` lists `binaries`.

## A screenshot with feedback

- Look at it only to understand the feedback: which screen, which region, which state, what is wrong or wanted.
- Write what it shows as text in `ui/experience.md` (a state, an interaction, a check) or `ui/design.md` (the layout, the look, a token). For example `Error: the banner sits above the filters and says "Orders could not load. Retry."`
- That text is what gets approved. The screenshot is not a source, not an attachment, and not a reference.
- Never save the screenshot, a crop of it, or an export of it under `docs/specs/`, `docs/`, or anywhere in the repo. Do not name its file path in the Markdown.
- When the screenshot and the Markdown disagree and the user did not say which is right, ask once which one stands. The Markdown text is written to match the answer.

## A binary file already under ui/

`ui_screens.py status` lists files under `ui/` that are not text (an image, a PDF, a design-tool file). `sync` and the plan gate refuse while one is there.

- Name each file and say what to do: describe what it shows in the Markdown, then remove the file from `ui/`.
- Offer to write that description now. Do not delete the file yourself; the user removes it.
- After it is gone, run `status` again and go on.
