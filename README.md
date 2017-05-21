# HADeploy

HADeploy is a tool specially designed to deploy application in BigData/NoSQL context with Hadoop cluster as first target.

In such context, deploying an application is not only matter of deploying some jar in some place. It also means creating a bunch of associated resources such as Hive table, Kafka topic, HBase table, HDFS folders and files, systems account, etc.

## Documentation

You will find documentation [at this location](http://www.hadeploy.com/)

## Base principles

### Application manifest

An application can be fully described in one file, hosting all components and resources description.

### Infrastructure independency

Application file is independent of target physical infrastructure. This target is defined in another file and HADeploy will take care of the merge on deployment

### Environment independency.

In the same way, the application file is independent of the environment (DEV, INT, PPRD, PROD,..). This ensure coherency and repeatable deployments among these contexts

### Declarative programming and reconciliation

HADeploy is a purely descriptive tool. As such usage will consist of defining the expected state of the deployed application and let the tool perform the reconciliation between expected and actual state.

### Idempotence

Such principle means HADeploy is a fully idempotent tools, as if expected state match the actual ones, the tool will not perform any further actions.

### Application instance isolation.

A typical deployment pattern allowed by HADeploy is to define ‘Application Container’, or ‘Application Lane’. Then several instance (or version) of an application can be installed and run in parallel.

### Kerberos support

HADeploy is able to deploy application on a Hadoop cluster secured by Kerberos. 

### Rights management

HADeploy will manage all permissions associated to the deployed components and resources.

### Plugins architecture

HADeploy is designed with a highly modular plugins architecture, thus allowing easy third party extension.

### Application Removal

As HADeploy knows about all the components of your application, it provides a REMOVAL mode, which restores the target cluster in its initial state.

### Open Source

HADeploy is a fully open source project, under GNU General Public License.

