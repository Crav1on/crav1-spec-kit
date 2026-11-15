# Other-owner mode

Read this when the pull request author, or a commit author on the branch, is not the current user. `scripts/build_walk.py owner` reports that. An unnamed current user is not a switch. Ask who, and do not guess.

Confirm before switching. First one sentence that names the owner, for example `PR 71 on feat/orders-cicd is person A's.` Then this card:

Card: Should I add my work to their pull request?
- **Add to their pull request (Recommended)** (`switch`): build T5 on PR 71's branch so it lands in PR 71; I comment after each push and never merge it. Why: the branch is already theirs.
- **Keep it as my own** (`own`): build as usual, and I open and merge the pull request myself.
- **Stop** (`stop`): change nothing and end the walk here.

`switch` sets `Owner: other` in this branch's progress file. `own` keeps `Owner: self`. Do not switch before that word.

In other-owner mode the walk never opens a pull request, never merges the base into the branch, and never merges or completes the pull request. `allowed` from the script is false for those four. A phase that would have been one of them becomes a comment, or a wait, instead.

After a push, write one pull request comment that says what was pushed. One push, one comment. Post it only after `yes`. The comment does not change the description.

`edit-description` is the only way to change the description, and only because this run asked. Without that word, leave the description as it is.

Ticks for tasks on this branch wait until that pull request is merged. The row stays `[ ]`. The Waiting line says it in plain words, for example `Waiting for person A to merge PR 71 before T5 is ticked.` Do not tick early.
