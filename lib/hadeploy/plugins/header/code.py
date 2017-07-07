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
import os
from hadeploy.core.plugin import Plugin


class HeaderPlugin(Plugin):
    
    def __init__(self, name, path, context):
        Plugin.__init__(self, name, path, context)

    def getSupportedActions(self):
        """Return list of supported actions. ['*'] means we will be involved in all action. (But do not add anything to an eventual action list)"""
        return ['*']

    def getPriority(self, action):
        return 1100
    
    def getTemplateAsFile(self, action, priority):
        """ Get the ansible playbook template. Always the same whatever action is"""
        f = os.path.join(self.path, "common.yml.jj2")
        return [f]

