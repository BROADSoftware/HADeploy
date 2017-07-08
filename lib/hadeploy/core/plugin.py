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
import misc

logger = logging.getLogger("hadeploy.plugin")


class Plugin:
    """" Plugin base interface
    
    System will call plugin's method the following order:
    
    onNewSnippet()
        Called in parsing phases. Used mainly to adjust the path relative to the hosting file (THe snippetPath).
        WARNING: At this stage, model object has not been validated against schema. So don't assume correctness.
    
    getSchema()
        Provide a partial pywkalify schema for input file validation
        Note than this is called only once, and is NOT action dependant

    getGroomingPriority()

    onGrooming()
        Called at first step. Used to:
        - Perform some chcking
        - Build some new data structures
        - ...
        If a plugin is dependant of another, It could ensure this later is loaded by checking context.TOBEDEFINED()

    getSupportedScopes()
        Return list of supported scope.

    getSupportedActions()
        Return list of supported actions
        ['*'] means will be involved in all action. (But do not add anything to an eventual action list)
        [] means will not be involved

    getPriority()
        MANDATORY. Define relative order of processing
        Return an integer or a list of integer providing the calling priority for a action.
        Returning a list means this plugin wants to be called several times

    getTemplateAsFile()
       Get the ansible playbook template, as a file name
       This snippet will be inserted in the overall playbook built for the action.
       Can return a single file name, a list of file name, or [] for nothing
       This function can also be overwritten to handle generation of secondary template. See hive, kafka or hbase plugin for example.

    getTemplateAsString()
       Get the ansible playbook template, as a string
       This snippet will be inserted in the overall playbook built for the action.
       Can return a single string, a list of string, or [] for nothing

    getRolesPaths():
        Allow to add roles path for Ansible run
        To override if roles path depends on the action, or are outside of the plugins
        
    buildAuxTemplates()
        All auxiliary, private template to be built
        
    """

    def __init__(self, name, path, context):
        self.name = name
        self.path = path
        self.context = context
        #logger.debug("Plugin '{0}':  type:'{1}' path:'{2}'".format(name, str(self.__class__), path))

    def __str__(self):
        return self.name
    def __repr__(self):
        return self.name
        
    def onNewSnippet(self, snippetPath):
        pass
        
    def getGroomingPriority(self):
        return 0     # We don't care. Will be called before all others
            
    def onGrooming(self):
        pass

    def getSupportedScopes(self):
        return []        

    def getSupportedActions(self):
        return []

    def getPriority(self, action):
        misc.ERROR("Plugin '{0}' is missing getPriority() method for action {1}".format(self.name, action))
    
    # Following function follow standard and documented naming convention. 
    # So override only in case of need, such as returning different values depending of the context. 
    
    def getSchema(self):
        schemaFile = os.path.join(self.path, "schema.yml")
        if os.path.isfile(schemaFile):
            return yaml.load(open(schemaFile))
        else:
            return None
    
    def getTemplateAsFile(self, action, priority):    
        f = os.path.join(self.path, "{0}.yml.jj2".format(action))
        logger.debug("Plugin:'{0}'  action:'{1}' => file:'{2}'".format(self.name, action, f))
        return f if os.path.isfile(f) else []

    def getTemplateAsString(self, action, priority):    
        return []
        
    def getRolesPaths(self, action, priority):
        p = os.path.join(self.path, "roles")
        return [p] if os.path.isdir(p) else []
        
    def buildAuxTemplates(self, action, priority):
        pass
        