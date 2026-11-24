# Design session start (1.200.0)

One entry. Starting fresh and coming back print the same screen. The script builds it from `session.json` and the topic files: `design_run.py screen --vendor copilot` with or without `--topic`, and `design_run.py resume --topic <topic> --vendor copilot` with no `--json`. Those two texts match for the same files. `resume --json` is the old field payload for a caller that reads `next_decision`; the skill does not print it.

## What the screen shows

A status line, where the user is, what is waiting and on whom, uncommitted files, any proposal pages, what needs doing, then `Run next` with one label above one command:

- No topic yet: start a topic, and open each topic that already exists.
- A topic with a decision still open: **Next decision** first (`/crav1-design-architecture <topic> next`), then the proposal, stages and park.
- Every decision settled: write stages, edit the proposal, review go-ahead, then park.
- Parked or ended: the same screen from the files. The come-back command is `/crav1-design-architecture <topic>`, never a `resume` word.

## Screen shape (1.201.1)

`Run next` comes first, with one reason line, then the status. A topic whose `goal.md` is on `design/<topic>` while this checkout is another branch gets the switch card. `resume --json` leaves Status as it is, including parked. A source that changed still marks that one decision reopened. Waiting lines name each person once, with the date recorded on the question, and stay near 120 characters. When every open decision is `to-question` or `to-research`, Run next names the open-questions command and the proposal. A parked screen has no Park command. An ended screen has one command, `reopen`. Proposal pages include dated files under `docs/architecture/proposals/` whose path or opening text names the topic.

## While it is open

The session stays open until the user parks or ends it. A decision, an ending or a commit does not close it. Free-form requests (edit the proposal, explain, compare, draft) stay inside the session: one question per card, nothing settled without a `choose-*` word, files only in the topic folder. Say the status line on every turn.

`Design session open: <topic>. Park: `/crav1-design-architecture <topic> park``

`next` is the guided card. A yes that adds or changes a decision starts that decision; do not add a stop-or-go card after it. When other decisions can still be made, recommend going on. Recommend stop only when nothing else can be decided, or the user asked to stop.

A decision that already waits on a named person is `to-question`, not a `choose-*`. A reopened decision needs `--revisit-yes` before settle, even when the choice stays the same. A short unique prefix such as `Your idea` matches the option; a miss lists the accepted names and writes nothing.

Park prints `Session parked` and the plain command. End or close prints `Session ended` and the same command. Both write `session.json` (`open`, `parked` or `ended`).
