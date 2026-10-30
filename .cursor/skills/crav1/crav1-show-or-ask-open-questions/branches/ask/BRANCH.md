# Show or ask open questions: Ask branch

Read only when `SKILL.md` routes here (`ask`). Moved word for word from `SKILL.md` in 1.106.0; the rules are unchanged. The shared sections in `SKILL.md` still apply. A `references/…` or `assets/…` path is relative to the skill folder, not this branch.

## Input

Everything after the command, and every `@`, is the input. The user names one of these:

- **A person or a group.** For example `Dana`, or `Finance`. Questions waiting for that person, and questions routed via that person, are theirs. "Finance via Dana" is a question for Dana.
- **A spec.** An `@` of a spec folder or its `spec.md`, or its title.
- **A topic.** A few words, such as `static IP` or `mTLS`.

They may also name the output kind and the language.

When the input names none of person, spec, or topic, stop and ask. Options only. The options are:

1. **A person** — gather the questions that person can answer. Reply with the name.
2. **A spec** — gather every open question on one spec. Reply with an `@` of the spec, or pick it.
3. **A topic** — gather open questions on that subject across all specs. Reply with the words.

## Pending first

Read `references/asked.md` ("Pending first") only when questions are already marked pending.

## Gather

Collect every open question that fits the selection.

Person, spec, topic, branch, and pull request (`pr71`, `#71`) follow `crav1-add-to-spec` `references/scope.md` (drop-in: `.cursor/skills/crav1/crav1-add-to-spec/references/scope.md`; plugin: sibling `skills/crav1-add-to-spec/references/scope.md`).

Skip a question that already has a clear `Answered:` line. Say how many were skipped and why. Skip a question with an `Asked:` line for this person unless the user asks to ask again. Say how many were skipped and when they were asked.

Every question that fits stays listed. Nothing is dropped to keep the list short. When the same question sits on two specs, it is one question in the draft, and both specs get the mark.

Show the gathered list in the chat, numbered, each with its spec path. That list is for the user. The draft is not.

## Output kind

Read `references/drafting.md` ("Output kind") only when you write the draft.

## Language

Read `references/drafting.md` ("Language") only when you write the draft.

## Write the draft

Read `references/drafting.md` ("Write the draft") only when you write the draft.

## Asked?

Read `references/asked.md` ("Asked?") only when you ask whether the draft was sent.
