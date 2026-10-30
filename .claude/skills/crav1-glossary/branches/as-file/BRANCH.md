# Glossary: As file branch

Read only when `SKILL.md` routes here (`as-file`). Moved word for word from `SKILL.md` in 1.106.0; the rules are unchanged. The shared sections in `SKILL.md` still apply. A `references/…` or `assets/…` path is relative to the skill folder, not this branch.

## As file

- The file is `.crav1/glossary-list.md` at the repo root. Create it with `.crav1/.gitignore` holding the one line `*`, so git ignores the folder. Do not touch the repo's `.gitignore`.
- Content: `# Glossary`, the count line, the **List** table, and ``Source: `docs/system/glossary.md` ``. Overwrite an older copy.
- In the chat: the count line and ``Glossary list file: `.crav1/glossary-list.md` (not in git) ``. Not the table.
- Write nothing else; never stage or commit it. No glossary: stop as **Find the glossary** says.
