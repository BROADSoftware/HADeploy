# source_host_credentials

## Synopsis

Provide a list of credentials to allow access to HDFS from host other than `hdfs_relay`.

This is used by files or trees operation when the source is a cluster node (`src: node:///...`)

## Attributes

Each item of the list has the following attributes:

Name | req?	| Description
--- | --- | ---
host|yes|The source host
principal|yes|A Kerberos principal allowing all HDFS related operation to be performed. See below
local_keytab_path|yes if<br>`node_keytab_path`<br>is not defined|A local path to the associated keytab file. This path is relative to the embeding file. See [below](#kerberos-authentication)
node_keytab_path|yes if<br>`local_keytab_path`<br>is not defined|A path to the associated keytab file on the node. See [below](#kerberos-authentication)
when|no|Boolean. Allow [conditional deployment](../../more/conditional_deployment) of this item.<br>Default `True` 

## Kerberos authentication
When performing a copy operation (files or trees) from a cluster's host to HDFS, if a `principal` and `..._keytab_path` variables are defined for this host, Kerberos authentication will be activated before issuing the operation. 

This means a `kinit` will be issued with provided values on this host before any HDFS access, and a kdestroy issued after. This has the following consequences:

* All HDFS operations will be performed on behalf of the user defined by the provided principal. 

* The `kinit` will be issued under this host [`ssh_user`](../inventory/hosts) account. This means any previous ticket own by this user on this node will be lost. 


Regarding the keytab file, two cases:

* This keytab file already exists on this host. In such case, the `node_keytab_path` must be set to the location of this file. And this host's [`ssh_user`](../inventory/hosts) must have read access on it.

* This keytab file is not present on this host. In such case the `local_keytab_path` must be set to its local location. HADeploy will take care of copying it on the remote host, in a location under `tools_folder`. Note you can also modify this target location by setting also the `node_keytab_path` parameter. In this case, 
it must be the full path, including the keytab file name. And the containing folder must exists.

## Example

```yaml
source_host_credentials:
- host: sr1
  principal: hdfs-mycluster
  node_keytab_path: /etc/security/keytabs/hdfs.headless.keytab
```