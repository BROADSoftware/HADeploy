# Release notes

## 0.5.0

- Plugins architecture refactoring
- New plugin: `ansible`, to insert raw Ansible playbook or role in the deployment.
- scope value are now checked.
- Every string value can now be encrypted.

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

