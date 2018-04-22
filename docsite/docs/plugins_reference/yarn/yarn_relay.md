# yarn_relay

## Synopsis

Most of Yarn commands will be performed using RessouceManager REST API's. This definition will provide informations for HADeploy to use this interface.

This is a reference part. Refer to the associated [`overview`](./yarn_overview) for a more synthetical view.

## Attributes

`yarn_relay` is a map with the following attributes:

Name | req?	 |	Description
--- | --- | ---
host|yes|The host which will be used for both launching services (using provided script), and accessing the RessourceManager UI REST interface
default_timeout_secs|no|Default value for `timeout_secs` value on [`yarn_services`](yarn_services) entries. Default to 90 seconds
principal|no|A Kerberos principal allowing all Yarn related operation to be performed. See [below](#kerberos-authentication)
local_keytab_path|no|A local path to the associated keytab file. This path is relative to the embedding file. See [below](#kerberos-authentication)
relay_keytab_path|no|A path to the associated keytab file on the relay host. See [below](#kerberos-authentication)
tools_folder|no|Folder used by HADeploy to store keytab if needed.<br>Default: `/tmp/hadeploy_<user>/` where `user` is the [`ssh_user`](../inventory/hosts) defined for this relay host.
when|no|Boolean. Allow [conditional deployment](../../more/conditional_deployment) of this item.<br>Default `True` 
rm_endpoint|no|Provide Yarn REST API entry point. Typically `namenode.mycluster.com:8088`. It could also be a comma separated list of entry point, which will be checked up to a valid one. This will allow resource manager H.A. handling. If not defined, will be looked up in local yarn-site.xml
hadoop_conf_dir|no|Specify Hadoop configurations file location, where HADeploy will lookup the `yarn-site.xml` file. Default to `/etc/hadoop/conf`.

## Resource Manager configuration lookup

If this `yarn_relay` host is properly configured as an Hadoop client, there should be no need to provide value to `hadoop_conf_dir` and/or `rm_endpoint`, 
as HADeploy will be able to lookup the Resource Manager Web URL by using default values. 


## Kerberos authentication

When `principal` and `..._keytab_path` variables are defined, Kerberos authentication will be activated for all Yarn operations. This means a `kinit` will be issued with provided values before any Yarn access, and a `kdestroy` issued after. This has the following consequences:

* All Yarn operations will be performed on behalf of the user defined by the provided principal. 

* The `kinit` will be issued on the relay host with the [`ssh_user`](../inventory/hosts) account. This means any previous ticket own by this user on this node will be lost. 

Regarding the keytab file, two cases:

* This keytab file already exists on the relay host. In such case, the `relay_keytab_path` must be set to the location of this file. And the relay host's [`ssh_user`](../inventory/hosts) must have read access on it.

* This keytab file is not present on the relay host. In such case the `local_keytab_path` must be set to its local location. HADeploy will take care of copying it on the remote relay host, 
in a location under `tools_folder`. Note you can also modify this target location by setting also the `relay_keytab_path` parameter. In this case, 
it must be the full path, including the keytab file name. And the containing folder must exists.

## Example

The simplest case:

```
yarn_relay:
  host: en1
```

And a more complete case, in a secured environment.

```
yarn_relay:
  host: en1
  principal: sa
  local_keytab_path: ./sa-gate17.keytab
  default_timeout_secs: 240
```
  
  



