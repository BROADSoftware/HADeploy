# elastic_modules

This ansible role host a set of modules aimed to manipulate indices and templates on an elastic search server.

* elasticsearch\_index: Allow creation/deletion/update of Elasticsearch index. Doc [at this location](docs/elasticsearch_index.txt)
* elasticsearch\_template: Allow creation/deletion/update of Elasticsearch index template. Doc [at this location](docs/elasticsearch_template.txt)


## Requirements

These modules need the `python-requests` package to be present on the remote node.

# Index creation example Playbook

Elastic index definition can be provided as a JSON text, using YAML block scalar, as below:

```yaml
- hosts: elastic1
  roles:
  - elastic_modules
  tasks:
  - name: Create index
    elasticsearch_index:
      name: index1
      elasticsearch_url: "http://elastic1.mydomain.com:9200"
      definition: |
        {
            "settings" : {
                "index": {
                    "number_of_shards" : 1
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
      state: present
```
(Take great care of indentation).

Or it can be provided in a pure YAML form:

```yaml
  - name: Create index
    elasticsearch_index:
      name: test1
      elasticsearch_url: "http://elastic1.mydomain.com:9200"
      definition:
        settings:
          index:
            number_of_shards: 1
        mappings:
          type1:
            properties:
              field1:
                type: text
      state: present
```

Note also the:

```yaml
  roles:
  - elastic_modules
```
Which have two functions:

- Include the module in the `library` path.
- Install the required `python-requests` package on the target host 


# Template creation example Playbook

Template definition follows the same pattern as index:

```yaml
- hosts: elastic1
  roles:
  - elastic_modules
  tasks:
  - name: Create template
    elasticsearch_template:
      name: tmpl1
      elasticsearch_url: "http://elastic1.mydomain.com:9200"
      definition: |
        {
          "index_patterns": ["xte*", "bar*"],
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
      state: present
```

or

```yaml
  - name: Create template
    elasticsearch_template:
      name: tmpl1
      elasticsearch_url: "http://elastic1.mydomain.com:9200"
      definition:
        index_patterns: 
        - "xte*"
        - "bar*"
        settings:
          index:
            number_of_shards: 1
        mappings:
          type1:
            _source:
              enabled: False
            properties:
              host_name:
                type: keyword
              created_at:
                type: date
                format: "EEE MMM dd HH:mm:ss Z YYYY"
      state: present
```


# Index creation idempotency

Idempotency is one of the key features of Ansible technology. In our case, this means creating an index is not just issuing a PUT on the server. We need to take current server state in account.

So, when required to create an Index, the `elasticsearch_index` module will:

- First, try to retrieve a index of the same name.
- If there is no such index, just create it and return successfully. This is the simplest case.
- If there is one, compare the existing definition to the provided one. In most case, the existing definition is richer than the one used to create it, as Elasticsearch engine populate it with some default value or some other meta-informations. So, this comparison try to figure out if all items provided by our definition are included in the current existing one.
- If yes, this means existing index is compliant with our provided definition. So, we can stop processing and return successfully.
- If no, the module will try to adjust if possible. For this it can use the [Update Indices Settings](https://www.elastic.co/guide/en/elasticsearch/reference/current/indices-update-settings.html) API or the [Put Mapping](https://www.elastic.co/guide/en/elasticsearch/reference/current/indices-put-mapping.html) one.

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

# Template creation idempotency

Template creation is managed almost the same way then Index creation. Except it is simpler, as a template can be recreated anytime, without loosing any data.

But keep in mind template recreation does not affect existing indices.

# Limitation

These modules does not provide authentication handling. Contribution welcome. 

# License

GNU GPL

Click on the [Link](COPYING) to see the full text.

