# crav1-read-environment: marks

Read only when the pointer in `SKILL.md` sends you here. Moved word for word from `SKILL.md` in 1.71.0; the rules are unchanged.

## Marks

Four sources, in this order: the resource name, the group, the tags, then a matching line in `docs/environments/marks.md`. The file is used after name, group, and tag. It does not replace them. The reader file says what the name, the group, and the tag are on that host. Google Cloud has no resource group. That absence is not a mark. Do not infer a mark from the subscription, the account, the project, the region, or a neighbor. A similar name is not a mark.

Split name, group, tag key, tag value, and the environment field of a marks line on every character that is not a letter. Those letter runs are the tokens. Compare tokens without regard to case. `Dev`, `DEV`, and `dev` are the same word. The whole-word rule still holds.

| Tokens | Class | Environment on the Seen line |
| --- | --- | --- |
| `dev`, `development` | non-prod | dev |
| `test`, `testing` | non-prod | test |
| `stage`, `staging` | non-prod | stage |
| `uat` | non-prod | uat |
| `qa` | non-prod | qa |
| `preprod`, or the neighboring tokens `pre` then `prod` | pre-prod | pre-prod |
| `prod`, `production`, `live` | production | prod, when the resource is prod-only and the user said yes |

A token is the whole word.

- `device` is not `dev`. `development` is dev.
- `protest`, `latest`, and `contest` are not `test`. `testing` is test.
- `backstage` and `staged` are not `stage`. `staging` is stage.
- `equation` and `equator` are not `uat`.
- `qatar` and `equal` are not `qa`.
- `preprod` is one token, and it is pre-prod.
- `pre-prod`, `pre_prod`, and `pre.prod` split into the neighboring tokens `pre` then `prod`. That pair is one pre-prod mark. The `prod` in that pair is not production. Order matters. `prod-pre` is production.
- `pre-production` splits into `pre` and `production`. `production` is production. That spelling is not pre-prod.
- `product` and `reproduce` are not `prod`.
- `live` is safe as a whole word, and it is production. `alive`, `lives`, `liveness`, `deliver`, `livestock`, and `livestream` are not `live`. `go-live` and `live-api` split to a `live` token and are production.

Inside one source, a production token wins over a non-prod token. That source says prod. The pre-prod pair is the exception: that `prod` is not a production token.

Across sources:

- **Prod-only.** The only environment class is production. No source says non-prod or pre-prod. That resource has no non-prod twin. A non-prod twin is another source on this same resource that says non-prod or pre-prod. That case is shared. A different resource with a similar name is not a twin. Do not read it for shape until the one yes. A no lists it as not read and it stays in Skipped. Cite the mark. A resource whose own name, group, or tag says prod, with no other source, is prod-only.
- **Shared.** One source says production and another source says non-prod or pre-prod. Treat it like pre-prod. Label it `shared with prod`. The line shows both sources, like `tag says dev; marks.md (pipeline X, stage Prod) says prod`. It is not prod-only.
- **Pre-prod.** A source says pre-prod, and no source says production. A non-prod token on another source does not make it a full read. The stricter class wins. Cite both sources.
- **Taken.** One or more non-prod environments, and no production or pre-prod class. The resource is read in full for those environments. Cite every source. One line can carry more than one `Seen in <host> <environment>.` when sources name different non-prod environments.
- **No mark.** No source has a token in the table. Do not read that resource yet. Evidence below may still mark it.

Do not read further properties on a resource that is still unmarked, except the private endpoint, VNet, or subnet id when testing connection evidence.

## marks.md

Path: `docs/environments/marks.md` in the project repo. The format note for people is `docs/environments-marks.md` in this kit. The skill defines the format here. Do not write the kit note into the project.

Each line has four fields, separated by ` | ` (space, pipe, space). Split on the first three separators only. The source is the rest of the line.

```text
<resource-id-or-name> | <group> | <environment> | <source>
```

- The first field is the resource id or the resource name.
- The second field is the group. Use `-` when the host has no group.
- The third field is one environment word. The same tokenizer maps it. `development` maps to dev. `pre-prod` and `preprod` map to pre-prod. `production` and `live` map to production.
- The source is `pipeline <name>, stage <stage>`, or `marked by the user`, or `marked by the user, suggested by group`.

A blank line is ignored. A line that starts with `#` is ignored. A line this skill cannot parse, or whose environment word is not in the table, is not used. List it as not used. Do not guess. Do not rewrite it.

A line matches a resource when the first field equals the resource id, or when the first field equals the name and the second field equals the group. Compare without regard to case. A similar name does not match. `app` does not match `app-api`. If a name and group match more than one resource, do not apply that line. List it as not used.

This skill creates `docs/environments/` and `marks.md` only when the user has confirmed at least one mark. It appends those lines. It never rewrites an existing line. It does not append a line that is already there. A second environment for the same resource is a new line.

Confirmed group suggestions use `marked by the user, suggested by group`. Marks the user names on the leftovers question use `marked by the user`. Prefer the resource id in the first field and the group in the second. Evidence marks are cited on the Seen line. They are not written to this file.
