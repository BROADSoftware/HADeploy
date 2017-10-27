# supervisor_groups

## Synopsis

It is often useful to group programs together into a process group so they can be controlled as a unit from Supervisor’s various controller interfaces, such as supervisorctl.

Refer to [supervisor documentation](http://supervisord.org/configuration.html#group-x-section-settings) for more information

## Attributes

Each item of the list has the following attributes:

Name | req? | 	Description
--- | ---  | ---
supervisor|yes|The supervisor managing this group
name|yes|Name of the group.
programs|yes|The list of program belonging tho this group.
priority|no|The priority assigned to this group. Refer to [supervisor documentation](http://supervisord.org/configuration.html#group-x-section-settings).
no_remove|no|Boolean: Prevent this program to be removed when HADeploy will be used with `--action remove`.<br>Default: `no`

## Example

```yaml
supervisor_groups:
- supervisor: tech1
  name: grp1
  programs:
  - program1
  - program2
```


