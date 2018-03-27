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
from hadeploy.core.templator import Templator
from hadeploy.core.const import SRC,DATA,ACTION_DEPLOY,ACTION_REMOVE,ACTION_START,ACTION_STOP,SCOPE_SUPERVISOR,ACTION_STATUS
from hadeploy.plugins.files.code import lookupSrc
from sets import Set

logger = logging.getLogger("hadeploy.plugins.supervisor")

ENABLED="enabled"
STATE="state"
ST_STARTED="started"
ST_STOPPED="stopped"
ST_CURRENT="current"


#ACTION_ON_NOTIFY="action_on_notify"
#AON_RESTART="restart"
#AON_RELOAD="reload"
#AON_NONE="none"
#validAon = Set([AON_NONE, AON_RELOAD, AON_RESTART])

validState= Set([ST_STARTED, ST_STOPPED, ST_CURRENT])

NAME="name"
NO_REMOVE="no_remove"
SCOPE="scope"
SCOPE_BY_NAME="scopeByName"     
_SCOPE_="_scope_"

SUPERVISORS="supervisors"
USER="user"
GROUP="group"
MANAGED="managed"
CONF_FILE_SRC="conf_file_src"
CONF_FILE_DST="conf_file_dst"
LOGS_DIR="logs_dir"
PID_DIR="pid_dir"
SOCKS_DIR="socks_dir"
INCLUDE_DIR="include_dir"
SUPERVISORCTL="supervisorctl"
HTTP_SERVER="http_server"
ENDPOINT="endpoint"
USERNAME="username"
PASSWORD="password"
AUTOSTART="autostart"

# The supervisor.conf file is a double template.
# Rendered a first time during build time (in buildAuxTemplates()), the result is in fact a runtime template, rendered by ansible
# All paths are absolute
CONF_FILE_SRC_JJ2="conf_file_src_jj2"
CONF_FILE_SRC_J2="conf_file_src_j2"
SERVICE_UNIT_JJ2="service_unit_jj2"
SERVICE_UNIT_J2="service_unit_j2"
SUPERVISORCTL_JJ2="supervisorctl_jj2"
SUPERVISORCTL_J2="supervisorctl_j2"


SUPERVISORS_TO_REMOVE="supervisorsToRemove"
SUPERVISORS_TO_MANAGE="supervisorsToManage"
SUPERVISOR_BY_NAME="supervisorByName"

SUPERVISOR="supervisor"
SUPERVISOR_PROGRAMS="supervisor_programs"
COMMAND="command"
SUPERVISOR_OWNER="supervisorOwner"      
SUPERVISOR_GROUP="supervisorGroup"      
SUPERVISOR_CONF="supervisorConf"        
PROGRAMS_TO_REMOVE="programsToRemove"
PROGRAMS_TO_MANAGE="programsToManage"
_NAME_="_name_"
NUMPROCS="numprocs"


SUPERVISOR_GROUPS="supervisor_groups"
PROGRAMS="programs"
GROUPS_TO_REMOVE="groupsToRemove"
GROUPS_TO_MANAGE="groupsToManage"
PROGRAM_BY_NAME="programByName"

#PROGRAMS_JJ2="programs_jj2"
#PROGRAMS_J2="programs_j2"
#PROGRAMS_DEST="programs_dest"
#UNPROGRAMS_JJ2="unprograms_jj2"
#UNPROGRAMS_J2="unprograms_j2"

GROUP_BY_NAME="groupByName"

class SupervisorPlugin(Plugin):
    
    def __init__(self, name, path, context):
        Plugin.__init__(self, name, path, context)
           
    def getGroomingPriority(self):
        return 2510     

    def getSupportedScopes(self):
        return [SCOPE_SUPERVISOR]        
 
    def getSupportedActions(self):
        return [ACTION_DEPLOY, ACTION_REMOVE,ACTION_START,ACTION_STOP,ACTION_STATUS]

    def getPriority(self, action):
        if action == ACTION_DEPLOY:
            return 7000
        elif  action == ACTION_REMOVE:
            return 1600
        elif  action == ACTION_START:
            return 6000
        elif  action == ACTION_STOP:
            return 4000
        elif  action == ACTION_STATUS:
            return 5000
        else:
            misc.ERROR("Plugin 'supervisor' called with invalid action: '{0}'".format(action))


    def onGrooming(self):
        misc.ensureObjectInMaps(self.context.model[DATA], [SUPERVISORS, SCOPE_BY_NAME], {})
        misc.applyWhenOnList(self.context.model[SRC], SUPERVISORS)
        misc.applyWhenOnList(self.context.model[SRC], SUPERVISOR_PROGRAMS)
        misc.applyWhenOnList(self.context.model[SRC], SUPERVISOR_GROUPS)
        self.groomSupervisors()
        self.groomPrograms()
        self.groomGroups()

    def groomSupervisors(self):
        if self.context.toExclude(SCOPE_SUPERVISOR):
            return
        model = self.context.model
        if SUPERVISORS in model[SRC]:
            misc.ensureObjectInMaps(self.context.model[DATA][SUPERVISORS], [SUPERVISOR_BY_NAME], {})
            for supervisord in model[SRC][SUPERVISORS]:
                if supervisord[NAME] in self.context.model[DATA][SUPERVISORS][SUPERVISOR_BY_NAME]:
                    misc.ERROR("supervisor '{0}' is defined twice!".format(supervisord[NAME]))
                self.context.model[DATA][SUPERVISORS][SUPERVISOR_BY_NAME][supervisord[NAME]] = supervisord                    
                misc.setDefaultInMap(supervisord, MANAGED, True)
                self.groomOneSupervisord(model, supervisord)
                # ---------------------- Insert in scope
                if not self.context.checkScope(supervisord[SCOPE]):
                    misc.ERROR("Supervisor {0}: scope attribute '{1}' does not match any host or host_group!".format(supervisord[NAME], supervisord[SCOPE]))
                else:
                    #misc.ensureObjectInMaps(self.context.model[DATA][SUPERVISORS][SCOPE_BY_NAME], [supervisord[SCOPE], SUPERVISORS], [])
                    #misc.ensureObjectInMaps(self.context.model[DATA][SUPERVISORS][SCOPE_BY_NAME], [supervisord[SCOPE], PROGRAMS], [])
                    #model[DATA][SUPERVISORS][SCOPE_BY_NAME][supervisord[SCOPE]][SUPERVISORS].append(supervisord)
                    if supervisord[MANAGED]:
                        misc.ensureObjectInMaps(self.context.model[DATA][SUPERVISORS][SCOPE_BY_NAME], [supervisord[SCOPE], SUPERVISORS_TO_MANAGE], [])
                        model[DATA][SUPERVISORS][SCOPE_BY_NAME][supervisord[SCOPE]][SUPERVISORS_TO_MANAGE].append(supervisord)
                        if not supervisord[NO_REMOVE]:
                            misc.ensureObjectInMaps(self.context.model[DATA][SUPERVISORS][SCOPE_BY_NAME], [supervisord[SCOPE], SUPERVISORS_TO_REMOVE], [])
                            model[DATA][SUPERVISORS][SCOPE_BY_NAME][supervisord[SCOPE]][SUPERVISORS_TO_REMOVE].append(supervisord)

    def groomOneSupervisord(self, model, supervisord):
        misc.setDefaultInMap(supervisord, CONF_FILE_DST, "/etc/supervisord_{0}.conf".format(supervisord[NAME]))
        misc.setDefaultInMap(supervisord, LOGS_DIR, "/var/log/supervisor_{0}".format(supervisord[NAME]))
        misc.setDefaultInMap(supervisord, PID_DIR, "/var/run/supervisor_{0}".format(supervisord[NAME]))
        misc.setDefaultInMap(supervisord, SOCKS_DIR, "/var/run/supervisor_{0}".format(supervisord[NAME]))
        misc.setDefaultInMap(supervisord, INCLUDE_DIR, "/etc/supervisord_{0}.d".format(supervisord[NAME]))
        misc.setDefaultInMap(supervisord, SUPERVISORCTL, "/usr/bin/supervisorctl_{0}".format(supervisord[NAME]))
        misc.setDefaultInMap(supervisord, NO_REMOVE, False)
        misc.setDefaultInMap(supervisord, ENABLED, True)
        misc.setDefaultInMap(supervisord, STATE, ST_STARTED)
        misc.setDefaultInMap(supervisord, MANAGED, True)
        supervisord[PROGRAM_BY_NAME] = {}
        supervisord[GROUP_BY_NAME] = {}
        if supervisord[STATE] not in validState:
            misc.ERROR("Supervisor {0}: state value '{1}' is not valid. Must be one of {2}".format(supervisord[NAME], supervisord[STATE], validState))
        #supervisord[PROGRAMS_JJ2] = os.path.join(self.path, "templates/programs.ini.jj2")
        #supervisord[PROGRAMS_J2] = "supervisor_{}_programs.ini.j2".format(supervisord[NAME])
        #supervisord[UNPROGRAMS_JJ2] = os.path.join(self.path, "templates/unprograms.ini.jj2")
        #supervisord[UNPROGRAMS_J2] = "supervisor_{}_unprograms.ini.j2".format(supervisord[NAME])
        #supervisord[PROGRAMS_DEST] = os.path.join(supervisord[INCLUDE_DIR], "_hadeploy_.ini") 
        
        if supervisord[MANAGED]:
            if HTTP_SERVER in supervisord:
                misc.setDefaultInMap(supervisord[HTTP_SERVER], ENDPOINT, "127.0.0.1:9001")
                if PASSWORD in supervisord[HTTP_SERVER]:
                    misc.setDefaultInMap(supervisord[HTTP_SERVER], USERNAME, supervisord[USER])
            if CONF_FILE_SRC in supervisord:
                path, _, errMsg = lookupSrc(model, supervisord[CONF_FILE_SRC])
                if path != None:
                    supervisord[CONF_FILE_SRC_JJ2] = path
                else:
                    misc.ERROR("Supervisor '{0}': {1}".format(supervisord[NAME], errMsg))
            else:
                supervisord[CONF_FILE_SRC_JJ2] = os.path.join(self.path, "templates/supervisord.conf.jj2")
            supervisord[CONF_FILE_SRC_J2] = "supervisord_{0}.conf.j2".format(supervisord[NAME])
            supervisord[SERVICE_UNIT_JJ2] = os.path.join(self.path, "templates/supervisord.service.jj2")
            supervisord[SERVICE_UNIT_J2] = "supervisord_{0}.service.j2".format(supervisord[NAME])
            supervisord[SUPERVISORCTL_JJ2] = os.path.join(self.path, "templates/supervisorctl.jj2")
            supervisord[SUPERVISORCTL_J2] = "supervisorctl_{0}".format(supervisord[NAME])
            

    def groomPrograms(self):
        if self.context.toExclude(SCOPE_SUPERVISOR):
            return
        model = self.context.model
        if SUPERVISOR_PROGRAMS in model[SRC]:
            for prg in model[SRC][SUPERVISOR_PROGRAMS]:
                if not SUPERVISOR_BY_NAME in  model[DATA][SUPERVISORS] or not prg[SUPERVISOR] in model[DATA][SUPERVISORS][SUPERVISOR_BY_NAME]:
                    misc.ERROR("supervisor_program '{}' refer to an undefined supervisor '{}'".format(prg[NAME], prg[SUPERVISOR]))
                else:
                    supervisord = model[DATA][SUPERVISORS][SUPERVISOR_BY_NAME][prg[SUPERVISOR]]
                if prg[NAME] in supervisord[PROGRAM_BY_NAME]:
                    misc.ERROR("supervisor_program '{}' is defined twice in supervisor '{}'".format(prg[NAME], supervisord[NAME]))
                # Register in model.data
                supervisord[PROGRAM_BY_NAME][prg[NAME]] = prg
                #model[DATA][SUPERVISORS][SCOPE_BY_NAME][supervisord[SCOPE]][PROGRAMS].append(prg)
                # Adjust attributes
                misc.setDefaultInMap(prg, NO_REMOVE, False)
                if prg[NO_REMOVE] and not supervisord[NO_REMOVE]:
                    misc.ERROR("Supervisor_program '{}' has no remove flag set while its supervisor ({}) has not!".format(prg[NAME], supervisord[NAME]))
                if CONF_FILE_SRC in prg:
                    path, _, errMsg = lookupSrc(model, prg[CONF_FILE_SRC])
                    if path != None:
                        prg[CONF_FILE_SRC_JJ2] = path
                    else:
                        misc.ERROR("Supervisor_program '{0}': {1}".format(prg[NAME], errMsg))
                else:
                    prg[CONF_FILE_SRC_JJ2] = os.path.join(self.path, "templates/program.conf.jj2")
                    if COMMAND not in prg:
                        misc.ERROR("Supervisor_program '{}': A 'command' parameter must be provided if using the default configuration file (No 'conf_file_src' parameter".format(prg[NAME]))
                prg[CONF_FILE_SRC_J2] = "supervisor_{}_program_{}.conf".format(supervisord[NAME], prg[NAME])
                prg[CONF_FILE_DST] = os.path.join(supervisord[INCLUDE_DIR], "{}_prg.ini".format(prg[NAME]))
                prg[SUPERVISOR_OWNER] = supervisord[USER]
                prg[SUPERVISOR_GROUP] = supervisord[GROUP]
                prg[SUPERVISOR_CONF] = supervisord[CONF_FILE_DST]
                misc.setDefaultInMap(prg, STATE, ST_STARTED)
                if NUMPROCS in prg and prg[NUMPROCS] > 1:
                    prg[_NAME_] = prg[NAME] + ":"    # This is in fact a group of process
                else:
                    prg[_NAME_] = prg[NAME]
                if prg[STATE] not in validState:
                    misc.ERROR("Supervisor_program {0}: state value '{1}' is not valid. Must be one of {2}".format(prg[NAME], prg[STATE], validState))
                misc.setDefaultInMap(prg, AUTOSTART, prg[STATE] == ST_STARTED)
                if SCOPE not in prg:
                    prg[SCOPE] = supervisord[SCOPE]
                # Note we don't set prg[USER], as we want to be unset in config file if not set
                # ---------------------- Insert in scope
                misc.ensureObjectInMaps(self.context.model[DATA][SUPERVISORS][SCOPE_BY_NAME], [prg[SCOPE], PROGRAMS_TO_MANAGE], [])
                model[DATA][SUPERVISORS][SCOPE_BY_NAME][prg[SCOPE]][PROGRAMS_TO_MANAGE].append(prg)
                if not prg[NO_REMOVE]:
                    misc.ensureObjectInMaps(self.context.model[DATA][SUPERVISORS][SCOPE_BY_NAME], [prg[SCOPE], PROGRAMS_TO_REMOVE], [])
                    model[DATA][SUPERVISORS][SCOPE_BY_NAME][prg[SCOPE]][PROGRAMS_TO_REMOVE].append(prg)
    
    def groomGroups(self):
        if self.context.toExclude(SCOPE_SUPERVISOR):
            return
        model = self.context.model
        if SUPERVISOR_GROUPS in model[SRC]:
            for grp in model[SRC][SUPERVISOR_GROUPS]:
                if not SUPERVISOR_BY_NAME in  model[DATA][SUPERVISORS] or not grp[SUPERVISOR] in model[DATA][SUPERVISORS][SUPERVISOR_BY_NAME]:
                    misc.ERROR("supervisor_group '{}' refer to an undefined supervisor '{}'".format(grp[NAME], grp[SUPERVISOR]))
                else:
                    supervisord = model[DATA][SUPERVISORS][SUPERVISOR_BY_NAME][grp[SUPERVISOR]]
                if grp[NAME] in supervisord[GROUP_BY_NAME]:
                    misc.ERROR("supervisor_group '{}' is defined twice in supervisor '{}'".format(grp[NAME], supervisord[NAME]))
                supervisord[GROUP_BY_NAME][grp[NAME]] = grp
                for prgName in grp[PROGRAMS]:
                    if prgName not in supervisord[PROGRAM_BY_NAME]:
                        misc.ERROR("supervisor_group '{}' refer to an undefined program '{}'".format(grp[NAME], prgName))
                    else:
                        prg = supervisord[PROGRAM_BY_NAME][prgName] 
                        # The program name must be patched:
                        prg[_NAME_] = grp[NAME] + ":" + supervisord[PROGRAM_BY_NAME][prgName][_NAME_]
                        if _SCOPE_ in grp:
                            if grp[_SCOPE_] != prg[SCOPE]:
                                misc.ERROR("supervisor_group '{}' host programs with different scope ({} != {}). Must be same".format(grp[NAME], grp[_SCOPE_], prg[SCOPE]))
                        else:
                            grp[_SCOPE_] = prg[SCOPE]
                misc.setDefaultInMap(grp, NO_REMOVE, False)
                if grp[NO_REMOVE] and not supervisord[NO_REMOVE]:
                    misc.ERROR("Supervisor_group '{}' has no remove flag set while its supervisor ({}) has not!".format(grp[NAME], supervisord[NAME]))
                grp[CONF_FILE_SRC_JJ2] = os.path.join(self.path, "templates/group.conf.jj2")
                grp[CONF_FILE_SRC_J2] = "supervisor_{}_group_{}.conf".format(supervisord[NAME], grp[NAME])
                grp[CONF_FILE_DST] = os.path.join(supervisord[INCLUDE_DIR], "{}_grp.ini".format(grp[NAME]))
                grp[SUPERVISOR_OWNER] = supervisord[USER]
                grp[SUPERVISOR_GROUP] = supervisord[GROUP]
                grp[SUPERVISOR_CONF] = supervisord[CONF_FILE_DST]
                grp[_NAME_] = grp[NAME] + ":"
                    
                # ---------------------- Insert in scope
                misc.ensureObjectInMaps(self.context.model[DATA][SUPERVISORS][SCOPE_BY_NAME], [grp[_SCOPE_], GROUPS_TO_MANAGE], [])
                model[DATA][SUPERVISORS][SCOPE_BY_NAME][grp[_SCOPE_]][GROUPS_TO_MANAGE].append(grp)
                if not grp[NO_REMOVE]:
                    misc.ensureObjectInMaps(self.context.model[DATA][SUPERVISORS][SCOPE_BY_NAME], [grp[_SCOPE_], GROUPS_TO_REMOVE], [])
                    model[DATA][SUPERVISORS][SCOPE_BY_NAME][grp[_SCOPE_]][GROUPS_TO_REMOVE].append(grp)
                    
  
    
    def buildAuxTemplates(self, action, priority):
        if self.context.toExclude(SCOPE_SUPERVISOR):
            return
        if action != ACTION_DEPLOY:
            return
        model = self.context.model
        if SUPERVISORS in model[SRC]:
            for supervisord in model[SRC][SUPERVISORS]:
                if supervisord[MANAGED]:
                    templator = Templator(["/"], supervisord)    # All template path are absolute
                    templator.generate(supervisord[CONF_FILE_SRC_JJ2], os.path.join(self.context.workingFolder, supervisord[CONF_FILE_SRC_J2]))
                    templator.generate(supervisord[SERVICE_UNIT_JJ2],  os.path.join(self.context.workingFolder, supervisord[SERVICE_UNIT_J2]))
                    templator.generate(supervisord[SUPERVISORCTL_JJ2],  os.path.join(self.context.workingFolder, supervisord[SUPERVISORCTL_J2]))
        if SUPERVISOR_PROGRAMS in model[SRC]:
            for prg in model[SRC][SUPERVISOR_PROGRAMS]:
                templator = Templator(["/"], prg)    # All template path are absolute
                templator.generate(prg[CONF_FILE_SRC_JJ2], os.path.join(self.context.workingFolder, prg[CONF_FILE_SRC_J2]))
        if SUPERVISOR_GROUPS in model[SRC]:
            for grp in model[SRC][SUPERVISOR_GROUPS]:
                templator = Templator(["/"], grp)    # All template path are absolute
                templator.generate(grp[CONF_FILE_SRC_JJ2], os.path.join(self.context.workingFolder, grp[CONF_FILE_SRC_J2]))


    
                
    
                

