# host_overrides

## Synopsis

Provide a list of host overriding values, to modify an existing inventory.

Typically used to patch an Ansible inventory (see ansible_inventory_file) with some new values

## Attributes

Each item of the list has the following attributes:


Name|req?|Description
---|---|---
name|yes|The name of the host to patch. Must be an existing host. Also may be 'all' or '*' to patch all hosts.
ssh_host|no|Allow to override ssh_host
ssh_user|no|Allow to override ssh_user
ssh_private_key_file|no|Allow to override ssh_private_key_file
ssh_password|no|Allow to override ssh_password
ssh_extra_args|no|Allow to override ssh_extra_args
force_setup|no|A common Ansible problem is when referencing host info for a host which has not being accessed, so there is no fact grabbed for it.<br>Setting this flag to `yes` will trigger an access to this host at the begining of the play.

> To suppress an attribute, set it to empty string: ''

## Example

Change the user for all HADeploy action for all hosts. And authenticate with a password instead of a key:

```yaml
host_overrides:
- name: all
  ssh_user: deployer      
  ssh_password: aNicePassword
  ssh_private_key_file: ''
```


## Tricks

If, when running HADeploy you encounter error like:

```bash
fatal: [dn1]: FAILED! => {"changed": false, "failed": true, "msg": "AnsibleUndefinedVariable: 'dict object' has no attribute 'ansible_fqdn'"}
```

it is most likely that you need to set `force_setup` on some host_group or host.  
