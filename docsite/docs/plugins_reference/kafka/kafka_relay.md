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
host|yes|The host on which all Kafka commands will be pushed for execution. THIS HOST MUST HAVE KAFKA INSTALLED ON. Specifically, HADeploy must be able to access the Kafka installation jar files.
zk_host_group|yes|The [`host_group`](../inventory/host_groups) representing the zookeeper quorum. This group must contain the hosts acting as zookeeper servers.<br>This group should have the `force_setup`flag set to `yes
zk_port|no|The zookeeper client port.<br>Default: `2181`
broker_id_map|no|With Kafka, each broker is identified with an id. When creating a Topic, one can let Kafka distribute partition's replica across the cluster. But, we may also need to specify explicitly the distribution of replica, with strict location rules.<br>In such case, we need to specify brokers at topic creation, using `broker_id`. As these `broker_id` are infrastructure dependent, our application deployment description would be tightly coupled to the target infrastructure.<br>To prevent, this, we introduce here a level of indirection, by a map where each key is a virtual `broker_id` (used in `assignment` in topic definition) and the value is the effective one.<br>If this map is not defined, then the virtual `broker_id` are same as the effective ones.
tools_folder|no|Folder used by HADeploy to install some tools for Kafka management.<br>Default: `/tmp/hadeploy_<user>/` where `user` is the [`ssh_user`](../inventory/hosts) defined for this relay host.
principal|no|A Kerberos principal allowing all Kafka related operation to be performed. See below
local_keytab_path|no|A local path to the associated keytab file. This path is relative to the embeding file. See [below](#kerberos-authentication)
relay_keytab_path|no|A path to the associated keytab file on the relay host. See [below](#kerberos-authentication)
become_user|no|A user account under which all kafka operations will be performed. Only used on non-Kerberos cluster.<br>Note: The [`ssh_user`](../inventory/hosts) defined for this relay host must have enough rights to switch to this `become_user` using the `become_method` below.<br>Default: No user switch, so the [`ssh_user`](../inventory/hosts) defined for this relay host will be used.
become_method|no|The method used to swith to this user. Refer to the Ansible documentation on this parameter.<br>Default: Ansible default (`sudo`).

## Kerberos authentication

When `principal` and `..._keytab_path` variables are defined, Kerberos authentication will be activated for all Kafka operations. This means a `kinit` will be issued with provided values before any Kafka access, and a `kdestroy` issued after. This has the following consequences:

* All Kafka operations will be performed on behalf of the user defined by the provided principal. 

* The `kinit` will be issued on the relay host with the [`ssh_user`](../inventory/hosts) account. This means any previous ticket own by this user on this node will be lost. 

Regarding the keytab file, two cases:

* This keytab file already exists on the relay host. In such case, the `relay_keytab_path` must be set to the location of this file. And the relay host's [`ssh_user`](../inventory/hosts) must have read access on it.

* This keytab file is not present on the relay host. In such case the `local_keytab_path` must be set to its local location. HADeploy will take care of copying it on the remote relay host, 
in a location under `tools_folder`. Note you can also modify this target location by setting also the `relay_keytab_path` parameter. In this case, 
it must be the full path, including the keytab file name. And the containing folder must exists.

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
  relay_keytab_path: /etc/security/keytabs/kafka.service.keytab
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
## Tricks

To find the `broker_ids` values, one may use the [`kdescribe`](https://github.com/Kappaware/kdescribe) tool:

If, when running HADeploy you encounter error like:

```bash
fatal: [dn1]: FAILED! => {"changed": false, "failed": true, "msg": "AnsibleUndefinedVariable: 'dict object' has no attribute 'ansible_fqdn'"}
```

it is most likely that you have not set `force_setup` on the `zk_host_group` group  
