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
from hadeploy.core.plugin import Plugin
import os
from hadeploy.core.const import PLUGINS_PATHS, SRC, PLUGINS, DEFAULT_PLUGINS,VARS,ENCRYPTED_VARS,DATA
import hadeploy.core.misc as misc

logger = logging.getLogger("hadeploy.plugins.master")

class MasterPlugin(Plugin):
  
    
    def __init__(self, name, path, context):
        Plugin.__init__(self, name, path, context)

    
    def onNewSnippet(self, snippetPath):
        #logger.debug("Called master self.onNewSnippet()")
        if PLUGINS_PATHS in self.context.model[SRC]:
            newList = []
            for p in self.context.model[SRC][PLUGINS_PATHS]:
                newList.append(misc.snippetRelocate(snippetPath, p))
            self.context.model[SRC][PLUGINS_PATHS] = newList

    def getPriority(self, action):
        return 0

    # This should be idempotent, as called twice (One on bootstrap, and on on regular case)
    def onGrooming(self):
        model = self.context.model
        #logger.debug("Called self.onGrooming() for plugin '{0}'".format(self.name))
        misc.ensureObjectInMaps(model[SRC], [PLUGINS_PATHS], [])
        # Add our internal plugins at the end of the list
        model[SRC][PLUGINS_PATHS].append(os.path.normpath(os.path.join(os.path.dirname(__file__), "../../plugins")))
        if not PLUGINS in model[SRC]:
            model[SRC][PLUGINS] = DEFAULT_PLUGINS
        # ---------------------------- Put encrypted vars aside
        misc.ensureObjectInMaps(model[DATA], [ENCRYPTED_VARS], {})
        toDel = []
        for k, v in model[SRC][VARS].iteritems():
            if isinstance(v, basestring)  and  v.startswith("$ANSIBLE_VAULT"):
                model[DATA][ENCRYPTED_VARS][k] = v
                toDel.append(k)
        for k in toDel:
            del(model[SRC][VARS][k])
            



