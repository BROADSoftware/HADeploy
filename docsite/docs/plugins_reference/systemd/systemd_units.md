# systemd_units

## Synopsis

Provide a list of `systemd` service units, related to the deployed application.

This will allow to declare node local application processes as system services. All `systemctl` commands (start, stop, status, ...) will then apply to this newly created service.

This module require `root` access on the target host. If you need to deploy local services under the control of a non-priviledged user, you can use the ['supervisor'](../supervisor/supervisor_overview) module.

This module will also allow HADeploy to handle start and stop of the defined services.

## Attributes

Each item of the list has the following attributes:

Name | req? | 	Description
--- | ---  | ---
name|yes|Name of the service.
scope|yes|On which target does this file be deployed? May be:<ul><li>A single `host` name</li><li>A single `host_group` name</li><li>Several `hosts` or `host_groups`, separated by the character ':'</li></ul>
unit_file|yes|The unit file, describing how and when this service will be launched. See below
no_remove|no|Boolean: Prevent this service to be removed when HADeploy will be used with `--action remove`.<br>Default: `no`
enabled|no|Is this service start on system boot ? Default: `yes`.
state|no|<lu><li>`started`: The service will be started on deployment</li><li>`stopped`: The service will be stopped on deployment.</li><li>`current`: The service state will be left unchanged during deployment. (stopped on initial creation).</li></ul>Default value: `current`.
action_on_notify|no|Action to be performed when this service is notified of the modification of some file it depend on.<br>Can be `restart`, `reload` or `none`. Default is `restart`.<br>Not all services support `reload`.<br>See the `notify` attribute the [`files`](../files/files) module.

## Unit files

A systemd unit file encode information about several system object type, such as services, device, mount point, etc... In our case, only services unit are of interest.

A systemd.service unit file will provide all information to handle operation of a service life cycle, such as start, stop, restart on failure, reload, etc.. Full documentation can be found [here](https://www.freedesktop.org/software/systemd/man/systemd.service.html#)

HADeploy will place the provided unit file in the `/usr/lib/systemd/system` folder and trigger appropriate opeation to make systemd aware of this newly created (or modified) file.

### Unit file example

The following is a unit file for a simple service providing a REST interface.

```
[Unit]
Description=HARelay (Helper REST server for Hadoop)

[Service]
Type=simple
User={{user}}
Group={{group}}
SyslogIdentifier=harelay
TimeoutSec=15
Restart=always
ExecStart=/bin/bash /opt/harelay/bin/harelay -c /opt/harelay/etc/config.conf

[Install]
WantedBy=multi-user.target

```
Note the following for the above example:

- The `Type=simple` means the process lauching by `ExecStart` is the main process and will NOT exit. In other word, it does not 'daemonize' itself.

- The process will be restarted by systemd in case of unattended exit, in all case (i.e on failure).

- The process will be executed as a specific user/group, defined by the `{{user}}` and `{{group}}` variable. It is expected these variables are set in a `vars` block in the HADeploy file. And than the unit file is a 'template'.

## Example

```yaml
vars:
  user: harelay
  group: harelay

files:
- { scope: edge_nodes, notify: harelay, src: "tmpl://harelay", dest_folder: "/opt/harelay/bin", owner: "${user}", group: "${group}", mode: "0755" }
- { scope: edge_nodes, notify: harelay, src: "tmpl://config.conf", dest_folder: "/opt/harelay/etc", owner: "${user}", group: "${group}", mode: "0644" }

systemd_units:
- name: harelay
  scope: edge_nodes
  unit_file: "tmpl://harelay.service.j2"
  
```

Note the `notify` attribute in the `files` entries, to trigger a service restart in case of modification of these files.

## Actions `stop` and `start`

The `services` plugin introduce two new actions:

```sh
hadeploy --src ..... --action stop
```

Will stop all services described by the `systemd_units` list. And 

```sh
hadeploy --src ..... --action start
```

Will start the same services. 
