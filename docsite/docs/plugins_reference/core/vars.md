# vars

## Synopsis

HADeploy allow you to defined variable which then will be substituted by surrounding the variable name with  "${ "and "}" (or '<<' and '>>', see below).

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
## Alternate notation

HADeploy added an alternate notation for variable by using '<<' and '>>'. This notation is mainly intended to be used in 'flow style' description. For example:

```yaml
files:

- {  when: <<isKerberos>>, scope: all, dest_folder: "/etc/security/keytabs", src="${appUser}.keytab" owner: ${appUser}, group: broadgroup, mode: "0400" }
```

If we where using `when: ${isKerberos}`, this will generate an error as the opening `{` will be confused with the start of the map delimiter.

The solution could be to write `when: "${isKerberos}"`. This will be parsed correctly, but the side effect will be to consider the variable as a String, 
not as a Boolean. Thus generating an error in this case (`when:` require a boolean).

So, to allow usage of non-String variable in 'flow style' notation, the `<<....>>` delimiters as been implemented. Of course, as in the previous example, both notation can be used simultaneously.

