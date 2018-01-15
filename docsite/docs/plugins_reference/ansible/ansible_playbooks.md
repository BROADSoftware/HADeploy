# ansible_playbooks

## Synopsis

Provide a list of Ansible playbooks which will be inserted in the overall deployment/removal processing.

Refer to [`overview`](./ansible_overview) for more information.

## Attributes

Each item of the list has the following attributes:

Name | req? | 	Description
--- | --- | ---
for_action|yes|This is the target action this playbook will be involved for. In must cases, will be `deploy` or `remove`.
priority|yes|This is the priority value to control when the playbook will be executed, regarding all other plugins. More information on this in [Execution order](../../more/execution_order/#plugin-priority)
playbook_text|yes if `playbook_file`<br>is not defined|The playbook itself, in a Yaml block. See the example below.
playbook_file|yes if `playbook_text`<br>is not defined|The name of a file hosting the playbook. This file will be searched in the folder list defined by [`playbooks_folders`](./playbooks_folders)
when|no|Boolean. Allow [conditional deployment](../../more/conditional_deployment) of this item.<br>Default `True` 

## Example
```yaml
ansible_playbooks:
- for_action: deploy
  priority: 5000
  playbook_text: |
    - hosts: edge_nodes
      tasks:
      - name: run this command and ignore the result
        shell: /usr/bin/somecommand
        ignore_errors: True
- for_action: deploy
  priority: 5000
  playbook_file: my_playbook.yml
```