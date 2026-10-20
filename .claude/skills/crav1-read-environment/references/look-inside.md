# crav1-read-environment: look inside

Read only when the pointer in `SKILL.md` sends you here. Moved word for word from `SKILL.md` in 1.71.0; the rules are unchanged.

## Look inside

Run this after the shape question, when that question is needed, and before any section. If leftovers stopped the read, skip it. Do not ask a section in the same step.

Two readers, in this order. Ask both reader questions in one questions call (1.70.0).

- **SQL** — [references/sql.md](sql.md) (drop-in: `.claude/skills/crav1-read-environment/references/sql.md`; plugin: this skill’s `references/sql.md`). Metadata only. Never a row.
- **Storage** — [references/storage.md](storage.md) (drop-in: `.claude/skills/crav1-read-environment/references/storage.md`; plugin: this skill’s `references/storage.md`). Structure only. Prefix depth is 2. Never a blob, a file count, or a size.

When the databases this pass found have no clear environment, say `There are no clear database environments.` Then ask that reader’s questions. Options only.

Before the question that opens a database or a store, say how to reach it and how much setup is needed. This skill does not install a tool. It does not create a login, a user, a firewall rule, a role, a SAS token, or a key. If access is missing, stop that reader and name what is missing. Do not open it. The other reader still runs. The sections still run.

A schema, a table, a container, or a prefix is evidence only when the whole-word token rule matches. Cite it on the Seen line. A similar name is not evidence. Do not write that cite into `docs/environments/marks.md`.

Production databases and production storage are never opened. A yes on prod-only does not open them. Prod-only shape is only what the resource list and the settings already show. Pre-prod and shared follow the yes already given, and stay shape and connections only.

What a yes finds joins the sections below. Do not add a section. Each fact says `Seen in <host> <environment>.`
