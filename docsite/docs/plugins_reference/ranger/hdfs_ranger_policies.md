# hdfs_ranger_policies

## Synopsis

Allow definition of a list of Apache Ranger policies for setting HDFS permissions

## Attributes
Each item of the list has the following attributes:

Name | req?	 |	Description
--- | ---  | ---
name|yes|The policy name. Will be decorated to mark it as managed by HADeploy, as described in [`ranger_relay`](./ranger_relay).
paths|yes|A list of HDFS path on which this policy will apply. Accept wildcard characters '*' and '?'
recursive|no|Did this policy apply recursively.<br>Default: `yes`
audit|no|Did this policy is audited by Ranger.<br>Default: `yes`
enabled|no|Allow this policy to be disabled.<br>Default: `yes`
no_remove|no|Boolean: Prevent this policy to be removed when HADeploy will be used in REMOVE mode.<br>Default: `no`
permissions|yes|A list of permissions defining rights granted by this policy. See below

## permissions

Each item of the permission list has the following attributes:

Name | req?	| Description
--- | ---  | ---
users|yes if `groups` is undefined|A list of users this policy will apply on. May be empty if some groups are defined.
groups|yes if `users` is undefined|A list of groups this policy will apply on. May be empty if some users are defined.
accesses|yes|The list of rights granted by this policy. May include `read`, `write` and `execute`.
delegate_admin|no|When a policy is assigned to a user or a group of users those users become the delegated admin. The delegated admin can update and delete the policies.<br>Default: `no`

## Examples
```yaml
hdfs_ranger_policies:
- name: "/apps/pixo"
  paths: [ "/apps/pixo" ]
  permissions:
  - { users: [ user1 ], groups: [ grp1, grp2 ], accesses: [ read, write, execute ] }
``` 
