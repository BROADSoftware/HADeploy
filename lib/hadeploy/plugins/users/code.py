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
from hadeploy.core.const import SRC,DATA, ACTION_DEPLOY, ACTION_REMOVE,SCOPE_USERS
import hadeploy.core.misc as misc
import os

logger = logging.getLogger("hadeploy.plugins.users")

USERS="users"
SCOPE="scope"
GROUPS="groups"
AUTHORIZED_KEYS="authorized_keys"
SYSTEM='system'
NO_REMOVE="no_remove"
MANAGED="managed"
CREATE_HOME="create_home"

SCOPE_BY_NAME="scopeByName"


class UsersPlugin(Plugin):
    
    def __init__(self, name, path, context):
        Plugin.__init__(self, name, path, context)

    def onNewSnippet(self, snippetPath):
        #logger.debug("Called users self.onNewSnippet()")
        if USERS in self.context.model[SRC]:
            for u in self.context.model[SRC][USERS]:
                if AUTHORIZED_KEYS in u:
                    absKeys = []
                    for key in u[AUTHORIZED_KEYS]:
                        absKeys.append(misc.snippetRelocate(snippetPath, key))
                    u[AUTHORIZED_KEYS] = absKeys

    def getGroomingPriority(self):
        return 2000

    def getSupportedScopes(self):
        return [SCOPE_USERS]        

    def getSupportedActions(self):
        if self.context.toExclude(SCOPE_USERS):
            return []
        else:
            return [ACTION_DEPLOY, ACTION_REMOVE]

    def getPriority(self, action):
        return 2000 if action == ACTION_DEPLOY else 7000 if action == ACTION_REMOVE else misc.ERROR("Plugin 'users' called with invalid action: '{0}'".format(action))
    
    def onGrooming(self):
        misc.applyWhenOnList(self.context.model[SRC], USERS)
        misc.applyWhenOnList(self.context.model[SRC], GROUPS)
        if self.context.toExclude(SCOPE_USERS):
            return
        misc.ensureObjectInMaps(self.context.model[DATA], [USERS, SCOPE_BY_NAME], {})
        groomUsers(self.context)
        groomGroups(self.context)

    def getTemplateAsFile(self, action, priority):
        if self.context.toExclude(SCOPE_USERS):
            return []
        else:
            return os.path.join(self.path, "{0}.yml.jj2".format(action))

# ---------------------------------------------------- Static functions


def ensureScope(context, scope):
    root = context.model[DATA][USERS][SCOPE_BY_NAME]
    if not scope in root:
        misc.ensureObjectInMaps(root, [scope, USERS], [])
        misc.ensureObjectInMaps(root, [scope, GROUPS], [])


def groomUsers(context):
    model = context.model
    if USERS in model[SRC]:
        for usr in model[SRC][USERS]:
            misc.setDefaultInMap(usr, NO_REMOVE, False)
            misc.setDefaultInMap(usr, SCOPE, "all")
            misc.setDefaultInMap(usr, MANAGED, True)
            if not usr[MANAGED]:
                if SYSTEM in usr or CREATE_HOME in usr or 'group' in usr or GROUPS in usr or 'password' in usr or 'comment' in usr:
                    misc.ERROR("User '{0}': When not managed, 'system', 'create_home', 'group', 'groups', 'comment' or 'password' attributes can't be defined!".format(usr['login']))
            else:
                misc.setDefaultInMap(usr, SYSTEM, False)
                misc.setDefaultInMap(usr, CREATE_HOME, True)
            if not context.checkScope(usr[SCOPE]):
                misc.ERROR("User {0}: Scope attribute '{1}' does not match any host or host_group!".format(usr['login'], usr[SCOPE]))
            # We group operation per scope, to optimize ansible run. Note of a scope exists, it must hold both 'users' and 'groups'
            ensureScope(context, usr[SCOPE])
            context.model[DATA][USERS][SCOPE_BY_NAME][usr[SCOPE]][USERS].append(usr)


def groomGroups(context):
    model = context.model
    if GROUPS in model[SRC]:
        for grp in model[SRC][GROUPS]:
            misc.setDefaultInMap(grp, SYSTEM, False)
            misc.setDefaultInMap(grp, MANAGED, True)
            misc.setDefaultInMap(grp, SCOPE, "all")
            misc.setDefaultInMap(grp, NO_REMOVE, False)
            if not context.checkScope(grp[SCOPE]):
                misc.ERROR("Group {0}: Scope attribute '{1}' does not match any host or host_group!".format(grp['name'], grp[SCOPE]))
            # We group operation per scope, to optimize ansible run. Note of a scope exists, it must hold both 'users' and 'groups'
            ensureScope(context, grp[SCOPE])
            context.model[DATA][USERS][SCOPE_BY_NAME][grp[SCOPE]][GROUPS].append(grp)
            
            