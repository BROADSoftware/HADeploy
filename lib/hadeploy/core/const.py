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

# default plugins list
DEFAULT_PLUGINS = [ 'header', 'ansible_inventory', 'inventory', 'users', 'ranger', 'files', 'hdfs', 'hbase', 'hive', 'kafka', 'footer']

DEFAULT_HDFS_RELAY_CACHE_FOLDER='/var/cache/hadeploy/files'

DEFAULT_TOOLS_FOLDER="/opt/hadeploy"