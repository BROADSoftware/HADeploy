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
import hadeploy.core.misc as misc
from hadeploy.core.plugin import Plugin
from hadeploy.core.const import SRC,DATA,SCOPE_ANSIBLE


ANSIBLE_PLAYBOOKS="ansible_playbooks"
PLAYBOOK="playbook"
ACTION="action"
PRIORITY="priority"

PLAYBOOKS_FOLDERS="playbooks_folders"
ROLES_FOLDERS="roles_folders"

PLAYBOOKS_BY_ACTION_BY_PRIORITY="playbooksByActionByPriority"

class AnsiblePlugin(Plugin):
    
    def __init__(self, name, path, context):
        Plugin.__init__(self, name, path, context)

        
    def onNewSnippet(self, snippetPath):
        model = self.context.model
        if PLAYBOOKS_FOLDERS in model[SRC]:
            l2 = []
            for p in model[SRC][PLAYBOOKS_FOLDERS]:
                l2.append(misc.snippetRelocate(snippetPath, p))
            model[SRC][PLAYBOOKS_FOLDERS] = l2
        if ROLES_FOLDERS in model[SRC]:
            l2 = []
            for p in model[SRC][ROLES_FOLDERS]:
                l2.append(misc.snippetRelocate(snippetPath, p))
            model[SRC][ROLES_FOLDERS] = l2
        
    def getGroomingPriority(self):
        return 1400     # We don't care. Will be called before all others


    def lookupPathInFolderList(self, path, folderListId, kind):
        if path.startswith("/"):
            return path
        else:
            if not folderListId in self.context.model[SRC]:
                misc.ERROR("Missing '{0}' definition while some {1} are not absolute (i.e: '{2}')".format(folderListId, kind, path))
            for folder in self.context.model[SRC][folderListId]:
                p = os.path.normpath(os.path.join(folder, path))
                if os.path.exists(p):
                    return p
            misc.ERROR("Unable to find {0} '{1}' in {2}".format(kind, path, self.context.model[SRC][folderListId]))
        
    def onGrooming(self):
        """ Main job is to build a referencial playbookByActionByPriority"""
        playbooksByActionByPriority = {}
        if not self.context.toExclude(SCOPE_ANSIBLE):
            src = self.context.model[SRC]
            if ANSIBLE_PLAYBOOKS in src:
                for pl in src[ANSIBLE_PLAYBOOKS]:
                    action = pl[ACTION]
                    priority = pl[PRIORITY]
                    playbook = self.lookupPathInFolderList(pl[PLAYBOOK], PLAYBOOKS_FOLDERS, "playbook")
                    misc.ensureObjectInMaps(playbooksByActionByPriority, [action], {})
                    misc.ensureObjectInMaps(playbooksByActionByPriority[action], [priority], [])
                    playbooksByActionByPriority[action][priority].append(playbook)
        self.referential = playbooksByActionByPriority
        # We don't need to expose this to template, but this can be usefull for debugging
        self.context.model[DATA][PLAYBOOKS_BY_ACTION_BY_PRIORITY] = playbooksByActionByPriority
                

    def getSupportedActions(self):
        return self.referential.keys()

    def getPriority(self, action):
        return self.referential[action].keys()

    def getTemplates(self, action, priority):
        return self.referential[action][priority]

    def getRolesPaths(self, action, priority):
        if ROLES_FOLDERS in self.context.model[SRC]:
            return self.context.model[SRC][ROLES_FOLDERS]
        else:
            return []

