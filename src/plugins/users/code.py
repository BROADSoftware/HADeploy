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
from plugin import Plugin
from const import SRC,DATA
import misc
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

USER_SCOPE_BY_NAME="usersScopeByName"


class UsersPlugin(Plugin):
    
    def __init__(self, name, path):
        Plugin.__init__(self, name, path)

    def onNewSnippet(self, context, snippetPath):
        #logger.debug("Called users self.onNewSnippet()")
        if USERS in context.model[SRC]:
            for u in context.model[SRC][USERS]:
                if AUTHORIZED_KEYS in u:
                    absKeys = []
                    for key in u[AUTHORIZED_KEYS]:
                        if not os.path.isabs(key):
                            absKeys.append(os.path.normpath(os.path.join(snippetPath, key)))
                        else:
                            absKeys.append(key)
                    u[AUTHORIZED_KEYS] = absKeys


    def onGrooming(self, context):
        groomUsers(context)
        groomGroups(context)


# ---------------------------------------------------- Static functions

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
            misc.ensureObjectInMaps(context.model[DATA], [USER_SCOPE_BY_NAME, usr[SCOPE], USERS], [])
            misc.ensureObjectInMaps(context.model[DATA], [USER_SCOPE_BY_NAME, usr[SCOPE], GROUPS], [])
            context.model[DATA][USER_SCOPE_BY_NAME][usr[SCOPE]][USERS].append(usr)


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
            misc.ensureObjectInMaps(context.model[DATA], [USER_SCOPE_BY_NAME, grp[SCOPE], USERS], [])
            misc.ensureObjectInMaps(context.model[DATA], [USER_SCOPE_BY_NAME, grp[SCOPE], GROUPS], [])
            context.model[DATA][USER_SCOPE_BY_NAME][grp[SCOPE]][GROUPS].append(grp)
            
            