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
import pprint            
import imp
import inspect
import logging
    
from plugin import Plugin
import misc
from const import SRC,DATA,HELPER

logger = logging.getLogger("hadeploy.context")

class Context:
    def __init__(self, workingFolder):
        self.plugins = []
        self.pluginByName = {}
        self.model = {}
        self.model[DATA] = {}
        self.workingFolder = workingFolder
        

    def loadPlugin(self, name, paths):
        for p in paths:
            path = os.path.join(p, name)
            if not os.path.isdir(path):
                misc.ERROR("Unable to find a plugin of name '{0}' in plugin paths {1}".format(name, paths))
            else:
                codeFile = os.path.join(path, "code.py")
                if os.path.isfile(codeFile):
                    #logger.debug("Plugin '{0}': Will load code from '{1}'".format(name, codeFile))
                    module = imp.load_source(name, codeFile)
                    pluginClass = None
                    for _, obj in inspect.getmembers(module):
                        if inspect.isclass(obj):
                            #logger.debug("Name: {0}  Obj:{1}".format(className, obj))
                            bases =  obj.__bases__
                            for base in bases:
                                if base == Plugin:
                                    pluginClass = obj
                    if pluginClass == None:
                        misc.ERROR("Invalid plugin '{0}' code.py: Missing MyPlugin(Plugin) class".format(name))
                    else:
                        #logger.debug("Plugin '{0}': Found class {1}".format(name, str(pluginClass)))
                        plugin = pluginClass(name, path)
                        logger.debug("Loaded plugin '{0}' with 'code.py' module  (path:'{1}')".format(name, path))    
                else:
                    # Module without code
                    logger.debug("Loaded plugin '{0}' without 'code.py' module  (path:'{1}')".format(name, path))    
                    plugin = Plugin(name, path)    
                self.plugins.append(plugin)
                self.pluginByName[plugin.name] = plugin

    def generateDebugFile(self):
        if SRC in self.model:
            path = os.path.normpath(os.path.join(self.workingFolder, "model_src.json"))
            output = file(path, 'w')
            pp = pprint.PrettyPrinter(indent=2, stream=output)
            pp.pprint(self.model[SRC])
        if DATA in self.model:
            path = os.path.normpath(os.path.join(self.workingFolder, "model_data.json"))
            output = file(path, 'w')
            pp = pprint.PrettyPrinter(indent=2, stream=output)
            pp.pprint(self.model[DATA])
        if HELPER in self.model:
            path = os.path.normpath(os.path.join(self.workingFolder, "model_helper.json"))
            output = file(path, 'w')
            pp = pprint.PrettyPrinter(indent=2, stream=output)
            pp.pprint(self.model[HELPER])

    def groom(self):
        for plugin in self.plugins:
            plugin.onGrooming(self)
        