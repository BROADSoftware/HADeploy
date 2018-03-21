# elasticsearch_servers

## Synopsis

Allow definition of a list of Elasticserch servers. These servers are intended to be refenced by [`elasticsearch_indices`](./elasticsearch_indices) and [`elasticsearch_templates`](./elasticsearch_templates) items. 

## Attributes

Each item of the list has the following attributes:

Name | req?	 |	Description
--- | ---  | ---
name|yes|The logical name given to this server 
relay_host|yes|From which host are the HTTP requests to elasticserch server issued.
url|yes|The base part of the url of the server. Typically: `http://elastic1.myserver.mydomain.com:9200/`
when|no|Boolean. Allow [conditional deployment](../../more/conditional_deployment) of this item.<br>Default `True` 

 

## Example


```yaml

elasticsearch_servers:
- name: elastic1
  relay_host: en1
  url: http://elastic1.myserver.mydomain.com:9200/
  
```

