# elasticsearch_indices

## Synopsis

Allow definition of a list of Elasticserch indices.

## Attributes

Each item of the list has the following attributes:

Name | req?	 |	Description
--- | ---  | ---
server|yes|The server this index will be created on. Refer to the logical name attribute of an [`elasticsearch_servers`](./elasticsearch_servers) list item.
name|yes|The name of this index. 
definition|yes|Index definition as a json string or as a YAML definition. See examples
recreate|no|Boolean: Will trigger Index destruction before recreating it. WARNING: All data will be lost!. Use with care.<br>Default: `no`.
no_remove|no|Boolean: Prevent this index to be removed when HADeploy will be used in REMOVE mode.<br>Default: `no`
when|no|Boolean. Allow [conditional deployment](../../more/conditional_deployment) of this item.<br>Default `True` 

## Example

In the following, the definition is provided as a JSON text:

```yaml
elasticsearch_indices:
- server: elastic1
  name: test1a
  definition: |
    {
        "settings" : {
            "index": {
                "number_of_shards" : 3,
                "number_of_replicas": 3
            }
        },
        "mappings" : {
            "type1" : {
                "properties" : {
                    "field1" : { "type" : "text" }
                }
            }
        }
    }  
```

It also can be provided in 'pure' YAML form:

```yaml
elasticsearch_indices:
- server: elastic1
  name: test1a
  definition:
    settings:
      index:
        number_of_shards: 3
        number_of_replicas: 3
    mappings:
      type1:
        properties:
          field1:
            type: text

```

## Idempotency

Idempotency is one of the key features of HADeploy. In our case, this means creating an index is not just issuing a PUT on the server. We need to take current server state in account.

So, when required to create an Index, HADeploy will:

- First, try to retrieve a index of the same name.
- If there is no such index, just create it and return successfully. This is the simplest case.
- If there is one, compare the existing definition to the provided one. In most case, the existing definition is richer than the one used to create it, 
as Elasticsearch engine populate it with some default value or some other meta-informations. 
So, this comparison try to figure out if all items provided by our definition are included in the current existing one.
- If yes, this means existing index is compliant with our provided definition. So, we can stop processing and return successfully.
- If no, the module will try to adjust if possible. For this it can use the 
[Update Indices Settings](https://www.elastic.co/guide/en/elasticsearch/reference/current/indices-update-settings.html) elasticsearch API or the
[Put Mapping](https://www.elastic.co/guide/en/elasticsearch/reference/current/indices-put-mapping.html) one.

Note that such adjustment have some limitation. For example, one can update the `number_of_replicas`, but not the `number_of_shards`. Refer to the links to the API above for more information about what can be updated in an open index.

In the case where index can't be updated to fulfill provided definition, an error is generated. 

Another point to take in account is, for the comparison to be effective, the provided definition must be defined as it will be retrieved by the [Get index](https://www.elastic.co/guide/en/elasticsearch/reference/current/indices-get-index.html) API.

For example, when retrieving an index, you will get the setting definition like:

```yaml
{
    "settings" : {
        "index" : {
            "number_of_shards" : 3, 
            "number_of_replicas" : 2 
        }
    }
}
```

But the elastic documentation state than you can also use a simplified form:

```yaml
{
    "settings" : {
        "number_of_shards" : 3,
        "number_of_replicas" : 2
    }
}
```
DON'T USE THIS SIMPLIFIED FORM in you index definition. It will mislead comparison thus generating errors.

### Default values.

Another common issue is default value handling. For example 

```yaml
   {
        .....
        "mappings" : {
            "type1" : {
                "properties" : {
                    "field1" : { "type" : "text", "index": true }
                }
            }
        }
    }  
```
Will generate an error. One must write:

```yaml
   {
        .....
        "mappings" : {
            "type1" : {
                "properties" : {
                    "field1" : { "type" : "text" }
                }
            }
        }
    }  
```
This because this is how the mapping is defined when retrieving index definition by GET API. (`"index": true` is the default). 

Of course, if you want to prevent some fields to be indexed, you will write:
```yaml
   {
        .....
        "mappings" : {
            "type1" : {
                "properties" : {
                    "field1" : { "type" : "text", "index": false }
                }
            }
        }
    }  
```

