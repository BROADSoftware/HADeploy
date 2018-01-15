# yarn_ranger_policies

## Synopsis

Allow definition of a list of Apache Ranger policies for setting Yarn permissions

## Attributes

Each item of the list has the following attributes:

Name | req?	|	Description
--- | --- | ---
name|yes|The policy name. Will be decorated to mark it as managed by HADeploy, as described in [ranger_relay](./ranger_relay).
queues|yes|A list of Yarn queues on which this policy will apply. Accept wildcard characters '*' and '?'.
audit|no|Did this policy is audited by Ranger.<br>Default: `yes`
enabled|no|Allow this policy to be disabled.<br>Default: `yes`
recursive|no|Did this policy apply recursively.<br>Default: `yes`
no_remove|False|Boolean: Prevent this policy to be removed when HADeploy will be used in REMOVE mode.<br>Default: `no`
permissions|yes|A list of permissions defining rights granted by this policy. See below
when|no|Boolean. Allow [conditional deployment](../../more/conditional_deployment) of this item.<br>Default `True` 


## permissions

Each item of the permission list has the following attributes:

Name | req?	| Description
--- | ---  | ---
users|yes if `groups` is undefined|A list of users this policy will apply on. May be empty if some groups are defined.
groups|yes if `users` is undefined|A list of groups this policy will apply on. May be empty if some users are defined.
accesses|yes|The list of rights granted by this policy. May include `submit-app` and `admin-queue`.
delegate_admin|no|When a policy is assigned to a user or a group of users those users become the delegated admin. The delegated admin can update and delete the policies.<br>Default: `no`

## Examples
```yaml
yarn_ranger_policies:
- name: puser1
  queues: 
  - user1
  audit: true
  permissions:
  - groups: 
    - users
    accesses:
    - submit-app
  - users:
    - admin 
    accesses:
    - submit-app
    - admin-queue
    delegate_admin: true
```