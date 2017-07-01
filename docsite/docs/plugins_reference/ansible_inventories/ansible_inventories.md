# ansible_inventories

## Synopsis

Provide a list of Ansible Inventory.

These inventories will be parsed, eventually merged with locally defined [`hosts`](../inventory/hosts) and [`host_groups`](../inventory/host_groups) and will allow target Ansible inventory file generation.

Also, some paramters may be modified by using [`host_overrides`](../inventory/host_overrides.md) and [`host_group_overrides`](../inventory/host_group_overrides.md). 

## Attributes

Each item of the list has the following attributes:

Name | req?	 |	Description
--- | --- | ---
file|yes|The Ansible inventory file path. If this path is not absolute, it will be relative to the HADeploy embedding file location.
vault_password_file|no|If this inventory host one or several encrypted files, one must provide a password for decryption. One method is to provide this password in a file.<br>The password must be a string stored as a single line of the file.<br>If this path is not absolute, it will be relative to the HADeploy embedding file location.<br>It can also be stored in the home folder of the sshd_user by using the ~/... notation.<br>In all cases, ensure permissions on the file are such that no one else can access your key and do not add your this file to source control.
ask_vault_password|no|Boolean. Another method to provide this password is to set this switch on. In this case, the user will be prompted to enter the password on each run.
name|no|Allow to provide a name to this inventory.<br>Useful if this list contains several entries which require a password. This name will be inserted in the prompt for the user.


## Example

```yaml
# This simplest case, with a single inventory
ansible_inventories:
- file: ".../some-ansible-folder/inventory"


# Build our own inventory from two Ansible inventories. And request user password with decorated prompt
ansible_inventories:
- name: "inv1" 
  files: ".../some-ansible-folder/inventory"
  ask_vault_password: yes
- name: "inv2"  
  file: ".../another-ansible-folder/inventory"
  ask_vault_password: yes
  
```
## Inventory merging

If a host with same name is defined both in [`hosts`](../inventory/hosts) and in an Ansible inventory, the one from the [`hosts`](../inventory/hosts) list will take precedence. 
This is same for the [`host_groups`](../inventory/host_groups). 

Note also a [`host_groups`](../inventory/host_groups)  can refer to a host in Ansible inventory.
