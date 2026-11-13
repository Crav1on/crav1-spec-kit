# Report writes

Feature, change, and build reports write nothing in the project. Playbook apply copies a filled file to `docs/playbooks/` (1.120.0). `report-data-model-full` writes one new snapshot and does not edit the model. During a walk that report is the only file written. Do not run another skill, except `apply` on yes at the end of a walk, for filled confirmed lines only. Do not start `/crav1-help`.
