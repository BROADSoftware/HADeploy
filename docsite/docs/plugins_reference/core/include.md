# include

## Synopsis

Allow inclusion of source file.

## Attributes

Could be a list of source file to include, or a simple source file name.

## Example
```yaml
include: infra.yml
include: app.yml
```
or
```yaml
include:
- infra.yml
- app.yml
```

If paths are not absolute, they will be relative to the HADeploy embedding file location.
 
The included file name can also be build from variables: 
 
```yaml
vars:
  env: dev
....

include: ./envs/${env}.yml
```
