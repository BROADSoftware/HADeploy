# local_files_folders

## Synopsis

Allow defining a list of local folder where HADeploy will lookup local files to be deployed on the target clusters.

## Attributes

A list of local folder path.

If path is not absolute, it will be relative to the HADeploy embedding file location.

## Example
```yaml
local_files_folders:
- "./files"
```
