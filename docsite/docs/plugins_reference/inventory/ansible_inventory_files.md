# ansible_inventory_files

## Synopsis

Define a list of Ansible Inventory files.

These files will be parsed, eventually merged with locally defined hosts and host_groups and will allow target Ansible inventory file generation

## Attributes

A list of Ansible inventory files path.

If path is not absolute, it will be relative to the HADeploy embedding file location.

> If you need to modify some attributes of one, several or all hosts, use [`host_overrides`](./host_overrides.md)

## Example

```yaml
# Build our own inventory from two Ansible inventories
ansible_inventory_files:
- ".../some-ansible-folder/inventory"
- ".../another-ansible-folder/inventory"
```
