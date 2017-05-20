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
import os
import yaml

logger = logging.getLogger("hadeploy.plugin")

class Plugin:
    def __init__(self, name, path, context):
        self.name = name
        self.path = path
        self.context = context
        #logger.debug("Plugin '{0}':  type:'{1}' path:'{2}'".format(name, str(self.__class__), path))

        
    def onNewSnippet(self, snippetPath):
        #logger.debug("Called default self.onNewSnippet() for plugin '{0}'".format(self.name))
        pass
        
            
    def onGrooming(self):
        #logger.debug("Called default self.onGrooming() for plugin '{0}'".format(self.name))
        pass
    
    def onTemplateGeneration(self):
        pass
    
    # Following function follow standard and documented naming convention. 
    # So override only in case of need, such as returning different values depending of the context. 
    
    def getSchema(self):
        schemaFile = os.path.join(self.path, "schema.yml")
        if os.path.isfile(schemaFile):
            return yaml.load(open(schemaFile))
        else:
            return None
    
    def getInstallTemplates(self):
        f = os.path.join(self.path, "install.yml.jj2")
        return [f] if os.path.isfile(f) else []

    def getRemoveTemplates(self):
        f = os.path.join(self.path, "remove.yml.jj2")
        return [f] if os.path.isfile(f) else []
        
    def getRolesPaths(self):
        p = os.path.join(self.path, "roles")
        return [p] if os.path.isdir(p) else []
        
    def getGroomingDependencies(self):
        return []
        
        