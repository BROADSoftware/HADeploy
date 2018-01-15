# kafka_ranger_policies

## Synopsis

Allow definition of a list of Apache Ranger policies for setting Kafka permissions

## Attributes

Each item of the list has the following attributes:

Name | req?	 |	Description
--- | ---  | ---
name|yes|The policy name. Will be decorated to mark it as managed by HADeploy, as described in [ranger_relay](./ranger_relay).
topics|yes|A list of topics on which this policy will apply. Accept wildcard characters '*' and '?'.
audit|no|Did this policy is audited by Ranger.<br>Default: `yes`
enabled|no|Allow this policy to be disabled.<br>Default: `yes`
no_remove|no|Boolean: Prevent this policy to be removed when HADeploy will be used in REMOVE mode.<br>Default: `no`
permissions|yes|A list of permissions defining rights granted by this policy. See below
when|no|Boolean. Allow [conditional deployment](../../more/conditional_deployment) of this item.<br>Default `True` 

## Permissions

Each item of the permission list has the following attributes:

Name | req?	| Description
--- | ---  | ---
users|yes if `groups` is undefined|A list of users this policy will apply on. May be empty if some groups are defined.
groups|yes if `users` is undefined|A list of groups this policy will apply on. May be empty if some users are defined.
ip_addresses|no|A list of source IP addresses this policy will apply on.
accesses|yes|The list of rights granted by this policy. May include `publish`, `consume`, `configure`, `describe`, `create`, `delete` and `kafka_admin`.
delegate_admin|no|When a policy is assigned to a user or a group of users those users become the delegated admin. The delegated admin can update, delete the policies.<br>Default: `no`

##Examples
```yaml
kafka_ranger_policies:
- name: "app1Kafka"
  topics: 
  - "app1_*"
  permissions:
  - users:
    - app1Admin
    accesses:
    - publish
    - consume
    - configure
    - describe
    - create
    - delete
    - kafka_admin
  - groups:
    - app1Consumers
    accesses:
    - consume
``` 


