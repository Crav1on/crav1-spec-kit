# What's known about one thing

Kit not in this project yet? [Install first](install.md) (Cursor and Claude Code; the slash commands match, the files do not). After a Cursor plugin install, the short command loop is [plugins/crav1/README.md](../plugins/crav1/README.md). Claude Code has no plugin.

Use this when the user asks about **one feature, slice, resource, or not-yet-feature**. Status and what is pending are this command. The answer comes from the specs first. A kit script this command runs uses the interpreter in [Running a kit script](reference/running-scripts.md).

This is cross-cutting. It is not its own lane. It may run from any lane. It does not move work into Specify, Plan, or Build. It does not start those lanes.

It is a later skill. It is not a starter option. When the user asks for startup options, that ask names only `/crav1-spark-to-spec`, `/crav1-ideas-to-spec`, `/crav1-bundle-to-specs`, `/crav1-existing-to-specs`, `/crav1-read-environment`, and `/crav1-fix-bug`. It does not run this command. The six starter options stay unchanged.

[Explain](from-explain-existing-system.md) (`/crav1-explain-existing-system`) reads `docs/system/` first. When the picture has nothing on the question, it quotes the first paragraph of a matching spec, labelled as coming from the spec, and names this command. It does not run this command. This command is the one feature. It reads the specs first.

The command writes nothing in the project until a filled playbook is applied. It does not run another skill, except apply at the end of a playbook walk on yes. It may name one.

## First prompt

New chat. Name the thing, or `@` a spec folder or a code folder.

```text
/crav1-what-do-we-know-about-this

What's the status of <the feature, slice, or resource>? What's pending?
```

One folder:

```text
/crav1-what-do-we-know-about-this
@docs/specs/<slug>/
```

That slash command *is* the prompt.

A name matches first as written (`fn-market-data`, a slug, a title). A sentence or two is matched on its key words. An `@` keeps the search inside that path. A focus such as "just the security bits" or "only what's pending" still runs the full read. The answer shows only those sections.

If the message has no name, no sentence, and no `@`, the command stops. Options only. It does not pick a thing.

Pasted minutes go to `/crav1-add-to-spec`. A long dump goes to `/crav1-add-to-spec`. This command stops and names that one. It does not run it.

## Reports (1.104.0)

Add one word to get a fixed report as a `.md` file instead of the free-form answer:

```text
/crav1-what-do-we-know-about-this report-feature-full xbid
/crav1-what-do-we-know-about-this report-change-short pr74
/crav1-what-do-we-know-about-this report-build-full @docs/specs/<slug>/
/crav1-what-do-we-know-about-this report-playbook-short CC Process 1.0
/crav1-what-do-we-know-about-this report-data-model-full orders
```

| Word | What you get |
| --- | --- |
| `report-feature-short` | Verdict, what it is, how it works, one flow diagram |
| `report-feature-full` | Every section: flows, C4 levels 1–2 (3 when described), deployment, decisions, delivery, live state |
| `report-change-short` | Verdict, 30-second version, what changes, one diagram |
| `report-change-full` | Architecture, branches, pipelines, the change, the discussion, open decisions; C4 only when architecture or pipelines matter |
| `report-build-short` | Status and the next tasks in dependency order |
| `report-build-full` | Every gap, the unblock order wave by wave, the task graph |
| `report-playbook-short` | Preview (1.109.0). Kept, Needs your answer (questions and spec conflicts, recommended + why), Compose, every kit step in order, an order diagram |
| `report-playbook-full` | Preview (1.109.0). Where it stands, the three buckets, every kit step, the order diagram, gaps no skill covers; then asks *Walk through it now?* (1.116.0) |
| `report-playbook-walk` | 1.116.0. Resumes the walk in chat at the first unanswered item of an existing playbook report |
| `report-data-model-full` | 1.118.0, export shape 1.121.0. One review of a saved data model, built from the saved records. Markdown and a PDF with the same prose and the diagrams drawn by name. It does not model again |

The command picks the template from the word, then reads only that template; the others stay closed. Diagrams are Mermaid wherever a picture helps. A live source that needs a sign-in or a permission is asked about first. The file goes to your Downloads folder when the agent can reach it, otherwise a temp folder, and the chat always links it. That first write does not change the project. A filled playbook is copied into the project only when it is applied.

A playbook lists; it does not take answers in chat. Kept decisions can still be changed, the merge order is a suggestion, and every step says what to type, what you should see, and when it is done (1.109.1). Above the Kept and Needs your answer items, a short block says how to change or answer each item, and every item says which step records it. Any **Conflict:** line in the covered specs is listed under Needs your answer as C1, C2, …, with both sides and a recommended answer (1.112.0). An early step answers the questions and settles the conflicts with `/crav1-resolve-open-questions`, whenever you come back, and names every N and C it covers. Kept, Needs your answer and conflict items are bullet blocks, not tables, each with a plain `Answer:` or `Change:` line right under it (1.115.1), so you can fill the file yourself or send it to people who do not use the kit; read it back with `/crav1-resolve-open-questions apply <file>`, which checks what changed in the specs since the report and asks about any clash before writing (1.110.0). Files filled in with the older table layout still read back. Compose is written out as bullets, and the order diagrams use syntax every viewer renders.

**Walk it in chat (1.116.0, chat 1.117.0).** After `report-playbook-full` writes the file, it asks *Walk through it now?*. On yes, it first offers to settle the answers that block several steps (for example the merge order; `skip` takes them in order), then walks in Steps order, one item at a time, each with a short *Why this matters* (where it came from, what it changes) and the recommendation. Reply `yes`, your own answer, `more` for the full background, or add what you know; jump with `go to N9`. The chat states each item in words and does not use the report's item ids, not even in parentheses. You can also ask back, push back or change direction: it redrafts only Compose, Merge order and Steps as needed. When what you say and the record do not match, it works out the outcome you want from the known facts and your words, one follow-up at a time, then summarizes and waits for an explicit yes before it writes. Each clear answer is saved into the report, and nothing touches a spec during the walk. It does not start help, and it does not run pr-status. At the end you get a summary and an offer to run `/crav1-resolve-open-questions apply` on your yes, which writes only the filled confirmed lines and copies a filled playbook to `docs/playbooks/<topic>.md` (1.120.0). Stop any time and resume with `report-playbook-walk`. That resume also accepts a `docs/playbooks/` path. A headless run never walks; it writes the file and says how to resume. A short playbook still does not walk.

Already applied, then new information landed in the specs? Do not re-walk the playbook: [what to run](from-tighten-and-plan.md#already-applied-then-new-information).

## Steps

| Phase | You | Agent |
| --- | --- | --- |
| Question | A name, a sentence or two, an `@`, or a focus | Stops when nothing was named. Does not scan the repo to pick a thing |
| Match | — | One pass. Exact name first, then key words. Spec titles and Match quotes weigh highest. One winner, or a list to choose from |
| Slice | Read the answer | The spec, the plan, the tasks, Match, and open questions. The path is named |
| No slice | Read what is known | Repo, code, and environment notes. A candidate slice. Names spark, ideas, or intake. Does not run it |
| Live | Yes or no when a resource is prod-only | Azure settings and recent changes. Azure DevOps work items, open pull requests, and branches. Each fact is a live read. Never data |
| Live failed | Retry or Skip | One prompt. Skip is the repo-only answer, with why the live checks did not run |
| Stop | Glance | Writes nothing in the project, except a filled playbook copied on apply. Does not start Specify, Plan, or Build |

Two or more close hits: one line each, then which. It does not guess.

A code-only hit, with no spec and no architecture note, says what the code shows and fills in Unexplained.

## What gets written

Nothing in the project for the free-form answer and for feature, change, and build reports. Those reports are one file outside the project. A playbook report's first write is the same. On apply, a filled playbook is copied to `docs/playbooks/<topic>.md`. A draft with no filled answer is not copied. `report-data-model-full` writes one new snapshot under the saved model, `report.md` and `report.pdf`, and does not edit the model.

No spec edit. No `plan.md`. No `tasks.md`. No marks. No application code.

The answer leaves out an empty section. It does not pad. A guess is labeled `(inference, not in the docs)`.

## After

When there is no slice, the answer names one next command. This command does not run it.

When something in the answer is unknown or a guess, and an open question in a spec asks the same thing, the answer ends with one `Next:` line (1.78.0, one line since 1.122.0), as [How a run ends](reference/run-ending.md) says. One match: `Next: /crav1-show-or-ask-open-questions ask research static IP, because the answer leaves that question open.` It adds the spec, as in `orders static IP`, only when those words would match more than one spec. Several questions match: one line for the command, not one line per question. Nothing matches: no line. It does not run it and asks nothing.

- One or two sentences: `/crav1-spark-to-spec`
- A pile of ideas and technical hunches: `/crav1-ideas-to-spec`
- Several features, or mixed files: `/crav1-bundle-to-specs`

When nothing is written down, it names those three.

Production follows `/crav1-read-environment`: shape and connections only, after the same yes or no. A no leaves that resource unread. This command does not run the environment read.

Reference page: [what-do-we-know-about-this](reference/skills/crav1-what-do-we-know-about-this.md)
