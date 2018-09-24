# elasticsearch_servers

## Synopsis

Allow definition of a list of Elasticsearch servers. These servers are intended to be refenced by [`elasticsearch_indices`](./elasticsearch_indices) and [`elasticsearch_templates`](./elasticsearch_templates) items. 

## Attributes

Each item of the list has the following attributes:

Name | req?	 |	Description
--- | ---  | ---
name|yes|The logical name given to this server 
relay_host|yes|From which host are the HTTP requests to elasticsearch server issued.
url|yes|The base part of the url of the server. Typically: `http://elastic1.myserver.mydomain.com:9200/`
when|no|Boolean. Allow [conditional deployment](../../more/conditional_deployment) of this item.<br>Default `True` 
username|no|The user name to log on this elasticsearch server. Must have enough rights to perform intended operations.
password|no|The password associated with the `username`. May be encrypted. Refer to [encrypted variables](../core/encrypted_vars)
validate_certs|no|Useful if the connection is using SSL. If no, SSL certificates will not be validated. This should only be used on personally controlled sites using self-signed certificates.<br>Default: `yes`
ca_bundle_relay_file|no|Useful if the connection is using SSL. Allow to specify a CA_BUNDLE file, a file that contains root and intermediate certificates to validate the elasticsearch server certificate in .pem format.<br>This file will be looked up on the relay host system, on which this module will be executed.
ca_bundle_local_file|no|Same as above, except this file will be looked up locally, relative to the main file. It will be copied on the relay host at the location defined by `ca_bundle_relay_file`

 

## Example

The simplest case:

```yaml
elasticsearch_servers:
- name: elastic1
  relay_host: en1
  url: http://elastic1.myserver.mydomain.com:9200/
```

For a secured elasticsearch cluster:

```yaml
elasticsearch_servers:
- name: elastic2
  relay_host: en1
  url: https://elastic2.myserver.mydomain.com:9200/
  validate_certs: false 
  username: elastic
  password: changeme  
```
## CA_BUNDLE

Internally, HADeploy use the python `requests` API to access elasticsearch. The provided `ca_bundle_relay_file` will be used as the `verify` parameter of all HTTP requests. More info  [here](http://docs.python-requests.org/en/master/user/advanced/#ssl-cert-verification).
 
If, for encrypting communication with elasticsearch you have generated a Certificate authority with
```
bin/elasticsearch-certutil ca 
``` 
as described in the [elastic documentation](https://www.elastic.co/guide/en/elasticsearch/reference/current/configuring-tls.html), the following python code will allow you to generate a CA_BUNDE file `elastic-stack-ca.crt.pem`.   

```python
# Need:
# sudo yum install pyOpenSSL
from OpenSSL import crypto

# Accept "" for empty password.
with open("elastic-stack-ca.p12", "rb") as file:
    p12 = crypto.load_pkcs12(file.read(), "capassword")

# PEM formatted certificate
cert =  crypto.dump_certificate(crypto.FILETYPE_PEM, p12.get_certificate())
print cert
f = open("elastic-stack-ca.crt.pem", "w")
f.write(cert)
f.close()
```




