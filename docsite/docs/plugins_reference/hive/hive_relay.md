# hive_relay

## Synopsis

Issuing some commands to specifics subsystem, such as HIVE require a quite complex client configuration.

To avoid this, HADeploy will not issue such command directly, but push the command on one of the cluster node, called ’Relay node'.
An edge node of the cluster would typically assume this function.

`hive_relay` will define which host will be used to relay operations for HIVE, and also how these operations will be performed.

There should be only one entry of this type in the HADeploy definition file.

## Attributes

`hive_relay` is a map with the following attributes:

Name | req?	| 	Description
--- | --- | ---
host|yes|The host on which all hive commands will be pushed for execution. Must be a fully configured as HIVE client.
tools_folder|no|Folder used by HADeploy to install some tools for HIVE management.<br>Default: `/tmp/hadeploy_<user>/` where `user` is the [`ssh_user`](../inventory/hosts) defined for this relay host.
principal|no|A Kerberos principal allowing all HIVE related operations to be performed. See below
local_keytab_path|no|A local path to the associated keytab file. This path is relative to the embeding file. See [below](#kerberos-authentication)
relay_keytab_path|no|A path to the associated keytab file on the relay host. See [below](#kerberos-authentication)
become_user|no|A user account under which all database and table operations will be performed. Only used on non-Kerberos cluster. It will determine table ownership.<br>Note: The [`ssh_user`](../inventory/hosts) defined for this relay host must have enough rights to switch to this `become_user` using the `become_method` below.<br>Default: No user switch, so the [`ssh_user`](../inventory/hosts) defined for this relay host will be used.
become_method|no|The method used to swith to this user. Refer to the Ansible documentation on this parameter.<br>Default: Ansible default (`sudo`).
report_file|no|Local path for a report file which will be (re)generated on each run.<br>This YAML file describe all performed operation and eventually un-achievable operation. It could be a starting point for a more sophisticated database migration processing.<br>Under the hood, all HIVE operation are performed by a special tools: [jdchive](https://github.com/BROADSoftware/jdchive). You will find more information about the schema of this report file [here](https://github.com/BROADSoftware/jdchive#report-file) 

## Kerberos authentication

When `principal` and `..._keytab_path` variables are defined, Kerberos authentication will be activated for all HIVE operations.
 
* All HIVE operations will be performed on behalf of the user defined by the provided principal. 

* This principal must have enough rights to be able to create HIVE databases and table. 

Regarding the keytab file, two cases:

* This keytab file already exists on the relay host. In such case, the `relay_keytab_path` must be set to the location of this file. And the relay host's [`ssh_user`](../inventory/hosts) must have read access on it.

* This keytab file is not present on the relay host. In such case the `local_keytab_path` must be set to its local location. HADeploy will take care of copying it on the remote relay host, 
in a location under `tools_folder`. Note you can also modify this target location by setting also the `relay_keytab_path` parameter. In this case, 
it must be the full path, including the keytab file name. And the containing folder must exists.

## Example
```yaml
hive_relay:
  host: en1
```
With Kerberos activated:
```yaml
hive_relay:
  host: en1
  principal: hive_admin
  relay_keytab_path: /etc/security/keytabs/hive_admin.keytab
```
