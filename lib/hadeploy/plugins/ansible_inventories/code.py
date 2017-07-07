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
import getpass

from ansible.inventory import Inventory
from ansible.parsing.dataloader import DataLoader
from ansible.vars import VariableManager

from hadeploy.core.plugin import Plugin
from hadeploy.core.const import SRC


HOSTS="hosts"
HOST_GROUPS="host_groups"
NAME="name"
SSH_PRIVATE_FILE_FILE="ssh_private_key_file"
GROUPS="groups"

ANSIBLE_INVENTORIES="ansible_inventories"
FILE="file"
NAME="name"
VAULT_PASSWORD_FILE="vault_password_file"
ASK_VAULT_PASSWORD="ask_vault_password"

logger = logging.getLogger("hadeploy.plugins.ansible")

class AnsiblePlugin(Plugin):
    
    def __init__(self, name, path, context):
        Plugin.__init__(self, name, path, context)


    def onNewSnippet(self, snippetPath):
        if ANSIBLE_INVENTORIES in self.context.model[SRC]:
            for inventory in self.context.model[SRC][ANSIBLE_INVENTORIES]:
                if FILE in inventory:
                    inventory[FILE] = misc.snippetRelocate(snippetPath, inventory[FILE])
                if VAULT_PASSWORD_FILE in inventory:
                    inventory[VAULT_PASSWORD_FILE] = misc.snippetRelocate(snippetPath, inventory[VAULT_PASSWORD_FILE])

    def getGroomingPriority(self):
        return 1200     # We don't care. Will be called before all others

    def getSupportedActions(self):
        """Return list of supported actions. ["*"] means we will be involved in all action. (But do not add anything to an eventual action list)"""
        return ["*"]

    def getPriority(self, action):
        return 1200
        
    def onGrooming(self):
        if ANSIBLE_INVENTORIES in self.context.model[SRC]:
            for inventory in self.context.model[SRC][ANSIBLE_INVENTORIES]:
                if not os.path.exists(inventory[FILE]):
                    misc.ERROR("Ansible inventory file '{0}' does not exists!".format(inventory[FILE]))
                else:
                    populateModelFromInventory(self.context.model[SRC], inventory)


def populateModelFromInventory(model, inventory):
    loader = DataLoader()
    if VAULT_PASSWORD_FILE in inventory:
        vpf = inventory[VAULT_PASSWORD_FILE]
        if not os.path.exists(vpf):
            misc.ERROR("Ansible vault password file '{0}' does not exists!".format(vpf))
        with open(vpf) as f:
            content = f.readlines()
        if len(content) == 0 or len(content[0].strip()) == 0:
            misc.ERROR("Invalid Ansible vault password file '{0}' content!".format(vpf))
        loader.set_vault_password(content[0].strip())
    elif ASK_VAULT_PASSWORD in inventory and inventory[ASK_VAULT_PASSWORD]:
        prompt = "Password for Ansible inventory{0}: ".format(" '" + inventory[NAME] + "'" if NAME in inventory else "")
        content = getpass.getpass(prompt)
        loader.set_vault_password(content.strip())
    variable_manager = VariableManager()
    
    if HOSTS not in model:
        model[HOSTS] = []
    if HOST_GROUPS not in model:
        model[HOST_GROUPS] = []
    
    try:
        inventory = Inventory(loader=loader, variable_manager=variable_manager, host_list=inventory[FILE])
    except Exception as e:
        misc.ERROR(str(e))
    
    variable_manager.set_inventory(inventory)
    
    hosts = inventory.get_hosts()
    
    existingHosts = set(map(lambda x : x[NAME], model[HOSTS]))
    #print(existingHosts)
    for host in hosts:
        if not host.name in existingHosts:
            h = {}
            h[NAME] = host.name.encode('utf8')
            for key in host.vars:
                if key.startswith('ansible_'):
                    key2 = key[len('ansible_'):].encode('utf8')
                    h[key2] = host.vars[key].encode('utf8')
                    # ssh_private_key_file may be relative to source inventory file. Set it absolute
                    if key2 == SSH_PRIVATE_FILE_FILE:
                        p = h[key2]
                        if not os.path.isabs(p):
                            h[key2] = os.path.normpath(os.path.join(os.path.dirname(inventory[FILE]), p))
            model[HOSTS].append(h)

    existingHostGroups = set(map(lambda x : x[NAME], model[HOST_GROUPS]))
    #print(existingHostGroups)
    hvars = variable_manager.get_vars(loader, host=hosts[0], include_hostvars=False)
    groups = hvars[GROUPS]
    for grpName in groups:
        if grpName != 'all' and grpName != 'ungrouped' and (not grpName in existingHostGroups):
            grp = {}
            grp[NAME] = grpName.encode('utf8')
            l = []
            for h in groups[grpName]:
                l.append(h.encode('utf8')) 
            grp[HOSTS] = l
            model[HOST_GROUPS].append(grp)
            
            
    