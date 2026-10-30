# crav1-read-environment: sections

Read only when the pointer in `SKILL.md` sends you here. Moved word for word from `SKILL.md` in 1.71.0; the rules are unchanged.

## The owner adds

You do not write those files. The skill that already owns the file adds only what is new, after that section’s answer. The handoff is the confirmed lines. It is not that skill’s interview, branch prompt, or first write. Do not start Specify, Plan, or Build.

Mark every added line `Seen in <host> <environment>.` Keep `shared with prod` when the confirmed line says it. Keep `prod only` when the confirmed line says it. Keep `Shape and connections only.` when the confirmed line says it. A prod-only line keeps `Seen in <host> prod.` Do not mark it as something the code shows. Do not rewrite a line that is already there. A connection is added only when the links section says the environment shows it.

**System.** `/crav1-refresh-system-notes` owns the picture in `docs/system` (skill `crav1-refresh-system-notes`, `SKILL.md`). It adds only a new sentence, node, edge, or connection line. If `docs/system/` is missing, it writes nothing.

**Architecture.** `/crav1-existing-to-specs` owns `docs/architecture/spec.md` (skill `crav1-existing-to-specs`, `branches/repos-only/BRANCH.md`). It appends only a new line when that file is already there. If the file is missing, it writes nothing. It does not create the file from the environment.

**Match.** `/crav1-add-to-spec` owns the quote on a feature spec that already exists (skill `crav1-add-to-spec`, `SKILL.md`). It adds the quote only on a slice Match already owns. If none does, it writes nothing. It does not create a slug.

**Left out.** `/crav1-existing-to-specs` owns `docs/architecture/left-out.md`. A line the environment now shows comes off that file. A line that stays is not rewritten. The line that comes off is not written back as a guess.

## Picture offer

When this run appended one or more lines to `docs/environments/marks.md`, ask once at the end. Do not ask when no marks line was added. Do not ask once per line.

The question is exactly:

The system picture may now be out of date. Run `/crav1-refresh-system-notes`?

Options are yes and no. Use the questions tool when it is available. Do not run `/crav1-refresh-system-notes` from this question. A yes waits for a later turn. A no ends without that command.

The confirmed system section is unchanged. After that section’s answer, `/crav1-refresh-system-notes` still adds only those confirmed lines. This question is not that handoff.

## Sections

Show one section at a time. Each section has its own question and its own answer. Do not merge sections into one list. Do not collapse the questions into one write-or-not question. List every item. Do not drop a resource, a skipped line, a link, a trigger, a fact, or a left-out line to keep a section short.

A fact already written in the destination file stays in its section and is marked already written. The owner does not add it again.

Use only these sections, in this order. Do not invent another section. Resources the user left unread, and pre-prod, shared, or prod-only resources they declined, stay out of Seen, Links, System, Architecture, and Match. A declined prod-only resource stays in Skipped. The counts at the end name them.

**Skipped.** Every production resource this pass did not read for shape. That is a prod-only resource the user declined, or a prod-only resource that was not asked because the read stopped. Each line is the resource name, the group, and the mark that said production. The line says skipped. It is not a fact and not a link. When every prod-only resource was read for shape, the section says nothing was skipped.

**Seen.** Every resource this pass took, plus every SQL or storage fact a yes on look inside returned. A full non-prod resource is in this list. A pre-prod, shared, or prod-only resource is in this list only after the user said yes. Each line cites the resource id, the name, the group, and every source. A schema, table, column, container, or prefix line cites that name and the token when one matched. Each line says `Seen in <host> <environment>.` Use the environment column in the mark table. A shared line also says `shared with prod` and shows both sources. A pre-prod or shared line also says `Shape and connections only.` A prod-only line says `Seen in <host> prod.` It also says `prod only` and `Shape and connections only.` The environment is prod. That sentence is the shape read. It is not a full production data read. It does not say the code shows it. When no resource was taken and no shape resource was read, the section says this host shows no non-prod resource. Do not invent one. A host that shows only prod-only shape lines lists those lines.

**Links.** A connection the environment shows on a seen resource: a field that names another resource id or hostname, and a trigger. Cite the resource id and the field. A trigger line shows the definition only: what starts the work, what it runs, and the schedule when it has one. A SQL job or trigger, and a storage trigger, use that same line when look inside reached them. Never a payload. Never a secret value. Never command text. A secret name may be cited. The secret value is not. The reader file lists the trigger kinds for that host. A similar name is not a connection. A seen resource does not become a link by itself. A link from a prod-only resource also says `prod only` and `Shape and connections only.` When no field and no trigger shows a connection, the section says no connection is shown. Do not offer a guessed link.

**System.** Seen facts, and links the environment shows, that belong in `docs/system`. A line from a prod-only resource also says `prod only` and `Shape and connections only.` When `docs/system/` is missing, the section says so. This command does not create that folder. When every line is already in the picture, the section says the picture is current.

**Architecture.** Seen facts, and links the environment shows, that belong in `docs/architecture/spec.md`. A line from a prod-only resource also says `prod only` and `Shape and connections only.` When that file is missing, the section says so. This command does not create it. When every line is already there, the section says the architecture spec is current.

**Match.** A seen fact that belongs on a slice Match already owns. That slice is a `docs/specs/<slug>/spec.md` (skip `_template`) that already has `## Match` for this fact. A line from a prod-only resource also says `prod only` and `Shape and connections only.` When no such spec exists, the section says no slice Match owns this. Do not create a slug. When more than one Match spec could take the fact, list each slug in the section. Do not drop one.

**Left out.** Every line under `## Left out` in `docs/architecture/left-out.md` that this environment now shows. A similar name is not enough. The environment has to show that fact. When the file is missing, or no line is shown, the section says no line comes off. A `## Dismissed` line stays dismissed. Do not offer it.

Stop. Do not write those files yourself. Show every section, then ask them in one questions call, one question per section (1.70.0). Stop until every section has an answer. Then the owner adds what was confirmed.

Use the questions tool when it is available. Options only. Put that section’s items in the question prompt. Do not shorten the prompt by dropping an item.

**Skipped, when it lists resources.** Options:

1. **Keep every resource in this section skipped.**
2. **I will edit this section.**

Do not offer an option that reads a production resource. The shape question already decided that.

**Skipped, when nothing was skipped.** Options:

1. **Nothing was skipped.**
2. **I will edit this section.**

**Seen, when it lists resources.** Options:

1. **These are seen in these environments.**
2. **None of this section.**
3. **I will edit this section.**

**Seen, when it shows no resource.** Options:

1. **This host shows no non-prod resource.**
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
