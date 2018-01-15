# hdfs_relay

## Synopsis

Issuing some commands to specifics subsystem, such as HDFS require a quite complex client configuration.

To avoid this, HADeploy will not issue such command directly, but push the command on one of the cluster node, called ’Relay node'.
An edge node of the cluster would typically assume this function.

`hdfs_relay` will define which host will be used to relay operations for HDFS, and also how these operations will be performed.

There should be only one entry of this type in the HADeploy definition file.

## Attributes

hdfs_relay is a map with the following attributes:

Name | req? |	Description
--- | --- | ---
host|yes|The host on which all HDFS commands will be pushed for execution.
cache_folder|no|A folder on this host, which will be used by HADeploy as cache storage. Mainly, all files targeted to HDFS will be first pushed in this cache. And will remains in it, to optimize idempotence.<br>Default: `{{ansible_user_dir}}/.hadeploy/files`, where `{{ansible_user_dir}}` is substitued by the home folder of the [`ssh_user`](../inventory/hosts) defined for this relay host.
user|no|The user account HADeploy will use to perform all HDFS related operation. Must have enough rights to do so.<br>Not to be defined when using Kerberos authentication.<br>Default: The [`ssh_user`](../inventory/hosts) defined for this relay host or `hdfs` if this user is `root`.
hadoop_conf_dir|no|Where HADeploy will lookup Hadoop configuration file.<br>Default: `/etc/hadoop/conf`
webhdfs_endpoint|no|HADeploy will perform several actions through WebHDFS REST interface. You can specify corresponding endpoint, if it is not defined in the usual configuration way.<br>Default: The value found in `<hadoop_conf_dir>/hdfs-site.xml`
principal|no|A Kerberos principal allowing all HDFS related operation to be performed. See below
local_keytab_path|no|A local path to the associated keytab file. This path is relative to the embeding file. See [below](#kerberos-authentication)
relay_keytab_path|no|A path to the associated keytab file on the relay host. See [below](#kerberos-authentication)
when|no|Boolean. Allow [conditional deployment](../../more/conditional_deployment) of this item.<br>Default `True` 

## Kerberos authentication

When `principal` and `..._keytab_path` variables are defined, Kerberos authentication will be activated for all HDFS folders, files and trees operations. This means a `kinit` will be issued with provided values before any HDFS access, and a `kdestroy` issued after. This has the following consequences:

* All HDFS operations will be performed on behalf of the user defined by the provided principal. The user parameter become irrelevant and providing it is an error.

* The `kinit` will be issued under the relay host [`ssh_user`](../inventory/hosts) account. This means any previous ticket own by this user on this node will be lost. 

Regarding the keytab file, two cases:

* This keytab file already exists on the relay host. In such case, the `relay_keytab_path` must be set to the location of this file. And the relay host's [`ssh_user`](../inventory/hosts) must have read access on it.

* This keytab file is not present on the relay host. In such case the `local_keytab_path` must be set to its local location. HADeploy will take care of copying it on the remote relay host, in a location under `tools_folder`. Note you can also modify this target location by setting also the `relay_keytab_path` parameter. In this case, 
it must be the full path, including the keytab file name. And the containing folder must exists.

## Example

The simplest case:

```yaml
hdfs_relay:
  host: en1
```
Same, with default value sets:

```yaml
hdfs_relay:
  host: en1
  user: hdfs
  hadoop_conf_dir: "/etc/hadoop/conf"
  webhdfs_endpoint: "namenode.mycluster.myinfra.com:50070"
```
The simplest case with Kerberos activated:

```yaml
hdfs_relay:
  host: en1
  principal: hdfs-mycluster
  relay_keytab_path: /etc/security/keytabs/hdfs.headless.keytab
```
