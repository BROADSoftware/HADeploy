# ansible plugin: Overview 

Aim of this plugin is to allow integration of ansible playbook in a deployment. 

This can be useful to handle some resources not (yet) managed by HADeploy, or to perform some very specifics operation.

Of course, you should be familiar with Ansible to eficiently use this plugin. And you may also be familiar with some internal HADeploy concept, such as [execution order](../../more/execution_order/#plugin-priority), 
if you have some dependencies between elements, and [variable resolution](../../more/under_the_hood/#variables), if you don't want everything to be hard-coded in your playbook

Let's comment a small example:

```yaml  
ansible_playbooks:
- for_action: deploy
  priority: 1500
  playbook_text: |
    - hosts: dn1
      vars:
         kdescribe_rpm_url: https://github.com/Kappaware/kdescribe/releases/download/v0.2.0/kdescribe-0.2.0-1.noarch.rpm
      roles:
      - kdescribe
```
Here, we defined the playbook directly in file. For this, we use the Yaml block scalar mode, introduced by `|`. Take care of indentation.

For this example, we launch an ansible role [`kdescribe`](https://github.com/BROADSoftware/bsx-roles/tree/master/kappatools/kdescribe), 
which install an [rpm package of the same name](https://github.com/Kappaware/kdescribe), and configure it.

This role need some variable to be set, as the package url. Note this variable could also be set outside the playbook:

```yaml  
vars:
  kdescribe_rpm_url: https://github.com/Kappaware/kdescribe/releases/download/v0.2.0/kdescribe-0.2.0-1.noarch.rpm

ansible_playbooks:
- for_action: deploy
  priority: 1500
  playbook_text: |
    - hosts: dn1
      roles:
      - kdescribe
```
Actually, All HADeploy variable are also Ansible variable. See [variable resolution](../../more/under_the_hood/#variables)
 
Another point is where Ansible will find this `kdescribe` role? 

or this, HADeploy provide a method to add some entries to the Ansible role path. For example:

```yaml  
roles_folders: 
- ../roles
```

But an Ansible playbook also allow definition of individual task. For example, there is a `kdescribe` role for installation and configuration. But not for removal. To do so, we can add:

```yaml  
- for_action: remove
  priority: 3000
  playbook_text: |
    - hosts: dn1
      tasks:
      - name: "Remove kdescribe"
        yum: name=kdescribe state=absent
```

> All examples provided here perform package `yum` management. As, so, they need to be executed with the [`ssh_user`](../inventory/hosts) set as `root` for the target host. Note the is a constraint of this sample, not of the `ansible` plugin.

## Action and priority

As we can see, a playbook is associated to an action. For example, the first example playbook will be involved only when HADeploy will be launched  with `--action deploy`, as stated by the `for_action` attribute.

Also, for this action, a `priority` is defined. This will allow to control when the playbook will be executed, regarding other plugins. More information on this in [Execution order](../../more/execution_order/#plugin-priority)

## Variables

The playbook itself can contain some variable, such as in the following example:
 
```yaml  
vars:
  kdescribe_rpm_url: https://github.com/Kappaware/kdescribe/releases/download/v0.2.0/kdescribe-0.2.0-1.noarch.rpm
  tools_target: dn1
 
ansible_playbooks:
- for_action: deploy
  priority: 1500
  playbook_text: |
    - hosts: ${tools_target}
      roles:
      - kdescribe 
```

Note than you can also play with Ansible variable. HADeploy will not interprets them and pass through to Ansible. For example, this will works as intended:

```yaml  
- for_action: remove
  priority: 1500
  playbook_text: |
    - hosts: ${tools_target}
      tasks:
      - name: Remove tools
        yum: name={{item}} state=absent
        with_items:
        - kdescribe
        - ktail
```


## Playbook in files

If you playbook is more than a couple of line or if you want it to be run for several target, it could be more convenient to define it in a file, and provide this file reference to HADeploy.

```yaml  
- for_action: remove
  priority: 3000
  playbook_file: remove_kdescribe.yml
```
The file may contains:

```yaml  
# ------------------------------------ Remove kdescribe.yml

- hosts: {{{src.vars.tools_target}}}
  tasks:
  - name: "Remove kdescribe"
    yum: name=kdescribe state=absent
```  
Note the way we access the `tools_target` variable. Explanation of this syntax can be found [here](../../more/under_the_hood/#variables). 

The key point is this file is a snippet which will be aggregated with many other to built the overall playbook, as described by [step 5 of the processing](../../more/under_the_hood) 

Another aspect is where to store these playbook files? As usual, a specific entry will provide a list of folders where HADeply will lookup your file:

```yaml  
playbooks_folders: 
- ../playbooks
```

## Implements new actions

HADeploy is currently designed to achieve 2 actions: `deploy` and `remove`.

With introduction of this `ansible` plugin, we introduced the fact target action can be defined explicitly. This is extended to the fact new action could also be defined.

For example, we can consider tools like `kdescribe` are not part of application deployment by itself, but of an auxiliary tooling deployment. So, we can define:

```yaml  
ansible_playbooks:
- for_action: deployTools
  priority: 1500
  playbook_text: |
    - hosts: ${tools_target}
      vars:
        kdescribe_rpm_url: https://github.com/Kappaware/kdescribe/releases/download/v0.2.0/kdescribe-0.2.0-1.noarch.rpm
      roles:
      - kdescribe
- for_action: removeTools
  priority: 1500
  playbook_text: |
    - hosts: ${tools_target}
      tasks:
      - name: "Remove kdescribe"
        yum: name=kdescribe state=absent
```

Doing so, we have introduced two new actions, `deployTools` and `removeTools`. Then we can provide them on the command line:

```yaml  
hadeploy --src app.yml --src infra.yml --action deployTools
```

 


