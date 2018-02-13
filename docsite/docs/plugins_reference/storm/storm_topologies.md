# storm_topologies

## Synopsis

Provide a list of Storm topologies to manage

This is a reference part. Refer to the associated [`overview`](./storm_overview) for a more synthetical view.

## Attributes

Each item of the list has the following attribute: 

Name | req? | 	Description
--- | ---  | ---
name|yes|Name of the topology.
launching_cmd|yes|The command to launch this topology. May be 'storm jar ...' for simple case. A launching script for more complex one. 
launching_dir|no|Will `cd` in this folder before launching 'launching_cmd' Must be an absolute path.<br>Default: `~`
wait_time_secs|no|The wait_time in seconds provided to the `kill' command (Delay between spouts deactivation and topology destruction)<br>Default: 30.
timeout_secs|no|Timeout before raising an error value when waiting a target state.<br>Default: Value set by [`storm_relay`](./storm_relay):`default_timeout_secs`
ranger_policy|no|Definition of Apache Ranger policy bound to this topology. Parameters are same as [`storm_ranger_policies`](../ranger/storm_ranger_policies) except than `topologies` should not be defined.<br>The policy name can be explicitly defined. Otherwise, a name will be generated as "`_<topology>_`".<br>See example below for more information
no_remove|no|Bolean. Used only for eventual associated ranger policy.  Setting to `yes`prevent this policy to be remove when  HADeploy will be used in REMOVE mode.<br>Default: `no`.
when|no|Boolean. Allow [conditional deployment](../../more/conditional_deployment) of this item.<br>Default `True` 

# Asynchronous launch

To preserve launching time, HADeploy launch all topologies in a simultaneous way, by using some asynchronous procesing. 

This can lead to difficulty to debug, as failing launch des not raise any error, except a timeout after quite long time. More on that [here](./storm_overview#asynchronous-mode)

# Example

```
storm_topologies:
- name: storm1
  launching_dir: ${basedir1}
  launching_cmd: "storm jar	./storm1-${storm1_version}-uber.jar com.mydomain.storm1.ClusterTopology"
  wait_time_secs: 10
- name: storm2
  launching_dir: ${basedir2}
  launching_cmd: "./launch2.sh"
  wait_time_secs: 15
```

```
storm_topologies:
- name: storm2
  launching_dir: /opt/storm2
  launching_cmd: "./launch2.sh"
  wait_time_secs: 10
  ranger_policy:
    audit: yes
    enabled: yes
    permissions:
    - users:
      - stormrunner
      accesses:
	  - 'fileDownload'
	  - 'killTopology'
	  - 'rebalance'
	  - 'activate'
	  - 'deactivate'
	  - 'getTopologyConf'
	  - 'getTopology'
	  - 'getUserTopology'
	  - 'getTopologyInfo'
```      

# The launching cmd or script

Here is some requirement about the launching command or script.

- It must ensure setting topology name same as the one provided in this description.

- If `launching_dir` is not defined, the the `launching_cmd` must be refer to absolute path for all its part.

- It must be fully synchronous, i.e. not running in the background. 

## For kerberos: client_jaas.conf

In a kerboros secured context, the storm command use a configuration file to define how it will authenticate against the Storm server. 

For HADeploy usage, this file must be configured to use the current ticket in the local cache. Unfortunatly, this is not always the case. Sometime, it may be configured to use another principal and keytab.

If this is the case, we suggest to explicitly provide such a configuration file: For example, in an Hortonworks context, one can write:

```
storm -c java.security.auth.login.config=/usr/hdp/current/storm-client/conf/client_jaas.conf jar ./myjar.jar com.mydomain.mytopology.ClusterTopology  $1
```

Here is the content of a `client_jaas.conf` we can use:

```
StormClient {
   com.sun.security.auth.module.Krb5LoginModule required
   useTicketCache=true
   renewTicket=true
   serviceName="nimbus";
};
```


 
