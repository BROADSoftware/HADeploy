# Under the hood

## Overview

As stated in the installation instruction, HADeploy use Ansible under the hood to perform operation on the remote hosts. As such Ansible is defined as a dependency for HADeploy installation.

The main steps of an HADeploy run are the following:

1. Load the application description by appending all `--src` files provided on the command line to build a single deployment file.

1. Check syntax of this deployment file, based on a YAML schema.

1. Build a data model in memory representing this file content.

1. Check this data model for consistency, enrich it, or transform some data to ease the next stages.

1. Generate a Jinja2 template by concatenating all template snippets provided by the plugin.

1. Render this template with the model to generate an Ansible playbook

1. Launch Ansible on this playbook.

## Variables

When using HADeploy in an advanced way (i.e using the `ansible` module, or developping your own plugin), you may be disturbed by different variable notation. 
There is in fact 3 kinds of variables involved in HADeploy

#### `${my_variable}` 

Or `<<my_variable>>`

This is the only variable notation you should be aware of for standart usage of HADeploy.

Such variables are resolved during step 1 (Building of the deployment file).

Refer to [alternate notation](../plugins_reference/core/vars/#alternate-notation) for the motivation of using `<<my_variable>>`.

#### `{{{my_variable}}}`

This is the variable notation used during the rendering of step 6. This will allow all snippets provided by the plugin to acccess variables of the model.

#### `{{my_variable}}`

This is the standard variable notation used by Ansible. HADeploy will not resolve such variables, passing them as is to Ansible playbook. So they will be resolved by Ansible in step 7.

This form need generaly to be quoted (`"{{my_variable}}"`). It must also be used for [encrypted values](../plugins_reference/core/encrypted_vars)

### Variable relationship

Although this variables act at different level, there is some mechanism to propagate user's value (The one with ${..} notation) to lower level.

- They are copied in the data model built in step 3, under the token `src.vars`. So, the variable `${my_variable}`can be accessed by `{{{src.vars.my_variable}}}`by a plugin playbook snippet.

- In the Ansible context, a `group_vars/all` file is generated, containing a line as `my_variable: my_value` for each user's variable. So, all the user's variable will be directly accessible by Ansible, in step 7.

## The working folder

In case of problem, it could be useful to have a look on the generated Ansible playbook.
This playbook is generated in a temporary folder, called the `working folder`. It is named as the action provided as parameter.

This folder is automatically created in `/tmp`, under a random name. 
To ease debugging, one can force this working folder to a specific location, using the `--workingFolder` command line option.

> Warning: In such case, the full content of the working folder will be deleted on each run...

But, this working folder not only contains the playbook. Here is a brief description of the files you may found in it:

Name|Description
---|---
ansible.cfg<br>inventory<br>group_vars folder|HAdeploy create a complete Ansible context to run Ansible inside.
`<action>`.yml.jj2|This is the Jinja2 source template, result of step 5 above, which will be merged with the data model to produce the file below.
`<action>`.yml|The playbook for targeted action, generated on step 6. i.e `deploy.yml` or `remove.yml`.
model_src.json|This is the part of the data model built from the sources file.
model_data.json|This is a the part of the data model where HADeploy store some intermediate structure.
model_helper.json|This is a part of the data model hosting some configuration information.
schema.yml|This is the YAML schema used to validate source input files. Will use [pykwalify](https://github.com/Grokzen/pykwalify) tool for validation.
desc_xxxx.yml.j2|Some helper files, specific to some plugins.

Note: If you launch HADeploy with `--action none` then it will generate ansible playbooks for all action it is aware off. But, it will not launch ansible. 
This is intended to validate description for all action.

## Plugins

A plugin is a component which may be involved in all phases described at the befinning of this page. It is typically made of:

* A partial schema. All plugin's YAML schema parts will be merged to provide the overall schema against which the deployement file will be validated.

* Some Python code called to check and enrich the model. This code must include a subclass of the `Plugin` class, to handle plugin properties and lifecycle.

* Several playbook snippet. Typically, one per supported action. For a given action, all plugin plabook's snippets will be concatenated to build the target playbook. These snippets are Jinja2 templates which will be merged with the data model.

All theses are optional. A plugin can also host:

* Ansible roles or modules.

* One or more helper. An helper is a specific program designed to manage services which offer only a Java API.

Currently, HADeploy is provided with the following internal plugin:

* `inventory` for target hosts management.
* `ansible_inventories` for direct integration of an Ansible inventories.
* `users` for management of local users and groups. 
* `files` for base file management.
* `hdfs` which extends the previous one for HDFS accesses.
* `hbase`
* `hive`
* `kafka`
* `ansible`
* `ranger`



## Embedded Ansible roles

* For HDFS access, HADeploy embeds the [hdfs_modules](https://github.com/BROADSoftware/hdfs_modules) Ansible modules in the HDFS plugin

* For Apache Ranger policy handling, HADeploy embeds the [ranger_modules](https://github.com/BROADSoftware/ranger_modules) Ansible modules in the Ranger plugin

## Embedded Helpers

### Hive

* For Hive based deployment, HADeploy embeds the [jdchive](https://github.com/BROADSoftware/jdchive) tool.

### HBase

* For HBase based deployment, HADeploy embeds the [jdchtable](https://github.com/BROADSoftware/jdchtable) tool.

* For HBase dataset loading, HADeploy embeds the [hbload](https://github.com/BROADSoftware/hbtools) tool.

### Kafka

* For Kafka based deployment, HADeploy embeds the [jdctopic](https://github.com/Kappaware/jdctopic) tool.



