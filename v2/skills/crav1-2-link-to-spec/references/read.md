# Read notes and ask the gap finder

Run the engine with the invocation words and `{}` on stdin.

When `needs_finder` is false, print `ending` and stop. No unread note is waiting.

When `needs_finder` is true, call `crav1-2-gap-finder-agent` once. The engine has written the finder inputs to files. Pass the four paths in `finder_files` and tell the agent to read them:

- `finder_files.notes`
- `finder_files.spec`
- `finder_files.decisions`
- `finder_files.tasks`

Do not paste those files into the chat. Do not split them by hand. `notes` in the reply is the list of note ids only.

The agent returns one JSON object and no other text. Do not assign `F-`, `G-`, `C-`, `D-`, `A-`, or `I-` ids. Do not edit the spec yourself.

Call the engine again with the same words and this object on stdin:

```json
{"finder": {"items": []}}
```

`items` is the agent's list, unchanged. Keep `at` out unless the user named a time.

Then:

- `ending` set: print it first. When `cards` is empty, stop. Nothing was written.
- `dry_run` true: print every card, then `proposed_items`. Stop. Nothing was written.
- `card_text` set: print that card and stop.
