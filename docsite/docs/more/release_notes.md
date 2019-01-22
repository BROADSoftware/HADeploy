# Release notes

## 0.6.1

 - In addition to login/password, Ranger authentication can now be performed through Kerberos.

## 0.6.0

- /var/run/supervisor_xxxx folder was sometime deleted (i.e. after a hard restart). Now automatically recreated
- Yarn service failed when existing job list was empty. Fixed
- Improving documentation on Yarn services integration with Kerberos.
- Added handling of secured access to elasticsearch cluster (Authentication and SSL).

#### INCOMPATIBILITY

- [kafka_relay](../plugins_reference/kafka/kafka_relay) has a new mandatory parameter: `kafka_version`. 
- Due to change in the Kerberos handling of the Kafka plugin, `principal` and `xxx_keytab_path` parameters has been removed from the [kafka_relay](../plugins_reference/kafka/kafka_relay) definition.

## 0.5.7

- Fixed this [DEPRECATION WARNING]: Using tests as filters is deprecated. Instead of using `result|succeeded` instead use `result is succeeded`
- `--action dumpvars` now display the file where the variable is defined.

## 0.5.6

- **Added a [Yarn plugin](../plugins_reference/yarn/yarn_overview) to handle Yarn services (long running jobs) lifecycle.**
- Storm topologies ACTIVE status is now displayed in upper case, for better visibility.
- HDFS plugin: `hadoop_conf_dir` and `webhdfs_endpoint` was not propagated on all HDFS commands. Fixed.
- Users plugin: When a user is not managed and an authorized_keys is to be set, HADeploy ensure home folder is accessible by performing an `su` command. 

## 0.5.5

- **Added Elasticsearch [indices](../plugins_reference/elastic/elasticsearch_indices) and [Templates](../plugins_reference/elastic/elasticsearch_templates) management.**
- Scope for Storm's notification handler was erroneous. Fixed
- Now allow missing both `ssh_private_key_file` and `ssh_password` in host definition. (As already stated in the doc)
- Notification system generated some errors when scope was limited to `files`. Fixed by suppressing notification in such case.
- Modification of [grooming order](./execution_order/) for `Storm`, `Systemd` and `Supervisor` plugins. Now grooming occurs before `files`, to handle notifications correctly.
- [ansible_inventories](../plugins_reference/ansible_inventories/ansible_inventories/) is now compatible with `ansible_user/host/...` variables (Formerly `ansible_ssh_user/host/...`).
- Refactoring of [supervisors](../plugins_reference/supervisor/supervisors/) plugin to have one configuration file per program and group (Instead of a single file for all).
- Added a `scope` attribute to [supervisor_programs](../plugins_reference/supervisor/supervisor_programs/) items. 
- Action `remove` on [Storm plugin](../plugins_reference/storm/storm_overview) now kill all running topologies.

## 0.5.4

- **Added an action `dumpvars`, to dump all variables.**
- With Ranger 0.7, there was unjustified 'changed' on policies settings. Fixed
- **Added a [Storm plugin](../plugins_reference/storm/storm_overview) to handle Storm topologies lifecycle.**
- **Added [Storm Ranger policies](../plugins_reference/ranger/storm_ranger_policies) management.**
- **Action `status` as been implemented in [Storm](../plugins_reference/storm/storm_overview#actions-stopstart-and-status), 
[Systemd](../plugins_reference/systemd/systemd_units#actions-stop-start-and-status) and [Supervisor](../plugins_reference/supervisor/supervisor_overview#actions-stop-start-and-status) plugins.**

#### INCOMPATIBILITY

- Notification syntax has been modified for [`files`](../plugins_reference/files/files) definition.

## 0.5.3

- In some cases, using include directive disrupted some relative file relocation. Fixed
- An [alternate variable notation](../plugins_reference/core/vars/#alternate-notation) (`<<...>>`) has been introduced to allow non-string variable in flow style notation.
- **[Conditional deployment](./conditional_deployment) was implemented in all plugins.**
- A switch `no_log` has been added to [`ranger_relay`](../plugins_reference/ranger/ranger_relay) to ease debugging.

## 0.5.2

- A change in the API of Ansible 2.4 broke `ansible_inventory` plugin. Fixed.

## 0.5.1

- Added almost all existing Ansible configuration variables for `hosts` and `host_override` in inventory.
- Added maven artifact download, using ['maven_repositories`](../plugins_reference/files/maven_repositories) definition.
- Changed all references to ansible variable `ansible_ssh_user` to `ansible_user` (Following Ansible evolution).
- Some (small) documentation improvements.
- Added `priority` attribute on [`host_overrides`](../plugins_reference/inventory/host_overrides)
- Added `systemd` plugin with [`systemd_units`](../plugins_reference/systemd/systemd_units) service management.
- Added `supervisor` plugin with [`supervisor`](../plugins_reference/supervisor/supervisor_overview) process controler management.

## 0.5.0

- Plugins architecture refactoring
- New plugin: [`ansible`](../plugins_reference/ansible/ansible_overview), to insert raw Ansible playbook or role in the deployment.
- scope value are now checked.
- Added an [`encrypted_vars`](../plugins_reference/core/encrypted_vars) block to have a more generic encryption capability.

#### INCOMPATIBILITY

- The `ranger_relay.admin_password` encrypted with 0.4.0 method must be modified to comply to new, generic syntax.

## 0.4.1

- Added [scope limitation](./altering_scope) mechanism on performed operation
- Default HDFS relay cache is now /tmp/hadeploy_{{ansible_ssh_user}}/files
- Added `remote_tmp = /tmp/.ansible-${USER}/tmp` in generated ansible.cfg

## 0.4.0

- Some quotes was missing in plugin yaml files. This generated errors when a HADeploy variable was substituted with a string begining with {{some_ansible_variable}}. Fixed
- `hdfs_relay.cache_folder` default value is modified, to be in the user home folder.
- `hbase_relay.tools_folder` default value is modified to be in `/tmp/hadeploy_{{ansible_ssh_user}}`
- `hive_relay.tools_folder` default value is modified to be in `/tmp/hadeploy_{{ansible_ssh_user}}`
- `kafka_relay.tools_folder` default value is modified to be in `/tmp/hadeploy_{{ansible_ssh_user}}`
- Local file definition now works with ~/xxx
- `hdfs_relay.user` default value is now `hdfs` only if `ssh_user`is root. Otherwise, is `ssh_user`
- Added global [`exit_on_fail`](../plugins_reference/inventory/exit_on_fail) flag.
- Added some retry on user/groups creation/removal
- Added `become_user/become_method` on `hbase_relay`
- Added `become_user/become_method` on `kafka_relay`
- Added `hbase_relay.local_keytab_path`
- Added `kafka_relay.local_keytab_path`
- Added `hdfs_relay.local_keytab_path`
- Added `source_host_credential.local_keytab_path`
- Added `groups` in `host_groups`
- Previous version was unable to fetch an existing Ansible inventory when it contains some encrypted file(s). 
The Description of Ansible inventory has been modified (now `ansible_inventories`) to include a password file or user password request.
- Added a method to encrypt password in `ranger_relay.admin_password`.   

#### DEPRECATION

`ansible_inventory_files` has been marked deprecated. Replaced by `ansible_inventories`.

#### INCOMPATIBILITY

There is some incompatible change with previous version. You may need to modify your source files:

* `hive_relay.user` is renamed `hive_relay.become_user`.
* `hbase_relay.keytab_path`is renamed `hbase_relay.relay_keytab_path`
* `kafka_relay.keytab_path`is renamed `kafka_relay.relay_keytab_path`
* `hdfs_relay.keytab_path`is renamed `hdfs_relay.relay_keytab_path`
* `source_host_credential.keytab_path`is renamed `source_host_credential.relay_keytab_path`
* For `files` and `trees`, `<node>:///` is replaced by `node://<node>/...` notation

