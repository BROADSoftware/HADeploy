# hbase_ranger_policies

## Synopsis

Allow definition of a list of Apache Ranger policies for setting HBase permissions

## Attributes

Each item of the list has the following attributes:

Name | req?	| Default |	Description
--- | --- | --- | ---
name|yes||The policy name. Will be decorated to mark it as managed by HADeploy, as described in [ranger_relay](./ranger_relay).
tables|yes||A list of HBase tables on which this policy will apply. Table should be expressed as `<namespace>:<tablename>`. Accept wildcard characters '*' and '?'.
column_families|no|`"*"`|A list of column families on which the policy will apply.
columns|no|`"*"`|A list of columns on which the policy will apply.
audit|no|True|Did this policy is audited by Ranger.
enabled|no|True|Allow this policy to be disabled.
no_remove|no|False|Boolean: Prevent this policy to be removed when HADeploy will be used in REMOVE mode
permissions|yes||A list of permissions defining rights granted by this policy. See below

## permissions

Each item of the permission list has the following attributes:

Name | req?	| Default |	Description
--- | --- | --- | ---
users|||A list of users this policy will apply on. May be empty if some groups are defined.
groups|||A list of groups this policy will apply on. May be empty if some users are defined.
accesses|yes||The list of rights granted by this policy. May include Read, Write, Create and Admin.
delegate_admin|no|False|When a policy is assigned to a user or a group of users those users become the delegated admin. The delegated admin can update and delete the policies

## Examples
```yaml
hbase_ranger_policies:
- name: "FullAccessToNamespace1"
  tables: [ "namespace1:*" ]
  permissions:
  - users:
    - ns1admin
    accesses:
    - read
    - write
    - create
    - admin
  - groups:
    - someUsers
    users:
    - anotherUser
    accesses:
    - read
- name: "ReadAccesstoTableData1InNamespace2"
  tables: [ "namespace2:data1" ]
  permissions:
  - groups:
    - users
    accesses:
    - read
```