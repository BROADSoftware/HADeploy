# Release notes

## 0.3.1

- Some quotes was missing in plugin yaml files. This generated errors when a HADeploy variable was substitued with a string begining with {{some_ansible_variable}}. Fixed
- `hdfs_relay.cache_folder` default value is modified, to be in the user home folder.
- `hbase_relay.tools_folder` default value is modified to be in `/tmp/hadeploy_{{ansible_ssh_user}}`
- `hive_relay.tools_folder` default value is modified to be in `/tmp/hadeploy_{{ansible_ssh_user}}`
- `kafka_relay.tools_folder` default value is modified to be in `/tmp/hadeploy_{{ansible_ssh_user}}`
- Local file definition now works with ~/xxx
- `hdfs_relay.user` default value is now `hdfs` only if `ssh_user`is root. Otherwise, is `ssh_user`
- Added global `exit_on_fail` flag.
- Added some retry on user/groups creation/removal
- INCOMPATIBILIY: `hive_relay.user` is renamed `hive_relay.become_user`.
- Added `become_user/become_method` on `hbase_relay`



