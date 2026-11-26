# Read notes and ask the gap finder

Run the engine with the invocation words and `{}` on stdin.

When `needs_finder` is false, print `ending` and stop. No unread note is waiting.

When `needs_finder` is true, call `crav1-2-gap-finder-agent` once. Give it only these fields from the engine reply:

- `notes` (each note's markdown)
- `spec_markdown`
- `decisions_markdown`
- `tasks_markdown`

The agent returns one JSON object and no other text. Do not assign `F-`, `G-`, `C-`, `D-`, `A-`, or `I-` ids. Do not edit the spec yourself.

Call the engine again with the same words and this object on stdin:

```json
{"finder": {"items": []}}
```

`items` is the agent's list, unchanged. Keep `at` out unless the user named a time.

Then:

- `dry_run` true: print every card, then `proposed_items`. Stop. Nothing was written.
- `card_text` set: print that card and stop.
- `ending` set: print it and stop.
