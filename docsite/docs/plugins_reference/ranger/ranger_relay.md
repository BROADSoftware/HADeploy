# ranger_relay

## Synopsis
All Apache Ranger command will be performed using Ranger HTTP/REST API. This definition will provide informations for HADeploy to use this interface.

There should be only one entry of this type in the HADeploy definition file.

## Attributes

ranger_relay is a map with the following attributes:

Name | req?	| Default |	Description
--- | --- | --- | ---
host|yes||From which host these commands will be launched. Typically, an edge node in the cluster. But may be a host outside the cluster.
ranger_url|yes||The Ranger base URL to access Ranger API. Same host:port as the Ranger Admin GUI. Typically: <br>`http://myranger.server.com:6080`<br>or<br>`https://myranger.server.com:6182`
ranger_username|yes||The user name to log on the Ranger Admin. Must have enough rights to manage policies
ranger_password|yes||The password associated with the admin_username
validate_certs|no|yes|Useful if Ranger Admin connection is using SSL. If no, SSL certificates will not be validated. This should only be used on personally controlled sites using self-signed certificates.
ca_bundle_relay_file|no||Useful if Ranger Admin connection is using SSL. Allow to specify a CA_BUNDLE file, a file that contains root and intermediate certificates to validate the Ranger Admin certificate.<br>In its simplest case, it could be a file containing the server certificate in .pem format. This file will be looked up on the relay host system, on which this module will be executed.
ca_bundle_local_file|no||Same as above, except this file will be looked up locally, relative to the main file. It will be copied on the relay host at the location defined by ca_bundle_relay_file
hdfs_service_name|no||In most cases, you should not need to set this parameter. It defines the Ranger Admin HDFS service, typically: `<yourClusterName>_hadoop`.<br>It must be set if there are several such services defined in your Ranger Admin configuration, to select the one you intend to use.
hbase_service_name|no||In most cases, you should not need to set this parameter. It defines the Ranger Admin HBase service, typically: `<yourClusterName>_hbase`.<br>It must be set if there are several such services defined in your Ranger Admin configuration, to select the one you intend to use.
kafka_service_name|no||In most cases, you should not need to set this parameter. It defines the Ranger Admin Kafka service, typically: `<yourClusterName>_kafka`.<br>It must be set if there are several such services defined in your Ranger Admin configuration, to select the one you intend to use.
policy_name_decorator|no|`HAD[{0}]`|To distinguish Ranger policy managed by HADeploy, a naming convention is applied by default. The policy name, as it will appears in the GUI Ranger interface will be in the form `HAD[<policyName>]`, where `<policyName>` is the name of the policy as you provide it.<br>This is achieved by wrapping the name with this pattern, where `{0}` is substituted with the policy name. <br>For python aware reader, this is performed as:<br>`"HAD[{0}]".format(policyName)`.<br>If you just want to have raw policy name, simply define the parameter with `{0}`.

## Example

A simple configuration:
```yaml
ranger_relay:
  host: en1
  ranger_url:  http://ranger.mycluster.mycompany.com:6080
  ranger_username: admin
  ranger_password: admin
```
A more secure configuration, with https and certificate validation:
```yaml
ranger_relay:
  host: en1
  ranger_url:  https://ranger.mycluster.mycompany.com:6182
  ranger_username: admin
  ranger_password: aYhGhP6=
  ca_bundle_local_file: cert/ranger_mycluster_cert.pem
  ca_bundle_relay_file: /etc/security/certs/ranger_mycluster_cert.pem
```
## Simple CA_BUNDLE
 
In its simplest case, a CA_BUNDLE can be simply the certificate of the Ranger server, in PEM format.

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

