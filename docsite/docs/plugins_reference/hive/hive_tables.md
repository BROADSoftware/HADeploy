# hive_tables

## Synopsis

Provide a list of HIVE tables required by the application. They will be created (or destroyed) by HADeploy.

## Attributes

Each item of the list has the following attributes:

Name | req?  |	Description
--- | --- | ---
name             |yes|The name of the table
database         |yes|The database this table belong to
external         |no |Boolean. Equivalent to the EXTERNAL Hive DDL clause
fields           |no |A list of fields definition describing the table's column. Refer to [Field definition](#field-definition) below
comment          |no |An optional comment associated to the table
location         |no |Equivalent to the LOCATION Hive DDL clause
properties       |no |A map of properties. Equivalent to TBLPROPERTIES Hive DDL clause
stored_as        |no |Specify the file format, such as SEQUENCEFILE, TEXTEFILE, RCFILE, ....<br/>Equivalent to STORED AS Hive DDL clause [1]
input_format     |no |Equivalent to STORED AS INPUT FORMAT '....' Hive DDL clause [1][2]
output_format    |no |Equivalent to STORED AS OUTPUT FORMAT '....' Hive DDL clause [1][2]
delimited        |no |A map of delimiter character. Equivalent to ROW FORMAT DELIMITED Hive DDL clause. Refer to [Delimited row format](#delimited-row-format) below [3]
serde            |no |Allow explicit definition of a `serde`'. Equivalent to ROW FORMAT SERDE Hive DDL clause [3]
serde_properties |no |A map of properties associated to the `serde`. Equivalent to WITH SERDEPROPERTIES Hive DDL clause
storage_handler  |no |Allow definition of the storage handler. Equivalent to STORED BY Hive DDL clause
partitions       |no |A list of fields definition describing the table's partitioning. Refer to [Field definition](#field-definition)  below
clustered_by     |no |Allow definition of a CLUSTERED BY Hive DDL clause. Refer to [Table clustering](#table-clustering) below
skewed_by        |no |Allow definition of a SKEWED BY Hive DDL Clause. Refer to [Skewed values](#skewed-values)
alterable        |no |Boolean. Allow most of ALTER TABLE commands to be automatically issued for table modification. Refer to [Altering table](#altering-table) below.<br>Default: `no`.
droppable        |no |Boolean. Allow this table to be dropped and recreated if definition is modified.<br>Default value is `yes` if the table is external, `no`for all other cases
no_remove        |no |Boolean: Prevent this database to be removed when HADeploy will be used in REMOVE mode.<br>Default: `no`
ranger_policy    |no |Definition of Apache Ranger policy bound to this table.<br>Parameters are same as [hive_ranger_policies](../ranger/hive_ranger_policies) except than `database`, `tables` and `columns` should not be defined. The policy will apply on all columns of this table.<br>The policy name can be explicitly defined. Otherwise, a name will be generated as "`_<database.table>_`".<br>See example below for more information
when|no|Boolean. Allow [conditional deployment](../../more/conditional_deployment) of this item.<br>Default `True` 
 
[1]: Storage format can be defined using two methods:

* Use `stored_by`. This will define implicitly `input_format`, `output_format` and, for some value the `serde`.
* Explictly define `input_format`, `output_format` and eventually `serde`.

The two approaches are exclusive. Defining both `stored_by` and `input/output_format` will generate an error.

[2] `input_format` and `output_format` must be defined both if used.

[3] `delimited` and `serde` are exclusive and can't be defined both.


### Field definition:

Here is the definition of a `field` element:

| Field Attribute | Req. | Description |
| ---   | :---: | --- |
|name   |yes|The name of the field|
|type   |yes|The type of the field. Note this file if used as-is, without interpretation from HADeploy.<br>This will allow to define Hive Complex Types here (arrays, maps, structs,union). See examples below.|
|comment|no |An optional comment|

### Delimited row format 

The `delimited` map can hold the following values:

```yaml
fields_terminated_by:
fields_escaped_by:
collection_items_terminated_by:
map_keys_terminated_by:
lines_terminated_by:
null_defined_as:
``` 

The characters must be expressed between single quote, and can be a regular character, an usual backslash escape sequence, or a unicode value. For example:

```yaml
...
delimited:
  fields_terminated_by: ','
  map_keys_terminated_by: '\u0009'  # Same as '\t'
  lines_terminated_by: '\n'
  null_defined_as: '\u0001'
``` 
> using octal notation (i.e. '\001') is not supported.

### Table clustering

Here is the definition of a `clustered_by` element:

| Attribute  | Req. | Description |
| ---        | :---: | --- |
|columns     |yes|This list of columns to CLUSTER BY |
|nbr_buckets |yes|The number of buckets|
|sorted_by   |no |A list of sort item element, as defined just below|

Inner sort item element:

|Attribute | Req. | Description |
| ---:     | :---: | --- |
|columns   |yes|A list of column |
|direction |no |The direction: `ASC` or `DESC`. Default is `ASC`|

Example:

```yaml
  ...
  clustered_by:
    columns:
    - userid
    - page_url
    sorted_by:
    - { column: userid, direction: asc }
    - { column: page_url, direction: desc }
    nbr_buckets: 16
```

Will be interpreted as:

```sql
 CLUSTERED BY(userid,page_url) SORTED BY (userid asc, page_url desc) INTO 16 BUCKETS
```

### Skewed values

Here is the definition of the `skewed_by` element:

| Attribute | Req. | Description |
| ---: | :---: | --- |
|columns                |yes|A list of column |
|values                 |yes|A list of list of values|
|stored\_as_directories |no |Boolean. Is skewed value stored as directory.<br>Default `no`|

Example:

```yaml
  ...
  skewed_by:
    columns:
    - key
    values:
    - [ 1 ]
    - [ 5 ]
    - [ 6 ]
    stored_as_directories: true
```

will be interpreted as:

```sql
SKEWED BY(key) ON(('1'),('5'),('6')) STORED AS DIRECTORIES
```

And:

```yaml
  skewed_by:
    columns:
    - col1
    - col2
    values:
    - [ "s1", 1 ]
    - [ "s3", 3 ]
    - [ "s13", 13 ]
    - [ "s78", 78 ]
```

will be interpreted as:

```sql
SKEWED BY(col1,col2) ON(('s1', 1),('s3', 3),('s13', 13),('s78',78))
```

## Altering table

The must tricky operation with tools like `HADeploy` is not table creation, but how it must behave on existing table evolution, specially if theses table already contains some data. 

In case of table schema update, operation can be classified in several categories:

* Modification which can be performed by issuing one or several ALTER TABLE command and which are independent of data layout. For example, changing a comment. These operations are automatically performed.

* Modification which can be performed by issuing one or several ALTER TABLE command, but may introduce a shift between the effective stored data and the new table definition definition. Such operation need to be allowed by setting the `alterable`flag to `yes`. 

> Most if not all ALTER TABLE commands will only modify Hive's metadata, and will not modify data. Users should make sure the actual data layout of the table/partition conforms with the new metadata definition.

* Modification which occurs on table which can be freely dropped without deleting the data. This is the case for example for EXTERNAL tables. In such case, the table is dropped and recreated in case of schema modification. This can be controlled using the `droppable` flag.
* Modification which can't be performed as too complex or there is no corresponding ALTER TABLE command. Such operation should be performed by an external, user defined, script. See below for more information.

### Database migration.

Database migration is a complex subject, as it involve not only modifying the database schema, but also adjusting existing data to comply for the new schema.

In some case, like adding a new column, it could be quite simple. But it is generally more involving. 

Just think of a simple use case: Breaking a `full_name` field (content: i.e. 'Sylvester STALLONE') in two fields: `first_name` ('Sylvester') and `last_name` ('STALLONE'). It is obvious you will need some application specific code to be executed to perform this.
 
This problem has been addressed by some tools in the RDBMS fields. But there is no miracle. These tools are in fact more frameworks which globally act the following way:

* Version database schema
* Request the user to provide a set of migration scripts to transform database version X to version Y
* For each migration, lookup source and target version. And try to find a appropriate sequence of user's migration scripts

Currently, HADeploy do not provide such solution yet. But, under the hood, all HIVE operation are performed by a special tools: [jdchive](https://github.com/BROADSoftware/jdchive). This tool has been designed with this migraton pattern in mind. Check [here](https://github.com/BROADSoftware/jdchive#database-migration)


## Table ownership

As there is no command such as 'ALTER TABLE SET USER...' the database owner will be the account under which the table creation commands was launched during database creation.

This account can be set be the `user`attribute of the [hive_relay](./hive_relay). If not, it will be the `ssh_user` attached to the host used for relaying (`hive_relay.host`).

Once the table is created, there is no way to change this table ownership.

## Example:

```yaml
hive_tables:
- name: testSimple
  database: jdctest1
  comment: "A first, simple test table"
  location: "/tmp/xxx"
  fields:
  - name: fname
    type: string
    comment: "First name"
  - name: lname
    type: string
    comment: "Last name"
- name: testRcFile
  database: jdctest1
  comment: "A RCFILE table"
  fields: [ { name: fname, type: string, comment: 'The first name' }, { name: lname, type: string } ]
  stored_as: RCFILE
```

Will be interpreted, for creation as:

```sql
CREATE  TABLE jdctest1.testSimple ( fname string COMMENT 'First name', lname string COMMENT 'Last name' ) COMMENT 'A first, simple test table' LOCATION 'hdfs://mycluster/tmp/xxx'
CREATE  TABLE jdctest1.testRcFile ( fname string COMMENT 'The first name', lname string ) COMMENT 'A RCFILE table' STORED AS RCFILE
```
And:

```yaml
hive_tables:
- name: testPartitions
  database: jdctest1
  comment: "A table with partitions"
  fields:
  - name: viewTime
    type: INT
  - name: userid
    type: BIGINT
  - name: page_url
    type: STRING
  - name: referrer_url
    type: STRING
  - name: ip
    type: STRING
    comment: "IP Address of the User"
  partitions:
  - name: dt
    type: STRING
  - name: country
    type: STRING
  stored_as: SEQUENCEFILE
  state: present
```

Will be interpreted, for creation as:

```sql
CREATE  TABLE jdctest1.testPartitions ( viewTime INT, userid BIGINT, page_url STRING, referrer_url STRING, ip STRING COMMENT 'IP Address of the User' ) COMMENT 'A table with partitions' PARTITIONED BY ( dt STRING, country STRING ) STORED AS SEQUENCEFILE

```
And:

```yaml
hive_tables:
- name: testSerde
  database: jdctest1
  comment: "Serde test"
  fields:
  - { name: host, type: STRING }
  - { name: identity, type: STRING }
  - { name: theuser, type: STRING }
  serde: "org.apache.hadoop.hive.serde2.RegexSerDe"
  serde_properties:
    input.regex: "([^ ]*) ([^ ]*) ([^ ]*)"
  state: present
  alterable: true
```

Will be interpreted, for creation as:

```sql
CREATE  TABLE jdctest1.testSerde ( host STRING, identity STRING, theuser STRING) COMMENT 'Serde test' ROW FORMAT SERDE 'org.apache.hadoop.hive.serde2.RegexSerDe' WITH SERDEPROPERTIES ( 'input.regex'='([^ ]*) ([^ ]*) ([^ ]*)')
```

### Complex Types example

Here, the field `value` is not a simple scalar one:

```yaml
- name: testComplex
  database: jdctest1
  external: true
  fields:
  - { name: compressed, type: boolean }
  - { name: value, type: "struct<contentType:string, message:string, sender:string, properties: array<struct<key:string,value:int>>, type:string>" }
  - { name: timestamp, type: string }
```

And same example, but expressed differently:

```yaml
- name: testComplex
  database: jdctest1
  external: true
  fields:
  - { name: compressed, type: boolean }
  - name: value
    type: |
      struct<
        contentType:string, 
        message:string, 
        sender:string, 
        properties: array<
          struct<
            key:string,
            value:int
          >
        >, 
        type:string
      >
  - { name: timestamp, type: string }
```

### Apache Ranger example

Following is an illustration of Apache Ranger policy association: The table is created with select and update permissions for all users of the 'users' group. And user 'sa' can also create new indexes.

```yaml
hive_tables:
- name: testranger
  database: jdctest1
  comment: "A first, simple test table"
  location: "/tmp/xxx"
  fields:
  - name: fname
    type: string
    comment: "First name"
  - name: lname
    type: string
    comment: "Last name"
  ranger_policy:
    permissions:
    - groups:
      - users
      accesses: 
      - select
      - update
    - users:
      - sa
      accesses:
      - index
```




## HBase table mapping

A frequent use case is the mapping of HBase table by HIVE, to ease querying. This can be achieved using HADeploy. 

### Example:

Provided the following HBase table definition:

```yaml
hbase_namespaces:
- name: test2

hbase_tables:
  - name: test2a
    namespace: test2
    column_families:
    - name: id
    - name: job
```
(Refer to [hbase_namespaces](../hbase/hbase_namespaces) and [hbase_tables](../hbase/hbase_tables) for more informations

One can easely map an external HIVE table: 

```yaml
hive_tables
- name: testHBase
  database: jdctest1
  fields:
  - { name: rowkey, type: string, comment: "The row key" }
  - { name: number, type: int }
  - { name: prefix, type: string }
  - { name: fname, type: string }
  - { name: lname, type: string }
  - { name: company, type: string }
  - { name: title, type: string }
  external: true
  storage_handler: "org.apache.hadoop.hive.hbase.HBaseStorageHandler"
  properties:
    hbase.table.name: "test2:test2a"
  serde_properties:
    hbase.columns.mapping: ":key,id:reg,id:prefix,id:fname,id:lname,job:cpny,job:title"
  state: present
```

Will be interpreted, for creation as:

```sql
CREATE EXTERNAL TABLE jdctest1.testHBase ( rowkey string COMMENT 'The row key', number int, prefix string, fname string, lname string, company string, title string ) STORED BY 'org.apache.hadoop.hive.hbase.HBaseStorageHandler' WITH SERDEPROPERTIES ( 'hbase.columns.mapping'=':key,id:reg,id:prefix,id:fname,id:lname,job:cpny,job:title') TBLPROPERTIES ( 'hbase.table.name'='test2:test2a')
```

