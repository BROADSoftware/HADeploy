# Copyright (C) 2017 BROADSoftware
#
# This file is part of HADeploy
#
# HADeploy is free software: you can redistribute it and/or modify
# it under the terms of the GNU General Public License as published by
# the Free Software Foundation, either version 3 of the License, or
# (at your option) any later version.
#
# HADeploy is distributed in the hope that it will be useful,
# but WITHOUT ANY WARRANTY; without even the implied warranty of
# MERCHANTABILITY or FITNESS FOR A PARTICULAR PURPOSE.  See the
# GNU General Public License for more details.
#
# You should have received a copy of the GNU General Public License
# along with HADeploy.  If not, see <http://www.gnu.org/licenses/>.

# ----------------------------------------------- Index in dict
SRC = "src"
DATA = "data"
HELPER = "helper"

VARS = "vars"

PLUGINS_PATHS = "plugins_paths"
PLUGINS = "plugins"

ANSIBLE_ROLES_PATHS = "ansible_roles_paths"

# ------------------------------------------------ Default values


DEFAULT_HDFS_KEYTABS_FOLDER="{{ansible_user_dir}}/.hadeploy/keytabs"

#DEFAULT_HDFS_RELAY_CACHE_FOLDER="{{ansible_user_dir}}/.hadeploy/files"
DEFAULT_TOOLS_FOLDER="/tmp/hadeploy_{{ansible_ssh_user}}"
DEFAULT_HDFS_RELAY_CACHE_FOLDER="/tmp/hadeploy_{{ansible_ssh_user}}/files"

# -------------- Shared between plugins 

INVENTORY="inventory"
HOST_BY_NAME="hostByName"
SSH_USER="ssh_user"

# default plugins list
#DEFAULT_PLUGINS = [ 'header', 'ansible_inventories', 'inventory', 'users', 'ranger', 'files', 'hdfs', 'hbase', 'hive', 'kafka', 'playbooks']
DEFAULT_PLUGINS = [ 'header', 'inventory', 'users', 'playbooks']

# Actions: deploy, remove, halt, launch, reset, report.
# To other pseudo/internal action:
# - groom: for grooming 
# - none: Do nothing, but build all templates, to check errors
#
DEPLOY_ACTION="deploy"
REMOVE_ACTION="remove"
NONE_ACTION="none"

