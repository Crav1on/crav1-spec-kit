# crav1-bundle-to-specs: sources

Read only when the pointer in `SKILL.md` sends you here. Moved word for word from `SKILL.md` in 1.71.0; the rules are unchanged.

## Imported sources

When an intake file is a mail, a transcript, minutes, a chat, a screenshot, a diagram, or another original that will be quoted into a spec, follow the imported-sources convention before the slice specs are written (drop-in: `.claude/skills/crav1-add-to-spec/references/sources.md`; plugin: sibling `skills/crav1-add-to-spec/references/sources.md`). Its personal-data and secrets check is in that file; flagged items, the transfer data policy, and the one question are in `references/sources-flagged.md`, and a mail's images in `references/sources-mail.md` and `references/sources-binary.md`, all in `crav1-add-to-spec`. Several documents get one folder each, `docs/sources/YYYY-MM-DD-<doc-slug>/`. After all are read, run the conflict pass that file describes. A run with no window uses that file's two-pass mode. Write each source folder once. Pass each folder path to the worker that quotes it. The worker writes the `Source:` and `Trace:` lines and does not import the file again. Do not commit. A file that is not an imported source does not get a folder.
