# Release notes

## 0.4.0

- Some quotes was missing in plugin yaml files. This generated errors when a HADeploy variable was substitued with a string begining with {{some_ansible_variable}}. Fixed
- `hdfs_relay.cache_folder` default value is modified, to be in the user home folder.
- `hbase_relay.tools_folder` default value is modified to be in `/tmp/hadeploy_{{ansible_ssh_user}}`
- `hive_relay.tools_folder` default value is modified to be in `/tmp/hadeploy_{{ansible_ssh_user}}`
- `kafka_relay.tools_folder` default value is modified to be in `/tmp/hadeploy_{{ansible_ssh_user}}`
- Local file definition now works with ~/xxx
- `hdfs_relay.user` default value is now `hdfs` only if `ssh_user`is root. Otherwise, is `ssh_user`
- Added global `exit_on_fail` flag.
- Added some retry on user/groups creation/removal
- Added `become_user/become_method` on `hbase_relay`
- Added `become_user/become_method` on `kafka_relay`
- Added `hbase_relay.local_keytab_path`
- Added `kafka_relay.local_keytab_path`
- Added `hdfs_relay.local_keytab_path`
- Added `source_host_credential.local_keytab_path`
- Added `groups` in `host_groups`

#### INCOMPATIBILITY

There is some incompatible change with previous version. You may need to modify your source files:

* `hive_relay.user` is renamed `hive_relay.become_user`.
* `hbase_relay.keytab_path`is renamed `hbase_relay.relay_keytab_path`
* `kafka_relay.keytab_path`is renamed `kafka_relay.relay_keytab_path`
* `hdfs_relay.keytab_path`is renamed `hdfs_relay.relay_keytab_path`
* `source_host_credential.keytab_path`is renamed `source_host_credential.relay_keytab_path`
* For `files` and `trees`, `<node>:///` is replaced by `node://<node>/...` notation

