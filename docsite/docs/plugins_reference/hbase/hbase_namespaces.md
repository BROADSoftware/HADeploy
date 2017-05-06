# hbase_namespaces

## Synopsis

Provide a list of HBase namespaces required by the application. They will be created (or destroyed) by HADeploy, except if managed flag is set to no.

## Attributes

Each item of the list has the following attributes:

Name | req? | Default |	Description
--- | --- | --- | ---
name|yes||The name of the HBase namespace. 
no_remove|no|no|Boolean: Prevent this namespace to be removed when HADeploy will be used in REMOVE mode.
managed|no|yes|If no, this namespace is not handled by HADeploy. It will not be created nor deleted. But HADeploy can create and delete tables in this namespace.
ranger_policy|no||Definition of Apache Ranger policy bound to this namespace. Parameters are same as [hbase_ranger_policy](../ranger/hbase_ranger_policies) except than `tables`, `columns_families` and `columns` should not be defined. The policy will apply on all column families and all columns of all tables in this namespace.<br>The policy name can be explicitly defined. Otherwise, a name will be generated as "`_<namespace>_`".<br>See example below for more information

## Example
```yaml
hbase_namespaces:
- name: broadns
```
If you want to use the 'default' namespace for some of your table, you may declare it.
```yaml
hbase_namespaces:
- name: broadns

- name: default
  no_remove: True
  managed: no
``` 
In this case, you need to set no_remove: True, as the default namespace can't of course be removed. Otherwise, an error will be generated. And, of course managed: False.

Note this is optional, as HADeploy internally create such definition for all namespace used but not declared.

An example with a bound [Apache Ranger policy](../ranger/hbase_ranger_policies):
```yaml
hbase_namespaces:
- name: broadns
  ranger_policy:
    permissions:
    - groups:
      - users
      accesses:
      - read
    - groups:
      - hbadmin
      accesses:
      - read
      - write
      - create
      - admin
```
 
