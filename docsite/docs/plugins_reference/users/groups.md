# groups

## Synopsis

Provide a list of Linux local groups required by the application 

## Attributes

Each item of the list has the following attributes:

Name|req?|Description
---|---|---
name|yes|The group name
system|no|Is this a System group.<br>Default: `no`
managed|no|Boolean: Does HADeploy manage this group? If not, no action will be performed on it, but a failure will the triggered if it does not exists.<br>Default: `yes` 
scope|no|On which host does this group will be created? May be:<ul><li>A single host name</li><li>A single host_group name</li><li>Several hosts or host_groups, separated by the character ':'</li></ul>Default: `all`
no_remove|no|Boolean: Prevent this group to be removed when HADeploy will be used in REMOVE mode.<br>Default: `no`
when|no|Boolean. Allow [conditional deployment](../../more/conditional_deployment) of this item.<br>Default `True` 
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
