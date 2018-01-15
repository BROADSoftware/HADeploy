# Conditional deployment

Sometime, you want to skip a particuliar object creation, based on specifics condition. 

It is quite easy to do with HADeploy, as most of the object declaration accept a `when:` attribute. If this boolean resolve to 'False', then the object creation will be skipped.

For example:

```yaml
vars:
  isKerberos: true
...
files:
- scope: all
  dest_folder: "/etc/security/keytabs"
  src: "${appUser}.keytab" 
  owner: "${appUser}"
  group: broadgroup
  mode: "0400"
  when: ${isKerberos}
```

Note than, as all variables, what is inside the ${...} delimiter is not limited to a single variable name, but is in fact a Jinja2 expression. So, it also could be, for example:
```yaml
...
files:
- scope: all
  ...
  when: ${isKerberos is defined and isKerberos}
```

Also, note the usefulness of the [alternate variable notation](../plugins_reference/core/vars/#alternate-notation) for the 'flow style' notation. 

```yaml
files:
- {  when: <<isKerberos>>, scope: all, dest_folder: "/etc/security/keytabs", src= "${appUser}.keytab" owner: "${appUser}", group: broadgroup, mode: "0400" }
```
