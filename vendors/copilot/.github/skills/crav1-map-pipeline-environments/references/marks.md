# crav1-map-pipeline-environments: marks

Read only when the pointer in `SKILL.md` sends you here. Moved word for word from `SKILL.md` in 1.71.0; the rules are unchanged.

## marks.md

Path: `docs/environments/marks.md` in the project repo. The format is the four fields in `/crav1-read-environment` and in `docs/environments-marks.md`. Do not write the kit note into the project.

```text
<resource-id-or-name> | <group> | <environment> | pipeline <name>, stage <stage>
```

The second field is the group the step showed. Use `-` when the step shows no group. The source is `pipeline <name>, stage <stage>`. One line per stage. Do not put two stages in one source.

Create `docs/environments/` and `marks.md` only when the user has confirmed at least one line. Append those lines. Never rewrite an existing line. Do not append a line that is already there. Already there means the same resource and the same environment word. `development` on an existing line is the same word as `dev`. Compare the resource the way `/crav1-read-environment` matches: the id, or the name plus the group, without regard to case. List that item as already written. A confirm does not append it again.

When an existing line matches the resource and the environment class differs, show the existing line and the proposed line. Do not rewrite the existing line. A confirmed append leaves the existing line and adds the new one. Say that the next environment read treats that disagreement as shared.

A line the user did not confirm is not written. Unclear items write nothing.
