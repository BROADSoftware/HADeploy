# YAML tricks

## Block merging

To provide more flexibility about source file organization, HADeploy allow you to split definition in several logical parts, using block merging.

For example, let's say you have the following:
```yaml
groups:
- name: grp1
- name: grp2

users: 
- login: user1
  groups: "grp1,grp2"
- login: user2
  groups: "grp1,grp2"
```

This could also be expressed:
```yaml
groups:
- name: grp1

groups:
- name: grp2

users: 
- login: user1
  groups: " grp1,grp2"

users:
- login: user2
  groups: " grp1,grp2"
```
or:
```yaml
groups:
- name: grp1

users: 
- login: user1
  groups: " grp1,grp2"

groups:
- name: grp2

users:
- login: user2
  groups: " grp1,grp2"
```
This can also be split in two files:
```yaml
groups:
- name: grp1

users: 
- login: user1
  groups: " grp1,grp2"
```

```yaml
groups:
- name: grp2

users:
- login: user2
  groups: " grp1,grp2"
```

Note than file order will be irrelevant, as effective deployment action ordering is NOT driven by the order of occurrence of declaration. See [Execution order](execution_order.md)

## YAML anchors

YAML anchors are a powerful YAML feature, which could be of great help in some cases.
For example, lets consider the following snippet:

```yaml
files:
- scope: hdfs
  src: file://myapp1.jar
  dest_folder: /apps/mayapp
  owner: myappuser
  group: myappgrp
  mode: "0644"
- scope: hdfs
  src: file://myapp2.jar
  dest_folder: /apps/mayapp
  owner: myappuser
  group: myappgrp
  mode: "0644"
- scope: hdfs
  src: file://myapp3.jar
  dest_folder: /apps/mayapp
  owner: myappuser
  group: myappgrp
  mode: "0644"
```
It can be written as:
```yaml
vars: 
  permsFiles: &permsFiles
    owner: myappuser
    group: myappgrp
    mode: "0644"

- scope: hdfs
  src: file://myapp1.jar
  dest_folder: /apps/mayapp
  <<: *permsFiles
- scope: hdfs
  src: file://myapp2.jar
  dest_folder: /apps/mayapp
  <<: *permsFiles
- scope: hdfs
  src: file://myapp3.jar
  dest_folder: /apps/mayapp
  <<: *permsFiles
```
Or, using flow style:
```yaml
vars: 
  permsFiles: &permsFiles
    owner: myappuser
    group: myappgrp
    mode: "0644"

- { scope: hdfs, src: file://myapp1.jar, dest_folder: /apps/mayapp, <<: *permsFiles }
- { scope: hdfs, src: file://myapp2.jar, dest_folder: /apps/mayapp, <<: *permsFiles }
- { scope: hdfs, src: file://myapp3.jar, dest_folder: /apps/mayapp, <<: *permsFiles }
```

