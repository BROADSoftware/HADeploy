# storm_relay

## Synopsis

Most of Storm commands will be performed using Storm UI HTTP/REST API. This definition will provide informations for HADeploy to use this interface.

This is a reference part. Refer to the associated [`overview`](./storm_overview) for a more synthetical view.

## Attributes

`storm_relay` is a map with the following attributes:

Name | req?	 |	Description
--- | --- | ---
host|yes|The host which will be used for both launching topologies and accessing the Storm UI REST interface
storm_ui_url|yes|The base URL to access Storm UI REST API. Same host:port as the Storm GUI.<br>Typically: <br>`http://mystormui.mycluster.com:8744`
async|no|Boolean Specify if the all the topologies can be launched simultaneously. Default: `yes`. More info [here](./storm_overview#asynchronous-mode).
default_timeout_secs|no|Default value for `timeout_secs` value on [`storm_topologies`](storm_topologies) entry. Default to 90 seconds
principal|no|A Kerberos principal allowing all Storm related operation to be performed. See [below](#kerberos-authentication)
local_keytab_path|no|A local path to the associated keytab file. This path is relative to the embeding file. See [below](#kerberos-authentication)
relay_keytab_path|no|A path to the associated keytab file on the relay host. See [below](#kerberos-authentication)
tools_folder|no|Folder used by HADeploy to store keytab if needed.<br>Default: `/tmp/hadeploy_<user>/` where `user` is the [`ssh_user`](../inventory/hosts) defined for this relay host.
when|no|Boolean. Allow [conditional deployment](../../more/conditional_deployment) of this item.<br>Default `True` 


## Kerberos authentication

When `principal` and `..._keytab_path` variables are defined, Kerberos authentication will be activated for all Storm operations. This means a `kinit` will be issued with provided values before any Storm access, and a `kdestroy` issued after. This has the following consequences:

* All Storm operations will be performed on behalf of the user defined by the provided principal. 

* The `kinit` will be issued on the relay host with the [`ssh_user`](../inventory/hosts) account. This means any previous ticket own by this user on this node will be lost. 

Regarding the keytab file, two cases:

* This keytab file already exists on the relay host. In such case, the `relay_keytab_path` must be set to the location of this file. And the relay host's [`ssh_user`](../inventory/hosts) must have read access on it.

* This keytab file is not present on the relay host. In such case the `local_keytab_path` must be set to its local location. HADeploy will take care of copying it on the remote relay host, 
in a location under `tools_folder`. Note you can also modify this target location by setting also the `relay_keytab_path` parameter. In this case, 
it must be the full path, including the keytab file name. And the containing folder must exists.

## Example

The simplest case:

```
storm_relay:
  host: en1
  storm_ui_url: "http://stui.mycluster.mydomain.com:8744/"
```

And a more complete case, in a secured environement.

```
storm_relay:
  host: en1
  storm_ui_url: "http://stui.mysecuredcluster.mydomain.com:8744/"
  async: no
  principal: sa
  local_keytab_path: ./sa-gate17.keytab
  default_timeout_secs: 240
```
  
  



