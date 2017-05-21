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
