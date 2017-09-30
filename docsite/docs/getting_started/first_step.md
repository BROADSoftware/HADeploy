# First step

An application deployment is performed based on a file (or a set of files) describing all its components. This description represents a target state HADeploy will have to reach by performing all transformation operation.

This description can be defined in a single file, or can be spread over several files for ease of management and separation of concerns.

All these files are defined using YAML syntax, as this syntax will allow both readability and concision. (If necessary, you will find a bunch of YAML tutorial on the net).

Following is a simple deployment: 

```yaml
# We only need to access the cluster's edge node. (1)
hosts:
- name: en
  ssh_host: en.cluster1.mydomain.com
  ssh_user: root
  ssh_private_key_file: "keys/build_key" 

# HDFS operations will be issued from this host: (2)
hdfs_relay:
  host: en

# Folders creation (3)
folders:
- { scope: en, path: /opt/broadapp, owner: broaduser, group: broadgroup, mode: "0755" }
- { scope: hdfs, path: /apps/broadapp, owner: broaduser, group: broadgroup, mode: "0755" }

# Files copy (4)
files:
- { scope: en, src: "http://my.server.com/repository/broadapp-0.3.2.jar", dest_folder: "/opt/broadapp",  owner: broaduser, group: broadgroup, mode: "0644" }
- { scope: en, src: "tmpl://launcher.sh", dest_folder: /opt/broadapp, owner: broaduser, group: broadgroup, mode: "0644" }

- { scope: hdfs, src: "tmpl://broadapp.cfg", dest_folder: "/apps/broadapp", owner: broaduser, group: broadgroup, mode: "0644" }

```

(1) First, we begin by the inventory part, describing the target cluster. Here, we will just need access to the edge node. 

(2) Then we define this last as the relay we will use to access HDFS.

> <sub>Issuing some commands to specifics subsystem, such as HDFS require a quite complex client configuration. 
To avoid this, HADeploy will not issue such command directly, but push the command on one of the cluster node (Typically an Edge node)</sub>

(3) Then, we create folders to store application items, one on the edge node, and one on HDFS. Note we also adjust related permissions and ownership.

(4) And last, we deploy the application's files. A jar and the launching script on the edge node, and a config file on HDFS.

> <sub>The launcher and config file are prefixed by `tmpl`. This means they can include parameters set on deployment to configure them accordingly to the target infrastructure. Such file will be called 'tempalates'</sub>




