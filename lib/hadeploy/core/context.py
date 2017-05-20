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

from const import DATA,ANSIBLE_ROLES_PATHS,HELPER
import schema
from sets import Set
        
INVENTORY="inventory"
HOST_BY_NAME="hostByName"        
HOST_GROUP_BY_NAME="hostGroupByName"


logger = logging.getLogger("hadeploy.context")


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
                    logger.debug("Plugin '{0}': Will load code from '{1}'".format(name, codeFile))
                    module = imp.load_source(name, codeFile)
                    pluginClass = None
                    for _, obj in inspect.getmembers(module):
                        if inspect.isclass(obj):
                            logger.debug("Name: {0}  Obj:{1}".format('className', obj))
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
                    # Plugin without code
                    logger.debug("Loaded plugin '{0}' without 'code.py' module  (path:'{1}')".format(name, path))    
                    plugin = Plugin(name, path, self)    
                self.plugins.append(plugin)
                self.pluginByName[plugin.name] = plugin
                return
        misc.ERROR("Unable to find a plugin of name '{0}' in plugin paths {1}".format(name, paths))

    def groom(self):
        pluginList = []
        pluginSet = Set()
        for plugin in self.plugins:
            self.addToGroomList(plugin, pluginList, pluginSet, 0)
        logger.debug("Grooming order:" + str(map(lambda x: x.name, pluginList)))
        for plugin in pluginList:
            plugin.onGrooming()
    
    def addToGroomList(self, plugin, pluginList, pluginSet, deep):
        if(deep > 10):
            misc.ERROR("Loop in plugins grooming dependencies")
        deps = plugin.getGroomingDependencies()
        for dep in deps:
            if dep in self.pluginByName:
                self.addToGroomList(self.pluginByName[dep], pluginList, pluginSet, deep+1)
        if plugin.name not in pluginSet:
            logger.debug("Plugin '{0}' added to groomList".format(plugin.name))
            pluginSet.add(plugin.name)
            pluginList.append(plugin)
        
        

    def generatePrivateTemplate(self):
        for plugin in self.plugins:
            plugin.onTemplateGeneration()
        

    # Build the schema for source validation, by merge of all schema plugin
    def getSchema(self):
        theSchema = {}
        for plugin in self.plugins:
            schema2 = plugin.getSchema()
            if schema2 != None:
                schema.schemaMerge(theSchema, schema2)
        return theSchema

           
    def checkScope(self, scope):
        l = scope.split(":")
        for h in l:
            if h == 'all':
                return True
            if INVENTORY in self.model[DATA] and HOST_BY_NAME in self.model[DATA][INVENTORY] and h in self.model[DATA][INVENTORY][HOST_BY_NAME]:
                return True
            if INVENTORY in self.model[DATA] and HOST_GROUP_BY_NAME in self.model[DATA][INVENTORY] and h in self.model[DATA][INVENTORY][HOST_GROUP_BY_NAME]:
                return True
            print("Unknown host or host_group: '{0}'".format(h))
            return False

    def buildInstallTemplate(self):
        output = file(os.path.normpath(os.path.join(self.workingFolder, "install.yml.jj2")), 'w')
        for plugin in self.plugins:
            tmpls = plugin.getInstallTemplates()
            if len(tmpls) > 0:
                output.write("\n# = = = = = = = = = = = = = = = = = = = = = = = = = = = = = = = = = = = = = = = = = = = = = PLUGIN {0}:\n\n".format(plugin.name))
                for tmpl in tmpls:
                    f = open(tmpl, 'r')
                    output.write(f.read())
                    f.close()
        output.close()
        
        
    def buildRemoveTemplate(self):
        output = file(os.path.normpath(os.path.join(self.workingFolder, "remove.yml.jj2")), 'w')
        for plugin in reversed(self.plugins):
            tmpls = plugin.getRemoveTemplates()
            if len(tmpls) > 0:
                output.write("\n# = = = = = = = = = = = = = = = = = = = = = = = = = = = = = = = = = = = = = = = = = = = = = PLUGIN {0}:\n\n".format(plugin.name))
                for tmpl in tmpls:
                    f = open(tmpl, 'r')
                    output.write(f.read())
                    f.close()
        output.close()
        
    def builRolesPath(self):
        rolesPaths = []
        for plugin in self.plugins:
            paths = plugin.getRolesPaths()
            for p in paths:
                rolesPaths.append(p)
        self.model[HELPER][ANSIBLE_ROLES_PATHS] = rolesPaths
            