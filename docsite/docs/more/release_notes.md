# Release notes

## 0.3.1

- Some quotes was missing in plugin yaml files. Triggered errors when a HADeploy variable was substitued with a string begining with a {{some_ansible_variable}}
- `hdfs_relay.cache_folder` default value is modified, to be in the user home folder.
- `hbase_relay.tools_folder` default value is modified to be in `/tmp/hadeploy_{{ansible_ssh_user}}`
- `hive_relay.tools_folder` default value is modified to be in `/tmp/hadeploy_{{ansible_ssh_user}}`
- `kafka_relay.tools_folder` default value is modified to be in `/tmp/hadeploy_{{ansible_ssh_user}}`
- Local file definition now works with ~/xxx


