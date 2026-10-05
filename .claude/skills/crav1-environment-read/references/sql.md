# SQL reader

`/crav1-environment-read` follows this reader after the first read is done, and before any section is asked. The host reader has already listed the server or the database. This reader opens one only when the user says yes. It reads metadata. It does not read rows.

If leftovers stopped the read, do not run this reader.

Azure, AWS, and Google Cloud use the commands in this file. Production is never opened. A host reader that listed the resource does not open it during that list.

## Scope

Open a relational database the first read already listed:

- Azure: `Microsoft.Sql/servers`, `Microsoft.Sql/servers/databases`, `Microsoft.Sql/managedInstances`, `Microsoft.SqlVirtualMachine/sqlVirtualMachines`, `Microsoft.DBforPostgreSQL/flexibleServers`, `Microsoft.DBforMySQL/flexibleServers`
- AWS: an RDS instance or an Aurora cluster whose engine is SQL Server, PostgreSQL, or MySQL
- Google Cloud: a Cloud SQL instance

Do not open Cosmos DB, Synapse, Spanner, BigQuery, Firestore, DynamoDB, or Redshift. Those stay resource facts from the first read.

Skip system databases named `master`, `tempdb`, `model`, `msdb`, `postgres`, `template0`, `template1`, `mysql`, `information_schema`, `rdsadmin`, or `cloudsqladmin`. `msdb` is queried only for jobs, and only for the job name, the target database, and the schedule.

## No database to open

If the first read found no database in scope, do not ask. Say no database is opened. Go on to the storage reader, then the sections.

If every database in scope is production only, including prod-only, do not ask. Say production is not opened. A yes to prod-only shape does not open it. Go on to the storage reader, then the sections.

## Clear environment

A database environment is clear when that server or database has one class, and no second environment uses it. The class is one non-prod environment, pre-prod, or shared with prod. A second environment uses it when a seen resource in another environment names its id or hostname, or when the server or database itself carries more than one non-prod environment.

An unmarked server or database is not clear. One server or database used by several environments is not clear.

When every database that can be opened is clear, do not ask question 1. Run the access check. Then ask question 2. List every database question 2 would open.

A pre-prod or shared database is listed only when the user already said yes to shape and connections. A no on that earlier question leaves it unopened. A production database is never listed and never opened. A prod-only database is a production database. The shape yes does not list it and does not open it.

## No clear environment

When the databases this pass found have no clear environment, stop and say this sentence:

There are no clear database environments.

Then ask, options only, one question at a time. List every unclear database in the prompt. Do not drop one.

Question 1. Are the environments in the same database (for example a schema per environment)?

1. **Yes**
2. **No**
3. **Not sure**

A yes means a later schema or name can be the environment, when the whole-word token rule matches. A no or a not sure does not invent a split.

Then run the access check. Then ask question 2, whichever answer question 1 was.

When some databases are clear and some are not, question 1 lists only the unclear ones. Question 2 lists every database a yes would open.

## Access check

Before question 2, check how to reach the database. Say the best way in that question’s prompt. Say how much setup is actually needed.

The best way needs no new login, no new firewall rule, and no new user. Prefer a login that is already there.

Say these three, each as present or missing:

- A login with read rights on metadata. Azure SQL and SQL Server use the existing `az login` and Entra authentication. AWS and Google Cloud use IAM authentication when the instance already has it. A password is not used.
- Network access. Say whether a firewall rule, a private endpoint, or a VPN is needed. Say that from the settings below. Do not print an IP range.
- The tool. SQL Server uses `sqlcmd`. PostgreSQL uses `psql` when it is already installed. MySQL uses `mysql` when it is already installed. `az sql`, `aws rds`, and `gcloud sql` show settings. They do not show tables.

This skill does not create a login, a firewall rule, or a user. It does not install a tool. It does not log in. It does not print a connection string, a password, or a token.

The check is management plane only. Do not run `sqlcmd`, `psql`, or `mysql` during the check.

## Question 2

Should the reader read the database schema, names, and structure?

1. **Yes. Read schema, names, and structure.**
2. **No. Do not open the database.**

A no does not open it. Go on to the storage reader, then the sections.

A yes opens only the databases listed in that question. If a login, network access, or the tool is missing, stop this reader. Name what is missing. Do not open the database. The first read still goes on to the storage reader, then the sections.

## What a yes reads

Metadata only:

- Schemas
- Table names and view names
- Columns and types
- Keys and relationships
- Stored procedure names and function names
- SQL Agent jobs, or other scheduled jobs, and triggers, when the catalog can be reached

A job or a trigger is a connection. The line shows the source, the target, and the schedule when it has one. It does not show command text or a body.

The only `SELECT` is a query in this file, against catalog views. Do not run a query that is not in this file. Do not `SELECT` from a user table or a user view. Do not read a row. Do not report a row count. Do not print procedure text, function text, trigger body, or job step command text.

List every schema, table, view, column, key, procedure, and function the query returns. Do not drop one to keep the list short.

### SQL Server

Tool: `sqlcmd`. If it is not on the path, it is missing. Point at `https://learn.microsoft.com/sql/tools/sqlcmd/sqlcmd-utility`. Do not install it.

Azure SQL, Managed Instance, and SQL Server use Entra. The flag is `-G`. Do not pass `-U` or `-P`.

```text
sqlcmd -S HOST -d DATABASE -G -Q "QUERY" -W -s "|" -y 0
```

On a SQL Server VM that already accepts integrated security, `-E` may replace `-G`. Do not pass a password.

Run these queries. One query per call. Do not add a column.

System schemas are not facts. Exclude `sys`, `INFORMATION_SCHEMA`, and `guest`.

```sql
SELECT s.name FROM sys.schemas AS s WHERE s.name NOT IN ('sys', 'INFORMATION_SCHEMA', 'guest');
SELECT SCHEMA_NAME(t.schema_id), t.name FROM sys.tables AS t WHERE SCHEMA_NAME(t.schema_id) NOT IN ('sys', 'INFORMATION_SCHEMA', 'guest');
SELECT SCHEMA_NAME(v.schema_id), v.name FROM sys.views AS v WHERE SCHEMA_NAME(v.schema_id) NOT IN ('sys', 'INFORMATION_SCHEMA', 'guest');
SELECT SCHEMA_NAME(o.schema_id), o.name, c.name, ty.name, c.max_length, c.precision, c.scale
FROM sys.columns AS c
JOIN sys.objects AS o ON o.object_id = c.object_id
JOIN sys.types AS ty ON ty.user_type_id = c.user_type_id
WHERE o.type IN ('U', 'V') AND SCHEMA_NAME(o.schema_id) NOT IN ('sys', 'INFORMATION_SCHEMA', 'guest');
SELECT SCHEMA_NAME(o.schema_id), o.name, i.name, c.name
FROM sys.indexes AS i
JOIN sys.objects AS o ON o.object_id = i.object_id
JOIN sys.index_columns AS ic ON ic.object_id = i.object_id AND ic.index_id = i.index_id
JOIN sys.columns AS c ON c.object_id = ic.object_id AND c.column_id = ic.column_id
WHERE (i.is_primary_key = 1 OR i.is_unique_constraint = 1) AND SCHEMA_NAME(o.schema_id) NOT IN ('sys', 'INFORMATION_SCHEMA', 'guest');
SELECT OBJECT_SCHEMA_NAME(fk.parent_object_id), OBJECT_NAME(fk.parent_object_id), fk.name,
       OBJECT_SCHEMA_NAME(fk.referenced_object_id), OBJECT_NAME(fk.referenced_object_id),
       COL_NAME(fkc.parent_object_id, fkc.parent_column_id),
       COL_NAME(fkc.referenced_object_id, fkc.referenced_column_id)
FROM sys.foreign_keys AS fk
JOIN sys.foreign_key_columns AS fkc ON fkc.constraint_object_id = fk.object_id
WHERE OBJECT_SCHEMA_NAME(fk.parent_object_id) NOT IN ('sys', 'INFORMATION_SCHEMA', 'guest');
SELECT SCHEMA_NAME(p.schema_id), p.name FROM sys.procedures AS p WHERE SCHEMA_NAME(p.schema_id) NOT IN ('sys', 'INFORMATION_SCHEMA', 'guest');
SELECT SCHEMA_NAME(o.schema_id), o.name FROM sys.objects AS o WHERE o.type IN ('FN', 'IF', 'TF', 'FS', 'FT') AND SCHEMA_NAME(o.schema_id) NOT IN ('sys', 'INFORMATION_SCHEMA', 'guest');
SELECT tr.name, OBJECT_SCHEMA_NAME(tr.parent_id), OBJECT_NAME(tr.parent_id)
FROM sys.triggers AS tr WHERE tr.parent_class = 1 AND OBJECT_SCHEMA_NAME(tr.parent_id) NOT IN ('sys', 'INFORMATION_SCHEMA', 'guest');
```

Jobs, when `msdb` answers. Do not select `command`.

```sql
SELECT j.name, js.step_name, js.database_name, js.subsystem, sch.name
FROM msdb.dbo.sysjobs AS j
LEFT JOIN msdb.dbo.sysjobsteps AS js ON js.job_id = j.job_id
LEFT JOIN msdb.dbo.sysjobschedules AS jsch ON jsch.job_id = j.job_id
LEFT JOIN msdb.dbo.sysschedules AS sch ON sch.schedule_id = jsch.schedule_id;
```

If the job query fails, say jobs are not reachable. Do not try another query. Azure SQL Database has no SQL Agent. That failure is expected there.

### PostgreSQL

Tool: `psql`, and only when it is already on the path. If it is missing, name it. Point at `https://www.postgresql.org/download/`. Do not install it.

Do not pass a password flag. When the instance already has IAM authentication, take a token with the command below and pass it to the client without printing it. Do not write the token into the repo. Do not echo a command that contains the token. If IAM authentication is off, stop this reader. Say a password login is not used.

```text
psql "host=HOST dbname=DATABASE user=USER sslmode=require" -c "QUERY" -A -F "|"
```

System schemas are not facts. Exclude `pg_catalog`, `information_schema`, and `pg_toast`.

```sql
SELECT schema_name FROM information_schema.schemata WHERE schema_name NOT IN ('pg_catalog', 'information_schema', 'pg_toast');
SELECT table_schema, table_name, table_type FROM information_schema.tables WHERE table_schema NOT IN ('pg_catalog', 'information_schema', 'pg_toast');
SELECT table_schema, table_name, column_name, data_type, character_maximum_length, numeric_precision, numeric_scale
FROM information_schema.columns WHERE table_schema NOT IN ('pg_catalog', 'information_schema', 'pg_toast');
SELECT tc.table_schema, tc.table_name, tc.constraint_name, tc.constraint_type, kcu.column_name
FROM information_schema.table_constraints AS tc
JOIN information_schema.key_column_usage AS kcu
  ON kcu.constraint_name = tc.constraint_name AND kcu.table_schema = tc.table_schema
WHERE tc.table_schema NOT IN ('pg_catalog', 'information_schema', 'pg_toast');
SELECT tc.table_schema, tc.table_name, tc.constraint_name, kcu.column_name,
       ccu.table_schema AS foreign_schema, ccu.table_name AS foreign_table, ccu.column_name AS foreign_column
FROM information_schema.table_constraints AS tc
JOIN information_schema.key_column_usage AS kcu
  ON kcu.constraint_name = tc.constraint_name AND kcu.table_schema = tc.table_schema
JOIN information_schema.constraint_column_usage AS ccu
  ON ccu.constraint_name = tc.constraint_name AND ccu.table_schema = tc.table_schema
WHERE tc.constraint_type = 'FOREIGN KEY' AND tc.table_schema NOT IN ('pg_catalog', 'information_schema', 'pg_toast');
SELECT routine_schema, routine_name, routine_type FROM information_schema.routines WHERE routine_schema NOT IN ('pg_catalog', 'information_schema', 'pg_toast');
SELECT trigger_schema, trigger_name, event_object_schema, event_object_table FROM information_schema.triggers WHERE trigger_schema NOT IN ('pg_catalog', 'information_schema', 'pg_toast');
```

Do not select `routine_definition` or `action_statement`.

When `cron.job` exists, jobs are reachable. Do not select the command column.

```sql
SELECT jobid, jobname, schedule FROM cron.job;
```

If that relation is missing, say jobs are not reachable.

### MySQL

Tool: `mysql`, and only when it is already on the path. If it is missing, name it. Point at `https://dev.mysql.com/doc/refman/8.4/en/mysql.html`. Do not install it.

The same token rule as PostgreSQL. Do not pass `-p` with a password.

```text
mysql --host=HOST --user=USER --database=DATABASE --enable-cleartext-plugin --batch -e "QUERY"
```

System schemas are not facts. Exclude `mysql`, `information_schema`, `performance_schema`, and `sys`.

```sql
SELECT schema_name FROM information_schema.schemata WHERE schema_name NOT IN ('mysql', 'information_schema', 'performance_schema', 'sys');
SELECT table_schema, table_name, table_type FROM information_schema.tables WHERE table_schema NOT IN ('mysql', 'information_schema', 'performance_schema', 'sys');
SELECT table_schema, table_name, column_name, data_type, character_maximum_length, numeric_precision, numeric_scale
FROM information_schema.columns WHERE table_schema NOT IN ('mysql', 'information_schema', 'performance_schema', 'sys');
SELECT table_schema, table_name, constraint_name, column_name, referenced_table_schema, referenced_table_name, referenced_column_name
FROM information_schema.key_column_usage WHERE table_schema NOT IN ('mysql', 'information_schema', 'performance_schema', 'sys');
SELECT routine_schema, routine_name, routine_type FROM information_schema.routines WHERE routine_schema NOT IN ('mysql', 'information_schema', 'performance_schema', 'sys');
SELECT trigger_schema, trigger_name, event_object_schema, event_object_table FROM information_schema.triggers WHERE trigger_schema NOT IN ('mysql', 'information_schema', 'performance_schema', 'sys');
SELECT event_schema, event_name, interval_value, interval_field, status FROM information_schema.events WHERE event_schema NOT IN ('mysql', 'information_schema', 'performance_schema', 'sys');
```

Do not select `routine_definition`, `action_statement`, or `event_definition`.

## Tokens in names

A schema or a name can show an environment. Tokenize it with the mark table in the skill. The whole word has to match. Cite it on the Seen line, like `schema dev says dev` or `table orders_test says test`.

`device` is not `dev`. `protest` is not `test`. A similar name is not evidence. Do not write this cite into `docs/environments/marks.md`.

After a no or a not sure, a name that matches no token is not a Seen line. Say the database shows no environment token.

## Pre-prod and shared

After the earlier yes, open for shape and connections only. Shape is schemas, table and view names, columns and types, and keys and relationships. Jobs and triggers are connections: source, target, and schedule. Say `Seen in <host> pre-prod.` or `Seen in <host> <environment>.` plus `shared with prod`. Say `Shape and connections only.` Never rows.

Do not open a prod-only database in this section. That yes does not apply here. Prod-only shape stays on the host reader: names, types, setting keys, and secret names from the resource list and the settings. Never a schema from inside the database. Never a row.

## Where facts go

Do not add a section. Each fact says `Seen in <host> <environment>.` Schema, table, view, column, key, procedure, and function facts join Seen, and then System, Architecture, Match, and Left out with the other facts. A job or a trigger joins Links.

## Azure commands

Read-only. Do not create, update, or delete. The access check uses these. `sqlcmd` waits until question 2 is yes.

- `az sql server show` and `az sql server firewall-rule list` for public network access and whether a firewall rule exists. Do not print the IP range.
- `az sql db list` and `az sql db show` for database names on a server the list already showed
- `az sql mi show` for a managed instance
- `az postgres flexible-server show` or `az mysql flexible-server show` for public network access and private endpoint. Do not print a password.
- The private endpoint the first read already showed

Public network access disabled, or only a private endpoint: the best way is a machine already on that network, then `sqlcmd -G` or the engine client. Say a VPN or that network is needed. Do not create a firewall rule.

Public network access enabled and the client is not allowed: say a firewall rule is needed. Do not create it.

## AWS commands

Read-only. Do not create, update, or delete. Do not read a secret value.

- `aws rds describe-db-instances` and `aws rds describe-db-clusters` for engine, endpoint, `PubliclyAccessible`, `IAMDatabaseAuthenticationEnabled`, and the subnet group. Do not print a master password.
- `aws rds generate-db-auth-token` only after a yes, and only when IAM authentication is already enabled. Do not print the token.

`PubliclyAccessible` false: say a VPN or a machine in the VPC is needed. Do not change a security group.

IAM authentication disabled: stop this reader when they say yes. Say a password login is not used. Do not call `aws secretsmanager get-secret-value`.

## Google Cloud commands

Read-only. Do not create, update, or delete. Do not start Cloud SQL Auth Proxy. Do not install it.

- `gcloud sql instances describe` for `ipConfiguration` (public IP, private network, SSL) and `databaseVersion`
- `gcloud sql databases list` for database names. This is not table metadata.
- `gcloud sql users list` to see whether the active account is already a user. Do not print a password. If it is not a user, say a database user with read rights on metadata is missing. Do not create one.
- `gcloud auth print-access-token` only after a yes, and only when IAM database authentication is already on. Do not print the token.

Private IP only: say a VPN or a machine on that network is needed. Do not enable a public IP.

## Hard rules

- Run only after the first read, and before any section. Leftovers that stopped the read skip this reader.
- No clear database environment: say `There are no clear database environments.` Then ask. Options only. One question at a time.
- Question 2 is asked only after the access check is said.
- A yes reads metadata only, and only with a query in this file.
- Never read a row. Never `SELECT` from a user table. Never print a connection string, a password, a token, or a secret.
- Never print procedure text, function text, a trigger body, or a job command.
- Production is never opened, including a prod-only database. A yes to prod-only shape does not open it. Pre-prod and shared stay shape and connections, and only after the earlier yes.
- A schema or a name is evidence only when the whole-word token rule matches.
- Do not install a tool. Do not log in. Do not create a login, a user, or a firewall rule.
- Missing access stops this reader and names the gap. The sections of the first read still run.
- Facts join the sections that already exist. They say `Seen in <host> <environment>.`
