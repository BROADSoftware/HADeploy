# Copyright (C) 2018 BROADSoftware
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
import os
from hadeploy.core.plugin import Plugin
from hadeploy.core.const import SRC,DEFAULT_TOOLS_FOLDER,ACTION_STATUS,ACTION_START,ACTION_STOP,ACTION_DEPLOY,ACTION_REMOVE,SCOPE_YARN,DATA

logger = logging.getLogger("hadeploy.plugins.kafka")

YARN_RELAY="yarn_relay"
YARN_SERVICES="yarn_services"

# Our private space in data model
YARN="yarn" 
ALL_SERVICES="allServices"
SERVICES_TO_KILL="servicesToKill"

class YarnPlugin(Plugin):
    
    def __init__(self, name, path, context):
        Plugin.__init__(self, name, path, context)


    def onNewSnippet(self, snippetPath):
        model = self.context.model
        if YARN_RELAY in model[SRC]: 
            if LOCAL_KEYTAB_PATH in model[SRC][YARN_RELAY]:
                model[SRC][YARN_RELAY][LOCAL_KEYTAB_PATH] = misc.snippetRelocate(snippetPath, model[SRC][YARN_RELAY][LOCAL_KEYTAB_PATH])

    def getGroomingPriority(self):
        return 2520

    def getSupportedScopes(self):
        return [SCOPE_YARN]        

    def getSupportedActions(self):
        if self.context.toExclude(SCOPE_YARN):
            return []
        else:
            # NB: We need to add ACTION_DEPLOY, as we need role 'yarn_modules' to be added in the playbook of deployment, for files notifications 
            return [ACTION_START, ACTION_STOP, ACTION_STATUS, ACTION_DEPLOY, ACTION_REMOVE]

    def getPriority(self, action):
        if action == ACTION_START:
            return 6400
        elif action == ACTION_STOP:
            return 3600
        elif action == ACTION_STATUS:
            return 5000
        elif action == ACTION_DEPLOY:
            return 7050
        elif action == ACTION_REMOVE:
            return 1550
        else:
            misc.ERROR("Plugin 'yarn' called with invalid action: '{0}'".format(action))

    def onGrooming(self):
        if self.context.toExclude(SCOPE_YARN):
            return
        misc.applyWhenOnSingle(self.context.model[SRC], YARN_RELAY)
        misc.applyWhenOnList(self.context.model[SRC], YARN_SERVICES)
        misc.ensureObjectInMaps(self.context.model[DATA], [YARN], {})
        groomYarnRelay(self.context.model)
        groomYarnServices(self.context.model)


HOST="host"
DEFAULT_TIMEOUT_SECS="default_timeout_secs"
PRINCIPAL="principal"
LOCAL_KEYTAB_PATH="local_keytab_path"
RELAY_KEYTAB_PATH="relay_keytab_path"
TOOLS_FOLDER="tools_folder"
KDEBUG="kdebug"

_RELAY_KEYTAB_FOLDER_="_relayKeytabFolder_"        
_KERBEROS_="_kerberos_"


def groomYarnRelay(model):
    if YARN_RELAY in model[SRC]:
        if not YARN_SERVICES in model[SRC] or len(model[SRC][YARN_SERVICES]) == 0:
            del(model[SRC][YARN_RELAY])
        else:
            misc.setDefaultInMap(model[SRC][YARN_RELAY], DEFAULT_TIMEOUT_SECS, 90)
            misc.setDefaultInMap(model[SRC][YARN_RELAY], TOOLS_FOLDER, DEFAULT_TOOLS_FOLDER)
            if PRINCIPAL in  model[SRC][YARN_RELAY]:
                if LOCAL_KEYTAB_PATH not in model[SRC][YARN_RELAY] and  RELAY_KEYTAB_PATH not in model[SRC][YARN_RELAY]:
                    misc.ERROR("yarn_relay: Please provide a 'local_keytab_path' and/or a 'relay_keytab_path' if you want to use a Kerberos 'principal'")
                model[SRC][YARN_RELAY][_KERBEROS_] = True
                if LOCAL_KEYTAB_PATH in model[SRC][YARN_RELAY]:
                    if not os.path.exists(model[SRC][YARN_RELAY][LOCAL_KEYTAB_PATH]):
                        misc.ERROR("yarn_relay: local_keytab_file '{0}' does not exists!".format(model[SRC][YARN_RELAY][LOCAL_KEYTAB_PATH]))
                if RELAY_KEYTAB_PATH not in model[SRC][YARN_RELAY]:
                    model[SRC][YARN_RELAY][_RELAY_KEYTAB_FOLDER_] = os.path.join(model[SRC][YARN_RELAY][TOOLS_FOLDER], "keytabs")
                    model[SRC][YARN_RELAY][RELAY_KEYTAB_PATH] = os.path.join( model[SRC][YARN_RELAY][_RELAY_KEYTAB_FOLDER_], os.path.basename(model[SRC][YARN_RELAY][LOCAL_KEYTAB_PATH]))
                misc.setDefaultInMap(model[SRC][YARN_RELAY], KDEBUG, False)
            else:
                if LOCAL_KEYTAB_PATH in model[SRC][YARN_RELAY] or RELAY_KEYTAB_PATH in model[SRC][YARN_RELAY]:
                    misc.ERROR("yarn_relay: Please, provide a 'principal' if you need to use a keytab")
                model[SRC][YARN_RELAY][_KERBEROS_] = False
            

LAUNCHING_CMD="launching_cmd"
KILLING_CMD="killing_cmd"
LAUNCHING_DIR="launching_dir"
TIMEOUT_SECS="timeout_secs"
NAME="name"
            
def groomYarnServices(model):
    if YARN_SERVICES in model[SRC] and len(model[SRC][YARN_SERVICES]) > 0 :
        if not YARN_RELAY in model[SRC]:
            misc.ERROR("A yarn_relay must be defined if at least one yarn_services is defined")
        for service in model[SRC][YARN_SERVICES]:
            misc.setDefaultInMap(service, LAUNCHING_DIR, "~")
            misc.setDefaultInMap(service, TIMEOUT_SECS, model[SRC][YARN_RELAY][DEFAULT_TIMEOUT_SECS])
            if LAUNCHING_DIR in service:
                if not os.path.isabs(service[LAUNCHING_DIR]) and not service[LAUNCHING_DIR].startswith("~"):
                    misc.ERROR("yarn_services '{}': launching_dir must be an absolute path".format(service[NAME]))
            if ALL_SERVICES in model[DATA][YARN]:
                model[DATA][YARN][ALL_SERVICES] = model[DATA][YARN][ALL_SERVICES] + "," + service[NAME]
            else:
                model[DATA][YARN][ALL_SERVICES] = service[NAME]
            if not KILLING_CMD in service:
                if SERVICES_TO_KILL in model[DATA][YARN]:
                    model[DATA][YARN][SERVICES_TO_KILL] = model[DATA][YARN][SERVICES_TO_KILL] + "," + service[NAME]
                else:
                    model[DATA][YARN][SERVICES_TO_KILL] = service[NAME]
                
                





