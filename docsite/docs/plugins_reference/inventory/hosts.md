# hosts

## Synopsis

Provide a list of hosts describing the target cluster.

## Attributes

Each item of the list has the following attributes:

Name|req?|Description
---|---|---
name|yes|The host name. May be whatever you want. HADeploy will always refer to this host by this name.
force_setup|no|A common Ansible problem is when referencing host info for a host which has not being accessed, so there is no fact grabbed for it.<br>Setting this flag to `yes` will trigger an access to this host at the begining of the play.<br>Default: `no`
ssh_host|yes|How to reach this host using ssh from the HADeploy node. Typically the FQDN. May also be the IP address.
ssh_user|yes|This user account under which HADeploy will perform its operation. Typically root.
ssh_private_key_file|no|The path to the private key file granting no password access to this host. If this path is not absolute, it will be relative to the HADeploy embedding file location.
ssh_password|no|The password to provide to access this host. This may be encrypted. Refer to [encrypted variables](../core/encrypted_vars)
ssh\_extra_args|no|This setting is always appended to the default ssh command line.
ssh_port|no|The ssh port number, if not 22
ssh\_common_args|no|This setting is always appended to the default command line for sftp, scp, and ssh. Useful to configure a ProxyCommand for a certain host (or group).
sftp\_extra_args|no|This setting is always appended to the default sftp command line.
scp\_extra_args|no|This setting is always appended to the default scp command line.
ssh_pipelining|no|Determines whether or not to use SSH pipelining.
ssh_executable|no|This setting overrides the default behavior to use the system ssh.
become|no|Allows to force privilege escalation
become_method|no|Allows to set privilege escalation method
become_user|no|Allows to set the user you become through privilege escalation
become_pass|no|Allows you to set the privilege escalation password. This may be encrypted. Refer to [encrypted variables](../core/encrypted_vars)
become_exe|no|Allows you to set the executable for the escalation method selected
become\_flags|no|Allows you to set the flags passed to the selected escalation method.
when|no|Boolean. Allow [conditional deployment](../../more/conditional_deployment) of this item.<br>Default `True` 


> If the user launching HADeploy have itself a private key granting access to all the hosts, there is no need to define `ssh_private_key_file` and `ssh_password` in any Ansible or HADeploy file.

## Example

```yaml
hosts:
- name: sr
  ssh_host: sr.cluster1.mydomain.com
  ssh_user: root
  ssh_private_key_file: "keys/build_key" 
  ssh_extra_args: "-o UserKnownHostsFile=/dev/null"
```

## Tricks

If, when running HADeploy you encounter error like:

```bash
fatal: [dn1]: FAILED! => {"changed": false, "failed": true, "msg": "AnsibleUndefinedVariable: 'dict object' has no attribute 'ansible_fqdn'"}
```

it is most likely that you need to set `force_setup` on some host_group or host.  
