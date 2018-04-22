# hbase_tables

## Synopsis

Provide a list of HBase tables required by the application 

## Attributes

Each item of the list has the following attributes:

Name | req? |	Description
--- | ---  | ---
namespace|yes|The HBase namespace hosting this table. May be defined in the hbase_namespaces list defined above, or will be assumed as already existing.
name|yes|The name of this table
properties|no|A list of properties, allowing definition of table properties.<br>You will find table properties definition is HBase documentation.<br>For a complete list, please refer to the Javadoc of the class `org.apache.hadoop.hbase.HTableDescriptor` of your HBase version.
column_families|yes|Provide a list of one or several column families. See below
presplit|no|Allow an initial region split schema to be defined. See below
no_remove|no|Boolean: Prevent this table to be removed when HADeploy will be used in REMOVE mode.<br>Default: `no`
ranger_policy|no|Definition of Apache Ranger policy bound to this table. Parameters are same as [hbase_ranger_policies](../ranger/hbase_ranger_policies) except than `tables`, `columns_families` and `columns` should not be defined. The policy will apply on all column families and all column of the table.<br>The policy name can be explicitly defined. Otherwise, a name will be generated as "`_<namespace>:<table>_`".<br>See example below for more information
when|no|Boolean. Allow [conditional deployment](../../more/conditional_deployment) of this item.<br>Default `True` 

## column_families

Each item of the column_families list has the following attributes:

Name | req?	| Default |	Description
--- | --- | --- | ---
name|yes||The name of this column family.
properties|no||A list of properties, allowing definition of this column family properties.<br>You will find table properties definition is HBase documentation.<br>For a complete list, please refer to the Javadoc of the class `org.apache.hadoop.hbase.HColumnDescriptor` of your HBase version.

## presplit

> NB: Please, note than unlike all other definition, presplitting is only effective at the initial table creation. If the table already exists, no modification is performed and the `presplit:` attribute is ignored.

Presplitting can be expressed with one of the following 2 methods:
```yaml
  presplit:
    splits: ['BENJAMIN', 'JULIA', 'MARTIN', 'PAUL', 'VALENTIN']
```
or:
```yaml
  presplit:
    start_key: "10000"
    end_key: "90000"
    num_region: 10
```
Note that internally HBase works with byte[], not String. So, in some case, the splitting must be expressed using hexadecimal notation. For example:
```yaml
  presplit:
    start_key: '\x00'
    end_key: '\xFF'
    num_region: 5
```
or:
```yaml
  presplit:
    splits:
    - '\x33'
    - '\x66'
    - '\x99'
    - '\xCC'
```
Note these two last presplit expressions will result in the same layout.

Some aspect to take care using such notation:

* String must be surrounded by simple quotes. If you want to use double quote, you will need to escape the backslash character (i.e: `"\\x33"`).
* Letters used for hexadecimal notation must always be upper case.
* If you need more information about this format, note than, internally, all theses strings are parsed using the function `org.apache.hadoop.hbase.util.Bytes.toBytesBinary()`

Example
```yaml
hbase_tables: 
- name: broadapp_t1
  namespace: broadgroup
  properties: 
    regionReplication: 1
    durability: ASYNC_WAL
  column_families:
  - name: cf1
    properties: 
      maxVersions: 12
      minVersions: 2
      timeToLive: 200000
```
Create a table with a single column family (`cf1`), without presplit
```yaml
hbase_tables: 
- name: testtable1
  namespace: ns1
  properties: 
    regionReplication: 1
    durability: ASYNC_WAL
  column_families:
  - name: cf1
    properties: 
      maxVersions: 12
      minVersions: 2
      timeToLive: 200000
      cacheBloomsOnWrite: true
      compressionType: NONE
  - name: cf2
    properties:
      maxVersions: 12
      minVersions: 2
      timeToLive: 200000
```
Create a table with two column families, with different set of properties
```yaml
hbase_tables: 
- name: testtable2
  namespace: ns2
  column_families:
  - name: cf1
  - name: cf2
  presplit:
    splits: ['BENJAMIN', 'JULIA', 'MARTIN', 'PAUL', 'VALENTIN']
no_remove: yes
```
Create a table with two column families, with all properties to default value. Table is presplitted on an estimated distribution of first names. This table will not be removed by the application removal processing.

Following will create a table with two columns families and grant read access to members of `users` group through Apache Ranger.
```yaml
hbase_tables: 
- name: testtable3
  namespace: ns1
  column_families:
  - name: cf1
  - name: cf2
  ranger_policy:
    permissions:
    - groups:
      - users
      accesses:
      - read 
```

