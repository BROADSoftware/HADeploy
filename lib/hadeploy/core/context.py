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
import imp
import inspect
import logging
        
from hadeploy.core.plugin import Plugin
import misc

from const import DATA,ANSIBLE_ROLES_PATHS,HELPER,INVENTORY,HOST_BY_NAME
import schema
import collections
from hadeploy.core import plugin
        
HOST_GROUP_BY_NAME="hostGroupByName"

logger = logging.getLogger("hadeploy.context")

class PluginExt:
    def __init__(self, plugin, priority):
        self.plugin = plugin
        self.priority = priority
        
    def __repr__(self):
        return "{0}({1})".format(self.plugin.name, self.priority)


class Context:
    def __init__(self, workingFolder):
        self.plugins = []
        self.pluginByName = {}
        self.model = {}
        self.model[DATA] = {}
        self.model[HELPER] = {}
        #self.workingFolder = os.path.abspath(workingFolder)
        self.workingFolder = workingFolder
        

    def loadPlugin(self, name, paths):
        for p in paths:
            path = os.path.join(p, name)
            if os.path.isdir(path):
                codeFile = os.path.join(path, "code.py")
                if os.path.isfile(codeFile):
                    ##logger.debug("Plugin '{0}': Will load code from '{1}'".format(name, codeFile))
                    module = imp.load_source(name, codeFile)
                    pluginClass = None
                    for _, obj in inspect.getmembers(module):
                        if inspect.isclass(obj):
                            #logger.debug("Name: {0}  Obj:{1}".format('className', obj))
                            bases =  obj.__bases__
                            for base in bases:
                                if base == Plugin:
                                    pluginClass = obj
                    if pluginClass == None:
                        misc.ERROR("Invalid plugin '{0}' code.py: Missing MyPlugin(Plugin) class".format(name))
                    else:
                        #logger.debug("Plugin '{0}': Found class {1}".format(name, str(pluginClass)))
                        plugin = pluginClass(name, path, self)
                        logger.debug("Loaded plugin '{0}' with 'code.py' module  (path:'{1}')".format(name, path))    
                else:
                    # Plugin without code (Impossible since plugin refactoring. Kept in cases)
                    logger.debug("Loaded plugin '{0}' without 'code.py' module  (path:'{1}')".format(name, path))    
                    plugin = Plugin(name, path, self)    
                self.plugins.append(plugin)
                self.pluginByName[plugin.name] = plugin
                return
        misc.ERROR("Unable to find a plugin of name '{0}' in plugin paths {1}".format(name, paths))

    def groom(self):
        pl = sorted(self.plugins, key=lambda plugin: plugin.getGroomingPriority())
        logger.debug("Plugin grooming order:{0}".format(pl))
        for plugin in pl:
            plugin.onGrooming()
    

    # Build the schema for source validation, by merging of all schema plugins
    def getSchema(self):
        theSchema = {}
        for plugin in self.plugins:
            schema2 = plugin.getSchema()
            if schema2 != None:
                schema.schemaMerge(theSchema, schema2)
        return theSchema

    def getAllSupportedActions(self):
        actions = set()
        for plugin in self.plugins:
            sas = plugin.getSupportedActions()
            if len(sas) > 0 and sas[0] != "*":
                actions.update(sas)
        return actions; 

    def getAllSupportedScopes(self):
        scopes = set()
        for plugin in self.plugins:
            sss = plugin.getSupportedScopes()
            scopes.update(sss)
        return scopes; 
        
    def getPluginExtForAction(self, action):
        """Retrieve list of plugins for a given action, ordered by priority"""
        pl = []
        for plugin in self.plugins:
            sas = plugin.getSupportedActions()
            if len(sas) > 0 and sas[0]  == "*" or action in sas:
                p = plugin.getPriority(action)
                if isinstance(p, collections.Iterable):
                    for p2 in p:
                        pl.append(PluginExt(plugin, p2))
                else:
                    pl.append(PluginExt(plugin, p))
        return sorted(pl, key= lambda pluginExt: pluginExt.priority)
        
    def buildTemplate(self, action, pluginExts):
        output = file(os.path.normpath(os.path.join(self.workingFolder, "{0}.yml.jj2".format(action))), 'w')
        for pluginExt in pluginExts:
            tmplAsFiles = pluginExt.plugin.getTemplateAsFile(action, pluginExt.priority)
            if isinstance(tmplAsFiles, basestring):
                tmplAsFiles = [tmplAsFiles]
            tmplAsStrings = pluginExt.plugin.getTemplateAsString(action, pluginExt.priority)
            if isinstance(tmplAsStrings, basestring):
                tmplAsStrings = [tmplAsStrings]
            if len(tmplAsFiles) > 0 or len(tmplAsStrings):
                output.write("\n# = = = = = = = = = = = = = = = = = = = = = = = = = = = = = = = = = = = = = = = = = = = = = PLUGIN {0}:\n\n".format(pluginExt.plugin.name))
            for tmpl in tmplAsFiles:
                #logger.debug("Plugin:'{0}'  action:'{1}' => file:'{2}'".format(pluginExt.plugin.name, action, tmpl))
                f = open(tmpl, 'r')
                output.write(f.read())
                f.close()
            for tmpl in tmplAsStrings:
                output.write(tmpl)
        output.close()
        
    def builRolesPath(self, action, pluginsExts):
        """Act as an additive way for 'none/all' mode."""
        if ANSIBLE_ROLES_PATHS in self.model[HELPER]:
            rolesPaths = set(self.model[HELPER][ANSIBLE_ROLES_PATHS])
        else:
            rolesPaths = set()
        for pluginExt in pluginsExts:
            paths = pluginExt.plugin.getRolesPaths(action, pluginExt.priority)
            rolesPaths.update(paths)
        self.model[HELPER][ANSIBLE_ROLES_PATHS] = list(rolesPaths)

    def generateAuxTemplates(self, action, pluginExts):
        for pluginExt in pluginExts:
            pluginExt.plugin.buildAuxTemplates(action, pluginExt.priority)

           
    def checkScope(self, scope):
        l = scope.split(":")
        for h in l:
            if h == 'all':
                return True
            if INVENTORY in self.model[DATA] and HOST_BY_NAME in self.model[DATA][INVENTORY] and h in self.model[DATA][INVENTORY][HOST_BY_NAME]:
                return True
            if INVENTORY in self.model[DATA] and HOST_GROUP_BY_NAME in self.model[DATA][INVENTORY] and h in self.model[DATA][INVENTORY][HOST_GROUP_BY_NAME]:
                return True
            #print("Unknown host or host_group: '{0}'".format(h))
            return False

        
    def toExclude(self, scope):
        if scope in self.excludedScopes:
            return True
        else:
            if(len(self.includedScopes) == 0) or "all" in self.includedScopes:
                return False
            else:
                return not scope in self.includedScopes
            