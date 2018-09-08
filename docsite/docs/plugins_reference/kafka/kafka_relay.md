# kafka_relay

## Synopsis


Issuing some commands to specifics subsystem, such as Apache Kafka require a quite complex client configuration.

To avoid this, HADeploy will not issue such command directly, but push the command on one of the cluster node, called ’Relay node'.

`kafka_relay` will define which host will be used to relay operations for Kafka, and also how these operations will be performed.

There should be only one entry of this type in the HADeploy definition file.

## Attributes

`kafka_relay` is a map with the following attributes:

Name | req?	 |	Description
--- | --- | ---
host|yes|The host on which all Kafka commands will be pushed for execution. THIS HOST MUST HAVE KAFKA INSTALLED ON. This can be validated by trying to locate and use commanes such as `kafka-topic.sh`.
zk_host_group|yes|The [`host_group`](../inventory/host_groups) representing the zookeeper quorum. This group must contain the hosts acting as zookeeper servers.<br>This group should have the `force_setup`flag set to `yes
kafka_version|yes|Specify the Kafka version. May be `0.10.0`, `1.0.0`, `1.1.1` or `2.0.0`. If your current version does not strictly match one of theses, you may try to select immediate previous version (i.e. use `0.10.0` for `0.11.0`).
zk_port|no|The zookeeper client port.<br>Default: `2181`
zk_path|no|The root path of Kafka in zookeeper.<br>Default:`'/'` 
broker_id_map|no|With Kafka, each broker is identified with an id. When creating a Topic, one can let Kafka distribute partition's replica across the cluster. But, we may also need to specify explicitly the distribution of replica, with strict location rules.<br>In such case, we need to specify brokers at topic creation, using `broker_id`. As these `broker_id` are infrastructure dependent, our application deployment description would be tightly coupled to the target infrastructure.<br>To prevent, this, we introduce here a level of indirection, by a map where each key is a virtual `broker_id` (used in `assignment` in topic definition) and the value is the effective one.<br>If this map is not defined, then the virtual `broker_id` are same as the effective ones.
tools_folder|no|Folder used by HADeploy to install some tools for Kafka management.<br>Default: `/tmp/hadeploy_<user>/` where `user` is the [`ssh_user`](../inventory/hosts) defined for this relay host.
become_user|no|A user account under which all kafka operations will be performed..<br>Note: The [`ssh_user`](../inventory/hosts) defined for this relay host must have enough rights to switch to this `become_user` using the `become_method` below.<br>Default: No user switch, so the [`ssh_user`](../inventory/hosts) defined for this relay host will be used.
become_method|no|The method used to swith to this user. Refer to the Ansible documentation on this parameter.<br>Default: Ansible default (`sudo`).
when|no|Boolean. Allow [conditional deployment](../../more/conditional_deployment) of this item.<br>Default `True` 

## Kerberos authentication

HADeploy Kafka topics management need access to Zookeeper. When Kerberos is activated on the target cluster, such access may be protected and forbidden for your deployment user. 

In such case, solution is to act as `kafka` user, by using the `become_user` attribute.

But keep in mind The [`ssh_user`](../inventory/hosts) defined for this relay host must have enough rights to switch to `kafka` user account using the `become_method`.

## Example

The simplest case:

```yaml
kafka_relay:
  host: br1
  zk_host_group: zookeepers
  kafka_version: "1.0.0"
```

The simplest case when Kerberos is activated:

```yaml
kafka_relay:
  host: br1
  zk_host_group: zookeepers
  kafka_version: "1.0.0"
  become_user: kafka
```

A more complex, with default value set and a `broker_id` mapping (Typical of an Hortonworks Kafka deployment).

```yaml
kafka_relay:
  host: br1
  zk_host_group: zookeepers
  kafka_version: "0.10.0"
  zk_port: 2181
  broker_id_map:
    1: 1001
    2: 1002
    3: 1003
```

## Tricks

### kdescribe

To find the `broker_ids` values, one may use the [`kdescribe`](https://github.com/Kappaware/kdescribe) tool:

### AnsibleUndefinedVariable

If, when running HADeploy you encounter error like:

```bash
fatal: [dn1]: FAILED! => {"changed": false, "failed": true, "msg": "AnsibleUndefinedVariable: 'dict object' has no attribute 'ansible_fqdn'"}
```

it is most likely that you have not set `force_setup` on the `zk_host_group` group  
