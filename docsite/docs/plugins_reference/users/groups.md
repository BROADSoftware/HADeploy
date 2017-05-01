# groups

## Synopsis

Provide a list of Linux local groups required by the application 

## Attributes

Each item of the list has the following attributes:

Name|req?|Default|Description
---|---|---|---
name|yes||The group name
system|no|false|Is this a System group
managed|no|true|Boolean: Does HADeploy manage this group? If not, no action will be performed on it, but a failure will the triggered if it does not exists. 
scope|no|all|On which host does this group be created? May be:<ul><li>A single host name</li><li>A single host_group name</li><li>Several hosts or host_groups, separated by the character ':'</li></ul>
no_remove|no|no|Boolean: Prevent this group to be removed when HADeploy will be used in REMOVE mode

## Example

```yaml
groups:

# A simple local group, created on all hosts.
- name: broadgroup

# A system group, created on host 'node1' and on all hosts belonging to the host_group 'hgrp1'.
# Will never be removed by HADeploy
- name: broadsystem
  system: yes
  managed: yes
  scope: node1:hgrp1
  no_remove: yes
```
