# vars

## Synopsis

HADeploy allow you to defined variable which then will be substituted by surrounding the variable name with  "${ "and "}"

There is also a method to provide variable definition on the command line when launching HADeploy. See [Launching HADeploy](/getting_started/next_step/#launching-hadeploy).

## Attributes

Attributes are variables name.

As demonstrated by the `app_jar_url:` in example below, entry, variable value can themself include other variable.

Note also than variable can be a scalar (String, int, etc...) but also a map.

## Example

```yaml
vars:
  app_version: "0.1.1"
  repository_server: "myserver.com"
  app_jar_url: "http://${repository_server}/repo/broadapp-${app_version}.jar"
  zookeeper:
    connection_timeout: 60000
    zkpath: /broadapp
```
