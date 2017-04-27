# HADeploy: Architecture and plugins.

## Overview

The main steps of an HADeploy run are the following:

* Load the application master description file. Let's call it the 'Master file'.

* Check its syntax, based on a YAML schema.

* Build a data model in memory representing this file content.

* Check this data model for coherency,enrich it, or transform some data to ease the next stages.

* From this model, generate an Ansible playbook

* Launch Ansible on this playbook.

Now is a short description of the main components of a plugin, and how it plug in the processing just described. 

A plugin is made of:

* A partial schema. All plugin's YAML schema parts will be merged to provide the overall schema against which the Master file will be validated.

* Some Python code called to check and enrich the model.

* A playbook snippet. All plugin plabook's snippets will be concatenated to build the target playbook. These snippets are Jinja2 templates which will be merged with the data model.

* Another playbook snippet for removal of the application.


## Plugins list

Each master file may contains the list of plugin required for its execution. For example:

```yaml
plugins:
- ansible_inventory
- folders
- files
- hbase
```
Note than plugins order may be of importance. It will drive the order of playbook execution. For example, it make sense to have folder creation before file copying take place.
 
 If no plugins list is present, the default value will be:

```yaml
plugins:
- ansible_inventory
- folders
- files
- hbase
- kafka
- hive
- ranger
```

If this list is explicity defined, it will overwrite the default value (There is no concatenation of the two lists). 

## Plugin path

HADeploy come with a set of builtin plugins. But, of course, aim is to be able to handle user's provided plugin. This can be easily achieved by defining a `plugins_paths` entry;

```yaml
plugins_paths:
- HADEPLOY_HOME/plugins
- ./myplugins
```

`HADEPLOY_HOME` is a special token representing the path of HADeploy installation.

If not starting with a '/', path are relative to the file holding the `plugin_paths` definition.

 
## Plugin internals

This part is of interest only if you intend to build your own plugin. (Which in fact is a very easy task).

If you read it, we strongly engage you to have a look simultaneously on some builtin plugins, to have a clear understanding of machnisme.

A plugin is a folder of the same name. This folder may contains the following elements:

File or folder | Description
---: | ---
`schema.yml`|The partial schema controlling Master file syntax.
`groomer.py`|Python code hosting plugins runtime function. See the other table below
`install.yml`|This is the Jinja2 template file which will be part of the resulting Ansible playbook used to deploy the application.  
`remove.yml`|This is the Jinja2 template file which will be part of the resulting Ansible playbook used to remove the application.
`roles`|A folder containing Ansible roles used by this plugin. If present, the path will be added to the `roles_path` of Ansible.
`files`|A folder containing some files required by the plugin.
`setup`|A script called during HADeploy installation. May be used to complete the plugin's setup. For example clone Ansible roles from github the the `roles`plugin folder.<br/>It could be of any language provided appropriate shebang is set, but we strongly advise to limit yourself to Shell script or Python.<br/>Also, it is assumed this script is idempotent. 

All these files and folder are optionnal.

The `groomer.py` python code may hold the following function.

Name | Description
--- | ---
`groom(model, context)`|Called after the data model has been loaded from the master application file. Allow whatever check or enrichment of this model.
`getSchema(context)`|Return a list of schema object, to be merged in the overall schema.<br>If not provided, a default function is used which return only the schema build from the plugin's `schema.yml`.<br>This is intended for very specific case where one wants to have different schema based on the context.   

### Context object

TODO 


### Logging system.
 
TODO

## The data model

TODO

## Raw Ansible  

TODO