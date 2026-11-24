# Save a technology note

Save only when the user asked: the word `save`, or yes on the save card. A headless or bot run saves only when its invocation says `save`.

1. The target spec is `save_to` from `find`, or the spec the user named (`in <spec>`). `architecture` means `docs/architecture/spec.md`. A spec's notes file is `notes.md` next to its `spec.md` (`docs/specs/<slug>/notes.md`; `docs/architecture/notes.md`). A design topic keeps its own notes through `/crav1-design-architecture note <topic>`.
2. Write the entry as JSON in the session's temp folder: `summary` (the short explanation as shown) and `links` (the `path#section` links from `find`).
3. Run `<interpreter> scripts/explain_tech.py --root <specs repo> save --tech "<technology>" --spec <slug|architecture> --input <entry.json> --vendor copilot` without `--yes`. It writes nothing and returns the path, the entry and the card. Show them.
4. After the yes (or with the `save` word), run the same command with `--yes`. It creates the notes file when it is missing, adds `## Technology notes` when that section is missing, and appends `### <technology> (YYYY-MM-DD)`, the summary and the links. A link that is not a file or section in the specs is refused, and so is a second note for the same technology on the same day.
5. End with `ending --tech "<technology>" --saved <path>`: commit with `/crav1-finalize-commit`.
