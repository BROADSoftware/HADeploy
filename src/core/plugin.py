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
import misc
import logging

logger = logging.getLogger("hadeploy.plugin")


def defaultOnLoad(plugin, context):
    logger.debug("Called default onLoad() for plugin '{0}'".format(plugin.name))
    pass

class Plugin:
    def __init__(self, name, paths):
        self.name = name
        self.load(paths)

    def load(self, paths):
        self.path = None
        self.module = None
        for p in paths:
            x = os.path.join(p, self.name)
            if os.path.isdir(x):
                self.path = x
                break
        if self.path == None:
            misc.ERROR("Unable to find a plugin of name '{0}' in plugin paths {1}".format(self.name, paths))
        # ----------- Handle python code
        codeFile = os.path.join(self.path, "code.py")
        if os.path.isfile(codeFile):
            logger.debug("Will load code from '{0}'".format(codeFile))
            self.module = imp.load_source(self.name, codeFile)
            self.onLoad = getattr(self.module, "onLoad", None)
        # ------------ Set default value for missing function
        if getattr(self, "onLoad", None) == None:
            self.onLoad = defaultOnLoad
        logger.debug("Loaded plugin {0}: {1}".format(self.name, self))    
        
            
        