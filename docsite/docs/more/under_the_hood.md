# Under the hood

## Overview

As stated in the installation instruction, HADeploy use Ansible under the hood to perform operation on the remote hosts. As such Ansible is defined as a dependency for HADeploy installation.

The main steps of an HADeploy run are the following:

* Load the application description by appending all `--src` files provided on the command line.

* Check its syntax, based on a YAML schema.

* Build a data model in memory representing this file content.

* Check this data model for consistency, enrich it, or transform some data to ease the next stages.

* From this model, generate an Ansible playbook

* Launch Ansible on this playbook.

## The working folder

In case of problem, it could be useful to have a look on the generated Ansible playbooks. 
These two playbooks (One for application deployment and one for application removal) are generated in a temporary folder, called the working folder.

This folder is automatically created in `/tmp`, under a random name. 
To ease debugging, one can force this working folder to a specific location, using the `--workingFolder` command line option.

> Warning: In such case, the full content of the working folder will be deleted on each run...

Here is a brief description of the files you may found in this folder:

Name|Description
---|---
ansible.cfg<br>inventory<br>group_vars folder|HAdeploy create a complete Ansible context to run Ansible inside.
install.yml|The playbook for application deployment
remove.yml|The playbook for application removal.
model_src.json|This is the part of the data model built from the sources file.
model_data.json|This is a the part of the data model where HADeploy store some intermediate structure.
model_helper.json|This is a part of the data model hosting some configuration information.
install.yml.jj2<br>remove.yml.jj2|These are the Jinja2 source template, merged with the data model to produce the install.yml and remove.yml files.
schema.yml|This is the YAML schema used to validate source input files. Will use [pykwalify](https://github.com/Grokzen/pykwalify) tool for validation.
desc_xxxx.yml.j2|Some helper files, specific to some plugins.




## Plugins

A plugin is a component which may be involved in all phases described at the befinning of this page. It is typically made of:

* A partial schema. All plugin's YAML schema parts will be merged to provide the overall schema against which the Master file will be validated.

* Some Python code called to check and enrich the model.

* A playbook snippet. All plugin plabook's snippets will be concatenated to build the target playbook. These snippets are Jinja2 templates which will be merged with the data model.

* Another playbook snippet for removal of the application.

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



