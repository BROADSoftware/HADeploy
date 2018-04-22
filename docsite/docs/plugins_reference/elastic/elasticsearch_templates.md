# elasticsearch_templates

## Synopsis

Allow definition of a list of Elasticsearch templates.

## Attributes

Each item of the list has the following attributes:

Name | req?	 |	Description
--- | ---  | ---
server|yes|The server this index will be created on. Refer to the logical name attribute of an [`elasticsearch_servers`](./elasticsearch_servers) list item.
name|yes|The name of this index. 
definition|yes|Template definition as a json string or as a YAML definition. See examples
no_remove|no|Boolean: Prevent this index to be removed when HADeploy will be used in REMOVE mode.<br>Default: `no`
when|no|Boolean. Allow [conditional deployment](../../more/conditional_deployment) of this item.<br>Default `True` 

## Example

In the following, the definition is provided as a JSON text:

```yaml
elasticsearch_templates:
- server: elastic1
  name: testtmpl1a
  definition: |
        {
          "index_patterns": ["foo*", "bar*"],
          "settings": {    
            "index": {
                "number_of_shards": 1
            }
          },
          "mappings": {
            "type1": {
              "_source": {
                "enabled": false
              },
              "properties": {
                "host_name": {
                  "type": "keyword"
                },
                "created_at": {
                  "type": "date",
                  "format": "EEE MMM dd HH:mm:ss Z YYYY"
                }
              }
            }
          }
        }      
```

It also can be provided in 'pure' YAML form:

```yaml
elasticsearch_templates:
- server: elastic1
  name: testtmpl1a
  definition:
    index_patterns: 
    - "foo*"
    - "bar*"
    settings:
      index:
        number_of_shards: 1
    mappings:
      type1:
        _source:
          enabled: True
        properties:
          host_name:
            type: text
            index: True
          created_at:
            type: date
            format: "EEE MMM dd HH:mm:ss Z YYYY"

```
## Idempotence

For Templates, there is no idempotence concern, as a template can be recreated at any time, without loosing any data.

But keep in mind template recreation does not affect existing indices.

