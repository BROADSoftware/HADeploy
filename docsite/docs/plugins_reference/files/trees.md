# trees

## Synopsis

Provide a list of trees to be deployed on the cluster. 

A tree is a folder with all its content. It will be recursively copied from the source to the target (Defined by the scope).

Target folder and all subfolder will be created with provided owner, group and folder_mode.

## Attributes

Each item of the list has the following attributes:

Name | req?	| Description
--- | --- | ---
src|yes|Source folder. May be in the form:<ul><li>`file://...` for fetching the folder content locally, from one of the folder provided by the [`local_files_folders:`](./local_files_folders) list</li><li>`file:///...` for fetching the folder content locally, with an absolute path on the HADeploy node.</li><li>`tmpl://...`  Source is a folder containing template files, which will be processed by Ansible/Jinja2 mechanism. Template files will be fetched locally, from one of the folders provided by the [`local_templates_folders:`](./local_templates_folders) list</li><li>`tmpl:///...` Same as above, except source template folder will be fetched from the HADeploy node with an absolute path.</li><li>`<node>:///...` This mode is only relevant when scope is `hdfs`. It allows grabbing a folder from one node of the cluster and pushes it to HDFS. Path must be absolute.</li></ul>
scope|yes|On which target does this file be deployed? May be:<ul><li>A single `host` name</li><li>A single `host_group` name</li><li>Several `hosts` or `host_groups`, separated by the character ':'</li><li>the `hdfs` token</li></ul>
dest_folder|yes|Target folder. Will be created on deployment if not existing. Must be an absolute path<br>WARNING: this folder will be deleted with all its content in REMOVE mode.
owner|yes|The owner of all the target files
group|yes|The group of all the target files
file_mode|yes|The permission of all the target files. Must be an octal representation embedded in a string (ie: "0644")
folder_mode|yes|The permission of all the target folders. Must be an octal representation embedded in a string (ie: "0755")
no_remove|no|Boolean: Prevent this folder to be removed from the target when HADeploy will be used in REMOVE mode.<br>Default: `no`
ranger_policy|no|Definition of Apache Ranger policy bound to this tree. Parameters are same as [`hdfs_ranger_policies`](../ranger/hdfs_ranger_policies) excepts than `paths` should not be defined as is automatically set to the folder path. Scope must be `hdfs`.<br>The policy name can be explicitly defined. Otherwise, a name will be generated as `"_<dest_folder>_"`.<br>See example below for more information.

> src: must reference a folder. To copy a single file, use the files definition.

## Example
```yaml
trees:
- scope: hdfs
  src: "file://data"
  dest_folder: "/apps/broadapp/init_data"
  owner: broadapp
  group: broadgroup
  file_mode: "0644"
  folder_mode: "0755"
 
- scope: hdfs
  src: "file://mytree"
  dest_folder: "/apps/broadapp/thetree"
  file_mode: "0000"
  folder_mode: "0000"
  ranger_policy:
    audit: no
    permissions:
    - users:
      - broadapp
      accesses:
      - read
      - write
      - execute
    - groups:
      - broadgroup
      accesses:
      - read
      - execute
```
  

