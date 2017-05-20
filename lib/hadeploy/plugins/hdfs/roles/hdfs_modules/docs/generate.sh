
ansible-doc -M ../library/ hdfs_cmd 2>/dev/null | sed 's/[(].*hdfs_modules[/]library.*[)]//' >hdfs_cmd.txt
ansible-doc -M ../library/ hdfs_file 2>/dev/null | sed 's/[(].*hdfs_modules[/]library.*[)]//' >hdfs_file.txt
ansible-doc -M ../library/ hdfs_info 2>/dev/null | sed 's/[(].*hdfs_modules[/]library.*[)]//' >hdfs_info.txt
ansible-doc -M ../library/ hdfs_put 2>/dev/null | sed 's/[(].*hdfs_modules[/]library.*[)]//' >hdfs_put.txt
