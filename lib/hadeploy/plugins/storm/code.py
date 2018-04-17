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
import os
from hadeploy.core.plugin import Plugin
from hadeploy.core.const import SRC,DEFAULT_TOOLS_FOLDER,ACTION_STATUS,SCOPE_STORM,ACTION_START,ACTION_STOP,ACTION_DEPLOY,ACTION_REMOVE

logger = logging.getLogger("hadeploy.plugins.storm")

STORM_RELAY="storm_relay"
STORM_TOPOLOGIES="storm_topologies"        

class StormPlugin(Plugin):
    
    def __init__(self, name, path, context):
        Plugin.__init__(self, name, path, context)


    def onNewSnippet(self, snippetPath):
        model = self.context.model
        if STORM_RELAY in model[SRC]: 
            if LOCAL_KEYTAB_PATH in model[SRC][STORM_RELAY]:
                model[SRC][STORM_RELAY][LOCAL_KEYTAB_PATH] = misc.snippetRelocate(snippetPath, model[SRC][STORM_RELAY][LOCAL_KEYTAB_PATH])

    def getGroomingPriority(self):
        return 2520

    def getSupportedScopes(self):
        return [SCOPE_STORM]        

    def getSupportedActions(self):
        if self.context.toExclude(SCOPE_STORM):
            return []
        else:
            # NB: We need to add ACTION_DEPLOY, as we need role 'storm_modules' to be added in the playbook of deployment, for files notifications 
            return [ACTION_START, ACTION_STOP, ACTION_STATUS, ACTION_DEPLOY, ACTION_REMOVE]

    def getPriority(self, action):
        if action == ACTION_START:
            return 6500
        elif action == ACTION_STOP:
            return 3500
        elif action == ACTION_STATUS:
            return 5000
        elif action == ACTION_DEPLOY:
            return 7100
        elif action == ACTION_REMOVE:
            return 1500
        else:
            misc.ERROR("Plugin 'storm' called with invalid action: '{0}'".format(action))

    def onGrooming(self):
        if self.context.toExclude(SCOPE_STORM):
            return
        misc.applyWhenOnSingle(self.context.model[SRC], STORM_RELAY)
        misc.applyWhenOnList(self.context.model[SRC], STORM_TOPOLOGIES)
        groomStormRelay(self.context.model)
        groomStormTopologies(self.context.model)


HOST="host"
ASYNC="async"
DEFAULT_TIMEOUT_SECS="default_timeout_secs"
PRINCIPAL="principal"
LOCAL_KEYTAB_PATH="local_keytab_path"
RELAY_KEYTAB_PATH="relay_keytab_path"
KDEBUG="kdebug"
LOCAL_KEYTAB_PATH="local_keytab_path"
RELAY_KEYTAB_PATH="relay_keytab_path"
TOOLS_FOLDER="tools_folder"
_RELAY_KEYTAB_FOLDER_="_relayKeytabFolder_"        
_KERBEROS_="_kerberos_"


def groomStormRelay(model):
    if STORM_RELAY in model[SRC]:
        if not STORM_TOPOLOGIES in model[SRC] or len(model[SRC][STORM_TOPOLOGIES]) == 0:
            del(model[SRC][STORM_RELAY])
        else:
            misc.setDefaultInMap(model[SRC][STORM_RELAY], ASYNC, True)
            misc.setDefaultInMap(model[SRC][STORM_RELAY], DEFAULT_TIMEOUT_SECS, 90)
            misc.setDefaultInMap(model[SRC][STORM_RELAY], TOOLS_FOLDER, DEFAULT_TOOLS_FOLDER)
            if PRINCIPAL in  model[SRC][STORM_RELAY]:
                if LOCAL_KEYTAB_PATH not in model[SRC][STORM_RELAY] and  RELAY_KEYTAB_PATH not in model[SRC][STORM_RELAY]:
                    misc.ERROR("storm_relay: Please provide a 'local_keytab_path' and/or a 'relay_keytab_path' if you want to use a Kerberos 'principal'")
                model[SRC][STORM_RELAY][_KERBEROS_] = True
                if LOCAL_KEYTAB_PATH in model[SRC][STORM_RELAY]:
                    if not os.path.exists(model[SRC][STORM_RELAY][LOCAL_KEYTAB_PATH]):
                        misc.ERROR("storm_relay: local_keytab_file '{0}' does not exists!".format(model[SRC][STORM_RELAY][LOCAL_KEYTAB_PATH]))
                if RELAY_KEYTAB_PATH not in model[SRC][STORM_RELAY]:
                    model[SRC][STORM_RELAY][_RELAY_KEYTAB_FOLDER_] = os.path.join(model[SRC][STORM_RELAY][TOOLS_FOLDER], "keytabs")
                    model[SRC][STORM_RELAY][RELAY_KEYTAB_PATH] = os.path.join( model[SRC][STORM_RELAY][_RELAY_KEYTAB_FOLDER_], os.path.basename(model[SRC][STORM_RELAY][LOCAL_KEYTAB_PATH]))
                misc.setDefaultInMap(model[SRC][STORM_RELAY], KDEBUG, False)
            else:
                if LOCAL_KEYTAB_PATH in model[SRC][STORM_RELAY] or RELAY_KEYTAB_PATH in model[SRC][STORM_RELAY]:
                    misc.ERROR("kafka_relay: Please, provide a 'principal' if you need to use a keytab")
                model[SRC][STORM_RELAY][_KERBEROS_] = False
            

LAUNCHING_CMD="launching_cmd"
LAUNCHING_DIR="launching_dir"
WAIT_TIME_SECS="wait_time_secs"
TIMEOUT_SECS="timeout_secs"
NAME="name"
NO_REMOVE="no_remove"
            
def groomStormTopologies(model):
    if STORM_TOPOLOGIES in model[SRC] and len(model[SRC][STORM_TOPOLOGIES]) > 0 :
        if not STORM_RELAY in model[SRC]:
            misc.ERROR("A storm_relay must be defined if at least one storm_topologies is defined")
        for topology in model[SRC][STORM_TOPOLOGIES]:
            misc.setDefaultInMap(topology, LAUNCHING_DIR, "~")
            misc.setDefaultInMap(topology, WAIT_TIME_SECS, 30)
            misc.setDefaultInMap(topology, TIMEOUT_SECS, model[SRC][STORM_RELAY][DEFAULT_TIMEOUT_SECS])
            misc.setDefaultInMap(topology, NO_REMOVE, False)  # Used only for associated ranger policy.
            if LAUNCHING_DIR in topology:
                if not os.path.isabs(topology[LAUNCHING_DIR]) and not topology[LAUNCHING_DIR].startswith("~"):
                    misc.ERROR("storm_topology '{}': launching_dir must be an absolute path".format(topology[NAME]))





