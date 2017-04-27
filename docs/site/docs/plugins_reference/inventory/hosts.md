# hosts
***

## Synopsis

Provide a list of hosts describing the target cluster.

## Attributes

Each item of the list has the following attributes:

Name|req?|Default|Description
---|---|---|---
name|yes||The host name. May be whatever you want. HADeploy will always refer to this host by this name.
ssh_host|yes||How to reach this host using ssh from the HADeploy node. Typically the FQDN. May also be the IP address.
ssh_user|yes||This user account under which HADeploy will perform its operation. Typically root.
ssh_private_key_file|no||The path to the private key file granting no password access to this host. If this path is not absolute, it will be relative to the HADeploy embedding file location.
ssh_password|no||The password to provide to access this host. WARNING: This is of course a huge security breach to provide password such this way.
ssh_extra_args|no||Allow providing extra argument to ssh connection.

> If the user launching HADeploy have itself a private key granting access to all the clusters hosts, there is no need to define `ssh_private_key_file` and `ssh_password` in any Ansible or HADeploy file.

## Example

```yaml
hosts:
- name: sr
  ssh_host: sr.cluster1.mydomain.com
  ssh_user: root
  ssh_private_key_file: "keys/build_key" 
  ssh_extra_args: "-o UserKnownHostsFile=/dev/null"
```
