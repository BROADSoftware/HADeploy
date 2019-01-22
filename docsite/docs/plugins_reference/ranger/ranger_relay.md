# ranger_relay

## Synopsis

All Apache Ranger commands will be performed using Ranger HTTP/REST API. This definition will provide informations for HADeploy to use this interface.

There should be only one entry of this type in the HADeploy definition file.

## Attributes

ranger_relay is a map with the following attributes:

Name | req? |	Description
--- | ---  | ---
host|yes|From which host these commands will be launched. Typically, an edge node in the cluster. But may be a host outside the cluster.
ranger_url|yes|The Ranger base URL to access Ranger API. Same host:port as the Ranger Admin GUI. Typically: <br>`http://myranger.server.com:6080`<br>or<br>`https://myranger.server.com:6182`
ranger_username|no|The user name to log on the Ranger Admin. Must have enough rights to manage policies
ranger_password|no|The password associated with the admin_username. May be encrypted. Refer to [encrypted variables](../core/encrypted_vars)
principal|no|A Kerberos principal allowing all Ranger related operation to be performed. See [below](#kerberos-authentication)
local_keytab_path|no|A local path to the associated keytab file. This path is relative to the embeding file. See [below](#kerberos-authentication)
relay_keytab_path|no|A path to the associated keytab file on the relay host. See [below](#kerberos-authentication)
tools_folder|no|Folder used by HADeploy to store keytab if needed.<br>Default: `/tmp/hadeploy_<user>/` where `user` is the [`ssh_user`](../inventory/hosts) defined for this relay host.
validate_certs|no|Useful if Ranger Admin connection is using SSL. If no, SSL certificates will not be validated. This should only be used on personally controlled sites using self-signed certificates.<br>Default: `yes`
ca_bundle_relay_file|no|Useful if Ranger Admin connection is using SSL. Allow to specify a CA_BUNDLE file, a file that contains root and intermediate certificates to validate the Ranger Admin certificate in .pem format.<br>This file will be looked up on the relay host system, on which this module will be executed.
ca_bundle_local_file|no|Same as above, except this file will be looked up locally, relative to the main file. It will be copied on the relay host at the location defined by `ca_bundle_relay_file`
hdfs_service_name|no|In most cases, you should not need to set this parameter. It defines the Ranger Admin HDFS service, typically: `<yourClusterName>_hadoop`.<br>It must be set if there are several such services defined in your Ranger Admin configuration, to select the one you intend to use.
hbase_service_name|no|In most cases, you should not need to set this parameter. It defines the Ranger Admin HBase service, typically: `<yourClusterName>_hbase`.<br>It must be set if there are several such services defined in your Ranger Admin configuration, to select the one you intend to use.
kafka_service_name|no|In most cases, you should not need to set this parameter. It defines the Ranger Admin Kafka service, typically: `<yourClusterName>_kafka`.<br>It must be set if there are several such services defined in your Ranger Admin configuration, to select the one you intend to use.
hive_service_name|no|In most cases, you should not need to set this parameter. It defines the Ranger Admin Hive service, typically: `<yourClusterName>_hive`.<br>It must be set if there are several such services defined in your Ranger Admin configuration, to select the one you intend to use.
yarn_service_name|no|In most cases, you should not need to set this parameter. It defines the Ranger Admin Yarn service, typically: `<yourClusterName>_yarn`.<br>It must be set if there are several such services defined in your Ranger Admin configuration, to select the one you intend to use.
storm_service_name|no|In most cases, you should not need to set this parameter. It defines the Ranger Admin Storm service, typically: `<yourClusterName>_storm`.<br>It must be set if there are several such services defined in your Ranger Admin configuration, to select the one you intend to use.
policy_name_decorator|no|To distinguish Ranger policy managed by HADeploy, a naming convention is applied by default. The policy name, as it will appears in the GUI Ranger interface will be in the form `HAD[<policyName>]`, where `<policyName>` is the name of the policy as you provide it.<br>This is achieved by wrapping the name with this pattern, where `{0}` is substituted with the policy name. <br>For python aware reader, this is performed as:<br>`"HAD[{0}]".format(policyName)`.<br>If you just want to have raw policy name, simply define the parameter with `{0}`.<br>Default: `HAD[{0}]`
no_log|no|Boolean. Prevent some messages to be displayed, as they can contains sensitive information. This can make debugging somewhat more difficult, so temporary setting this swith to `False` may be useful to get more information (Including sensitive ones!).<br>Default `True` 
when|no|Boolean. Allow [conditional deployment](../../more/conditional_deployment) of this item.<br>Default `True` 

## Kerberos authentication

When `principal` and `..._keytab_path` variables are defined, Kerberos authentication will be activated for all Ranger operations. This means a `kinit` will be issued with provided values before any Ranger access, and a `kdestroy` issued after. This has the following consequences:

* All Ranger operations will be performed on behalf of the user defined by the provided principal. **This user must have enough rights to perform required policy manipulation.** Granting this user with 'admin' role through Ranger UI is the simplest way to achieve this.

* The `kinit` will be issued on the relay host with the [`ssh_user`](../inventory/hosts) account. This means any previous ticket own by this user on this node will be lost. 

Regarding the keytab file, two cases:

* This keytab file already exists on the relay host. In such case, the `relay_keytab_path` must be set to the location of this file. And the relay host's [`ssh_user`](../inventory/hosts) must have read access on it.

* This keytab file is not present on the relay host. In such case the `local_keytab_path` must be set to its local location. HADeploy will take care of copying it on the remote relay host, 
in a location under `tools_folder`. Note you can also modify this target location by setting also the `relay_keytab_path` parameter. In this case, 
it must be the full path, including the keytab file name. And the containing folder must exists.

## Example

A simple configuration:

```yaml
ranger_relay:
  host: en1
  ranger_url:  http://ranger.mycluster.mycompany.com:6080
  ranger_username: admin
  ranger_password: admin
```
A more secure configuration, with https, certificate validation and encrypted password.

```yaml
encrypted_vars:
  ranger_password: |
    $ANSIBLE_VAULT;1.1;AES256
    34396662613462623565323936616330623661623065343033646136643635653430636238613962
    3537343131346462343138343064313937646366363435340a633532366162623838376436366362
    61393033343932303636653066336130616132383463373934396265306364363562613565613165
    6163613739303430650a356136353865623534643237646166393230613933396166663963633538
    3664

ranger_relay:
  host: en1
  ranger_url:  https://ranger.mycluster.mycompany.com:6182
  ranger_username: admin
  ranger_password: "{{ranger_password}}"  
  ca_bundle_local_file: cert/ranger_mycluster_cert.pem
  ca_bundle_relay_file: /etc/security/certs/ranger_mycluster_cert.pem
```

When using such encryption feature, you will need to provide a password when launching HADeploy. Otherwise you will have an error like the following: 

```bash
The offending line appears to be:

  vars:
      rangerPassword: !vault |
                      ^ here
```

More detail on how to encrypt a value and providing a password on execution at [encrypted variables](../core/encrypted_vars)

A configuration using Kerberos authentication:

```yaml
ranger_relay:
  host: en1
  ranger_url:  http://ranger.mycluster.mycompany.com:6080
  principal: sa
  local_keytab_path: ./sa-gate17.keytab  
```

## CA_BUNDLE

Internally, HADeploy use the python `requests` API to access Ranger. The provided `ca_bundle_relay_file` will be used as the `verify` parameter of all HTTP requests. More info  [here](http://docs.python-requests.org/en/master/user/advanced/#ssl-cert-verification).
 
In some cases, a CA_BUNDLE may be simply the certificate of the Ranger server, in PEM format.

To grab this certificate, you may use a tiny python program like the following:
```python
import ssl

if __name__ == '__main__':
    cert = ssl.get_server_certificate(("ranger.mycluster.corp.com", 6182), ssl_version=ssl.PROTOCOL_SSLv23)
    print cert
    f = open("cert.pem", "w")
    f.write(cert)
    f.close()
```    


