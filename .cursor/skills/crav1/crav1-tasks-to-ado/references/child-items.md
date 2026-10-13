# Child work items

Use with the shared [azure-boards.md](../../crav1-specs-to-ado/references/azure-boards.md) (org and project, finding `az`, failures, fields, HTML, tags, show). This file adds the child type and the parent link.

## Work item types

```text
az boards work-item type list --organization <org-url> --project <project> --detect false -o json
```

Offer the returned names. Do not create a type.

## Fields of the child type

```text
az devops invoke --area wit --resource workitemtypesfield --route-parameters project=<project> type=<type> --organization <org-url> --detect false --api-version 7.1 -o json
```

Acceptance Criteria is present when a returned field has reference name `Microsoft.VSTS.Common.AcceptanceCriteria`. When it is not, the verify line goes at the end of the Description as a paragraph `Acceptance` and that field is not sent.

## Create with a parent

```text
az boards work-item create --type "<type>" --title "<title>" --organization <org-url> --project <project> --detect false --fields "System.State=New" "System.Description=<html>" "Microsoft.VSTS.Common.AcceptanceCriteria=<html>" "System.Tags=<tags>" "System.AssignedTo=<owner>"
az boards work-item relation add --id <new-id> --relation-type parent --target-id <feature-id> --organization <org-url> --detect false
```

Omit Acceptance Criteria when there is no verify line or the type lacks the field. Omit Assigned To when no owner is stated. Omit Area, Iteration, and Priority. When the relation add fails after the create, say the item was created without its parent, give the id, and offer Retry for the link only. Do not create it again.

## Update

```text
az boards work-item update --id <id> --organization <org-url> --project <project> --detect false --fields "<only fields the user accepted>"
```

Check the parent with `az boards work-item show --id <id> --expand relations`. The parent is the `System.LinkTypes.Hierarchy-Reverse` relation.
