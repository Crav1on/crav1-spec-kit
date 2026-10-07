# Keep the picture current

Kit not in this project yet? [Install first](install.md) (Cursor and Claude Code; the slash commands match, the files do not). After a Cursor plugin install, the short command loop is [plugins/crav1/README.md](../plugins/crav1/README.md). Claude Code has no plugin.

Use this when **system notes already exist** under `docs/system/` and something was added that the picture does not show yet.

The picture is three places: the short description in `landscape.md`, the context diagram in `diagrams.md`, and how the parts connect (`## How the parts connect` in `landscape.md`). This command adds what is new. It does not rewrite what is already there. It does not design the change. It does not build it.

This is cross-cutting. It is not its own lane. It can run on its own. The same passes that already append a glossary row also run this update: spark, ideas, intake, match, and the siblings that already append (match-dump and code-into-specs). Repos-to-spec updates the picture in its own pass. Those passes do not rewrite existing glossary rows. This command does not write glossary rows.

Some commands do not update the picture themselves. At the end of the run they ask, yes or no: The system picture may now be out of date. Run `/crav1-keep-current`? They do not run this command. `/crav1-complete-features` asks when a slice is marked done or retired. `/crav1-fix-bug` and `/crav1-fix-live` ask when the fix changes how the parts connect. `/crav1-environment-read` asks after lines are added to `docs/environments/marks.md`. `/crav1-add-to-spec` asks once at the end of a run that came from environment-read or suggest-tests-for-code, not once per item. `/crav1-implement-task` and `/crav1-complete-task` do not ask.

This is not [from the repos](from-repos.md) (`/crav1-repos-to-spec`). That command reads the repos the user named and writes one architecture spec the lanes can extend, plus these notes. Spark, ideas, intake, and match still create notes for a feature or a dump. [Explain](from-explain.md) reads the notes and does not update them.

## First prompt

New chat. Not the host plan UI.

```text
/crav1-keep-current
@docs/system/
@docs/specs/

Add what the specs already state to the picture. Do not rewrite what is already there. Do not write code.
```

That slash command *is* the prompt.

## Steps

| Phase | You | Agent |
| --- | --- | --- |
| Notes | — | Stops when `docs/system/` is missing. Points at spark, ideas, intake, match, or repos-to-spec when the user named repos and brought no dump. Does not seed the folder |
| What is new | — | A part or a connection a spec already states and the picture does not. Skips a sentence marked inferred. Does not invent one from the repo |
| Write | Glance | Appends a sentence, a diagram node or edge, or a connection line. Leaves existing lines as they are |
| Stop | `/crav1-finalize-commit` if a file changed | Does not plan, implement, or commit. Names that command only when a file changed |

Nothing new: it says the picture is current and writes nothing.

## What gets written

Only the three picture places. Starters: [docs/system/_template/landscape.md](system/_template/landscape.md) and [docs/system/_template/diagrams.md](system/_template/diagrams.md).

An empty short description (the template sentence) is filled with one sentence the specs already support. An empty diagram (the template sample) is replaced with the parts the specs already name. After that, later runs only append.

No feature-index row from this command. No glossary row. No `spec.md`. No `plan.md`. No `tasks.md`. No application code.

## After

If a file changed:

```text
/crav1-finalize-commit
```

That puts the picture update in git. No push. This command does not commit for you.
