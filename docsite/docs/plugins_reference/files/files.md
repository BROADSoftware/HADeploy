# files

## Synopsis

Provide a list of files to be deployed on the cluster.

## Attributes

Each item of the list has the following attributes:

Name | req? | 	Description
--- | ---  | ---
src|yes|Source file. May be in the form:<ul><li>`http://...` for fetching the file from a remote http server</li><li>`https://...` for fetching the file from a remote https server</li><li>`file://...` for fetching the file locally, from one of the folder provided by the [`local_files_folders:`](./local_files_folders) list</li><li>`file:///...` for fetching the file locally, with a absolute path on the HADeploy node.</li><li>`tmpl://...`  Source is a template, which will be processed by Ansible/Jinja2 mechanism. Template will be fetched locally, from one of the folders provided by the [`local_templates_folders:`](./local_templates_folders) list</li><li>`tmpl:///...` Same as above, except source template will be fetched from the HADeploy node with an absolute path.</li><li>`<node>:///...` This mode is only relevant when scope is hdfs. It allows grabbing a file from one node of the cluster and pushes it to HDFS. Useful when, for example, some application require configuration files from client nodes to be pushed on HDFS. Path must be absolute.</li></ul>Note that in this last case, if kerberos is enabled on the cluster, one must provide credential for the operation to be successful. See [`source_host_credentials`](../hdfs/source_host_credentials) definition is this reference part.
scope|yes|On which target does this file be deployed? May be:<ul><li>A single `host` name</li><li>A single `host_group` name</li><li>Several `hosts` or `host_groups`, separated by the character ':'</li><li>the `hdfs` token</li></ul>
dest_folder|yes|Target folder. Must exists
dest_name|no|The target file name.<br>Default: The basename of src
owner|yes|The owner of the file
group|yes|The group of the file
mode|yes|The permission of the file. Must be an octal representation embedded in a string (ie: "0755").
validate_certs|no|Boolean; In case of `src: https://...` Setting to false, will disable strict certificate checking, thus allowing self-signed certificate.<br>Default: `yes`
force_basic_auth|no|Boolean; In case of `src: http://...` or `src: https://...`. The underlying module only sends authentication information when a webservice responds to an initial request with a 401 status. Since some basic auth services do not properly send a 401, logins will fail. This option forces the sending of the Basic authentication header upon initial request.
url_username|no|String; In case of `src: http://...` or `src: https://...`. The username for use in HTTP basic authentication. This parameter can be used without url_password for sites that allow empty passwords.
url_password|no|String; In case of `src: http://...` or `src: https://...`. The password for use in HTTP basic authentication
no_remove|no|Boolean: Prevent this file to be removed when HADeploy will be used in REMOVE mode.<br>Default: `no`
ranger_policy|no|Definition of Apache Ranger policy bound to this file. <br>Parameters are same as [`hdfs_ranger_policies`](../ranger/hdfs_ranger_policies) items, excepts than paths should not be defined as automatically set to the file path, and the policy is not recursive by default.<br>Scope must be hdfs.<br>The policy name can be explicitly defined. Otherwise, a name will be generated as `"_<targetPath>_"`.<br>See example below for more information.

> NB: `src:` must not reference a folder. To create a folder, use the `folders` definition and to copy a folder content, use the `trees` definition.

## Example

```yaml
files:
- src: https://my.repository.server/repo/myapp/myapp-0.2.2.jar
  scope: egde_nodes
  dest_folder: /opt/myapp
  owner: root
  group: root
  mode: "0644"
  validate_certs: no

- scope: hdfs
  src: "tmpl://pixo.cfg.j2" 
  dest_folder: "/apps/pixo/conf"
  dest_name: "pico.cfg"
  mode: "0000"
  ranger_policy:
    permissions:
    - users:
      - pixo
      accesses:
      - read
      - write
```

