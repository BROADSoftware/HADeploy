# yarn_services

## Synopsis

Provide a list of Yarn services to manage

This is a reference part. Refer to the associated [`overview`](./yarn_overview) for a more synthetical view.

## Attributes

Each item of the list has the following attribute: 

Name | req? | 	Description
--- | ---  | ---
name|yes|Name of the service. This should match the name of the batch job.
launching_cmd|yes|The command to launch this service. Typically call a script hosting a `spark-submit` or a `yarn jar` command. 
launching_dir|no|Will `cd` in this folder before launching 'launching_cmd' Must be an absolute path.<br>Default: `~`
killing_cmd|no|The command to kill this service. If not provided, the service will be killed using the Resource Manager REST API. See [Overview/Service shutdown](./yarn_overview/#services-shutdown)  
timeout_secs|no|Timeout before raising an error value when waiting a target state.<br>Default: Value set by [`yarn_relay`](./yarn_relay):`default_timeout_secs`
when|no|Boolean. Allow [conditional deployment](../../more/conditional_deployment) of this item.<br>Default `True` 


# Example

```
yarn_services:
- name: datastep
  launching_cmd: ./launcher.sh
  launching_dir: ${basedir}
```      

# The launching script

Here is some requirement about the launching script.

- HADeploy identify Yarn services by its name. So care must be taken to ensure the service name match the one provided in the definition. This can easily be achieved using the `--name` option on the yarn/spark `submit` command. See [example here](./yarn_overview/#example)

- The launching script be synchronous (not running in background) but must exit after launching the job. For Spark, the `--conf "spark.yarn.submit.waitAppCompletion=false"` option can be used. See example below.


 
