# users

## Synopsis

Provide a list of Linux local users required by the application 

## Attributes

Each item of the list has the following attributes:


Name|req?|Description
---|---|---
login|yes|The user's name
comment|no|Description of the user's account
group|no|Set the user primary group.
groups|no|Puts the user in this comma-delimited list of groups..
system|no|Is this a System user.  (Note this can't be changed after user creation).<br>Default: `no`
managed|no|Boolean: Does HADeploy manage this user?<br>If `false`, no action will be performed on it (except `authorized_keys` and `can_sudo_to` handling), but a failure will the triggered if it does not exists.<br>Default: `yes` 
scope|no|al|On which host does this group be created? May be:<ul><li>A single host name</li><li>A single host_group name</li><li>Several hosts or host_groups, separated by the character ':'</li></ul>Default: `all`
can\_sudo_to|no|A comma separated list of account this user will be able to 'sudo' into. May also be 'ALL'. Note this will be applied even if `managed == no`.
create_home|no|Unless set to no, a home directory will be made for the user when the account is created or if the home directory does not exist.<br>Default: `yes`
password|no|Set the user's password to this crypted value.
no_remove|no|Boolean: Prevent this group to be removed when HADeploy will be used in REMOVE mode.<br>Default: `no`
authorized_keys|no|Provide a list of public key files, which will be added to this user account in its authorized_keys file. Note this will be applied even if `managed==no`.<br>If these public key file locations are not absolute, they will be relative to the HADeploy embedding file location.

# Example

```yaml
users:
- login: broadapp
  comment: "Broadapp technical account"
  groups: "broadgroup"
  authorized_keys:
  - keys/id_rsa.pub

- login: broaduser
  scope: control_nodes
  comment: "Broadapp user account"
  groups: "broadgroup",
  can_sudo_to: "hdfs, yarn"
  password: "$6$MySalt32$IrUOiWSpX.....8vkQfZgOslTQz.skFMhIWha.NLijJla/"
```

# Trick

A method to generate the crypted form of a password:

```bash
python -c 'import crypt; print crypt.crypt("xxxxxx", "$6$MySalt32$")'
```

