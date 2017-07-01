# host_groups

## Synopsis

Provide a list of group of hosts.

## Attributes

Each item of the list has the following attributes:


Name|req?|Description
---|---|---
name|yes|The name of the host group
hosts|no|A list of hosts included in this group. Each host must be defined in the [`hosts:`](./hosts) part (Or the associated Ansible inventory).
groups|no|A list of `host_group` from wich all hosts will be included in this group. Allow group composition, and also group renaming.
force_setup|no|A common Ansible problem is when referencing host info for a host which has not being accessed, so there is no fact grabbed for it.<br>Setting this flag to `yes` will trigger an access to all hosts of this group at the begining of the play.<br>Default: `no`

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

# Group renaming
- name: brokers
  groups:
  - kafka_brokers
```

## Tricks

If, when running HADeploy you encounter error like:

```bash
fatal: [dn1]: FAILED! => {"changed": false, "failed": true, "msg": "AnsibleUndefinedVariable: 'dict object' has no attribute 'ansible_fqdn'"}
```

it is most likely that you need to set `force_setup` on some host_group or host.  
