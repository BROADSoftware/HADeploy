# supervisor_programs

## Synopsis

Provide a list of program managed by one (or several) [supervisors](./supervisors) instances.

This is a reference part. Refer to the associated [`overview`](./supervisor_overview) for a more synthetical view.

## Attributes

Each item of the list has the following attributes:

Name | req? | 	Description
--- | ---  | ---
supervisor|yes|The supervisor managing this program
name|yes|Name of the program.
scope|no|On which target does this supervisor's program be deployed? May be:<ul><li>A single `host` name</li><li>A single `host_group` name</li><li>Several `hosts` or `host_groups`, separated by the character ':'</li></ul>Default to the supervisor's scope
command|yes if `conf_file_src` is not provided|The command to launch. Refer to the [supervisor documentation](http://supervisord.org/configuration.html#program-x-section-values)
no_remove|no|Boolean: Prevent this program to be removed when HADeploy will be used with `--action remove`.<br>Default: `no`
user|no|From the [supervisor documentation](http://supervisord.org/configuration.html#program-x-section-values): Instruct supervisord to use this UNIX user account as the account which runs the program. The user can only be switched if supervisord is run as the root user. If supervisord can’t switch to the specified user, the program will not be started.<br>Default is the supervisord's user.
state|no|<lu><li>`started`: The program will be started on deployment</li><li>`stopped`: The program will be stopped on deployment.</li><li>`current`: The program state will be left unchanged during deployment. (stopped on initial creation).</li></ul>Default value: `started`.
autostart|no|Boolean. If true, this program will start automatically when supervisord is started. Refer to the [supervisor documentation](http://supervisord.org/configuration.html#program-x-section-values)
process_name|no|Refer to the [supervisor documentation](http://supervisord.org/configuration.html#program-x-section-values)
numprocs|no|Integer. Refer to the [supervisor documentation](http://supervisord.org/configuration.html#program-x-section-values)
numprocs_start|no|Integer. Refer to the [supervisor documentation](http://supervisord.org/configuration.html#program-x-section-values)
priority|no|Integer. Refer to the [supervisor documentation](http://supervisord.org/configuration.html#program-x-section-values)
startsecs|no|Integer. Refer to the [supervisor documentation](http://supervisord.org/configuration.html#program-x-section-values)
startretries|no|Integer. Refer to the [supervisor documentation](http://supervisord.org/configuration.html#program-x-section-values)
autorestart|no|Refer to the [supervisor documentation](http://supervisord.org/configuration.html#program-x-section-values)
exitcodes|no|List of Integer. Refer to the [supervisor documentation](http://supervisord.org/configuration.html#program-x-section-values)
stopsignal|no|Refer to the [supervisor documentation](http://supervisord.org/configuration.html#program-x-section-values)
stopwaitsecs|no|Integer. Refer to the [supervisor documentation](http://supervisord.org/configuration.html#program-x-section-values)
stopasgroup|no|Boolean. Refer to the [supervisor documentation](http://supervisord.org/configuration.html#program-x-section-values). May be required if your program fork another one.
killasgroup|no|Boolean. Refer to the [supervisor documentation](http://supervisord.org/configuration.html#program-x-section-values)
redirect_stderr|no|Boolan. Refer to the [supervisor documentation](http://supervisord.org/configuration.html#program-x-section-values)
stdout_logfile|no|Refer to the [supervisor documentation](http://supervisord.org/configuration.html#program-x-section-values)
stdout_logfile_maxbytes|no|Refer to the [supervisor documentation](http://supervisord.org/configuration.html#program-x-section-values)
stdout_logfile_backups|no|Integer. Refer to the [supervisor documentation](http://supervisord.org/configuration.html#program-x-section-values)
stderr_logfile|no|Refer to the [supervisor documentation](http://supervisord.org/configuration.html#program-x-section-values)
stderr_logfile_maxbytes|no|Refer to the [supervisor documentation](http://supervisord.org/configuration.html#program-x-section-values)
stderr_logfile_backups|no|Integer. Refer to the [supervisor documentation](http://supervisord.org/configuration.html#program-x-section-values)
environment|no|List of String. Refer to the [supervisor documentation](http://supervisord.org/configuration.html#program-x-section-values)
directory|no|Refer to the [supervisor documentation](http://supervisord.org/configuration.html#program-x-section-values)
umask|no|Refer to the [supervisor documentation](http://supervisord.org/configuration.html#program-x-section-values)
when|no|Boolean. Allow [conditional deployment](../../more/conditional_deployment) of this item.<br>Default `True` 


## Example

```yaml
supervisor_programs:
- name: program1
  supervisor: tech1
  command: "/bin/bash /opt/tsupervisor/program1.sh"
```
This snippet create a program 'program1' running as a daemon. This program being a simple shell script (`program1.sh`) and will be managed by the [`supervisor named tech1`](./supervisors/#example).

This program can then be managed (stopped/restarted/...) by:

- The Web interface provided by the supervisor, if any.

- The command line interface `supervisorctl_tech1`

- HADeploy using `--action start` and `--action stop`.

Another example, with more parameters:

```yaml
supervisor_programs:
- name: program2
  supervisor: tech1
  command: "/bin/bash /opt/tsupervisor/program2.sh"
  stopasgroup: yes
  environment:
  - MY_HOME="/opt/program2"
  - JAVA_HOME="/usr/java/jdk1.8.0_74"
  directory: /opt/program2/work
  stdout_logfile: /opt/program2/logs/program2.out
  stderr_logfile: /opt/program2/logs/program2.err
```

## About managed programs

* **Programs meant to be run under supervisor should not daemonize themselves**. Instead, they should run in the foreground. They should not detach from the terminal from which they are started.
More info [here](http://supervisord.org/subprocess.html#nondaemonizing-of-subprocesses)

* If the launched programs fork one or several child processes, there may be a problem on stop. Only the initial process will be killed by supervisor, and all children will become orphan. 
There will be two solutions for this:

    * Catch the `stopsignal` and then kill all child processes.
    
    * Set the `stopasgroup` flag
    
    This last solution is of course the simplest. 
    
    A typical case encountering this issue is a java programs launched by a wrapper script.


