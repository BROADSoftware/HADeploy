# Execution order

The order of action performed on the target host does NOT depend of the order in the description file. Action order is the following:

* Linux local groups are created
* Linux local users are created.
* Apache Ranger policies are applied 
* Linux nodes folders are created.
* Files and trees with nodes as target are deployed
* hdfs_relay host is configured, if needed
* HDFS folders are created
* Files and trees with HDFS as target are deployed
* hbase_relay host is configured if needed.
* HBase namespaces and table are created.
* HBase datasets are loaded
* hive_relay host is configured if needed.
* Hive databases and tables are created
* kafka_relay host is configured, if needed
* Kafka topics are created

Removal action order is the reverse.

Inside each action group, order is preserved. For example, with:

```yaml
folders:
- { scope: en, path: /etc/broadapp, owner: root, group: root, mode: "0755" }
- { scope: en, path: /opt/broadapp, owner: root, group: root, mode: "0755" }
```
`/etc/broadapp` will be create before `/opt/broadapp`.

Same for variables. This is a single pass evaluation. So, obviously:
```yaml
  app_version: "0.1.1"
  repository_server: "myserver.com"
  app_jar_url: "http://${repository_server}/repo/broadapp-${app_version}.jar"
```
Will be OK. While:
```yaml
  app_jar_url: "http://${repository_server}/repo/broadapp-${app_version}.jar"
  app_version: "0.1.1"
  repository_server: "myserver.com"
```
Will fail, with a `variable undefined` error.

## Plugin Priority

The order described above result from an ordering of the plugin execution. 

To achieve this, internally, each plugin is granted with a priority for each action. And execution follow ascending order of priority.

Here are the values per plugin and action:

|        Plugin       |   grooming |   deploy   | remove   |
|---                  |     ---    |     ---    |   ---    |
|header               |   1100     |   1100     |   1100   |
|ansible_inventories  |   1200     |   1200     |   1200   |
|inventory            |   1300 (3) |   1300     |   1300   |
|ansible              |   1400     |   (2)      |   (2)    |
|users                |   2000     |   2000     |   7000   |
|ranger               |   8000 (1) |   2500     |   6000   |
|files                |   3000     |   3000     |   4000   |
|hdfs                 |   3500 (4) |   3500     |   3500   |
|hbase                |   4000     |   4000     |   3000   |
|hive                 |   4500     |   4500     |   2500   |
|kafka                |   5000     |   5000     |   2000   | 

NB: `grooming` is an internal action, performed on [step 4 of the run](./under_the_hood)

These priorities value are of interest if you insert some raw ansible playbooks or roles (Using [`ansible`](../plugins_reference/ansible/ansible_overview) module) and want to control at which steps they will be executed.

(1): Ranger grooming must occurs after all ranger aware resources grooming

(2): Configured by the user in the deployment file

(3): Must be after ansible inventory, for host overriding

(4): Must be after files

