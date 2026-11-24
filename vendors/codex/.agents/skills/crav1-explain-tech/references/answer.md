# The answer

## Short (the default)

About 150 to 250 words, in this order, each a bold lead:

1. **What it is.** One or two plain sentences.
2. **How it works.** Two or three sentences.
3. **Where it shows up.** Each place in the specs from `find`, as a link to the exact file and section, with a few words on what that place says. A design topic mention (`decided: false`) is said as under discussion, not decided. More than four places: the four most telling, then `and N more`.
4. **Why it is used.** Why the spec uses it, from what the spec says; or why it would fit, said as a fit, not a fact.
5. **Main tradeoff.** The one cost or limit that matters most here.
6. **One alternative.** One real alternative and when it would win.

Then the Run next from `ending`. The Run next is first among the endings; each label sits on its own line above a command alone in its code span. No `Next:` line. Then offer the save card when the answer is tied to one spec.

## Deeper (`deeper`)

About 300 to 900 words. The same sections, each expanded, plus **How it fits with the rest of the spec** before **One alternative**: what it connects to, what depends on it, which decisions and open questions touch it. Still read-only.

## Not in the specs

When `find` returns `in_spec: false`, say so plainly under **Where it shows up**: `The specs do not mention <technology>.` Explain it in general terms and never invent a spec link. End with `ending --not-in-spec`, which names research.

## Missing facts

When a fact the answer needs is not in the specs (a limit, a cost, a decision), say it is not written down and name who has it from `owners`: an ADR's deciders, an `Owner:` line, or the spec's `## Approval needed` names. With no owner found, say so and point to research (`$crav1-show-or-ask-open-questions ask research <topic>`). Never guess the fact.

## Samples

`assets/sample-short.md`, `assets/sample-deeper.md` and `assets/sample-not-in-spec.md` show the shape; kit-lint runs `check` on them.
