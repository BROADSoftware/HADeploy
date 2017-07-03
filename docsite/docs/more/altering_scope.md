# Altering scope

Sometime, it may be usefull to execute only parts of a full deployment. May be you have only a small modification to propagate, 
and we want cut off execution time. Or may be some part are not relevant for your current context.

HADeploy provide a mechanisme to scope the deployment (or removal) process to only some part, thus achieving partial execution.

This mechanisme is driven by:

- The entry [`included_scopes`](../plugins_reference/core/included_scopes) in the application definition file, which define the list of 'scopes' as the only ones to execute.
- The command line parameter `--scope` which allow full overriden of this list on command line.
- The entry [`excluded_scopes`](../plugins_reference/core/excluded_scopes) in the application definition file, which define a list of 'scopes' to exclude from execution.
- The command line parameter `--noScope` which can provide other scopes to add the the exclusion list.

## Scopes list

The valid scope values are:

Name|Description
--- | ---
all|All scopes.
none|Nothing (Empty execution).
files|Files, Folders and Trees on the nodes. 
hdfs|Files, Folders and Tree on HDFS.
hbase|All HBase releted operations (Including Datasets).
kafka|All Kafka related operations.
hive|All Hive related operations.
ranger|All Ranger related operations.

Plus all the values provided as 'scope' attribute for the [`files`](../plugins_reference/files/files),
[`folders`](../plugins_reference/files/folders) and [`trees`](../plugins_reference/files/trees) entries.

## As Command line parameters

A stated above, the `included_scopes` list can also be provided on the command line:

```bash
hadeploy --src app.yml --src infra.yml --scope files --scope kafka,hbase --action DEPLOY
```
Note there is two methods to provide multiple scopes: Entering `--scope`several times, or provide a comma separated list of value (But without spaces).

And to add to the `excluded_scopes` list, there is the `--noScope` parameter, with the same logic:
 
```bash
hadeploy --src app.yml --src infra.yml --noScope ranger --noScope hive,hbase --action DEPLOY
```

