# host_overrides

## Synopsis

Provide a list of host overriding values, to modify an existing inventory.

Typically used to patch an Ansible inventory (see ansible_inventory_file) with some new values

## Attributes

Each item of the list has the following attributes:


Name|req?|Description
---|---|---
name|yes|The name of the host to patch. Must be an existing host. Also may be 'all' or '*' to patch all hosts.
force_setup|no|A common Ansible problem is when referencing host info for a host which has not being accessed, so there is no fact grabbed for it.<br>Setting this flag to `yes` will trigger an access to this host at the begining of the play.
ssh_host|no|Allow to override ssh_host
ssh_user|no|Allow to override ssh_user
ssh_private_key_file|no|Allow to override ssh_private_key_file
ssh_password|no|Allow to override ssh_password. This may be encrypted. Refer to [encrypted variables](../core/encrypted_vars)
ssh_port|no|Allow to override ssh_port
ssh_extra_args|no|Allow to override ssh_extra_args
ssh_common_args|no|Allow to override ssh_common_args
sftp_extra_args|no|Allow to override sftp_extra_args
scp_extra_args|no|Allow to override scp_extra_args
ssh_pipelining|no|Allow to override ssh_pipelining
ssh_executable|no|Allow to override ssh_executable
become|no|Allow to override become
become_method|no|Allow to override become_method
become_user|no|Allow to override become_user
become_pass|no|Allow to override become_pass. This may be encrypted. Refer to [encrypted variables](../core/encrypted_vars)
become_exe|no|Allow to override become_exe
priority|no|An integer number allowing to order overriding in case of multiple `host_override` on the same host(s). See example below.<br>Default: 100



> To suppress an attribute, set it to empty string: ''

## Examples

We want to address a VM built using Vagrant. For this, we can use the Vagrant generated ansible inventory. Such inventory instruct HADeploy to access the VM under the `vagrant`account. 
So, we need to instruct HADeploy to become `root`in order to perform privileged operation. 

```yaml
ansible_inventories: 
- file: "../../iac/vgrvm1/.vagrant/provisioners/ansible/inventory/vagrant_ansible_inventory"

host_overrides:
- name: all
  become_user: root
```
Of course, this works because the `vagrant` account has been granted by vagrant with appropriate sudo rights. 

This other example change the user for all HADeploy action for all hosts. And authenticate with a (encrypted) password instead of a key:

```yaml

encrypted_vars:
  deployer_password: |
    $ANSIBLE_VAULT;1.1;AES256
    65626166653134326137613232323336373139393036383532333863623630363662303531306539
    6637306363343836376633353439656634613638643031660a636238323663353337313333663438
    30306234306463626338663637623563393735653237323833323064316561653237393538303762
    6363326232656461310a656631386135663764386565366566633537633665646562626236393462
    6231

host_overrides:
- name: all
  ssh_user: deployer      
  ssh_password: "{{deployer_password}}"
  ssh_private_key_file: ''
```
Refer to [encrypted variables](../core/encrypted_vars) for more information.

### Priority

Here is an illustration of the `priority` attribute usage: 

```yaml
host_overrides:
- name: all
  become_user: root

....  

host_overrides:
- name: all
  become_user: ''
  priority: 110
```
This will result with `become_user` not set. 

While:

```yaml
host_overrides:
- name: all
  become_user: root

....  

host_overrides:
- name: all
  become_user: ''
  priority: 90
```
Will result with `become_user` set to `root`. (Default value is 100, so the first one take precedence).

This feature may be usefull when building complex configuration by merging several inventory files.

## Tricks

If, when running HADeploy you encounter error like:

```bash
fatal: [dn1]: FAILED! => {"changed": false, "failed": true, "msg": "AnsibleUndefinedVariable: 'dict object' has no attribute 'ansible_fqdn'"}
```

it is most likely that you need to set `force_setup` on some host_group or host.  
