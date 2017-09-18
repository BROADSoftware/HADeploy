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

import logging
import hadeploy.core.misc as misc
import os
from hadeploy.core.plugin import Plugin
from hadeploy.core.const import SCOPE_SYSTEMD,ACTION_DEPLOY, ACTION_REMOVE


logger = logging.getLogger("hadeploy.plugins.systemd")

class FilesPlugin(Plugin):
    
    def __init__(self, name, path, context):
        Plugin.__init__(self, name, path, context)

           
    def getGroomingPriority(self):
        return 3200     

    def getSupportedScopes(self):
        return [SCOPE_SYSTEMD]        
 
    def getSupportedActions(self):
        return [ACTION_DEPLOY, ACTION_REMOVE]

    def getPriority(self, action):
        return 3200 if action == ACTION_DEPLOY else 3800 if action == ACTION_REMOVE else misc.ERROR("Plugin 'Files' called with invalid action: '{0}'".format(action))

    def onGrooming(self):
        model = self.context.model

