# crav1-explain-existing-system: missing

Read only when the pointer in `SKILL.md` sends you here. Moved word for word from `SKILL.md` in 1.71.0; the rules are unchanged.

## When the notes are missing

Run only when `docs/system/` exists and a note is already written (a short description that is not the template sentence, a diagram that is not only the template sample, a connection line, a repo row, a glossary row, or an ADR). If that is missing, stop. Point at the command that writes the notes. Do not invent them. Do not seed `docs/system/`. Do not create a slug. Do not write a summary file.

Point at one command when what they brought makes it obvious. Do not run it.

- One or two sentences, no notes yet: `/crav1-spark-to-spec`
- A pile of ideas, no notes yet: `/crav1-ideas-to-spec`
- Mixed files or several features, no notes yet: `/crav1-bundle-to-specs`
- Repos plus a dump, no notes yet: `/crav1-existing-to-specs`
- Named repos and no dump, no notes yet: `/crav1-existing-to-specs`

If they brought none of those, name those five commands and stop.

The template sentence `What this product/system is, in one short paragraph.` is not a short description. The template diagram `user[User] --> app[App]` with no other node is not a diagram of this system.

Then run **Feature index and the picture** before you finish, whenever `docs/system/landscape.md` can be read.

## When the picture has nothing on the question

The picture has nothing on the question when the notes never mention what they asked. That is a can-it answer that is not written down, a named part the notes do not contain, or a whole-system answer whose short description is still the template sentence.

Match a slice by whole name only. The names that count are the slug, the spec title, and the main resource name, the same three as **Feature index and the picture**. The question matches a slice only when it uses one of those whole names. A shorter piece, a longer name that only contains it, a synonym, or a similar spelling is not a match.

When one slice matches, quote the first paragraph of that `docs/specs/<slug>/spec.md`. The first paragraph is the first block of prose after the title line. Skip a heading. Do not quote a table. Label it `From the spec (docs/specs/<slug>/spec.md):` and then the paragraph. Name `/crav1-what-do-we-know-about-this`. Do not run it. The quote is labelled as coming from the spec. It is not the picture's answer.

When more than one slice matches that whole name, do not pick one. Name each slug. Name `/crav1-what-do-we-know-about-this`. Do not run it. Do not quote.

When no spec matches either, say the picture has nothing on the question and no spec matches. Name `/crav1-what-do-we-know-about-this`. Do not run it. Do not guess a slice.

When the spec has no prose paragraph, say the spec has no first paragraph, and still name `/crav1-what-do-we-know-about-this`. Do not run it.

## Research marked stale

On every run, when this answer opens a spec, and when the feature-index check reads a spec for its title, also read `## Research findings` on that spec. Also read a `docs/research/` note that those findings link to, and any stale block on that note. Follow the readers section of `crav1-add-to-spec` `references/research-stale.md` (drop-in: `.cursor/skills/crav1/crav1-add-to-spec/references/research-stale.md`; plugin: sibling `skills/crav1-add-to-spec/references/research-stale.md`).

When a stale mark is there, say the research is stale. Quote the mark. Name the path. One line per mark. Do not treat that research as current. Do not clear the mark. Do not drop a mark to keep the list short. When no mark is there, do not invent one.
