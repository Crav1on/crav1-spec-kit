# crav1-map-pipeline-environments: targets

Read only when the pointer in `SKILL.md` sends you here. Moved word for word from `SKILL.md` in 1.71.0; the rules are unchanged.

## Targets

For each stage, find the Azure targets each deploy step deploys to. The reference file lists the task inputs. A step that is not a deploy step contributes no target.

Record, when the step shows them:

- the resource id, or the app name when no id is shown
- the resource group
- the service connection’s subscription id and name, when the endpoint shows them

The subscription is context on the item. It is not a fifth field on the marks line. Do not print a service principal secret, a password, a key, or a certificate. Do not print the endpoint JSON.

**Marks only what the step names.** A step that deploys into a resource group marks the app or the resource id that step names. It does not mark the other resources in the group. The group is the second field on that resource’s line. That field is the context `/crav1-read-environment` can use later for a group suggestion. A step that names a group and no app and no resource id marks nothing. List the group as context under that stage. Do not write a line whose first field is the group.

Prefer a resource id the step shows. Do not build an id from a subscription and a guessed provider. When the step shows an app name, the first field is that name.

An id and a name are the same resource only when the id’s last segment equals the name and the group is the same. Compare without regard to case. A similar name is not the same resource. `app` does not match `app-api`. When you cannot tell, list them as separate resources. Say they were not merged.

Follow a variable only when the value is plain. Plain means a value written in the pipeline YAML, a parameter default written there, or a variable group value whose `isSecret` is not true. A secret variable, a Key Vault link, a missing name, a cycle, or a runtime expression is unresolved. The target that depends on it is unclear. Do not print the secret. Do not print a plain value that is a connection string, a key, or a password. The resource name inside a plain value can still be the target.

An inline script names a target only when the script text shows an app name or a resource id as a plain value. A script file path is not read. Do not open that file. A target that exists only in that file is unresolved.

A Bicep file, an ARM template file, or a Terraform file is not the pipeline definition. Do not open it. Names that appear as task inputs still count.
