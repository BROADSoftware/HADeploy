# HADeploy

HADeploy is a tool specially designed to deploy application in BigData/NoSQL context with Hadoop cluster as first target.

In such context, deploying an application is not only matter of deploying some jar in some place. It also means creating a bunch of associated resources such as Hive table, Kafka topic, HBase table, HDFS folders and files, systems account, etc.

## Documentation

You will find documentation [at this location](https://github.com/BROADSoftware/hadeploy/blob/master/docs/hadeploy.pdf)

## Base principles

###Reconciliation and idempotence

HADeploy is a purely descriptive tool. As such usage will consist of defining the expected state of the
deployed application and let the tool perform the reconciliation between expected and actual state.
Such principle means HADeploy is a fully idempotent tools, as if expected state match the actual ones,
the tool will not perform any further actions.

###Infrastructure independency.

Deploying an application not only need to be aware of all application components, but also of the
target infrastructure.
Such infrastructure may be described separately of the main application description, or its information
could be extracted from other Infrastructure management tools (Such as Chef, Puppet, Ansible ...).

###Continuous delivery

As a reconciliation tool, HADeploy can be used not only for the initial deployment of the application,
but also for all its lifecycle (update and removal).

As such it will make its best effort to perform all non-destructive operation to modify actual resource's
state to reach target configuration.

###Context management
HADeploy allow name of all resources to include variables part, thus allowing several deployment of
the same application to coexist on the same infrastructure.

###Application Removal

As HADeploy knows about all the components of your application, it provides a REMOVAL mode, which restores the target cluster in its initial state.
