# playbooks_folders

## Synopsis

Allow definition of a list of local folder where HADeploy will lookup playbook files defined in [`ansible_playbooks`](./ansible_playbooks) entry

Refer to [`overview`](./ansible_overview) for more information.

## Attributes

A list of local folder path.

If path is not absolute, it will be relative to the HADeploy embedding file location.

## Example

```yaml
playbooks_folders: 
- ../playbooks
```
