# Imported sources: flagged items

Read only when the personal-data and secrets check in [sources.md](sources.md) flags an item or finds a secret, or when a skill points here for the transfer data policy. [sources.md](sources.md) is the convention. Moved word for word from `sources.md` in 1.71.2; the rules are unchanged.

## Personal data

### Transfer data policy

The rule is once per repo and one shared policy for Cursor and Claude Code. It has two copies. Claude Code project: `.claude/rules/crav1-transfer-data-policy.md`. Read the copy for the host that is running. When only one copy exists, use it and write the other copy from it with the same words. When the kit writes the rule, it writes both copies together. When both exist and differ, say so and ask the user which one wins. Do not merge them. Then write the other copy from the one they picked. Do not read or write a user-level file. The user changes the rule by editing or deleting that file.

The template is this skill's `assets/crav1-transfer-data-policy.mdc` (drop-in: `.claude/skills/crav1-add-to-spec/assets/crav1-transfer-data-policy.mdc`; plugin: this skill's `assets/crav1-transfer-data-policy.mdc`).

The file lists types, one per line. This version checks personal data. A later type can be added as its own line. It lists `auto-accept` or `review`. It lists where the repo is hosted, in the user's words. It does not list a secrets choice.

When the file exists and those three parts are present, apply it. Show one line that names the file and what it chose: the types, auto-accept or review, and where the repo is hosted. Do not ask the setup questions.

When the file is missing a type, a recommendation, or the hosted line, or the recommendation is not `auto-accept` or `review`, say what is missing. Do not guess. Ask the setup questions for this run. Do not rewrite the file unless the user says yes to save.

When no rule exists, and the check found a flagged item or a secret, ask the setup questions once for the run. A later source in that run uses the same answers. Do not ask them again in that run. Use the questions tool when it is available, except for the hosted question. Stop until the user answers.

1. **Which types should this check cover?** The only option this version offers is personal data. The rule stores one type per line, so a later type can be added.
2. **Apply the recommendations automatically, or review them on each run?** The options are auto-accept the recommendations, and review each run.
3. **Where is this repo hosted?** Free text. Not options. Do not invent a place. The note uses this answer.
4. **Save these answers as the transfer data policy for this repo?** Yes or no. Yes writes the file from the template. Replace `- <type>` with one line per chosen type. This version writes `- personal data` when the user picks that type. Replace `<auto-accept or review>` with `auto-accept` or `review`. Replace `<where this repo is hosted>` with the user's words. Do not leave the angle-bracket placeholders. Do not add a secret, a phone number, or an email address. No uses the answers this run only and does not write the file.

When nothing is flagged and there is no secret, say so in one line and continue. Do not ask the setup questions. Do not show the note.

### The note and the list

When there is a flagged item or a secret, show this note once, above the list. Mark it as not legal advice. Replace `<hosted>` with the hosted words from the rule, or from the answer this run. Do not leave the placeholder.

This is not legal advice. Keeping a work mail as a project record fits, because a spec quote must trace to the source. Keep only what that trace needs. Where the repo is hosted matters. This repo is hosted at <hosted>. The client's or the employer's data and retention policy comes first. Removing something after it is pushed means rewriting git history.

Then show the list.

Number each item that has a recommendation. The line shows the text, the kind, and where it sits. The line ends with `Recommended: keep.` or `Recommended: redact.`

List each unplaced item after the numbers. The line shows the text, the kind, and where it sits. The line says there is no recommendation.

List secrets last. One line per kind. Do not number them. Do not show the value. The line says redacted.

### One question for the recommendations

Ask this question when there is at least one numbered item, and the rule or this run says review. One question. Three answers. Use the questions tool when it is available. Stop until the user picks.

1. **Accept all recommendations.**
2. **Go through them one by one.** The recommendation is shown on each item, and in its question as the first option with ` (Recommended)`.
3. **Change some.** The user names items to flip, for example keep 3, redact 5.

Accept all recommendations applies every numbered recommendation.

Go through them one by one asks keep or redact for each numbered item. One item at a time. Options only. Use the questions tool when it is available. The recommended choice is the first option, labelled ` (Recommended)`, for example `Redact (Recommended)`, then the other. Stop until the user picks.

Change some waits for the user to name the items. The named choice replaces the recommendation for that item. An item they do not name keeps its recommendation. When a number is not on the list, or the reply does not name an item, ask again. Do not guess.

When the rule or this run says auto-accept, do not ask that question. Apply each numbered recommendation. That auto-accept covers these keep and redact lines. Images inside a mail says when it also covers an image recommendation.

Unplaced items are still asked, whatever was picked, including auto-accept, all in one questions call (1.70.0), one question per item. Options are keep and redact. There is no recommendation. Use the questions tool when it is available. Stop until the user picks.

When there is no numbered item, do not ask the three-answer question. Ask the unplaced items. A secret is not a question.

**Keep.** That text stays.

**Redact.** Remove that item from the file that will be written, and from the quote. Note the redaction in the README, by kind, not by pasting the value. The file is then no longer the untouched original. The README says so.

A detail that is readable only in an image follows the same keep or redact. When that image will be compressed, the samples are the redacted image. When that image will be converted to text, the redact removes the item from `<name>.md` and from the quote. When the option for that image is commit as-is, a redact cannot leave the image unchanged. Say so and ask the user to pick compress, convert to text, or leave it out for that image. Do not edit an as-is image.

Do not write the source files until every flagged item has an answer and every image inside a mail has an answer. A secret is already answered by this section. The rule file may be written when the user says yes, before the source files. Do not write an unredacted copy into the repo. When a screenshot or an embedded image will be compressed, the samples are the redacted image. The user commits later. A redacted value is not in the file they will commit. Do not commit.
