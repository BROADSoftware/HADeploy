# host_groups

## Synopsis

Provide a list of group of hosts.

## Attributes

Each item of the list has the following attributes:


Name|req?|Default|Description
---|---|---|---
name|yes||The name of the host group
hosts|yes||The list of the hosts for this group. Each host must be defined in the hosts: part (Or the associated Ansible inventory).
force_setup|no|no|A common Ansible problem is when referencing host info for a host which has not being accessed, so there is no fact grabbed for it.<br>Setting this flag to `yes` will trigger an access to all hosts of this group at the begining of the play.

Note than same host can belong to several groups.

## Example

```yaml

host_groups:
- name: data_nodes
  hosts:	# This host list in standart YAML style
  - dn1
  - dn2
  - dn3

- name: control_nodes
  hosts: [ "sr", "en", "nn1", "nn2" ]	# And these in YAML 'flow style

- name: empty_group
  hosts: []
 
```