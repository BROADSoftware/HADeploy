# hdfs_ranger_policies

Synopsis
Allow definition of a list of Apache Ranger policies for setting HDFS permissions
Attributes
Each item of the list has the following attributes:
Name	req?	Default	Description
name	yes		The policy name. Will be decorated to mark it as managed by HADeploy, as described in ranger_relay.
paths	yes		A list of HDFS path on which this policy will apply. Accept wildcard characters '*' and '?'
recursive	no	True	Did this policy apply recursively.
audit	no	True	Did this policy is audited by Ranger.
enabled	no	True	Allow this policy to be disabled.
no_remove	no	False	Boolean: Prevent this policy to be removed when HADeploy will be used in REMOVE mode
permissions	yes		A list of permissions defining rights granted by this policy. See below
permissions
Each item of the permission list has the following attributes:
Name	req?	Default	Description
users			A list of users this policy will apply on. May be empty if some groups are defined.
groups			A list of groups this policy will apply on. May be empty if some users are defined.
accesses	yes		The list of rights granted by this policy. May include Read, Write and Execute.
delegate_admin	no	False	When a policy is assigned to a user or a group of users those users become the delegated admin. The delegated admin can update, delete the policies
Examples
hdfs_ranger_policies:
- name: "/apps/pixo"
  paths: [ "/apps/pixo" ]
  permissions:
  - { users: [ user1 ], groups: [ grp1, grp2 ], accesses: [ read, write, execute ] }
 
