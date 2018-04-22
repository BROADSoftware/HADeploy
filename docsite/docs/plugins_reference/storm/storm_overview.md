# Storm plugin: Overview

Aim of the Storm plugin is to handle Storm topologies lifecycle.

- Start topologies

- Stop topologies

- Get current topologies status

This is achieved by:

- Issuing command to the Storm subsystem through the Storm UI REST API

- Start topology when required using a user provided launching script.

All these operations are performed on a specific node included in the cluster. This node is designated as a [`storm_relay`](./storm_relay)

## Topologies deployment.

The deployment of each topology by itself is NOT in the scope of this plugin. Typically this consist in:

- Create a deployment folder.

- Deploying a jar

- Deploying one or several configuration files

- Enventually, deploying a script to launch the topology.

This at least on the Storm relay node and eventually on one or several other nodes, for resiliency. 

All these tasks can be achieved using this HADeploy [`folders`](../files/folders) and [`files`](../files/files) specification. 

Templating mechanism and support of Maven repository built in the [`files`](../files/files) plugin will be of great help here. 


## Actions `stop`,`start` and `status`

The `storm` plugin introduce three new actions:

```sh
hadeploy --src ..... --action start
```

Will start all toplogies described by the [`storm_topologies`](./storm_topologies) list. And 

```sh
hadeploy --src ..... --action stop
```

Will kill the same toplogies. While 

```sh
hadeploy --src ..... --action status
```

will display current status of the topologies, in a rather primitive form.

Also, the Storm plugin kill all running topologies at one of the first step of the removal action (`--action remove`).

Of course, all this will occur only on topologies HADeploy is aware of (Defined with [`storm_topologies`](./storm_topologies)). Other topologies will not be impacted.

## Asynchronous mode

A single topology launch take a signifiant amount of time. When there are several ones to launch, performing all launch simultaneously can save a lot of time. This is the default behavior of HADeploy.

In this default mode, all launching commands are run in a detached mode. Then HADeploy wait for all topologies to reach the `active` state.

But this mode has a drawback. If a launch fail, there is no easy way to get the error message. 
This is why this mode can be deactivated by setting the `async` attribute of [`storm_relay`](./storm_relay) to false. 
In such case, topologies wil be launched one at a time, and in case of error, processing will stop and appropriate error message will be raised.

### Topologies killing.

When HADeploy is instructed to halt all topologies (`--action stop`), it also perform this task asynchronously.

- All topologies are swithed to the `KILLED` state.

- Then HADeploy wait for all topologies to terminate, after the defined 'wait_time_secs' (Delay between spouts deactivation and topology destruction)

Setting the `async` flag of of [`storm_relay`](./storm_relay) to false has no effect on this behavior.

## Notifications: Topologies restart

Let's say we now want to update the topology's jar or one of the associated configuration files.

We can modify it and trigger a new deployment. HADeploy will notice the modification and push the new version on the target hosts. But, the running topologies will be unafected.

We can restart it manually. But, HADeploy provide a mechanisme to automate this. By adding a `notify` attribute to the [`files`](../files/files) definition. See the example below.

Note also if the deployment trigger the restart of several topologies, both kill and restart will be performed asynchronously, to save time.

## Example

Here is a snippet describing the deployment of two very simple topologies:

```yaml
vars:
  storm_launcher_host: en1
  basedir1: "/opt/storm1"
  basedir2: "/opt/storm2"
  user: stormrunner
  group: stormrunner
  storm1_version: "0.1.0-SNAPSHOT"
  storm2_version: "0.3.0-SNAPSHOT"

storm_relay:
  host: ${storm_launcher_host}
  storm_ui_url: "http://stui.mycluster.mydomain.com:8744/"

maven_repositories:
- name: myrepo
  snapshots_url: http://myrepo.mydomain.com/nexus/repository/maven-snapshots/
  releases_url: http://myrepo.mydomain.com/nexus/repository/maven-releases/

folders:
- { path: "${basedir1}", scope: "${storm_launcher_host}", owner: "${user}", group: "${group}", mode: "755" }
- { path: "${basedir2}", scope: "${storm_launcher_host}", owner: "${user}", group: "${group}", mode: "755" }

files:
- { scope: "${storm_launcher_host}", src: "mvn://myrepo/com.mydomain/storm1/${storm1_version}/uber", 
    notify: ['storm://storm1'], dest_folder: "${basedir1}", owner: "${user}", group: "${group}", mode: "0644" }
- { scope: "${storm_launcher_host}", src: "mvn://myrepo/com.mydomain/storm2/${storm2_version}/uber", 
    notify: ['storm://storm2'], dest_folder: "${basedir2}", owner: "${user}", group: "${group}", mode: "0644" }

- { scope: "${storm_launcher_host}", src: "tmpl://launch2.sh", dest_folder: "${basedir2}", 
    notify: ['storm://storm2'], owner: "${user}", group: "${group}", mode: "0744" }


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
This is of course not complete, as it lack at least the target cluster definition.

Please refer to [`storm_relay`](./storm_relay) and [`storm_topologies`](./storm_topologies) for a complete description. And to [`files`](../files/files) for the `notify` syntax.

Of course, before being able to launch the topologies (`--action start`), a deployment must be performed before (`--action deploy`)


