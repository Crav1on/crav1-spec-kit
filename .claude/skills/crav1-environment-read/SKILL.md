---
name: crav1-environment-read
description: >-
  Read the host and the environment the user named. Each host has its own
  reader. This build has an Azure reader only. Another named host stops
  with no reader. Never production. The reader lists only what that
  environment actually has. A resource with no environment mark stops and
  is not read. The skill only reads. It does not write docs/system,
  docs/architecture/spec.md, feature specs, or docs/architecture/left-out.md.
  After the user confirms a section, the skill that already owns the file
  adds only what is new. A fact is seen in that environment, not something
  the code shows. A link only when the environment shows the connection.
  Does not start Specify, Plan, or Build.
disable-model-invocation: true
icon: cloud
color: cyan
---

# Environment read

The user names the host and the environment at the start. You read that environment. You do not guess the host. You never read production.

Command: `/crav1-environment-read`.

This is cross-cutting. It is not a lane. It does not move work into Specify, Plan, or Build. It does not start those lanes.

This skill only reads. It does not write `docs/system`, `docs/architecture/spec.md`, a feature spec, or `docs/architecture/left-out.md`. After the user confirms a section, the skill that already owns that file adds only what is new. A fact is marked seen in that environment. It is not marked as something the code shows. It does not become a link unless the environment actually shows the connection.

This is not `/crav1-repos-to-spec`. That command reads repos. This command reads a named environment. This is not `/crav1-match-to-specs`. Match needs a dump and writes one spec per slice. This command does not create a slug. This is not `/crav1-code-into-specs`.

## Start

Everything after `/crav1-environment-read`, and every `@`, is the pointer.

The user names both the host and the environment in that message. Examples: Azure dev, Google Cloud test, AWS dev. The environment is dev or test. The user names the environment, not the subscription.

If they named no host, stop. Ask them to name the host and the environment. Do not guess. Do not pick Azure because it has a reader. Do not read.

If they named a host and no environment, stop. Ask them to name dev or test. Do not guess. Do not treat a subscription name as the environment. Do not read.

If they named production, prod, or live, stop. Say this skill never reads production. Do not list resources. Do not call a reader.

If they named an environment that is not dev and not test, stop. Ask them to name dev or test. Do not guess. Do not read.

Use the questions tool when it is available. Options only. Do not ask them to type a path.

**No host named.** Options:

1. **Azure**
2. **Google Cloud**
3. **AWS**
4. **I will name the host.**

Stop until they pick. A pick of Azure, Google Cloud, or AWS still needs the environment. Ask dev or test next. **I will name the host** waits for that name. Do not read between the answers.

**Host named, environment missing.** Options:

1. **dev**
2. **test**

Do not offer production.

## Reader

Each host has its own reader. The reader lists only what that named environment actually has. A host with no reader stops. Say this host has no reader. Do not pretend to read it. Do not borrow another host’s reader.

This build has an Azure reader only. It is [references/azure.md](references/azure.md) (drop-in: `.claude/skills/crav1-environment-read/references/azure.md`; plugin: this skill’s `references/azure.md`).

Check the host name before any read.

- **GitHub, CI, Azure DevOps, or Azure Pipelines** — stop. This skill does not read them. Do not pretend to. Do not treat Azure DevOps as Azure.
- **Azure** — follow that reader. The host name is Azure, not Azure DevOps.
- **Google Cloud, AWS, or any other named host** — stop. This host has no reader.

If the Azure reader cannot read (`az` missing, or not logged in), stop. Say so. Do not invent a resource.

## Marks

The reader takes only a resource whose name, group, or tag says the named environment (dev or test). Anything marked production is skipped and listed as skipped. It is not a fact. A resource with no environment mark stops the read. Ask. That resource is not read. Do not infer the mark from the subscription, the region, or a neighbor.

List every unmarked resource in the question. Do not drop one to keep the question short.

Options:

1. **Leave every unmarked resource unread and continue.**
2. **Stop the read.**

Either answer leaves those resources unread. Continue goes on with resources that have a mark. Stop writes nothing and asks no section.

## Sections

Show one section at a time. Each section has its own question and its own answer. Do not merge sections into one list. Do not collapse the questions into one write-or-not question. List every item. Do not drop a resource, a skipped line, a link, a fact, or a left-out line to keep a section short.

A fact already written in the destination file stays in its section and is marked already written. The owner does not add it again.

Use only these sections, in this order. Do not invent another section.

**Skipped.** Every resource marked production. Each line is the resource name, the group, and the mark that said production. The line says skipped. It is not a fact and not a link. When none are marked production, the section says nothing was skipped.

**Seen.** Every resource the reader took for the named environment. Each line cites the resource id, the name, the group, and whether the name, the group, or a tag said dev or test. Each line says `Seen in <host> <environment>.` It does not say the code shows it. When the named environment has no such resource, the section says this environment shows no resource. Do not invent one.

**Links.** A connection the environment shows on a seen resource: a field that names another resource id or hostname. Cite the resource id and the field. A similar name is not a connection. A seen resource does not become a link by itself. When no field shows a connection, the section says no connection is shown. Do not offer a guessed link.

**System.** Seen facts, and links the environment shows, that belong in `docs/system`. When `docs/system/` is missing, the section says so. This command does not create that folder. When every line is already in the picture, the section says the picture is current.

**Architecture.** Seen facts, and links the environment shows, that belong in `docs/architecture/spec.md`. When that file is missing, the section says so. This command does not create it. When every line is already there, the section says the architecture spec is current.

**Match.** A seen fact that belongs on a slice Match already owns. That slice is a `docs/specs/<slug>/spec.md` (skip `_template`) that already has `## Match` for this fact. When no such spec exists, the section says no slice Match owns this. Do not create a slug. When more than one Match spec could take the fact, list each slug in the section. Do not drop one.

**Left out.** Every line under `## Left out` in `docs/architecture/left-out.md` that this environment now shows. A similar name is not enough. The environment has to show that fact. When the file is missing, or no line is shown, the section says no line comes off. A `## Dismissed` line stays dismissed. Do not offer it.

Stop. Do not write files yourself. Ask the section in front of you. Stop until that section has an answer. Then the owner adds. Then ask the next section. Do not ask the next section in the same questions call.

Use the questions tool when it is available. Options only. Put that section’s items in the question prompt. Do not shorten the prompt by dropping an item.

**Skipped, when it lists resources.** Options:

1. **Keep every resource in this section skipped.**
2. **I will edit this section.**

Do not offer an option that reads a production resource.

**Skipped, when nothing was skipped.** Options:

1. **Nothing was skipped.**
2. **I will edit this section.**

**Seen, when it lists resources.** Options:

1. **These are seen in this environment.**
2. **None of this section.**
3. **I will edit this section.**

**Seen, when it shows no resource.** Options:

1. **This environment shows no resource.**
2. **I will edit this section.**

**Links, when the environment shows at least one.** Options:

1. **The environment shows every connection in this section.**
2. **I will edit this section.**

**Links, when none is shown.** Options:

1. **No connection is shown.**
2. **I will edit this section.**

Do not add an option that accepts a guessed link.

**System, Architecture, or Match, when it lists new lines.** Options:

1. **Add every new line in this section.**
2. **Add none of this section.**
3. **I will edit this section.**

**System, when the folder is missing.** Options:

1. **Add none. The folder is missing.**
2. **I will edit this section.**

**Architecture, when the file is missing.** Options:

1. **Add none. The file is missing.**
2. **I will edit this section.**

**Match, when no slice owns this.** Options:

1. **Add none. No slice Match owns this.**
2. **I will edit this section.**

**System or Architecture, when the file is current.** Options:

1. **Nothing new.**
2. **I will edit this section.**

**Left out, when it lists lines the environment shows.** Options:

1. **Take every shown line off left-out.md.**
2. **Take none off.**
3. **I will edit this section.**

**Left out, when no line comes off.** Options:

1. **No line comes off.**
2. **I will edit this section.**

When the answer is **I will edit this section**, stop. Wait for the edited section. That edit is the answer. Do not ask that section again. Sections already answered stay answered. A line they struck stays out. A resource they add that the reader did not take stays out. A link they add that the environment does not show stays out. Say the environment does not show it. Omitting a listed item does not drop it.

A skipped confirm writes no file. The skipped lines stay skipped.

## The owner adds

You do not write the file. The skill that already owns it adds only what is new, after that section’s answer. The handoff is the confirmed lines. It is not that skill’s interview, branch prompt, or first write. Do not start Specify, Plan, or Build.

Mark every added line `Seen in <host> <environment>.` Do not mark it as something the code shows. Do not rewrite a line that is already there. A connection is added only when the links section says the environment shows it.

**System.** `/crav1-keep-current` owns the picture in `docs/system` (drop-in: `.claude/skills/crav1-keep-current/SKILL.md`; plugin: sibling `skills/crav1-keep-current/SKILL.md`). It adds only a new sentence, node, edge, or connection line. If `docs/system/` is missing, it writes nothing.

**Architecture.** `/crav1-repos-to-spec` owns `docs/architecture/spec.md` (drop-in: `.claude/skills/crav1-repos-to-spec/SKILL.md`; plugin: sibling `skills/crav1-repos-to-spec/SKILL.md`). It appends only a new line when that file is already there. If the file is missing, it writes nothing. It does not create the file from the environment.

**Match.** `/crav1-add-to-spec` owns the quote on a feature spec that already exists (drop-in: `.claude/skills/crav1-add-to-spec/SKILL.md`; plugin: sibling `skills/crav1-add-to-spec/SKILL.md`). It adds the quote only on a slice Match already owns. If none does, it writes nothing. It does not create a slug.

**Left out.** `/crav1-repos-to-spec` owns `docs/architecture/left-out.md`. A line the environment now shows comes off that file. A line that stays is not rewritten. The line that comes off is not written back as a guess.

## Stop

Do not plan. Do not implement. Do not commit. Do not start Specify, Plan, or Build. Do not run `/crav1-spark-to-spec`, `/crav1-ideas-to-spec`, `/crav1-intake-to-specs`, `/crav1-match-to-specs`, `/crav1-plan-from-spec`, `/crav1-implement-task`, `/crav1-feature-branch`, or `/crav1-finalize-commit`.

Output only:

- Host and environment, or that the read stopped before a reader
- The reader used, or that this host has no reader
- Counts: seen, skipped, unmarked and not read, connections shown
- Files the owners changed, or that nothing was written
- Next: `/crav1-finalize-commit` when a file changed (no push). When nothing was written, name no command. Do not run it.

## Hard rules

- No host named: stop. Do not guess the host.
- No environment named: stop. The user names the environment, not the subscription.
- Never production. A resource marked production is skipped and listed as skipped.
- A host with no reader stops. This build reads Azure only. Do not pretend to read Google Cloud, AWS, or any other host.
- Do not read Azure DevOps, GitHub, or CI.
- A resource with no environment mark stops the read and is not read.
- This skill does not write `docs/system`, `docs/architecture/spec.md`, a feature spec, or `docs/architecture/left-out.md`.
- A fact is seen in that environment. It is not something the code shows.
- A link is added only when the environment shows the connection. Do not invent a link.
- One section at a time. Every item stays listed.
- The owner adds only what is new. Do not rewrite a line that is already there.
- A slice Match does not already own is not a new slug.
- Do not start Specify, Plan, or Build.

## Style

Be concise. Cite the resource id. Prefer the smaller fact. Do not fill a gap with an architecture you invented.
