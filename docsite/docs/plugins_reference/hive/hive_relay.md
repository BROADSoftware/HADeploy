# hive_relay

## Synopsis

Allow definition of how all HIVE commands will be performed.

There should be only one entry of this type in the HADeploy definition file.

## Attributes

`hive_relay` is a map with the following attributes:

Name | req?	| Default |	Description
--- | --- | --- | ---
host|yes||The host on which all hive commands will be pushed for execution. Must be a fully configured as HIVE client.
tools_folder|no|/opt/hadeploy|Folder used by HADeploy to install some tools for HIVE management.<br>If you intend to deploy with a non-root account, this value must be modified. Refer to specific chapter (LINK).
principal|no||A Kerberos principal allowing all HIVE related operations to be performed. See below
keytab_path|no||A path to the associated keytab file on the relay host.
user|no|ssh_user|A user account under which all database and table operation will be performed. On non-Kerberos cluster this will determine table ownership.
become_method|no|sudo|The method used to swith to this user. Refer to the Ansible documentation on this parameter.
report_file|no||Local path for a report file which will be (re)generated on each run.<br>This YAML file describe all performed operation and eventually un-achievable operation.I could be a starting point for a more sophisticated database migration processing. See [HIVE assets migration](../../more/hive_assets_migration)


## Kerberos authentication

When principal and keytab_path variables are defined, Kerberos authentication will be activated for all HIVE operations.
 
* All HIVE operations will be performed on behalf of the user defined by the provided principal. 
* This principal must have enough rights to be able to create HIVE databases and table. 
* And the host's `ssh_user` must have read access on the provided keytab file.

Note also this keytab file must exists on the relay host. If it is not the case, one may copy it using file copy of HADeploy. This wills works as all file copy on the nodes are performed before any HIVE operation (See Execution order in Miscellaneous chapter). (LINK)

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
  keytab_path: /etc/security/keytabs/hive_admin.keytab
```
