# Secured Hadoop clusters

## Kerberos support

All Kerberos configuration will occur in the relay definition. So, refer to

* [hdfs_relay](../plugins_reference/hdfs/hdfs_relay.md)
* [hive_relay](../plugins_reference/hive/hive_relay.md)
* [hbase_relay](../plugins_reference/hbase/hbase_relay.md)
* [kafka_relay](../plugins_reference/kafka/kafka_relay.md)
* [source_host_credentials](../plugins_reference/hdfs/source_host_credentials.md)

In the Reference part for how to configure Kerberos access for all HADeploy operations.


## Ranger tricks

### SSL Certificate validation

If Ranger admin is configured with SSL, default configuration will require an valid certificate, one recognized be a registered certificate authority. If this is not the case, all Ranger access will throw an error, unless you:

* Disable certificate validation: `validate_certs: no` in [ranger_relay](../plugins_reference/ranger/ranger_relay.md)

Or:

* Provide a CA_BUNDLE.

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

### Resources collision

Apache Ranger does not allow to have several policies granting access to the same set of resources (Path, table, topics,...).

To work around this limitation, a simple trick it to add an un-existing, fake resource to the resource list on one of the colliding policies.

For example:
```yaml
kafka_ranger_policies:
- name: "allToJim"
  topics: 
  - "*"
  - "dummy_topic"
  permissions:
  - users:
    - jim
  accesses:
    - publish
    - consume
    - configure
    - describe
    - create
    - delete
    - kafka_admin
```     
