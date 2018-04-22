# kafka_topics

## Synopsis

Provide a list of Kafka topics, which will be managed by HADeploy

## Attributes

Each item of the list has the following attributes:

Name | req? |	Description
--- | --- | ---
name|yes|The name of the topic
properties|no|A map of properties associated to the topic. Refer to the kafka documentation for a complete list of available properties.
partition_factor|yes if assignments is not defined|Specify the number of partition of the topic.
replication_factor|yes if assignments is not defined|Specify the number of replica for each partition.
assignments|yes if rep/part factors are not specified|A Map where the key is the partition# and the value a list of `broker_id`.<br>This allow to manual definition of the distribution of partition's replica, with strict location rules.
no_remove|no|Boolean: Prevent this group to be removed when HADeploy will be used in REMOVE mode.<br>Default: `no`
ranger_policy|no|Definition of Apache Ranger policy bound to this topic. Parameters are same as [`kafka_ranger_policy`](../ranger/kafka_ranger_policies) except than `topics` should not be defined.<br>The policy name can be explicitly defined. Otherwise, a name will be generated as "`_<topic>_`".<br>See example below for more information
when|no|Boolean. Allow [conditional deployment](../../more/conditional_deployment) of this item.<br>Default `True` 

## Example

Simple case. We let Kafka decide on which brokers our replica will be set:
```yaml
kafka_topics:
- name: broadapp_t1
  partition_factor: 3
  replication_factor: 2
  properties:
    retention.ms: 630720000000
    retention.bytes: 858993459200
```
The same, topic, but we specify explicitly our placement of replica:
```yaml
kafka_topics:
- name: broadapp_t1
  assignments:
    0: [ 1, 2 ]
    1: [ 2, 3 ]
    2: [ 3, 1 ]
  properties:
    retention.ms: 630720000000
    retention.bytes: 858993459200
```
If `hdfs_relay` host a `broker_id_map` as the following:
```yaml
kafka_relay:
  ...
  broker_id_map:
    1: 1001
    2: 1002
    3: 1003
```
Then the first partition (#0) will have two replicas, placed on brokers of id 1001 and 1002.

If `hdfs_relay` does not contains a `broker_id_map`, then the first partition (#0) will have two replicas, placed on brokers of id 1 and 2. 

> NB: Recent version of Kafka introduced a 'Rack awareness' capability which ensure a good distribution of replica amongst several racks. This explicit partition assignment may now be used only on very specifics cases.

> NB: Partition re-assignment on topic modification is not supported. One may use the kafka provided partition reassignment tool (kafka-reassign-partitions.sh) for this.
 
Another example, with a Apache Ranger policy granting Publish and Consume rights to the users of group users:
```yaml
kafka_topics:
- name: broadapp_t1
  partition_factor: 3
  replication_factor: 2
  ranger_policy:
    audit: no
    permissions:
    - groups:
      - users
      accesses:
    - Consume
    - Publish
```

## Trick

To find the `broker_ids` values, one may use the `kdescribe` tool:

[https://github.com/Kappaware/kdescribe](https://github.com/Kappaware/kdescribe)
 
