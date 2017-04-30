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
HADEPLOY_HOME = "HADEPLOY_HOME"

PLUGINS_PATHS = "plugins_paths"
PLUGINS = "plugins"


# ------------------------------------------------ Defaut values
# default plugins_paths, from HADEPLOY_HOME:
DEFAULT_PLUGINS_PATHS = ["src/plugins"]

# default plugins list
DEFAULT_PLUGINS = [ 'inventory', 'test1', 'test2']