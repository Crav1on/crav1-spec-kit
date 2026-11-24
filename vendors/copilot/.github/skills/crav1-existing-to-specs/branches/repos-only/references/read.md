# Repos to spec: **Read (no files yet)**

Part of `branches/repos-only/BRANCH.md`, read only when that file sends you here. Moved word for word in 1.107.0; the rules are unchanged. Paths in backticks are relative to the skill folder.

## Read (no files yet)

Read the named repos. On a later re-read, also read `docs/architecture/spec.md`, `docs/architecture/left-out.md` when that file exists, and the real notes in `docs/system/` so you know which lines are already there. Then show the confirmation in sections. Do not merge those sections into one list. Do not write files.

On every re-read, check the code again for every line in `docs/architecture/left-out.md`, especially the lines under `## Left out`. A similar name, a README wish, or a matching identifier that the code does not actually call is not enough.

- When the code now shows the fact, that line is a confirmed fact. Put it in that repo’s section and cite the path. It is not a guess. It does not stay in the left-out section.
- When the code now shows a real link, that line is a link. Put it in the links section and cite the path. It does not stay in the left-out section. Confirming a guess does not turn it into a link. Only the code does.
- When the code still does not show it, a `## Left out` line stays in the left-out section. A `## Dismissed` line stays dismissed. Do not offer a dismissed line.

Use only these sections. One section per named repo, for that repo’s confirmed facts. One section for inferred guesses. One section for links. One section for left-out. Do not invent another section.

List every item in its section. Do not drop a confirmed fact, a guess, a link, or a left-out line to keep a section short. On a later re-read, mark a fact or a link that is already a line as already written. Keep it in its section. The write does not add it again.

**Named repo.** One section. The heading is that repo’s name. Confirmed facts for that repo only. A fact the code shows. A reader can point at a file, a type, a route, a config key, or a dependency. Cite the path on every line. A fact with no path is not confirmed. When this repo shows no confirmed fact, the section says so. Do not invent a fact.

A smaller fact beats a story. A name a file shows stays confirmed. A purpose the code does not state is inferred.

**Inferred.** One section. A guess. A purpose, a product story, or a “should” the code does not state. A guess stays out until this section’s answer accepts it, or the left-out section’s answer accepts it. Then it is accepted from a guess, not a fact the code shows. When the read has no new guess, the section says so. Do not invent a guess. Do not put a guessed link in this section as something to accept. Do not list a guess that is already under `## Left out` or `## Dismissed`.

**Links.** One section. A link is code in one named repo that reaches another named repo: a call, an import, a URL, a client, a queue, or a config entry. Cite the path. A link is written only when the code shows it. A comment, a README wish, or a similar name is not a link. Confirming a guess does not turn it into a link. One named repo has no second repo to reach. The section says only one repo was named. Do not invent a link inside that repo and call it a link between repos. When more than one repo was named and the code shows no link, the section says no link between these repos is in the code. Do not offer a guessed link as something to accept.

**Left out.** One section, asked in the same questions call as the others (1.70.0); it lists the inferred guesses with the note that a guess accepted under inferred drops out of it. List every line under `## Left out` that the code still does not show, and every guess the inferred answer did not accept. Each line is the guess, and it says the code does not show it. It is not a confirmed fact and it is not a link. When no such line remains, the section says no line is left out. Do not list a `## Dismissed` line. Do not drop a line to keep the section short.

Stop. Do not write files. Each section gets its own question and its own answer. Do not collapse those questions into one write-or-not question. Stop until each section has an answer. Those answers are the only stop before writing. Do not open a feature interview, an architecture interview, or an export-format question.

Use the questions tool when it is available. Options only. One question per section, in this order: each named repo, then inferred, then links, then left out, all in one questions call (1.70.0). Put that section’s items in the question prompt. Do not shorten the prompt by dropping an item. When the tool cannot take several questions in one call, list them in one message and take the answers together. Do not write between answers.

**Named repo, when it lists facts.** Options:

1. **Write every fact in this section.**
2. **Write none of this section.**
3. **I will edit this section.**

**Named repo, when it has no confirmed fact.** The section already says so. Options:

1. **Write none of this section.**
2. **I will edit this section.**

**Inferred, when it lists guesses.** Options:

1. **Accept none.**
2. **Accept every guess in this section.**
3. **I will edit this section.**

**Inferred, when it has no guess.** The section already says so. Options:

1. **Accept none.**
2. **I will edit this section.**

**Links, when the code shows at least one.** Options:

1. **Write every link in this section.**
2. **I will edit this section.**

**Links, when the code shows none.** The section already says only one repo was named, or that no link between these repos is in the code. Options:

1. **Write that line.**
2. **I will edit this section.**

Do not add an option that accepts a guessed link.

**Left out, when it lists lines.** Options:

1. **Keep every line left out.**
2. **Accept every line.**
3. **Dismiss every line.**
4. **I will edit this section.**

**Left out, when no line is left out.** The section already says so. Options:

1. **No line is left out.**
2. **I will edit this section.**

In a left-out edit, mark each line accept, keep left out, or dismiss. A line with no mark stays left out. Omitting a line does not dismiss it and does not drop it. Dismiss means that line is not offered again.

When the answer is **I will edit this section**, stop. Wait for the edited section. That edit is the answer. Do not write yet. Do not ask that section again. Sections already answered stay answered. A confirmed fact they struck stays out. A fact they add that the code does not show stays out. A guess they do not accept stays out of the spec. A guess the inferred section or the left-out section accepts is written later as accepted from a guess, not as a fact the code shows. Confirming a guess does not turn it into a link. If they add a link the code does not show, do not write that link. Say the code does not show it. A link they struck stays out.
