# hbase_relay

## Synopsis

Issuing some commands to specifics subsystem, such as HBase require a quite complex client configuration.

To avoid this, HADeploy will not issue such command directly, but push the command on one of the cluster node, called ’Relay node'.
An edge node of the cluster would typically assume this function.

`hbase_relay` will define which host will be used to relay operations for HBase, and also how these operations will be performed.

There should be only one entry of this type in the HADeploy definition file.

## Attributes

`hbase_relay` is a map with the following attributes:

Name | req? |	Description
--- | --- | ---
host|yes|The host on which all hbase commands will be pushed for execution. Must be fully configured as HBase client.
tools_folder|no|Folder used by HADeploy to install some tools for HBase management.<br>Default: `/tmp/hadeploy_<user>/` where `user` is the [`ssh_user`](../inventory/hosts) defined for this relay host.
principal|no|A Kerberos principal allowing all HBase related operation to be performed. See below
keytab_path|no|A path to the associated keytab file on the relay host.

## Kerberos authentication

When principal and keytab_path variables are defined, Kerberos authentication will be activated for all HBase operations.
 
* All HBase operations will be performed on behalf of the user defined by the provided principal. 
* This principal must have enough rights to be able to create namespaces and HBase table. Normally, there should be at least one principal and keytab file created with these privileges by the system during Kerberos setup.
* And the host's `ssh_user` must have read access on the provided keytab file.

Note also this keytab file must exists on the relay host. If it is not the case, one may copy it using file copy of HADeploy. This wills works as all file copy on the nodes are performed before any HBase operation (See Execution order in Miscellaneous chapter). (LINK)

## Example
```yaml
hbase_relay:
  host: en1
```
With Kerberos activated:
```yaml
hbase_relay:
  host: en1
  principal: hbase-mycluster
  keytab_path: /etc/security/keytabs/hbase.headless.keytab
  
  
```
