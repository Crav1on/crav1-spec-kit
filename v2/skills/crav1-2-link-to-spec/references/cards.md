# Cards, park, and resume

A card is already on screen, or the user said `park` or `resume`. Send the word back to the engine. Do not call the gap finder again. Do not rebuild the cards.

## Park and resume

`park` with no card word saves the open run and prints the same card. A later chat says `resume`. The session file is the only memory. Send `{}` on stdin.

`resume` loads that file and prints the card that was waiting. `resume` plus a card word answers it. An answer word alone, while the run is parked, is refused. Say `resume` and the word.

`resume dry-run` prints the remaining cards and the proposed items and writes nothing.

`pick-some` and `change-some` take numbers, for example `pick-some 1 3`.

## What the words do

The engine ranks cards. A high-impact gap is its own card. Low-impact gaps that do not say MUST share one assumption card. Open questions that already have an `answer.matched` event share one card: "These N open questions have answers in the SoT".

| Card | Words |
| --- | --- |
| Silent gap | `add-pointer`, `open-question`, `leave-out`, and `skip` |
| Conflicting gap | `prefer-source`, `keep-spec`, `ask-owner`, and `skip` |
| Vague gap | `use-proposed`, `ask-owner`, `leave-out`, and `skip` |
| Assumptions | `accept-all`, `change-some`, `skip` |
| Answers | `close-all`, `pick-some`, `skip` |

Each option names its impact and its undo. A recommendation is present only when a fact is cited. Otherwise the card names the missing fact and who could give it.

`close-all` and `pick-some` write one decision per closed question and an `Answered:` line on that question. `skip` writes no line. `accept-all` and `change-some` write assumption lines. MUST is never written as an assumption.

Pass the word to `link-to-spec` with `{}` on stdin. Print the next `card_text`, or the `ending` when the run is finished. The ending comes first. Do not add a `Next:` line. Do not tell the user to edit a file.
