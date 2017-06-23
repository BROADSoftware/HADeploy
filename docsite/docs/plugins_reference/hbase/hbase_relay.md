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
local_keytab_path|no|A local path to the associated keytab file. This path is relative to the embeding file. See [below](#kerberos-authentication)
relay_keytab_path|no|A path to the associated keytab file on the relay host. See [below](#kerberos-authentication)
become_user|no|A user account under which all namespace and table operations will be performed. Only used on non-Kerberos cluster.<br>Note: The [`ssh_user`](../inventory/hosts) defined for this relay host must have enough rights to switch to this `become_user` using the `become_method` below.<br>Default: No user switch, so the [`ssh_user`](../inventory/hosts) defined for this relay host will be used.
become_method|no|The method used to swith to this user. Refer to the Ansible documentation on this parameter.<br>Default: Ansible default (`sudo`).

## Kerberos authentication

When `principal` and `..._keytab_path` variables are defined, Kerberos authentication will be activated for all HBase operations.
 
* All HBase operations will be performed on behalf of the user defined by the provided principal. 
* This principal must have enough rights to be able to create namespaces and HBase table. 

Regarding the keytab file, two cases:

* This keytab file already exists on the relay host. In such case, the `relay_keytab_path` must be set to the location of this file. And the relay host's [`ssh_user`](../inventory/hosts) must have read access on it.
<br>Normally, for HBase, there should be at least one principal and keytab file created with full privileges by the system during Kerberos setup.
* This keytab file is not present on the relay host. In such case the `local_keytab_path` must be set to its local location. HADeploy will take care of copying it on the remote relay host, 
in a location under `tools_folder`. Note you can also modify this target location by setting also the `relay_keytab_path` parameter. In this case, 
it must be the full path, including the keytab file name. And the containing folder must exists.


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
  relay_keytab_path: /etc/security/keytabs/hbase.headless.keytab
  
  
```
