# Approval needed, in a draft

Read this when the selection includes an `## Approval needed` item, or when show lists what is still open.

Gather each item that has no matching `Approved:` line. An item with that line is skipped. Say how many were skipped. An `Asked:` line for this person skips the item unless they ask to ask again.

The draft may be a mail, a meeting agenda, a chat message, or a PR comment. A PR comment is the text they would paste on the pull request. Nothing is sent, posted, or replied.

The draft names the person (`Person:`), what they are asked to approve, and enough context. No spec slug, path, file, or task id. `Holds:` stays in the spec and is not copied into the draft.

Yes writes `Asked:` under the item. Pending writes `Pending:`. No writes nothing. The channel for a PR comment is `PR comment`. The same lines as an open question, from skill `crav1-add-to-spec`, `references/open-questions.md`.

Show lists each unapproved item with its person and its `Holds:` tasks, beside the open questions. It writes nothing.
