# crav1-read-environment: grouping

Read only when the pointer in `SKILL.md` sends you here. Moved word for word from `SKILL.md` in 1.71.0; the rules are unchanged.

## Group suggestion

After evidence, whatever is still unmarked in a group where other resources have a mark is one question. List every such resource. Each line says `probably <env>, same group as <marked resource or pipeline>`. Cite the pipeline when that sibling’s mark is a pipeline line. Otherwise cite the marked resource. When the sibling’s mark is a deployment, cite that marked resource, not the deployment name.

Suggest an environment only when every marked resource in that group agrees on one class. A shared resource does not agree with the others. A prod-only resource agrees only with other production marks. When they do not agree, do not suggest. Those resources stay unmarked. Google Cloud has no resource group. Do not invent one from the project. A suggestion there does not apply. AWS uses an AWS resource group. The account and the region are not a group.

Options:

1. **Accept every suggestion.**
2. **Accept none.**
3. **I will edit this list.**

Accept appends a line for each accepted resource: `marked by the user, suggested by group`. Then classify those resources again. **I will edit this list** stops this question. Wait for the edited list. A line they kept is accepted. A resource they add that was not suggested stays out.

When nothing is suggested, do not ask. Go on to leftovers.

## Leftovers

Everything still unmarked is one question. List every unmarked resource. List every group that still has one. Do not drop one to keep the question short.

Options:

1. **Leave every unmarked resource unread and continue.**
2. **Stop the read.**
3. **I'll mark these myself.**

Continue leaves those resources unread and goes on to the shape question, when that question is needed, then look inside, then the sections. Stop asks no further question, does not look inside, and asks no section. It does not read further. Marks already confirmed stay appended. Do not append anything else. Pre-prod, shared, and prod-only resources that were not asked stay not read. Those prod-only resources stay skipped.

**I'll mark these myself** waits for the reply, the same way an edited section waits. The reply names an environment for a resource or for a group. Do not invent an environment they did not name. The environment word has to be one this skill knows. Map it with the mark table. A group reply writes one line per still-unmarked resource in that group. The source is `marked by the user`. A resource that was not listed stays unmarked. Naming prod or live on one leftover does not stop the whole read. That resource is then prod-only, unless another source says non-prod or pre-prod. That disagreement makes it shared. Then classify again and go on to the shape question, when that question is needed, then look inside, then the sections.

When nothing is unmarked, do not ask. Go on to the shape question, when that question is needed, then look inside.

## Pre-prod, shared, and prod-only

Before any pre-prod, shared, or prod-only resource is read for shape, ask one yes/no question. Ask it after evidence, the group suggestion, and the leftovers question, so a mark the user just confirmed is included. If leftovers stopped the read, do not ask. If none of those three classes has a resource, do not ask. List every pre-prod resource, every shared resource, and every prod-only resource. When a class has none, say that class has none. Do not drop one to keep the question short. Do not read their properties before the answer. A connection-field look at a prod-only resource, for evidence, is not this read.

Use the questions tool when it is available. Options only.

1. **Yes. Read these for shape and connections only.**
2. **No. List them as not read.**

The prompt says: read pre-prod, shared-with-prod, and prod-only resources for shape and connections only?

One answer covers all three classes. A yes reads each listed resource for shape and connections only. Shape and connections means names, types, setting keys, routes the settings already show, timers, links, and secret names. A setting value is shown only when it is a resource id or a hostname. Never data. Never secret values. Never row or blob contents. Do not read request logs or traffic. A no lists them as not read. They are not seen. A prod-only resource from that no stays in Skipped. Look inside does not open a database or store that this answer left unread. Look inside never opens a production database or production storage, including a prod-only one the user said yes to. Prod-only shape on a database or a store is only what the resource list and the settings already show.

Then run Look inside. Then ask the sections.
