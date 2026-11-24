# crav1-map-pipeline-environments: naming

Read only when the pointer in `SKILL.md` sends you here. Moved word for word from `SKILL.md` in 1.71.0; the rules are unchanged.

## Stage name

The stage name gives the environment. Tokenize that name with the Marks rule in `/crav1-read-environment`. The words below are that rule. Do not add a word. Do not drop a word. Do not keep a different list.

Use the stage `displayName` when it is set. Otherwise use the stage identifier. A classic release environment name is the stage name.

Split the stage name on every character that is not a letter. Those letter runs are the tokens. Compare tokens without regard to case. `Dev`, `DEV`, and `dev` are the same word. The whole-word rule still holds.

| Tokens | Class | Environment on the marks line |
| --- | --- | --- |
| `dev`, `development` | non-prod | dev |
| `test`, `testing` | non-prod | test |
| `stage`, `staging` | non-prod | stage |
| `uat` | non-prod | uat |
| `qa` | non-prod | qa |
| `preprod`, or the neighboring tokens `pre` then `prod` | pre-prod | pre-prod |
| `prod`, `production`, `live` | production | prod |

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

Inside one stage name, a production token wins over a non-prod token. That stage says prod. The pre-prod pair is the exception: that `prod` is not a production token.

A job name is not the stage name. A deployment slot name is not the stage name. A slot named staging does not make the environment stage.

Read the deployment job `environment:` name and show it on the item. It does not replace the stage name. When the stage name has a token and that `environment:` name has a different class, the resource is unclear. Say the two names disagree. Do not pick one. When the stage name has no token, the resource is unclear even if `environment:` has a token. Show that name in the reason.

## Cases

Group targets by resource across the pipelines you read. A resource is one of these cases.

**One environment.** Every stage that deploys it has the same class, or every stage is non-prod and the words differ. Propose one marks line per stage. Each line uses that stage’s environment word. Several non-prod words are not shared. Shared is the next case. Say on the item when the non-prod words differ. A resource that is only pre-prod is this case. A resource that is only production is this case. The line uses `prod`. Say that the next environment read treats a resource whose only mark is production as prod-only. That read asks once, with pre-prod and shared, before it reads shape and connections. This skill still does not read that Azure resource.

**Shared.** At least one stage is non-prod or pre-prod, and at least one stage is production. List the resource with both stages. The marks format has no `shared` word. Do not write one. Propose one line per stage, each with that stage’s own environment word, in the four-field format `docs/environments-marks.md` already defines. Say that `/crav1-read-environment` treats those lines as shared with prod. Pre-prod with production is this case, because that read already treats pre-prod and production as shared.

**Unclear.** The stage name has no environment word, the stage name and `environment:` disagree, or the target is an unresolved variable. List the resource with the reason. Propose no mark.

A group-only deploy stays with the case of its stage. It has no proposed line.
