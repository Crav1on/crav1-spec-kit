# When architecture is missing

Read only when the pointer in `SKILL.md` sends you here. Moved word for word from `SKILL.md` in 1.95.1; the rules are unchanged.

A spec describes the design when `docs/specs/<slug>/spec.md` (skip `_template`) already states how the thing is shaped: users and journeys, constraints, decisions, diagrams, ADRs, or an approach the file already wrote. A file that is only a title, only open questions, or only a match status with no design, does not.

`docs/system/` describes the design when `landscape.md`, `diagrams.md`, or `adr/` already states what the system is. An empty folder, or a glossary alone, does not.

Point at one command when what they brought makes it obvious. Do not run it.

- One or two sentences, no design yet: `/crav1-spark-to-spec`
- A pile of ideas, no design yet: `/crav1-ideas-to-spec`
- Mixed files or several features, no design yet: `/crav1-bundle-to-specs`
- Repos plus a dump, no design yet: `/crav1-existing-to-specs`
- A spec folder exists and does not describe the design: `/crav1-add-to-spec` when they already have the information, otherwise spark or ideas for a new slug unless they said extend
- They picked the change, specs exist, and no spec describes that change: `/crav1-add-to-spec`

If they brought none of those, name the four commands that create the architecture (spark, ideas, intake, match) and stop.
