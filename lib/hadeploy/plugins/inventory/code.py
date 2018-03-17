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
from hadeploy.core.const import SRC, DATA,HOST_BY_NAME, INVENTORY, SSH_USER
import hadeploy.core.misc as misc
import os
from sets import Set

logger = logging.getLogger("hadeploy.plugins.inventory")


HOSTS="hosts"
SSH_PRIVATE_FILE_FILE="ssh_private_key_file"
HOST_OVERRIDES="host_overrides"
HOST_GROUP_OVERRIDES="host_group_overrides"
NAME="name"
HOST_GROUPS="host_groups"
GROUPS="groups"
SSH_HOST="ssh_host"
SSH_PASSWORD="ssh_password"
SSH_EXTRA_ARGS="ssh_extra_args"
FORCE_SETUP="force_setup"
PRIORITY="priority"

HOST_GROUP_BY_NAME="hostGroupByName"
HOSTS_TO_SETUP="hostsToSetup"

EXIT_ON_FAIL="exit_on_fail"

ANSIBLE_MODEL="_ansible_model_"

class InventoryPlugin(Plugin):
    
    def __init__(self, name, path, context):
        Plugin.__init__(self, name, path, context)
        self.myHostGroups = []
    
    def onNewSnippet(self, snippetPath):
        #logger.debug("Called inventory self.onNewSnippet()")
        if HOSTS in self.context.model[SRC]:
            for h in self.context.model[SRC][HOSTS]:
                if SSH_PRIVATE_FILE_FILE in h and h[SSH_PRIVATE_FILE_FILE] != '':
                    h[SSH_PRIVATE_FILE_FILE] = misc.snippetRelocate(snippetPath, h[SSH_PRIVATE_FILE_FILE])
        if HOST_OVERRIDES in self.context.model[SRC]:
            for h in self.context.model[SRC][HOST_OVERRIDES]:
                if SSH_PRIVATE_FILE_FILE in h and h[SSH_PRIVATE_FILE_FILE] != '':
                    h[SSH_PRIVATE_FILE_FILE] = misc.snippetRelocate(snippetPath, h[SSH_PRIVATE_FILE_FILE])
            
    def getGroomingPriority(self):
        return 1300     

    
    def getSupportedActions(self):
        """Return list of supported actions. ["*"] means we will be involved in all action. (But do not add anything to an eventual action list)"""
        return ["*"]

    def getPriority(self, action):
        return 1300
    

    def onGrooming(self):
        self.context.model[DATA][INVENTORY] = {}
        misc.applyWhenOnList(self.context.model[SRC], HOSTS)
        misc.applyWhenOnList(self.context.model[SRC], HOST_GROUPS)
        misc.applyWhenOnList(self.context.model[SRC], HOST_OVERRIDES)
        misc.applyWhenOnList(self.context.model[SRC], HOST_GROUP_OVERRIDES)
        buildHostDicts(self.context.model)
        flattenGroups(self.context.model)
        handleHostOverrides(self.context.model)
        handleHostGroupOverrides(self.context.model)
        check(self.context.model)
        prepareAnsibleModel(self.context.model)
        misc.setDefaultInMap(self.context.model[SRC], EXIT_ON_FAIL, True)
        

# ---------------------------------------------------- Static functions

def prepareAnsibleModel(model):
    if HOSTS in model[SRC]:
        for host in model[SRC][HOSTS]:
            ansibleModel = {}
            for key in host:
                # Handle name change in Ansible 2.0
                if key == "ssh_host" or key == "host":
                    ansibleModel["ansible_host"] = host[key]
                elif key == "ssh_port" or key == "port":
                    ansibleModel["ansible_port"] = host[key]
                elif key == "ssh_user" or key == "user":
                    ansibleModel["ansible_user"] = host[key]
                # Fix a delta between HADeploy and Ansible attributes
                elif key == "ssh_password":
                    ansibleModel["ansible_ssh_pass"] = host[key]
                # Skip attributes not intended to Ansible
                elif key == "name" or key == "force_setup":
                    pass 
                else:
                    ansibleModel["ansible_" + key] = host[key]
                # Force become if needed
                if "ansible_become_user" in ansibleModel or "ansible_become_pass" in ansibleModel or "ansible_become_method" in ansibleModel or "ansible_become_exe" in ansibleModel:
                    ansibleModel["ansible_become"] = True
            host[ANSIBLE_MODEL] = ansibleModel
                    

def buildHostDicts(model):
    # logger.debug("Build host dicts")
    hostByName = {}
    if HOSTS in model[SRC]:
        for host in model[SRC][HOSTS]:
            hostByName[host[NAME]] = host
    model[DATA][INVENTORY][HOST_BY_NAME] = hostByName
    hostGroupByName = {}
    if HOST_GROUPS in model[SRC]:        
        for hg in model[SRC][HOST_GROUPS]:
            if HOSTS not in hg:
                hg[HOSTS] = []
            if GROUPS not in hg:
                hg[GROUPS] = []
            hostGroupByName[hg[NAME]] = hg
    model[DATA][INVENTORY][HOST_GROUP_BY_NAME] = hostGroupByName

def flattenGroups(model):
    if HOST_GROUPS in model[SRC]:
        for hg in model[SRC][HOST_GROUPS]:
            flattenGroup(model[DATA][INVENTORY][HOST_GROUP_BY_NAME], hg, 0, hg[NAME])
    
    
    
def flattenGroup(hostGroupByName, hg, loopCount, outerGroupName):
    if(loopCount > 50):
        misc.ERROR("Infinite loop on host_groups '{0}' recursion".format(outerGroupName))
    if GROUPS in hg:
        for childGroupName in hg[GROUPS]:
            if not childGroupName in hostGroupByName:
                misc.ERROR("Group '{0}': Inner group '{1}' does not exists!")
            else:
                childGroup =  hostGroupByName[childGroupName]
                flattenGroup(hostGroupByName, childGroup, loopCount + 1, outerGroupName)
                for h in childGroup[HOSTS]:
                    if not h in hg[HOSTS]:
                        hg[HOSTS].append(h)
        del(hg[GROUPS]) # Mark it as flattened
           
    
def check(model):
    hostsToSetup = Set()
    if HOSTS in model[SRC]:
        for h in model[SRC][HOSTS]:
            misc.setDefaultInMap(h, FORCE_SETUP, False)
            if SSH_USER not in h:
                misc.ERROR("Hosts:'{0}': 'ssh_user must be defined!".format(h[NAME]))
            if (SSH_PRIVATE_FILE_FILE in h) and (SSH_PASSWORD in h):
                misc.ERROR("Hosts:'{0}': 'ssh_private_key_file' and 'ssh_password' can't be both defined!".format(h[NAME]))
            #if (not SSH_PRIVATE_FILE_FILE in h) and (not 'ssh_password' in h):
            #    misc.ERROR("Hosts:'{0}': One of 'ssh_private_key_file' or 'ssh_password' must be defined!".format(h[NAME]))
            if SSH_PRIVATE_FILE_FILE in h:
                if not os.path.exists(h[SSH_PRIVATE_FILE_FILE]):
                    misc.ERROR("host:{0}': ssh_private_key_file  '{1}' does not exists!".format(h[NAME], h[SSH_PRIVATE_FILE_FILE]))
            if h[FORCE_SETUP]:
                hostsToSetup.add(h[NAME])
    if HOST_GROUPS in model[SRC]:
        for hg in model[SRC][HOST_GROUPS]:
            misc.setDefaultInMap(hg, FORCE_SETUP, False)
            for hname in hg[HOSTS]:
                if not hname in model[DATA][INVENTORY][HOST_BY_NAME]:
                    misc.ERROR("Group '{0}': Host '{1}' is not defined!".format(hg[NAME], hname))      
                if hg[FORCE_SETUP]:
                    hostsToSetup.add(hname)
    model[DATA][INVENTORY][HOSTS_TO_SETUP] = list(hostsToSetup)

def handleHostOverrides(model):
    if HOST_OVERRIDES in model[SRC]:
        for hover in model[SRC][HOST_OVERRIDES]:
            misc.setDefaultInMap(hover, PRIORITY, 100)
        hoverList =  sorted(model[SRC][HOST_OVERRIDES], key = lambda hover: hover[PRIORITY])
        for hover in hoverList:
            if hover[NAME] == 'all' or hover[NAME] == '*':
                if HOSTS in model[SRC]:
                    for host in model[SRC][HOSTS]:
                        handleHostOverride(host, hover)
                else:
                    misc.ERROR("No host definition at all. Can't override")
            else:
                if hover[NAME] in model[DATA][INVENTORY][HOST_BY_NAME]:
                    handleHostOverride(model[DATA][INVENTORY][HOST_BY_NAME][hover[NAME]], hover)
                else:
                    misc.ERROR("Trying to override unexisting host: '{0}'".format(hover[NAME]))
                                
def handleHostOverride(host, overrider):
    for key in overrider:
        if key != "name":
            host[key] = overrider[key]
    todel = []
    for k in host:
        if host[k] == "":
            todel.append(k)
    for k in todel:
        del host[k]

def handleHostGroupOverrides(model):
    if HOST_GROUP_OVERRIDES in model[SRC]:
        for hgover in model[SRC][HOST_GROUP_OVERRIDES]:
            if hgover[NAME] == 'all' or hgover[NAME] == '*':
                for hg in model[SRC][HOST_GROUPS]:
                    handleHostGroupOverride(hg, hgover)
            else:
                if hgover[NAME] in model[DATA][INVENTORY][HOST_GROUP_BY_NAME]:
                    handleHostGroupOverride(model[DATA][INVENTORY][HOST_GROUP_BY_NAME][hgover[NAME]], hgover)
                else:
                    misc.ERROR("Trying to override unexisting host_group: '{0}'".format(hgover[NAME]))
                    

def handleHostGroupOverride(hostGroup, overrider):
    if HOSTS in overrider:
        hostGroup[HOSTS] = overrider[HOSTS]
    if FORCE_SETUP in overrider:
        hostGroup[FORCE_SETUP] = overrider[FORCE_SETUP]
        