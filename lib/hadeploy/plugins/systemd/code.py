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
from hadeploy.core.plugin import Plugin
from hadeploy.core.const import SRC,DATA,SCOPE_SYSTEMD,ACTION_DEPLOY,ACTION_REMOVE,ACTION_START,ACTION_STOP,ACTION_STATUS
from hadeploy.plugins.files.code import lookupSrc
from sets import Set

logger = logging.getLogger("hadeploy.plugins.systemd")

SYSTEMD_UNITS="systemd_units"
NAME="name"
SCOPE="scope"
UNIT_FILE="unit_file"
NO_REMOVE="no_remove"
_UNIT_FILE_="_unit_file_"


SYSTEMD="systemd"
SCOPE_BY_NAME="scopeByName"     

_SRC_="_src_"
_DISPLAY_SRC_="_displaySrc_"

ENABLED="enabled"
STATE="state"
ST_STARTED="started"
ST_STOPPED="stopped"
ST_CURRENT="current"

ACTION_ON_NOTIFY="action_on_notify"
AON_RESTART="restart"
AON_RELOAD="reload"
AON_NONE="none"

validState= Set([ST_STARTED, ST_STOPPED, ST_CURRENT])
validAon = Set([AON_NONE, AON_RELOAD, AON_RESTART])

class SystemdPlugin(Plugin):
    
    def __init__(self, name, path, context):
        Plugin.__init__(self, name, path, context)
           
    def getGroomingPriority(self):
        return 2500     

    def getSupportedScopes(self):
        return [SCOPE_SYSTEMD]        
 
    def getSupportedActions(self):
        return [ACTION_DEPLOY, ACTION_REMOVE,ACTION_START,ACTION_STOP,ACTION_STATUS]

    def getPriority(self, action):
        if action == ACTION_DEPLOY:
            return 6000
        elif  action == ACTION_REMOVE:
            return 1800
        elif  action == ACTION_START:
            return 5000
        elif  action == ACTION_STOP:
            return 5000
        elif  action == ACTION_STATUS:
            return 5000
        else:
            misc.ERROR("Plugin 'systemd' called with invalid action: '{0}'".format(action))


    def onGrooming(self):
        misc.ensureObjectInMaps(self.context.model[DATA], [SYSTEMD, SCOPE_BY_NAME], {})
        misc.applyWhenOnList(self.context.model[SRC], SYSTEMD_UNITS)
        self.groomSystemd()
                    
    def groomSystemd(self):
        if self.context.toExclude(SCOPE_SYSTEMD):
            return
        model = self.context.model
        unitNames = Set()
        if SYSTEMD_UNITS in model[SRC]:
            for unit in model[SRC][SYSTEMD_UNITS]:
                if unit[NAME] in unitNames:
                    misc.ERROR("systemd_unit '{0}' is defined twice!".format(unit[NAME]))
                unitNames.add(unit[NAME]) 
                misc.setDefaultInMap(unit, NO_REMOVE, False)
                misc.setDefaultInMap(unit, ENABLED, True)
                misc.setDefaultInMap(unit, STATE, ST_CURRENT)
                if unit[STATE] not in validState:
                    misc.ERROR("Systemd_unit {0}: state value '{1}' is not valid. Must be one of {2}".format(unit[NAME], unit[STATE], validState))
                misc.setDefaultInMap(unit, ACTION_ON_NOTIFY, AON_RESTART)
                if unit[ACTION_ON_NOTIFY] not in validAon:
                    misc.ERROR("Systemd_unit {0}: action_on_notify value '{1}' is not valid. Must be one of {2}".format(unit[NAME], unit[ACTION_ON_NOTIFY], validAon))
                # ---------------------- Lookup unit file
                path, displaySrc, errMsg = lookupSrc(model, unit[UNIT_FILE])
                if path != None:
                    unit[_UNIT_FILE_] = path
                    unit[_DISPLAY_SRC_] = displaySrc
                else:
                    misc.ERROR("Systemd_unit '{0}': {1}".format(unit[NAME], errMsg))
                # ---------------------- Insert in scope
                if not self.context.checkScope(unit[SCOPE]):
                    misc.ERROR("Systemd_unit {0}: scope attribute '{1}' does not match any host or host_group!".format(unit[NAME], unit[SCOPE]))
                else:
                    misc.ensureObjectInMaps(self.context.model[DATA][SYSTEMD][SCOPE_BY_NAME], [unit[SCOPE], SYSTEMD], [])
                    model[DATA][SYSTEMD][SCOPE_BY_NAME][unit[SCOPE]][SYSTEMD].append(unit)
    
 
                

