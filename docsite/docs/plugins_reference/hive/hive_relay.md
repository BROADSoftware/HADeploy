# hive_relay

## Synopsis

Allow definition of how all HIVE commands will be performed.

There should be only one entry of this type in the HADeploy definition file.

## Attributes

`hive_relay` is a map with the following attributes:

Name | req?	| 	Description
--- | --- | ---
host|yes|The host on which all hive commands will be pushed for execution. Must be a fully configured as HIVE client.
tools_folder|no|Folder used by HADeploy to install some tools for HIVE management.<br>If you intend to deploy with a non-root account, this value must be modified. Refer to specific chapter (LINK).<br>Default: `/opt/hadeploy`
principal|no|A Kerberos principal allowing all HIVE related operations to be performed. See below
local_keytab_path|no|A local path to the associated keytab file. This path is relative to the embeding file. See [below](#kerberos-authentication)
relay_keytab_path|no|A path to the associated keytab file on the relay host. See [below](#kerberos-authentication)
user|no|A user account under which all database and table operation will be performed. On non-Kerberos cluster this will determine table ownership.<br>Default:`ssh_user`
become_method|no|The method used to swith to this user. Refer to the Ansible documentation on this parameter.<br>Default: `sudo` (Ansible default)
report_file|no|Local path for a report file which will be (re)generated on each run.<br>This YAML file describe all performed operation and eventually un-achievable operation. It could be a starting point for a more sophisticated database migration processing.<br>Under the hood, all HIVE operation are performed by a special tools: [jdchive](https://github.com/BROADSoftware/jdchive). You will find more information about the schema of this report file [here](https://github.com/BROADSoftware/jdchive#report-file) 


## Kerberos authentication

When `principal` and `..._keytab_path` variables are defined, Kerberos authentication will be activated for all HIVE operations.
 
* All HIVE operations will be performed on behalf of the user defined by the provided principal. 
* This principal must have enough rights to be able to create HIVE databases and table. 

Regarding the keytab file, two cases:

* This keytab file already exists on the relay host. In such case, the `relay_keytab_path` must be set to the location of this file. And the relay host's `ssh_user` must have read access on it.
* This keytab file is not present on the relay host. In such case the `local_keytab_path` must be set to its local location. HADeploy will take care of copying it on the remote relay host, in a location under `tools_folder`. Note you can also modify this target location by setting also the `relay_keytab_path` parameter.

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
