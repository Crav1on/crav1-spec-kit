# crav1-map-pipeline-environments: start questions

Read only when the pointer in `SKILL.md` sends you here. Moved word for word from `SKILL.md` in 1.86.5; the rules are unchanged.

## Start questions

**No host named.** Options:

1. **Azure DevOps**
2. **I will name the host.**

Stop until they pick. **Azure DevOps** still needs the org and the project. Ask the org next. **I will name the host** waits for that name. If that name is not Azure DevOps, stop as above. Do not read between the answers.

**Host named, org missing.** Options:

1. **I will name the org.**

Stop until they name it. Do not offer a typed path. Do not list orgs. Do not read.

**Org named, project missing.** List projects with `az devops project list` after the CLI checks below. Options: one option per project the org shows, then **I will name the project.** List every project. Do not drop one to keep the list short. Stop until they pick. If the org shows no project, say so and stop. If the list fails, say the project list failed and stop. Do not guess a project.

**A named pipeline matches nothing.** List the pipelines the project shows. Options: one option per pipeline, with YAML, classic build, or classic release on the option. List every pipeline. Stop until they pick. A similar name is not a match. Compare without regard to case. If two pipelines share the name, list both with the id. Do not pick one.
