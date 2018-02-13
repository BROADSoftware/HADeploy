# storm_ranger_policies

## Synopsis

Allow definition of a list of Apache Ranger policies for setting permissions on Storm server access

## Attributes

Each item of the list has the following attributes:

Name | req?	 |	Description
--- | ---  | ---
name|yes|The policy name. Will be decorated to mark it as managed by HADeploy, as described in [ranger_relay](./ranger_relay).
topologies|yes|A list of topologies on which this policy will apply. Accept wildcard characters '*' and '?'.
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
accesses|yes|The list of rights granted by this policy. May include `submitTopology`, `fileUpload`, `fileDownload`, `killTopology`, `rebalance`, `activate`, `deactivate`, `getTopologyConf`, `getTopology`, `getUserTopology`, `getTopologyInfo` and `uploadNewCredentials`.
delegate_admin|no|When a policy is assigned to a user or a group of users those users become the delegated admin. The delegated admin can update, delete the policies.<br>Default: `no`

##Examples

This example will:

- Grant the right to 'stormrunner' user to launch new topology

- Grant all rights to 'stormrunner' on all topologies where name begin with 'storm'.

```yaml
storm_ranger_policies:
- name: "stormrunnerAsSubmitter"
  topologies: 
  - "*"
  - "dummy1"
  permissions:
  - users:
    - stormrunner
    accesses:
    - 'submitTopology'
    - 'fileUpload'
    
- name: "stormrunnerAsPartialAdmin"
  topologies: 
  - "storm*"
  permissions:
  - users:
    - stormrunner
    accesses:
    - 'submitTopology'
    - 'fileUpload'
    - 'fileDownload'
    - 'killTopology'
    - 'rebalance'
    - 'activate'
    - 'deactivate'
    - 'getTopologyConf'
    - 'getTopology'
    - 'getUserTopology'
    - 'getTopologyInfo'
    - 'uploadNewCredentials'
``` 

Note the trick on the first definition: Adding a 'dummy1' prevent this rule to clash with another one applying on all topologies (Ranger does to allow two policies to apply on the same set of topologies).



