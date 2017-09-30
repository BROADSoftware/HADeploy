# Next step

We will describe here the deployment of a simple application, 'broadapp', which will need to deploy some artifacts and resources on a Hadoop cluster, both on nodes and on HDFS.

We will not deeply enter in the detail of all items. You will find more exhaustive description in the Reference part of this document.

> <sub>NOTE: This sample is intended to demonstrate the basic features of HADeploy. It is not intended to define 'Best Practices' about Hadoop Application deployment.</sub>

This example will be divided in two parts: One describing the target Hadoop cluster (Infrastructure description) and a second one the application deployment itself (Application description) 

## Infrastructure description 

There is two methods to provide HADeploy with the target infrastructure description. One is to explicitly list all hosts. Another one is to refer to an already existing Ansible Inventory.

Let's start with the first one: 

### Explicit description

The infrastructure is described in a file with the following content:

```yaml
# ------------------------------------- Infrastructure part

hosts:
# A first host expressed the standard yaml style
- name: sr
  ssh_host: sr.cluster1.mydomain.com
  ssh_user: root
  ssh_private_key_file: "keys/build_key" 
# And these others using more consise yaml 'flow style'
- { name: en1, ssh_host: en.cluster1.mydomain.com, ssh_user: root, ssh_private_key_file: "keys/build_key" }
- { name: nn1, ssh_host: nn1.cluster1.mydomain.com, ssh_user: root, ssh_private_key_file: "keys/build_key" }
- { name: nn2, ssh_host: nn2.cluster1.mydomain.com, ssh_user: root, ssh_private_key_file: "keys/build_key" }
- { name: dn1, ssh_host: dn1.cluster1.mydomain.com, ssh_user: root, ssh_private_key_file: "keys/build_key" }
- { name: dn2, ssh_host: dn2.cluster1.mydomain.com, ssh_user: root, ssh_private_key_file: "keys/build_key" }
- { name: dn3, ssh_host: dn3.cluster1.mydomain.com, ssh_user: root, ssh_private_key_file: "keys/build_key" }

host_groups:
- name: data_nodes
  hosts:	# This host list in standart YAML style
  - dn1
  - dn2
  - dn3
- name: control_nodes
  hosts: [ "sr", "en", "nn1", "nn2" ]	# And these in YAML 'flow style'
- name: zookeepers
  hosts: [ "sr", "nn1", "nn2" ]

hdfs_relay:
  host: en1

kafka_relay:
  host: br1
  zookeeper:
    host_group: zookeepers

hbase_relay:
  host: en1
```

First, we will describe the several hosts our cluster is made of. Each host as a name: entry, by which we will reference it, and others entries describing how to access it through ssh.

The specified `ssh_user:` is typically `root`, as it must be a user with enough rights to perform all the required actions.

Then we will find a block of [`host_groups`](/plugins_reference/inventory/host_groups): description. This will simply allow grouping hosts by function, and easing hosts's reference.

Then is the definition of the [`hdfs_relay`](/plugins_reference/hdfs/hdfs_relay): specifying which host will support all HDFS related operations.

Then is the definition of the [`kafka_relay`](/plugins_reference/kafka/kafka_relay): which will be relaying all topics creation, modification and removal operations. As such it need to know how to access zookeeper and to be able to access Kafka library folder as it use corresponding jar files. The simplest solution is to use a broker node for this task.

And last is the definition of [`hbase_relay`](/plugins_reference/hbase/hbase_relay): which will be relaying all HBase table creation, modification and removal operation. 

### From an existing Ansible inventory.

Those familiar to Ansible should have noted such description is very similar to the way Ansible describe its inventory.

If the target cluster is already described in an Ansible inventory file, then one may simple reference it instead of duplicate information.

In such case, the infrastructure part of the file will look like:

```yaml
# ------------------------------------- Infrastructure part

ansible_inventories:
- file: ".../some-ansible-build/inventory"

host_groups:
- name: control_nodes
  hosts: [ "sr1", "en1", "en2", "nn1", "nn2" ]
- name: zookeepers
  hosts: [ "sr1", "nn1", "nn2" ]

hdfs_relay:
  host: en1

kafka_relay:
  host: br1
  zookeeper:
    host_group: zookeepers

hbase_relay:
  host: en1
```
In our case, we add some [`host_groups`](/plugins_reference/inventory/host_groups) as we need them for the following, and there were not defined in the source Ansible inventory

Note we also have the ability to modify only some attributes of one, several or all hosts of this Ansible inventory. See [`host_overrides`](/plugins_reference/inventory/host_overrides) in the reference part.

## Application description

Here is the file describing the application deployment:

```yaml
# ------------------------------------ Environment part
# Except if begining with /, All path are relative to this file
local_files_folders:
- "./files"

local_templates_folders:
- "./templates"

# ------------------------------------- Application part

vars:
  app_version: "0.1.1"
  repository_server: "myserver.com"
  app_jar_url: "http://${repository_server}/repo/broadapp-${app_version}.jar"
  zookeeper:
    connection_timeout: 60000
    zkpath: /broadapp


groups:
  - scope: all
    name: broadgroup

users:
- login: broadapp
  comment: "Broadapp technical account"
  groups: "broadgroup"

- { login: broaduser, scope: control_nodes, comment: "Broadapp user account", groups: "broadgroup", can_sudo_to: "hdfs, yarn" }

folders:
- { scope: "en1:data_nodes", path: /var/log/broadapp, owner: broadapp, group: broadgroup, mode: "0755" }
- { scope: en1, path: /etc/broadapp, owner: root, group: root, mode: "0755" }
- { scope: en1, path: /opt/broadapp, owner: root, group: root, mode: "0755" }

- { scope: hdfs, path: /apps/broadapp, owner: broadapp, group: broadgroup, mode: "0755" }

files:
- { scope: en1, src: "${app_jar_url}", dest_folder: "/opt/broadapp",  owner: root, group: root, mode: "0644", validate_certs: no }
- { scope: en1, src: "tmpl://broadapp.cfg.j2", dest_folder: /etc/broadapp, dest_name: broadapp.cfg, owner: root, group: root, mode: "0644" }

- { scope: hdfs, src: "${app_jar_url}", dest_folder: "/apps/broadapp", dest_name: broadapp.jar, owner: broadapp, group: broadgroup, mode: "0644", validate_certs: no }

trees:
- { scope: hdfs, src: "file://data", dest_folder: "/apps/broadapp/init_data", owner: broadapp, group: broadgroup, file_mode: "0644", folder_mode: "0755" }
    

kafka_topics:
- name: broadapp_t1
  partition_factor: 3
  replication_factor: 2
  properties:
    retention.ms: 630720000000
    retention.bytes: 858993459200

hbase_namespaces:
- name: broadgroup

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

Let's describe it part by part:

### Environment part

```yaml
# ------------------------------------ Environment part
# Except if begining with /, All path are relative to this file
local_files_folders:
- "./files"

local_templates_folders:
- "./templates"
```

This part describes the local environment, from where to find the files, which will be pushed on the target clusters.

Also allow defining a template folder, where all the template source files will be stored (Templating is a powerful mechanism for defining configuration files. HADeploy use Ansible template subsystem, based on Jinja2).

### Vars
```yaml
vars:
  app_version: "0.1.1"
  repository_server: "myserver.com"
  app_jar_url: "http://${repository_server}/repo/broadapp-${app_version}.jar"
  zookeeper:
    connection_timeout: 60000
    zkpath: /broadapp
```
HADeploy allow you to defined variable which then will be substituted by surrounding the variable name with  "${ "and "}"

And, as demonstrated by the `app_jar_url:` entry, variable value can themself include other variable.

Note also than variable can be a scalar (String, int, etc...) but also a map.

There is also a method to provide variable definition on the command line when launching HADeploy. See [Launching HADeploy](#launching-hadeploy) below.

### Groups

This block allows definition of Linux groups.

```yaml
groups:
  - scope: all
    name: broadgroup
```
Here we create a Linux local group named broadgroup on all hosts of the clusters.

Some of the items of HADeploy definition file have a `scope:` attribute, which defines the target on which action will be performed. Such attribute may be optional and may have `all` as default value. So, the following is equivalent:

```yaml
groups:
  - name: broadgroup
```

### Users

This block will allow us to define Linux account required by the application.
```yaml
users:
- login: broadapp
  comment: "Broadapp technical account"
  groups: "broadgroup"

- { login: broaduser, scope: control_nodes, comment: "Broadapp user account", groups: "broadgroup",
      can_sudo_to: "hdfs, yarn" }
```

Each entry will support most of the usual user's configuration parameters. See [`users`](/plugins_reference/users/users) in the Reference part.

As for groups, we can define on which hosts users will be created using the `scope:` attribute.

### Folders

This block allow us to define the directory used by the application, with all associated permissions

```yaml
folders:
- { scope: en1, path: /etc/broadapp, owner: root, group: root, mode: "0755" }
- { scope: en1, path: /opt/broadapp, owner: root, group: root, mode: "0755" }
- { scope: "en1:data_nodes", path: /var/log/broadapp, owner: broadapp, group: broadgroup, mode: "0755" }

- { scope: hdfs, path: /apps/broadapp, owner: broadapp, group: broadgroup, mode: "0755" }
```

Note again the `scope:` attribute; with allow specifying where the directory will be created:

For a single node of name en1:
```yaml
scope: en1
```

For the same en node, plus all hosts belonging to the `data_nodes` group:

```yaml
scope: en1:data_nodes
```

Here the folder will not be create on one or several hosts, but on the HDFS file system:

```yaml
scope: hdfs
```

### Files

Then the following block will set the application file in place, also with permission.

```yaml
files:
- { scope: en1, src: "${app_jar_url}", dest_folder: "/opt/broadapp",  owner: root, group: root, mode: "0644", validate_certs: no }
- { scope: en1, src: "tmpl://broadapp.cfg.j2", dest_folder: /etc/broadapp, dest_name: broadapp.cfg, owner: root, group: root, mode: "0644" }

- { scope: hdfs, src: "${app_jar_url}", dest_folder: "/apps/broadapp", dest_name: broadapp.jar, owner: broadapp, group: broadgroup, mode: "0644", validate_certs: no }
```

Here again, the `scope:` attribute indicates where to store the file. And the `src:` attribute is an URI, providing a choice of sources. More on that in the reference part.

Note also variable are surrounded by quotes. This is required when using 'flow style', otherwise the opening '{' will be confused when the start of map delimiter.

### Trees

HADeploy also provide ability to copy recursively a folder with all its content.

The following definition will copy all the content of the data folder on HDFS, under the path `/apps/broadapp/init_data`.

All copied files ownership and permission will be adjusted with the provided values. Also, inner subfolder will be created if any, and ownership and permission also adjusted.

```yaml
trees:
- { scope: hdfs, src: "file://data", dest_folder: "/apps/broadapp/init_data", owner: broadapp, group: broadgroup, file_mode: "0644", folder_mode: "0755" }
```

### kafka_topics
This block define a Kafka topic which would be required by the application:

```yaml   
kafka_topics:
- name: broadapp_t1
  partition_factor: 3
  replication_factor: 2
  properties:
    retention.ms: 630720000000
    retention.bytes: 858993459200
```

You will find here typical parameters of a Kafka topic: name, partition and replication factor, and a set of properties.

### Hbase namespaces and tables

```yaml
hbase_namespaces:
- name: broadgroup

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

This block defines one namespace broadgroup and a HBase table named broadapp_t1 in it, with specifics properties and one column family.

## Templates

Note in the `files:` part of this sample the second file with `src:` attribute: `tmpl://broadapp.cfg.j2`.

```yaml
files:
...
- { scope: en1, src: "tmpl://broadapp.cfg.j2", dest_folder: /etc/broadapp, dest_name: broadapp.cfg, owner: root, group: root, mode: "0644" }
```

The tmpl scheme stands for 'template'. And the corresponding source template will be fetched from one of the folders defined by the `local_templates_folders` list described previously.

Now, let's dig inside this file. Here is what it could look like:

**Broadapp Config file:**

```
zookeeper.connect={% for host in groups['zookeepers'] %}{% if not loop.first %},{% endif %}{{  hostvars[host]['ansible_fqdn'] }}:2181{% endfor %}${zookeeper.zkpath}

zookeeper.connection.timeout.ms={{ zookeeper.connection_timeout }}
```

Here we see how we can refer to the `zookeeper.connection_timeout` variable we defined in a previous `vars:` block.

The `zookeeper.connect` value is a bit more complex. It is a typical Ansible pattern used to build a zookeeper quorum value. 

Important point to note is, in a template, we have access to both variable defined in the HADeploy definition file and to all the variables grabbed by Ansible from remote hosts (Called Facts in Ansible terminology).

## Project layout

HADeploy project layout may be simple. For examples, in our case, it could be:
```
app.yml
files/
infra/cluster1.yml
keys/build_key
templates/broadapp.cfg.j2
```

Note the file folder is empty, as we fetch our binary resources from a repository server. We could also define a self-contained project as the following:
```
app.yml
files/broadapp-0.1.1.jar
infra/cluster1.yml
keys/build_key
templates/broadapp.cfg.j2
```

Then, the `app_jar_url` should be set to
```yaml
vars:
  app_jar_url: "file://broadapp-${app_version}.jar"
```

## Launching HADeploy

Let's assume we have [installed HADeploy](/installation) and have arranged to have the `....../hadeploy/bin` folder in our PATH (See Installation above), and we are in our project directory.
 
To launch the deployment, just type:

```bash
hadeploy --src app.yml --src infra/cluster1.yml --action deploy
```

And to perform the reverse action (Fully remove all application from target cluster):

```bash
hadeploy --src app.yml --src infra/cluster1.yml --action remove
```

HADeploy command line also allow direct variable definition, with the form --var name=value. For example:

```bash
hadeploy --var app_version=0.1.2 --src app.yml --src infra/cluster1.yml --action deploy
```

Note in this case, the value will be overwritten by the one provided in app.yml. So you will have to remove from the definition file a variable you intend to specify on the command line.

The general rule is than variable definitions are evaluated/overridden in order of which they appears. So the order of --var and --src on the command line is significant.

Some other option of the HADeploy command are described in other chapters:

* `--workingFolder`: Refer to [`Under_the_hood`](/more/under_the_hood) chapter.

* `--askVaultPassword` and `--vaultPasswordFile`: Refer to [Encrypted variables](/plugins_reference/core/encrypted_vars)

* `--scope` and `--noScope`: Refer to [Altering scope](/more/altering_scope)
