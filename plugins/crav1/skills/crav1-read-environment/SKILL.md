---
name: crav1-read-environment
description: >-
  Read the host the user named. Each host has its own reader. This build
  has readers for Azure, AWS, and Google Cloud. Another named host stops
  with no reader. Naming production, prod, or live stops. One pass
  reads every non-prod environment. Pre-prod, resources shared with
  prod, and prod-only resources are shape and connections only, after
  one yes. Never production data. After that read, and before any
  section, optional SQL metadata and storage structure, only when the
  user says yes. Never rows. Never blobs. Never open production.
  Appends confirmed lines to docs/environments/marks.md. Does not write
  docs/system, docs/architecture/spec.md, feature specs, or
  docs/architecture/left-out.md. After the user confirms a section, the
  skill that already owns the file adds only what is new. A fact is seen
  in that environment. A prod-only line says prod only. A link only when
  the environment shows the connection. Does not start Specify, Plan, or
  Build.
disable-model-invocation: true
icon: cloud
color: cyan
---

# Environment read

The user names the host at the start. You read every non-prod environment on that host in one pass. You do not guess the host. You never read production data. A prod-only resource is shape and connections only, after one yes.

Command: `/crav1-read-environment`.

This command is a starter option. When the user asks for startup options, name only `/crav1-spark-to-spec`, `/crav1-ideas-to-spec`, `/crav1-bundle-to-specs`, `/crav1-existing-to-specs`, `/crav1-read-environment`, and `/crav1-fix-bug`. That ask names the list. It does not run this command and does not move work into a lane. Every other skill is a later skill. This command still runs only when the user names the host. Naming production, prod, or live stops.

This is cross-cutting. It is not a lane. It does not move work into Specify, Plan, or Build. It does not start those lanes.

Cloud commands stay read-only. This skill does not create, update, delete, deploy, start, stop, or set a cloud resource. It does not install a CLI. It does not log in. The only file this skill writes is `docs/environments/marks.md`, and only by appending a line the user confirmed. It does not write `docs/system`, `docs/architecture/spec.md`, a feature spec, or `docs/architecture/left-out.md`. After the user confirms a section, the skill that already owns that file adds only what is new. A fact is marked seen in that environment. It is not marked as something the code shows. It does not become a link unless the environment actually shows the connection.

This is not `/crav1-existing-to-specs`. That command reads repos. This command reads a host. This is not `/crav1-existing-to-specs`. Match needs a dump and writes one spec per slice. This command does not create a slug. This is not `/crav1-add-to-spec`. `/crav1-map-pipeline-environments` proposes pipeline lines for `docs/environments/marks.md`. This command does not run it and does not write those lines.

The host readers list a database and a storage account. They do not open them. After the first read, and before any section, this command can look inside. SQL metadata is [references/sql.md](references/sql.md). Storage structure is [references/storage.md](references/storage.md). Drop-in: `.cursor/skills/crav1/crav1-read-environment/references/`. Plugin: this skill’s `references/`. Both run only when the user says yes. A no leaves them unopened. The first read does not list tables, columns, prefixes, or blobs as facts.

## Start

Everything after `/crav1-read-environment`, and every `@`, is the pointer.

The user names the host in that message. Examples: Azure, AWS, Google Cloud. They do not pick dev or test. The user names the host, not the subscription, the account, or the project.

If they named no host, stop. Ask them to name the host. An environment word is not a host. Do not guess. Do not pick a host because it has a reader. Do not read.

If they named production, prod, or live, stop. Say this skill never reads production. Do not list resources. Do not call a reader. A non-prod word in the same message does not make a production read safe.

If they named the host and also a non-prod word, such as Azure dev, do not stop and do not narrow the pass. Say once that this pass reads every non-prod environment. Then read.

If they named only an environment word and no host, stop. Ask them to name the host. Do not treat that word as the host. Do not read.

Options only. Do not ask them to type a path.

**No host named.** Options:

1. **Azure**
2. **Google Cloud**
3. **AWS**
4. **I will name the host.**

Stop until they pick. A pick of Azure, Google Cloud, or AWS is the host. Do not ask dev or test. **I will name the host** waits for that name. Do not read between the answers. If that name is production, prod, or live, stop as above.

## Reader

Read `references/reader.md` ("Reader") only when you pick the reader (az, files, or both).

## Marks

Read `references/marks.md` ("Marks") only when you write or read environment marks (any line in marks.md).

## marks.md

Read `references/marks.md` ("marks.md") only when you append to docs/environments/marks.md.

## Evidence

Read `references/evidence.md` ("Evidence") only when a line needs its evidence written or checked.

## Group suggestion

Read `references/grouping.md` ("Group suggestion") only when several resources could be one group.

## Leftovers

Read `references/grouping.md` ("Leftovers") only when resources are left over after the sections.

## Pre-prod, shared, and prod-only

Read `references/grouping.md` ("Pre-prod, shared, and prod-only") only when a resource is used by more than one environment or only by prod.

## Look inside

Read `references/look-inside.md` ("Look inside") only when the user asks to look inside a resource.

## Sections

Read `references/sections.md` ("Sections") only when you reach the sections (after the reader and the marks).

## The owner adds

Read `references/sections.md` ("The owner adds") only when the owner adds lines by hand.

## Stop

Read `references/after.md` ("Stop") only when the run stops early or ends.

## Picture offer

Read `references/sections.md` ("Picture offer") only when the run ends and a picture could be offered.

## Hard rules

- No host named: stop. Do not guess the host.
- The user names the host, not the subscription, the account, or the project. They do not pick dev or test. One pass reads every non-prod environment.
- Naming production, prod, or live stops the read. Do not list resources.
- Never read production data. Never a secret value. Never a row or a blob from production.
- A resource whose only mark is production is prod-only. It has no non-prod twin. A similar name on another resource is not a twin. Prod-only is shape and connections only, and only after the one yes with pre-prod and shared. A no lists it as not read and it stays in Skipped.
- `live` is production when it is a whole word.
- A host with no reader stops. This build reads Azure, AWS, and Google Cloud. Do not pretend to read any other host.
- Do not read Azure DevOps, GitHub, or CI.
- Name the missing CLI or the missing login. Do not install a CLI. Do not log in.
- Pre-prod, a resource shared with prod, and a prod-only resource are shape and connections only, and only after the one yes. The prompt asks for all three together. A no lists them as not read. Shape is names, types, setting keys, routes the settings already show, timers, links, and secret names. Never data. Never secret values. Never row or blob contents.
- Sources that disagree between non-prod and production make the resource shared. Cite both sources.
- Evidence is the three kinds above, strongest first. A similar name is not evidence.
- This skill’s only write is an append to `docs/environments/marks.md` of a line the user confirmed. Create that file only after at least one confirmed mark. Never rewrite an existing line.
- This skill does not write `docs/system`, `docs/architecture/spec.md`, a feature spec, or `docs/architecture/left-out.md`.
- A fact is seen in that environment. It is not something the code shows.
- A link, including a trigger definition, is added only when the environment shows the connection. Do not invent a link. Do not show a payload or a secret value. A prod-only link says `prod only`.
- After the first read, and before any section, SQL and storage look-inside run only when the user says yes. SQL is metadata only. Storage is structure only, prefix depth 2. Never a row. Never a blob, a file count, or a size. Never a connection string, a key, or a secret.
- Look-inside hard rules: read `references/look-inside.md` ("Look-inside hard rules") before any SQL or storage look-inside.
- One question at a time. Every item stays listed.
- The owner adds only what is new. Do not rewrite a line that is already there.
- After one or more `docs/environments/marks.md` lines are added, ask the picture question once. Do not run `/crav1-refresh-system-notes` from that question.
- A slice Match does not already own is not a new slug.
- Do not start Specify, Plan, or Build.

## Style

Be concise. Cite the resource id. Prefer the smaller fact. Do not fill a gap with an architecture you invented.
