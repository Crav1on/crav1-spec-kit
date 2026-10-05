# Storage reader

`/crav1-environment-read` follows this reader after the SQL reader, and before any section is asked. The host reader has already listed the account or the bucket. This reader opens it only when the user says yes. It reads structure. It does not read files.

If leftovers stopped the read, do not run this reader.

Azure, AWS, and Google Cloud use the commands in this file. Production is never opened.

## Scope

Open storage the first read already listed:

- Azure: `Microsoft.Storage/storageAccounts`. Containers, file shares, queues, and tables are parts of that account.
- AWS: an S3 bucket. The bucket is the container. Prefixes are the folders.
- Google Cloud: a Cloud Storage bucket. Prefixes are the folders.

Do not open disks, snapshots, backup vaults, container registries, EFS, or Azure NetApp. Those stay resource facts from the first read.

## Depth

Prefix depth is 2.

- Level 1 is the name before the first `/`.
- Level 2 is the next name.
- Do not go to level 3.

A prefix is a folder name. A blob, an object, or a file is not a prefix. If a response includes files, discard those entries. Do not record a file name, a size, or a count. Do not say how many files were discarded.

One request per prefix. Ask for at most 100 prefixes. If the service says more exist, say the list stopped at 100. Do not follow a continuation token through files.

## No storage to open

If the first read found no storage in scope, do not ask. Say no storage is opened. Go on to the sections.

If every store in scope is production only, including prod-only, do not ask. Say production is not opened. A yes to prod-only shape does not open it. Go on to the sections.

An unmarked account or bucket stays unread. Do not open it. If nothing else is in scope, say there is no storage account with a clear environment. Do not ask.

A pre-prod or shared store is opened only when the user already said yes to shape and connections. A no on that earlier question leaves it unopened. A prod-only store is production. The shape yes does not open it.

## Access check

Before the question, check how to reach the store. Say the best way in the question prompt. Say how much setup is actually needed. List every account or bucket the question would open. If one store is used by more than one environment, say that in the same prompt.

Two planes:

- **Management plane.** Account or bucket settings: network rules, public access, lifecycle, versioning, soft delete, and, on Azure, container names and file share names. Azure uses `az storage account show` with the existing `az login`. No key.
- **Data plane.** Prefixes, queue names, and table names. Azure prefixes need the Storage Blob Data Reader role, already assigned. Queue names need Storage Queue Data Reader. Table names need Storage Table Data Reader. AWS and Google Cloud use the login that is already there, with read rights on the bucket.

Say which plane the settings show as reachable. A private endpoint, a firewall default of deny, or a bucket that is not public means network access has to already exist. Say whether a firewall rule, a private endpoint, or a VPN is needed. Do not print an IP range.

This skill does not create a role assignment, a SAS token, or a key. It does not install a tool. It does not log in. It does not print a key or a connection string.

The check uses the management-plane commands below. Do not list prefixes during the check.

## Question

Should the reader read the storage structure?

1. **Yes. Read structure only.**
2. **No. Do not open storage.**

A no does not open it. Go on to the sections.

A yes reads structure for every store listed in that question. If the management plane is missing, stop this reader. Name what is missing. Do not open the store. The sections of the first read still run.

If the management plane works and the data plane does not, keep the management-plane facts. Say the data-plane role or network access is missing. Do not read prefixes. Do not use a key, a SAS token, or a connection string to get past it. Do not create a role.

## What a yes reads

Structure only:

- The account or the bucket
- Container names, or the bucket itself on AWS and Google Cloud
- File share names, queue names, and table names, when the host has them
- Prefixes, to depth 2
- Public or private access
- Lifecycle rules
- Versioning and soft delete, on or off
- What points at it: a connection the first read already showed, plus a storage trigger

A trigger is a connection. The line shows the source, the target, and the schedule when it has one. Never a payload. Never a secret.

Do not read a blob. Do not download an object. Do not list every blob. Do not report a file count or a size. Do not list versions of an object. Do not read queue messages or table entities. Do not read files inside a share. Directory names follow the same depth rule. A file in that response is discarded.

List every container, share, queue, table, and prefix the bounded calls return. Do not drop one to keep the list short.

### Azure

Management plane:

- `az storage account show` for `allowBlobPublicAccess`, `networkRuleSet`, and private endpoints
- `az storage account management-policy show` for lifecycle rules. Cite the prefix filter, the action, and the days.
- `az storage account blob-service-properties show` for versioning and soft delete. Cite on or off. Do not list blob versions.
- `az storage container-rm list` for container names and `publicAccess`. Say public or private.
- `az storage share-rm list` for file share names

Data plane, `--auth-mode login` only. Never `--account-key`. Never `--connection-string`. Never a SAS.

Prefixes, one container at a time:

```text
az storage blob list --account-name ACCOUNT --container-name CONTAINER --auth-mode login --delimiter / --num-results 100
```

Keep prefix entries only. Discard blob entries. Level 2 repeats the call with `--prefix` set to the level-1 prefix. Do not pass a marker that walks blob pages.

Queue names: `az storage queue list --account-name ACCOUNT --auth-mode login`. Names only. If it fails for auth, say Storage Queue Data Reader is missing.

Table names: `az storage table list --account-name ACCOUNT --auth-mode login`. Names only. If it fails for auth, say Storage Table Data Reader is missing. Do not query entities.

Share directories, depth 2: `az storage directory list --account-name ACCOUNT --share-name SHARE --auth-mode login`. Directory names only. Discard files. Level 2 passes the level-1 directory. Do not call `az storage file list` to enumerate files.

Triggers, when that resource is one the host reader is allowed to read. Skip a trigger the first read already listed.

- An Event Grid subscription on the account. Source, target, and event types.
- A function blob trigger. Binding, blob path, and function.
- A Data Factory storage-event trigger. Trigger type, pipeline, and schedule when it has one.

### AWS

S3. Do not call `aws s3 sync`, `aws s3 cp`, or `aws s3 ls` with a recursive flag.

- `aws s3api get-public-access-block` and `aws s3api get-bucket-policy-status` for public or private. Do not print the bucket policy.
- `aws s3api get-bucket-lifecycle-configuration` for lifecycle rules
- `aws s3api get-bucket-versioning` for versioning on or off. Do not list object versions.
- `aws s3api list-objects-v2 --bucket BUCKET --delimiter / --max-keys 100` for level 1. Keep `CommonPrefixes` only. Discard `Contents`. Do not record a key, a size, or a count. If `IsTruncated` is true, say the list stopped at 100. Do not pass a continuation token. Level 2 repeats the call with `--prefix` set to the level-1 prefix.
- `aws s3api get-bucket-notification-configuration` for the event type and the topic, queue, or function. Do not show a secret. Skip a notification the first read already listed.

There is no file-share, queue, or table service inside an S3 bucket. Do not invent one. SQS and SNS stay resources from the first read. A notification that names them is the connection.

### Google Cloud

Do not call `gcloud storage cat`, `gcloud storage cp`, `gcloud storage du`, or `gcloud storage ls` with `-r` or `**`.

- `gcloud storage buckets describe gs://BUCKET` for public access prevention, uniform bucket-level access, versioning, soft delete, and lifecycle. Cite public or private, and on or off. Do not list object versions.
- `gcloud storage ls gs://BUCKET/` for level 1. Keep names that end with `/`. Discard object lines. Stop at 100 prefixes. Level 2 is `gcloud storage ls gs://BUCKET/PREFIX/`.
- `gcloud storage buckets notifications list gs://BUCKET` for the event type and the topic. Do not show a secret.

There is no file-share, queue, or table service inside a Cloud Storage bucket. Do not invent one.

## Tokens in names

A container, a share, a queue, a table, or a prefix can show an environment. Tokenize it with the mark table in the skill. The whole word has to match. Cite it on the Seen line, like `prefix dev says dev`.

`device` is not `dev`. A similar name is not evidence. Do not write this cite into `docs/environments/marks.md`.

A name that matches no token does not become an environment. The store keeps the environment the first read already gave it. If that store had no environment, the name is not a Seen line. Say the store shows no environment token.

## Pre-prod and shared

After the earlier yes, the read is still structure only. Say `Seen in <host> pre-prod.` or `Seen in <host> <environment>.` plus `shared with prod`. Say `Shape and connections only.` Never a blob.

Do not open a prod-only store in this section. That yes does not apply here. Prod-only shape stays on the host reader: names, types, setting keys, and secret names from the resource list and the settings. Never a prefix from inside the account. Never a blob.

## Where facts go

Do not add a section. Each fact says `Seen in <host> <environment>.` Account, container, share, queue, table, prefix, access, lifecycle, versioning, and soft-delete facts join Seen, and then System, Architecture, Match, and Left out with the other facts. A trigger joins Links.

## Hard rules

- Run only after the SQL reader, and before any section. Leftovers that stopped the read skip this reader.
- Say the access check in the question prompt. Options only. One question.
- A yes reads structure only. Prefix depth is 2. At most 100 prefixes per request.
- Never read, download, or list every blob. Never report a file count or a size. List prefixes, not files.
- Never print a key, a SAS token, or a connection string.
- Production is never opened, including a prod-only store. A yes to prod-only shape does not open it. Pre-prod and shared stay shape and connections, and only after the earlier yes.
- A name or a prefix is evidence only when the whole-word token rule matches.
- Do not install a tool. Do not log in. Do not create a role assignment, a SAS token, or a key.
- Missing management-plane access stops this reader and names the gap. Missing data-plane access stops prefixes and is named. Management-plane facts that already succeeded stay.
- The sections of the first read still run.
- Facts join the sections that already exist. They say `Seen in <host> <environment>.`
