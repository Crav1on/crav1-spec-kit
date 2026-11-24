# Repos to spec: **First write**, **Left-out file**, **Missing architecture spec**

Part of `branches/repos-only/BRANCH.md`, read only when that file sends you here. Moved word for word in 1.107.0; the rules are unchanged. Paths in backticks are relative to the skill folder.

### First write

`docs/architecture/spec.md` is missing, and the system notes are missing or only the untouched template. Write the architecture spec, the left-out file, and the system notes. Replace the template fills.

| File | Fill |
| --- | --- |
| `spec.md` | The sections in `assets/spec.md`. Confirmed facts under **Confirmed** and under the repo heading, each with a path. Accepted guesses only under **Accepted from a guess**, each saying the code does not show it. Leave that section empty when they accepted none. Under **How the repos connect**, one line per link the code shows, with the path. When only one repo was named, the only line is `Only one repo was named.` When more than one repo was named and the code shows no link, the only line is `No link between these repos is in the code.` **Open questions** name what the code does not show. A guess they did not accept stays out of this file. Do not add a Left out heading. |
| `landscape.md` | One short paragraph of what the code shows these repos are. Replace the template sentence. Under `## How the parts connect`, one line per link the code shows. When only one repo was named, one line: `Only one repo was named.` When more than one repo was named and the code shows no link, one line: `No link between these repos is in the code.` **v0** is the architecture the code already shows, in one line. Leave **Later** empty. Bulk assumptions are confirmed facts only. When the code states none, write `None the code states.` Constraints are only ones the code shows. When it shows none, write `None the code states.` Leave the feature index empty until the spec file exists, then one row: slug `architecture`, spec `docs/architecture/spec.md`, Repos column lists the destination and the named repos, Notes `architecture`. |
| `repos.md` | Every named repo, plus the destination when it is the new clean repo. Status `exists` when the checkout is a real repo. Put the URL when the checkout has one. The new clean repo stays without a remote. Boundaries only when the code shows one. Include the `## Synced at` section. For each repo this run read, set its `Synced at` line as under **Synced at** below. A new clean repo with no commit stays empty. Add the `Work items go to` column when it is missing; leave its cells empty. Never fill a home here: the first Azure Boards skill that needs one asks ([work-item-homes.md](../../../../crav1-ado-sync/branches/push-features/references/work-item-homes.md)). |
| `diagrams.md` | One context diagram. Replace the sample. One heading, one sentence, one fence. Nodes are the named repos. An edge only when the code shows that link. When only one repo was named, one node and no edge, and the sentence says only one repo was named. When more than one repo was named and the code shows no link, draw the nodes and no edge, and the sentence says no link was found. Do not invent a user, a service, or a queue. |
| `glossary.md` | From `assets/system/glossary.md`. See the glossary rules below. |
| `adr/` | Only where the code shows a real choice, with real alternatives. Otherwise write no ADR. A guess is not an ADR. |

**Glossary.** `glossary.md` is part of the landscape, not a feature spec. Source is the code in the named repos. Do not invent terms, expansions, or definitions. Do not write TBD or to be decided. A row is only a word or abbreviation that code already uses. When that same code already says the expansion or meaning, put that text in Meaning. When the code never says what it means, set Meaning to `to be researched`. Skip ordinary English. A code identifier is not a row unless the code already treats that word as a term. Write the file even when it has no rows. An accepted guess does not add a row.

The picture is the short description, the context diagram, and `## How the parts connect`. This write fills those three from the confirmed facts the repo sections’ answers kept. Do not run `/crav1-refresh-system-notes`.

### Left-out file

Write `docs/architecture/left-out.md` from `assets/left-out.md` on the first write and on the missing-architecture-spec pass. On a later re-read, update that file. When it is missing, write it. Do not put this file under `docs/system/` or `docs/specs/`. Do not copy its lines into `spec.md`.

Each line names the guess and then says `The code does not show it.` A line here is not a confirmed fact and not a link.

- **Left out.** A guess the inferred answer did not accept. A line already under `## Left out` that this answer keeps. Keep every such line. Do not drop one to keep the file short. Do not reword a line that stays.
- **Dismissed.** A line the left-out answer dismisses. Move it here. Do not reword the guess. Do not offer it again in the inferred section or the left-out section. Keep it in the file so the next read knows.
- **Remove.** A line the read moved to a confirmed fact or a link. A line the left-out answer accepts. Take it off this file. An accepted line is written in `spec.md` under **Accepted from a guess** and still says the code does not show it. It is not a link. A line the read moved to a fact or a link is removed even when that section’s answer strikes it. Do not put a struck fact or a struck link back in this file. The code shows it, so it is not a guess. The next read can offer it again as a fact or a link.

When the code still does not show a left-out line, the line stays under `## Left out` unless this answer accepts it or dismisses it.

### Missing architecture spec

A real note is already in `docs/system/`, and `docs/architecture/spec.md` is missing. Write that spec, using the `spec.md` row above, and write the left-out file. Leave every file under `docs/system/` as it is. The one exception is the `Synced at` line in `repos.md` under **Synced at** below, and only when `repos.md` already exists. Do not add any other line. Do not rewrite any other line. Do not create `repos.md` on this pass. Do not fill a gap in those notes on this pass. Do not run `/crav1-refresh-system-notes`.
