# local_templates_folders

## Synopsis

Allow definition of a list of local folder where HADeploy will lookup local templates to be deployed on the target clusters.

## Attributes

A list of local folder path.

If path is not absolute, it will be relative to the HADeploy embedding file location.

## Example
```yaml
local_templates_folders:
- "./templates"
```