# folders

## Synopsis

Provided a list of folders to be created and configured on the target infrastructure

## Attributes

Each item of the list has the following attributes:

Name | req?	| 	Description
--- | --- | ---
path|yes|The path of the folder to create
scope|yes|On which target does this folder be create? May be:<ul><li>A single `host` name</li><li>A single `host_group` name</li><li>Several `hosts` or `host_groups`, separated by the character ':'</li><li>the `hdfs` token.</li></ul>
owner|yes|The owner of the file
group|yes|The group of the file
mode|yes|The permission of the file. Must be an octal representation embedded in a string (ie: "0755")
no_remove|no|Boolean: Prevent this folder to be removed when HADeploy will be used in REMOVE mode.<br>Default: `no`
ranger_policy|no|Definition of Apache Ranger policy bound to this folder. Parameters are same as [`hdfs_ranger_policies`](../ranger/hdfs_ranger_policies) excepts than `paths` should not be defined as is automatically set to the folder path. Scope must be hdfs.<br>The policy name can be explicitly defined. Otherwise, a name will be generated as "`_<path>_`".<br>See example below for more information|
when|no|Boolean. Allow [conditional deployment](../../more/conditional_deployment) of this item.<br>Default `True` 

# Example
```yaml
folders:
- path: /var/log/myapp
  scope: all
  owner: myapp
  group: myapp
  model: "0755"

- path: /apps/myapp
  scope: hdfs
  owner: myapp
  group: myapp
  model: "0755"
  ranger_policy:
  permissions:
  - groups:
    - group1
    accesses:
    - read
    - execute
```  

