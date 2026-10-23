# When they pick `change`

Read when they pick `change` after seeing the blocks.

- If they say rewrite, run the draft step again on the **same** file set and style source, and discard the previous wording.

- If they paste a full new Summary and/or Description, use that text (cleanup only: no Conventional Commits unless the style source is git log that already uses them). Their pasted Description replaces the body, including its last line.
- If they give notes (“shorter summary”, “mention verify.md”), rewrite just those parts. Keep the trailing work-item mention as the last line of the Description unless the note changes or removes it.
- Ask which field if it is unclear.
- Then show the new paste blocks and **then** the same choices again (`commit` still first). Never commit in the same turn as `change` unless they also said `commit` **after** seeing the new blocks.
