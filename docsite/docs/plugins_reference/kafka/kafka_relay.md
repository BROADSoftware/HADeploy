# kafka_relay

## Synopsis


Issuing some commands to specifics subsystem, such as Apache Kafka require a quite complex client configuration.

To avoid this, HADeploy will not issue such command directly, but push the command on one of the cluster node, called ’Relay node'.

`kafka_relay` will define which host will be used to relay operations for Kafka, and also how these operations will be performed.

There should be only one entry of this type in the HADeploy definition file.

## Attributes

kafka_relay is a map with the following attributes:

Name | req?	 |	Description
--- | --- | ---
host|yes|The host on which all Kafka commands will be pushed for execution. THIS HOST MUST HAVE KAFKA INSTALLED ON. Specifically, HADeploy must be able to access the Kafka installation jar files.
zk_host_group|yes|The `host_group` representing the zookeeper quorum. This group must contain the hosts acting as zookeeper servers.
zk_port|no|The zookeeper client port.<br>Default: `2181`
broker_id_map|no|With Kafka, each broker is identified with an id. When creating a Topic, one can let Kafka distribute partition's replica across the cluster. But, we may also need to specify explicitly the distribution of replica, with strict location rules.<br>In such case, we need to specify brokers at topic creation, using `broker_id`. As these `broker_id` are infrastructure dependent, our application deployment description would be tightly coupled to the target infrastructure.<br>To prevent, this, we introduce here a level of indirection, by a map where each key is a virtual `broker_id` (used in `assignment` in topic definition) and the value is the effective one.<br>If this map is not defined, then the virtual `broker_id` are same as the effective ones.
tools_folder|no|Folder used by HADeploy to install some tools for Kafka management.<br>If you intend to deploy with a non-root account, this value must be modified. Refer to specific chapter. (LINK). Default: `/opt/hadeploy`
principal|no|A Kerberos principal allowing all Kafka related operation to be performed. See below
keytab_path|no|A path to the associated keytab file on the relay host. See below

## Kerberos authentication

When `principal` and `keytab_path` variables are defined, Kerberos authentication will be activated for all Kafka operations. This means a `kinit` will be issued with provided values before any Kafka access, and a `kdestroy` issued after. This has the following consequences:

* All Kafka operations will be performed on behalf of the user defined by the provided principal. 
* The `kinit` will be issued under the relay host `ssh_user` account (`root` by default). This means any previous ticket own by this user on this node will be lost. 
* And `ssh_user` must have read access on the provided keytab file.

Note also this keytab file must exists on the relay host. If it is not the case, one may copy it using file copy of HADeploy. This wills works as all file copy on the nodes are performed before any Kafka operation (See Execution order in Miscellaneous chapter). (LINK)

## Example

The simplest case:
```yaml
kafka_relay:
  host: br1
  zk_host_group: zookeepers
```
The simplest case with Kerberos activated:
```yaml
kafka_relay:
  host: br1
  zk_host_group: zookeepers
  principal: kafka/dn1.my.cluster.com
  keytab_path: /etc/security/keytabs/kafka.service.keytab
```
A more complex, with default value set and a `broker_id` mapping (Typical of an Hortonworks Kafka deployment).
```yaml
kafka_relay:
  host: br1
  zk_host_group: zookeepers
  zk_port: 2181
  broker_id_map:
    1: 1001
    2: 1002
    3: 1003
```
## Trick

To find the `broker_ids` values, one may use the [`kdescribe`](https://github.com/Kappaware/kdescribe) tool:


 
