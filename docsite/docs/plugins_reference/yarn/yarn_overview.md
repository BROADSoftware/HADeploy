# Yarn plugin: Overview

### Goal

Aim of the Yarn plugin is to handle Yarn services Life cycle

- Start Yarn services

- Stop Yarn services

- Get current Yarn service status

By 'Yarn services', we mean Yarn jobs running indefinitely, such as Spark Streaming jobs. 

This all also named as 'Yarn Long Running Services', or 'Yarn Long Running Jobs'.

***This plugin is NOT intended to manage Batch jobs.***

### How it works

This is achieved by:

- Issuing command to the Yarn Resource Manager through its REST API

- Start Yarn service when required using a user provided launching script.

All these operations are performed on a specific node included in the cluster. This node is designated as a [`yarn_relay`](./yarn_relay).

### Requirement

There is some requirement for the launching script.

- HADeploy identify Yarn services by its name. So care must be taken to ensure the service name match the one provided in the definition. 
This can easily be achieved using the `--name` option on the yarn/spark `submit` command. See example below.

- The launching script must exit after launching the job. For Spark, the `--conf "spark.yarn.submit.waitAppCompletion=false"` option can be used. See example below.

## Yarn services deployment.

The deployment of each services by itself is NOT in the scope of this plugin. Typically this consist in:

- Create a deployment folder.

- Deploying a jar

- Deploying one or several configuration files

- Eventually, deploying a script to launch the service.

This at least on the Yarn relay node and eventually on one or several other nodes, for resiliency. 

All these tasks can be achieved using this HADeploy [`folders`](../files/folders) and [`files`](../files/files) specification. 

Templating mechanism and support of Maven repository built in the [`files`](../files/files) plugin will be of great help here. 


## Actions `stop`,`start` and `status`

The `yarn` plugin introduce three new actions:

```sh
hadeploy --src ..... --action start
```

Will start all services described by the [`yarn_services`](./yarn_services) list. And 

```sh
hadeploy --src ..... --action stop
```

Will kill the same services. While 

```sh
hadeploy --src ..... --action status
```

will display current status of the services, in a rather primitive form.

Also, the Yarn plugin kill all running services at one of the first step of the removal action (`--action remove`).

Of course, all this will occur only on services HADeploy is aware of (Defined with [`yarn_services`](./yarn_services)). Other services will not be impacted.

## Services shutdown.

When HADeploy is instructed to halt all services (`--action stop`), by default, it will use the RM REST API, setting application in the 'KILLED' state. This is equivalent to a `yarn application --kill` command.

An alternate way to shutdown a yarn job is to provide a script issuing the kill command, and to define such script using the `killing_cmd` attribute. This can be used in the following case: 

- If your application provide a more graceful shutdown method

- If your cluster is secured by Kerberos and if the RM REST API is not secured by SPNEGO. In such case, using such API will not allow setting of the appropriate user, and a killing script is a far more easy solution. 

## Notifications: Services restart

Let's say we now want to update the service's jar or one of the associated configuration files.

We can modify it and trigger a new deployment. HADeploy will notice the modification and push the new version on the target hosts. But, the running services will be unaffected.

We can restart it manually. But, HADeploy provide a mechanism to automate this. By adding a `notify` attribute to the [`files`](../files/files) definition. See the example below.

## Ranger support.

Ranger handling on Yarn jobs is based on Yarn Queue management. HADeploy allow you to define such permission using [yarn_ranger_policies](../ranger/yarn_ranger_policies/).

## Example

Here is a snippet describing the deployment of a simple Yarn services 'datastep':

```yaml

vars:
  yarn_launcher_host: en1
  basedir: "/opt/datastep"
  user: dsrunner
  group: dsrunner
  datastep_version: "0.1.0-SNAPSHOT"

yarn_relay:
  host: ${yarn_launcher_host}

maven_repositories:
- name: myrepo
  snapshots_url: http://myrepo.mydomain.com/nexus/repository/maven-snapshots/
  releases_url: http://myrepo.mydomain.com/nexus/repository/maven-releases/

folders:
- { path: "${basedir}", scope: "${yarn_launcher_host}", owner: "${user}", group: "${group}", mode: "755" }

files:
- { scope: "${yarn_launcher_host}", src: "mvn://myrepo/com.mydomain/datastep/${datastep_version}/uber", 
    notify: ['yarn://datastep'], dest_folder: "${basedir}", owner: "${user}", group: "${group}", mode: "0644" }

- { scope: "${yarn_launcher_host}", src: "tmpl://submit.sh", dest_folder: "${basedir}", 
    notify: ['yarn://datastep'], owner: "${user}", group: "${group}", mode: "0744" }

- { scope: "${yarn_launcher_host}", src: "tmpl://kill.sh", dest_folder: "${basedir}", 
    notify: ['yarn://datastep'], owner: "${user}", group: "${group}", mode: "0744" }

yarn_services:
- name: datastep
  launching_cmd: ./submit.sh
  launching_cmd: ./kill.sh
  launching_dir: ${basedir}

```

And here is what could be a simplistic submit script template:

```bash
#/bin/bash

{% if kerberos is defined and kerberos %}
kinit -kt /etc/security/keytabs/{{user}}.keytab {{user}}
{% endif %}

spark-submit --name datastep --master yarn --deploy-mode cluster --class com.mydomain.datastep.Main \
	--conf "spark.yarn.submit.waitAppCompletion=false" \
	--jars {{basedir}}/datastep-{{datastep_version}}-uber.jar 

{% if kerberos is defined and kerberos %}
kdestroy
{% endif %}

```

And a killing script:

```bash
#/bin/bash

{% if kerberos is defined and kerberos %}
kinit -kt /etc/security/keytabs/{{user}}.keytab {{user}}
{% endif %}

APPLICATION_ID=$(yarn application --appStates RUNNING --list 2>/dev/null | awk "{ if (\$2==\"datastep\") print \$1 }")

if [ "$APPLICATION_ID" = "" ]
then
	echo "?? Not running"
else
	yarn application --kill ${APPLICATION_ID} 2>/dev/null
	echo "$APPLICATION_ID Killed!"
fi

{% if kerberos is defined and kerberos %}
kdestroy
{% endif %}

```

This is of course not complete, as it lack at least the target cluster definition.

Please refer to [`yarn_relay`](./yarn_relay) and [`yarn_services`](./yarn_services) for a complete description. And to [`files`](../files/files) for the `notify` syntax.

Of course, before being able to launch the services (`--action start`), a deployment must be performed before (`--action deploy`)

