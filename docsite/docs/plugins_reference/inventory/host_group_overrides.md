# host_group_overrides

## Synopsis

Provide a list of host group overriding values, to modify an existing inventory.

Typically used to patch an Ansible inventory (see [`ansible_inventory_files`](../ansible_inventory/ansible_inventory_files)) with some new values

## Attributes

Each item of the list has the following attributes:

Name|req?|Default|Description
---|---|---|---
name|yes||The name of the host to patch. Must be an existing host. Also may be 'all' or '*' to patch all hosts.
hosts|no||Allow to override the original hosts list
force_setup|no||A common Ansible problem is when referencing host info for a host which has not being accessed, so there is no fact grabbed for it.<br>Setting this flag to `yes` will trigger an access to all hosts of this group at the begining of the play.



## Example

A common pitfall is the infamous `AnsibleUndefinedVariable: 'dict object' has no attribute 'ansible_fqdn'` message. 
This is due to the fact we are referencing some variables (`ansible_fqdn`) of hosts which are not part of the playbook.

The following example force all hosts of the `zookeepers` group to be included at the top of the playbook 

```yaml
host_group_overrides:
- name: zookeepers
  force_setup: yes
```
