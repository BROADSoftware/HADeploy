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
from sets import Set

from hadeploy.core.plugin import Plugin
from hadeploy.core.const import SRC,DATA,DEFAULT_HDFS_RELAY_CACHE_FOLDER,INVENTORY,HOST_BY_NAME,SCOPE_FILES,SCOPE_HDFS,ACTION_DEPLOY,ACTION_REMOVE,\
    SCOPE_SYSTEMD, SCOPE_SUPERVISOR, SCOPE_STORM, SCOPE_YARN

"""
    This plugin also prepare data for the HDFS plugin, conditioned by the fact an hdfs_relay is defined
"""

#DEFAULT_HDFS_RELAY_CACHE_FOLDER='/var/cache/hadeploy/files'


NO_REMOVE="no_remove"
FILES="files"
FOLDERS="folders"
TREES="trees"

NODE_FILE_TO_HDFS="nodeFileToHdfs"
NODE_TREE_TO_HDFS="nodeTreeToHdfs"

HDFS="hdfs"
HDFS_RELAY="hdfs_relay"
CACHEFOLDERS="cacheFolders"
LOCAL_FILES_FOLDERS="local_files_folders"
LOCAL_TEMPLATES_FOLDERS="local_templates_folders"
SOURCE_HOST_CREDENTIALS="source_host_credentials"

# items attributes
FSRC="src"
SCOPE="scope"
DEST_NAME="dest_name"
CACHE_FOLDER="cache_folder"
DEST_FOLDER="dest_folder"
VALIDATE_CERTS="validate_certs"
FORCE_BASIC_AUTH="force_basic_auth"

SCOPE_BY_NAME="scopeByName"     

NODE_TO_HDFS_BY_NAME="nodeToHdfsByName"     

_SRC_="_src_"
_TARGET_="_target_"
_TARGETFOLDERS_="_targetFolders_"
_DISPLAY_SRC_="_displaySrc_"
_CACHE_TARGET_="_cacheTarget_"
_TSRC_="_tsrc_"

NODE_TO_HDFS_FLAG="_nodeToHdfs_"

MAVEN_REPOSITORIES="maven_repositories"
MAVEN_REPO_BY_NAME="mavenRepoByName"
URL="url"
RELEASES_URL="releases_url"
SNAPSHOTS_URL="snapshots_url"
LASTEST_URL="latest_url"
_REPO_URL_="_repoUrl_"

_REPO_ = "_repo_"
_GROUP_ID_ = "_groupId_"
_ARTIFACT_ID_ = "_artifactId_"
_VERSION_ = "_version_"
TIMEOUT="timeout"
_EXTENSION_="_extension_"
WILL_USER_MAVEN_REPO = "willUseMavenRepo"    
_CLASSIFIER_="_classifier_"    
SYSTEMD_NOTIFICATIONS="systemdNotifications"
SUPERVISOR_PRG_NOTIFICATIONS="supervisorPrgNotification"
STORM_NOTIFICATIONS="stormNotifications"
YARN_NOTIFICATIONS="yarnNotifications"

NOTIFY="notify"
_NOTIFY_="_notify_" # Need an id for the Ansible listener, valid for both systemd_unit and supervisor
SYSTEMD_UNITS="systemd_units"
SUPERVISOR_PROGRAMS="supervisor_programs"
SUPERVISOR="supervisor"
NAME="name"

logger = logging.getLogger("hadeploy.plugins.files")

class FilesPlugin(Plugin):
    
    def __init__(self, name, path, context):
        Plugin.__init__(self, name, path, context)


    def onNewSnippet(self, snippetPath):
        model = self.context.model
        if LOCAL_FILES_FOLDERS in model[SRC]:
            l2 = []
            for p in model[SRC][LOCAL_FILES_FOLDERS]:
                l2.append(misc.snippetRelocate(snippetPath, p))
            model[SRC][LOCAL_FILES_FOLDERS] = l2
        if LOCAL_TEMPLATES_FOLDERS in model[SRC]:
            l2 = []
            for p in model[SRC][LOCAL_TEMPLATES_FOLDERS]:
                l2.append(misc.snippetRelocate(snippetPath, p))
            model[SRC][LOCAL_TEMPLATES_FOLDERS] = l2

           
    def getGroomingPriority(self):
        return 3000     

    def getSupportedScopes(self):
        return [SCOPE_FILES,SCOPE_HDFS]        
 
    def getSupportedActions(self):
        return [ACTION_DEPLOY, ACTION_REMOVE]

    def getPriority(self, action):
        return 3000 if action == ACTION_DEPLOY else 4000 if action == ACTION_REMOVE else misc.ERROR("Plugin 'Files' called with invalid action: '{0}'".format(action))

    def onGrooming(self):
        model = self.context.model
        misc.ensureObjectInMaps(model[DATA], [FILES, SCOPE_BY_NAME], {})
        if HDFS in self.context.pluginByName:
            # We need to anticipate on works performed by hdfs plugin, as we need it right now
            misc.ensureObjectInMaps(model[DATA], [HDFS, NODE_TO_HDFS_BY_NAME], {})
            misc.ensureObjectInMaps(model[DATA], [HDFS, FILES], [] )
            misc.ensureObjectInMaps(model[DATA], [HDFS, FOLDERS], [] )
            misc.ensureObjectInMaps(model[DATA], [HDFS, TREES], [] )
            misc.ensureObjectInMaps(model[DATA], [HDFS, CACHEFOLDERS], Set())
            misc.applyWhenOnSingle(self.context.model[SRC], HDFS_RELAY)
            misc.applyWhenOnList(self.context.model[SRC], SOURCE_HOST_CREDENTIALS)
        if HDFS_RELAY in model[SRC]:
            misc.setDefaultInMap(model[SRC][HDFS_RELAY], CACHE_FOLDER, DEFAULT_HDFS_RELAY_CACHE_FOLDER)
        misc.applyWhenOnList(self.context.model[SRC], MAVEN_REPOSITORIES)
        misc.applyWhenOnList(self.context.model[SRC], FOLDERS)
        misc.applyWhenOnList(self.context.model[SRC], FILES)
        misc.applyWhenOnList(self.context.model[SRC], TREES)
        groomMavenRepositories(self.context)
        groomFolders(self.context)
        groomFiles(self.context)
        groomTrees(self.context)
        
        # Handle scope exclusion        
        if self.context.toExclude(SCOPE_FILES):
            scopeToRemove = []
            for scope in model[DATA][FILES][SCOPE_BY_NAME]:
                if(self.context.toExclude(scope)):
                    scopeToRemove.append(scope)
            for scope in scopeToRemove:
                del(model[DATA][FILES][SCOPE_BY_NAME][scope])
        if(self.context.toExclude(SCOPE_HDFS) and HDFS in model[DATA]):
            model[DATA][HDFS][FILES] = []
            model[DATA][HDFS][FOLDERS] = []
            model[DATA][HDFS][TREES] = []
            model[DATA][HDFS][NODE_TO_HDFS_BY_NAME] = {}
        
        if HDFS in model[DATA] and len(model[DATA][HDFS][NODE_TO_HDFS_BY_NAME]) == 0 and len(model[DATA][HDFS][FILES]) == 0 and len(model[DATA][HDFS][FOLDERS]) == 0 and len(model[DATA][HDFS][TREES]) == 0:
            # Optimization for execution time
            if HDFS_RELAY in model[SRC]:
                del(model[SRC][HDFS_RELAY])
        setWillUseMavenRepo(model)
        setServiceNotifications(self.context)        
        
            
# ---------------------------------------------------- Static functions

        
def setWillUseMavenRepo(model):        
    # Set a flag for scope including maven_repository, as we will need specific lxml package.
    for _, scope in (model[DATA][FILES][SCOPE_BY_NAME]).iteritems():
        scope[WILL_USER_MAVEN_REPO] = False
        for f in scope[FILES]:
            if _REPO_ in f:
                scope[WILL_USER_MAVEN_REPO] = True
    model[DATA][HDFS][WILL_USER_MAVEN_REPO] = False
    for f in model[DATA][HDFS][FILES]:
        if _REPO_ in f:
            model[DATA][HDFS][WILL_USER_MAVEN_REPO] = True



def lookupSystemdUnit(model, unitName):
    if SYSTEMD_UNITS in model[SRC]:
        for unit in model[SRC][SYSTEMD_UNITS]:
            if unit[NAME] == unitName:
                return unit
    else:
        return None

def lookupSupervisorProgram(model, prgName):
    # prgName must be in the form "supervisor/program"
    x = prgName.split("/")
    if len(x) == 2:
        if SUPERVISOR_PROGRAMS in model[SRC]:
            for prg in model[SRC][SUPERVISOR_PROGRAMS]:
                if prg[SUPERVISOR] == x[0] and prg[NAME] == x[1]:
                    return prg
    return None

SUPERVISORS="supervisors"

# When we need this info, grooming is not yet performed on supervisor
#def lookupSupervisorScope(model, supervisorName):
#    if SUPERVISORS in model[SRC]:
#        for s in model[SRC][SUPERVISORS]:
#            if s[NAME] == supervisorName:
#                return s[SCOPE]
#    return None

STORM_TOPOLOGIES="storm_topologies"
NOTIFY_SYSTEMD_PREFIX="systemd://"
NOTIFY_SUPERVISOR_PREFIX="supervisor://"
NOTIFY_STORM_PREFIX="storm://"
NOTIFY_YARN_PREFIX="yarn://"

def lookupTopology(model, name):
    if STORM_TOPOLOGIES in model[SRC]:
        for t in model[SRC][STORM_TOPOLOGIES]:
            if t[NAME] == name:
                return t
    return None
    
YARN_SERVICES="yarn_services"
    
def lookupYarnService(model, name):
    if YARN_SERVICES in model[SRC]:
        for s in model[SRC][YARN_SERVICES]:
            if s[NAME] == name:
                return s
    return None
    

        
def setServiceNotifications(context):
    model = context.model
    # Set a list of notification handler to setup per scope
    for scopeName, scope in (model[DATA][FILES][SCOPE_BY_NAME]).iteritems():
        misc.ensureObjectInMaps(scope, [SYSTEMD_NOTIFICATIONS], {})
        misc.ensureObjectInMaps(scope, [SUPERVISOR_PRG_NOTIFICATIONS], {})
        misc.ensureObjectInMaps(scope, [STORM_NOTIFICATIONS], {})
        misc.ensureObjectInMaps(scope, [YARN_NOTIFICATIONS], {})
        for f in scope[FILES]:
            if NOTIFY in f:
                f[_NOTIFY_] = []
                for notification in f[NOTIFY]:
                    if  notification.startswith(NOTIFY_SYSTEMD_PREFIX):
                        if not context.toExclude(SCOPE_SYSTEMD): 
                            if not notification in scope[SYSTEMD_NOTIFICATIONS]:
                                # Not already notified
                                unitName = notification[len(NOTIFY_SYSTEMD_PREFIX):]
                                unit = lookupSystemdUnit(model, unitName)
                                if unit:
                                    if scopeName != unit[SCOPE]:
                                        misc.ERROR("Files: '{}': Scope is '{}' while scope of systemd_unit '{}' is '{}'. Must be same".format(f[FSRC], scopeName, unit[NAME], unit[SCOPE]))
                                    scope[SYSTEMD_NOTIFICATIONS][notification] = unit
                                else:
                                    misc.ERROR("Files: '{}': There is no systemd_unit named '{}' defined in this deployment".format(f[FSRC], unitName))
                            f[_NOTIFY_].append(notification)
                    elif notification.startswith(NOTIFY_SUPERVISOR_PREFIX):
                        if not context.toExclude(SCOPE_SUPERVISOR):
                            if not notification in scope[SUPERVISOR_PRG_NOTIFICATIONS]:
                                prgName = notification[len(NOTIFY_SUPERVISOR_PREFIX):]
                                prg = lookupSupervisorProgram(model, prgName)
                                if prg:
                                    #prgScope = lookupSupervisorScope(model, prg[SUPERVISOR]) 
                                    prgScope = prg[SCOPE]
                                    if scopeName != prgScope: 
                                        misc.ERROR("Files: '{}': Scope is '{}' while scope of supervisor program '{}' is '{}'. Must be same".format(f[FSRC], scopeName, prg[NAME], prgScope))
                                    scope[SUPERVISOR_PRG_NOTIFICATIONS][notification] = prg
                                else:
                                    misc.ERROR("Files: '{}': There is no supervisor/program '{}' defined in this deployment".format(f[FSRC], prgName))
                            f[_NOTIFY_].append(notification)
                    elif notification.startswith(NOTIFY_STORM_PREFIX):
                        if not context.toExclude(SCOPE_STORM):
                            if not notification in scope[STORM_NOTIFICATIONS]:
                                topologyName = notification[len(NOTIFY_STORM_PREFIX):]
                                topology = lookupTopology(model, topologyName)
                                if topology:
                                    scope[STORM_NOTIFICATIONS][notification] = topology
                                else:
                                    misc.ERROR("Files: '{}': There is no topology '{}' defined in this deployment".format(f[FSRC], topologyName))
                            f[_NOTIFY_].append(notification)
                    elif notification.startswith(NOTIFY_YARN_PREFIX):
                        if not context.toExclude(SCOPE_YARN):
                            if not notification in scope[YARN_NOTIFICATIONS]:
                                serviceName = notification[len(NOTIFY_YARN_PREFIX):]
                                service = lookupYarnService(model, serviceName)
                                if service:
                                    scope[YARN_NOTIFICATIONS][notification] = service
                                else:
                                    misc.ERROR("Files: '{}': There is no yarn_services '{}' defined in this deployment".format(f[FSRC], serviceName))
                            f[_NOTIFY_].append(notification)
                    else:
                        misc.ERROR("Files: '{0}': notify '{1}' must begin with 'systemd://', 'supervisor://' or 'storm://'".format(f[FSRC], notification))
                if len(f[_NOTIFY_]) == 0:
                    del(f[_NOTIFY_])
                    
                    
def ensureScope(model, scope):
    root = model[DATA][FILES][SCOPE_BY_NAME]
    if not scope in root:
        misc.ensureObjectInMaps(root, [scope, FILES], [])
        misc.ensureObjectInMaps(root, [scope, FOLDERS], [])
        misc.ensureObjectInMaps(root, [scope, TREES], [])

def ensureHdfsScope(model, scope):
    root = model[DATA][HDFS][NODE_TO_HDFS_BY_NAME]
    if not scope in root:
        misc.ensureObjectInMaps(root, [scope, FILES], [])
        misc.ensureObjectInMaps(root, [scope, TREES], [])

def groomFolders(context):
    model = context.model
    if FOLDERS in model[SRC]:
        for folder in model[SRC][FOLDERS]:
            misc.setDefaultInMap(folder, NO_REMOVE, False)
            if folder[SCOPE] == HDFS:
                if not HDFS_RELAY in model[SRC]:
                    misc.ERROR("Scope of folder '{0}' is 'hdfs' while no hdfs_relay was defined!".format(folder['path']))
                else:
                    model[DATA][HDFS][FOLDERS].append(folder)
            else:
                if not context.checkScope(folder[SCOPE]):
                    misc.ERROR("Folder {0}: Scope attribute '{1}' does not match any host or host_group and is not 'hdfs'!".format(folder['path'], folder[SCOPE]))
                else:
                    ensureScope(model, folder[SCOPE])
                    context.model[DATA][FILES][SCOPE_BY_NAME][folder[SCOPE]][FOLDERS].append(folder)
   
def groomFiles(context):
    model = context.model
    if FILES in model[SRC]:
        for f in model[SRC][FILES]:
            misc.setDefaultInMap(f, NO_REMOVE, False)
            if f[FSRC].startswith('file://'):
                groomFileFiles(f, model)
            elif f[FSRC].startswith('http://') or  f[FSRC].startswith('https://'):
                groomHttpFiles(f, model)
            elif f[FSRC].startswith('tmpl://'):
                groomTmplFiles(f, model)
            elif f[FSRC].startswith('node://'):
                groomNodeToHdfsFiles(f, model)
            elif f[FSRC].startswith('mvn://'):
                groomMavenFiles(f, model)
            else:
                misc.ERROR("Files: {0} is not a valid form for 'src' attribute. Unknown scheme".format(f[FSRC]))
            if f[SCOPE] == HDFS:
                if not HDFS_RELAY in model[SRC]:
                    misc.ERROR("Scope of file '{0}' is 'hdfs' while no hdfs_relay was defined!".format(f[SRC]))
                else:
                    model[DATA][HDFS][FILES].append(f)
                    # This one is intended to be used in the cache
                    f[_CACHE_TARGET_] = os.path.normpath(model[SRC][HDFS_RELAY][CACHE_FOLDER] + "/" +  manglePath(f[_TARGET_]))
                    model[DATA][HDFS][CACHEFOLDERS].add(os.path.dirname(f[_CACHE_TARGET_]))
            else:
                if not context.checkScope(f[SCOPE] ):
                    misc.ERROR("File {0}: Scope attribute '{1}' does not match any host or host_group and is not 'hdfs'!".format(f[FSRC], f[SCOPE]))
                else:
                    if NODE_TO_HDFS_FLAG in f:
                        ensureHdfsScope(model, f[SCOPE])
                        model[DATA][HDFS][NODE_TO_HDFS_BY_NAME][f[SCOPE]][FILES].append(f)
                    else:
                        ensureScope(model, f[SCOPE])
                        context.model[DATA][FILES][SCOPE_BY_NAME][f[SCOPE]][FILES].append(f)
                
        
def groomNodeToHdfsFiles(f, model):
    groomNodeToHdfsFilesOrTrees(f, model)
    

# Simpler to handle this here than in hdfs plugin
def groomNodeToHdfsFilesOrTrees(f, model):
    misc.setDefaultInMap(f, DEST_NAME,  os.path.basename(f[FSRC]))
    f[_TARGET_] = os.path.normpath(os.path.join(f[DEST_FOLDER], f[DEST_NAME]))
    src = f[FSRC][len("node://"):]
    p = src.find("/")
    if p != -1:
        node = src[:p]
        if not node in model[DATA][INVENTORY][HOST_BY_NAME]:
            misc.ERROR("Files: {0} is not a valid form for 'src' attribute: Node '{1}' does not exists".format(f[FSRC], node))
        else:
            if f[SCOPE] != HDFS:
                misc.ERROR("Files: {0} is not a valid form for 'src' attribute: Copying from node is only valid for 'hdfs' scope".format(f[FSRC]))
            else:
                path = src[p:]
                if not path.startswith("/"):
                    misc.ERROR("Files: {0} is not a valid form for 'src' attribute: Copying from node require an absolute path".format(f[FSRC]))
                f[_SRC_] = path
                f[SCOPE] = node
                f[NODE_TO_HDFS_FLAG] = True    # Flag it as a special meaning
    else:
        misc.ERROR("Files: {0} is not a valid form as 'src' attribute".format(f[FSRC]))

    
def manglePath(folder):
    return folder
    #return folder.replace("/", "_")


def groomFileFiles(f, model):
    misc.setDefaultInMap(f, DEST_NAME,  os.path.basename(f[FSRC]))
    f[_TARGET_] = os.path.normpath(os.path.join(f[DEST_FOLDER], f[DEST_NAME]))
    path = f[FSRC][len('file://'):] 
    f[_DISPLAY_SRC_] = path
    if not path.startswith("/"):
        path = lookupInLocalFiles(path, model)
    else:
        if not os.path.exists(path):
            misc.ERROR("'{0}' does not exists".format(path))
    if os.path.isdir(path):
        misc.ERROR("File '{0}' is a folder. Use 'trees' block to copy a folder in a recursive way".format(f[FSRC]))
    f[_SRC_] = path

def groomHttpFiles(f, model):
    misc.setDefaultInMap(f, DEST_NAME,  os.path.basename(f[FSRC]))
    f[_TARGET_] = os.path.normpath(os.path.join(f[DEST_FOLDER], f[DEST_NAME]))
    misc.setDefaultInMap(f, VALIDATE_CERTS, True)
    misc.setDefaultInMap(f, FORCE_BASIC_AUTH, False)

def groomTmplFiles(f, model):
    misc.setDefaultInMap(f, DEST_NAME,  os.path.basename(f[FSRC]))
    f[_TARGET_] = os.path.normpath(os.path.join(f[DEST_FOLDER], f[DEST_NAME]))
    path = f[FSRC][len('tmpl://'):] 
    f[_DISPLAY_SRC_] = path
    if not path.startswith("/"):
        path = lookupInLocalTemplates(path, model)
    else:
        if not os.path.exists(path):
            misc.ERROR("'{0}' does not exists".format(path))
    if os.path.isdir(path):
        misc.ERROR("Files: '{0}' is is a folder. Can't be a template source. Use 'trees' block to copy a folder in a recursive way".format(f[FSRC]))
    f[_SRC_] = path

def lookupInLocalFiles(path, model):
    if LOCAL_FILES_FOLDERS not in model[SRC]:
        misc.ERROR("Missing 'local_files_folders' definition while some files://... definition are not absolute")
    for ff in model[SRC][LOCAL_FILES_FOLDERS]:
        p = os.path.normpath(os.path.join(ff, path))
        if os.path.exists(p):
            return p
    misc.ERROR("Unable to find '{0}' in local_file_folders={1}".format(path, model[SRC][LOCAL_FILES_FOLDERS]))


def lookupInLocalTemplates(path, model):
    if LOCAL_TEMPLATES_FOLDERS not in model[SRC]:
        misc.ERROR("Missing 'local_templates_folders' definition while some tmpl://... definition are not absolute")
    for ff in model[SRC][LOCAL_TEMPLATES_FOLDERS]:
        p = os.path.normpath(os.path.join(ff, path))
        if os.path.exists(p):
            return p
    misc.ERROR("Unable to find '{0}' in local_templates_folders={1}".format(path, model[SRC][LOCAL_TEMPLATES_FOLDERS]))


def groomTrees(context):
    model = context.model
    if TREES in model[SRC]:
        for t in model[SRC][TREES]:
            misc.setDefaultInMap(t, NO_REMOVE, False)
            if t[SCOPE] == HDFS:
                if not HDFS_RELAY in model[SRC]:
                    misc.ERROR("Scope of tree '{0}' is 'hdfs' while no hdfs_relay was defined!".format(t[FSRC]))
                else:
                    # Need to setup cache now
                    t[_CACHE_TARGET_] = os.path.normpath(model[SRC][HDFS_RELAY][CACHE_FOLDER] + "/" +  manglePath(t[DEST_FOLDER]))
                    model[DATA][HDFS][CACHEFOLDERS].add(os.path.dirname(t[_CACHE_TARGET_]))
            if t[FSRC].startswith('file://'):
                groomFileTrees(t, model)
            elif t[FSRC].startswith('tmpl://'):
                groomTmplTrees(t, model)
            elif t[FSRC].startswith('node://'):
                groomNodeToHdfsTrees(t, model)
            else:
                misc.ERROR("Tree: {0} is not a valid form for 'src' attribute. Unknown scheme".format(t[FSRC]))
            if t[SCOPE] == HDFS:
                model[DATA][HDFS][TREES].append(t)
            else:
                if not context.checkScope(t[SCOPE] ):
                    misc.ERROR("Tree {0}: Scope attribute '{1}' does not match any host or host_group and is not 'hdfs'!".format(t[FSRC], t[SCOPE]))
                else:
                    if NODE_TO_HDFS_FLAG in t:
                        ensureHdfsScope(model, t[SCOPE])
                        model[DATA][HDFS][NODE_TO_HDFS_BY_NAME][t[SCOPE]][TREES].append(t)
                    else:
                        ensureScope(model, t[SCOPE])
                        context.model[DATA][FILES][SCOPE_BY_NAME][t[SCOPE]][TREES].append(t)


def groomFileTrees(tree, model):
    path = tree[FSRC][len('file://'):] 
    tree[_DISPLAY_SRC_] = path
    if not path.startswith("/"):
        path = lookupInLocalFiles(path, model)
    if not os.path.isdir(path):
        misc.ERROR("{0} is a not folder. Use 'files' block to single file".format(tree[FSRC]))
    if not path.endswith('/'):
        path = path + "/"
    tree[_SRC_] = path
    if tree[SCOPE] != HDFS:
        addTargetFolders(tree, tree[DEST_FOLDER])
    else:
        if not tree[_CACHE_TARGET_].endswith('/'):
            tree[_CACHE_TARGET_] = tree[_CACHE_TARGET_] + '/'


def addTargetFolders(tree, targetRoot):
    # Build a list of target folder, as we need to explicitly set rights on them (ansible.copy does not set rights for existing ones).
    targetFolders = []
    targetFolders.append(targetRoot)
    for dirpath, dirnames, _ in os.walk(tree[_SRC_], topdown=True, onerror=None, followlinks=False):
        dirpath = os.path.join(targetRoot, dirpath[len(tree[_SRC_]):])
        for d in dirnames:
            targetFolders.append(os.path.join(dirpath, d))
    tree[_TARGETFOLDERS_] = targetFolders


def groomTmplTrees(tree, model):
    path = tree[FSRC][len('tmpl://'):] 
    tree[_DISPLAY_SRC_] = path
    if not path.startswith('/'):
        path = lookupInLocalTemplates(path, model)
    if not os.path.isdir(path):
        misc.ERROR("tree: {0} is is not a folder. Use 'files' block to copy a single template".format(tree[FSRC]))
    if not path.endswith('/'):
        path = path + "/"
    tree[_SRC_] = path
    if tree[SCOPE] != HDFS:
        addTargetFolders(tree, tree[DEST_FOLDER])
        addTmplList(tree, tree[DEST_FOLDER])
    else:
        addTargetFolders(tree, tree[_CACHE_TARGET_])
        addTmplList(tree, tree[_CACHE_TARGET_])
        if not tree[_CACHE_TARGET_].endswith("/"):
            tree[_CACHE_TARGET_] = tree[_CACHE_TARGET_] + "/"


def addTmplList(tree, targetRoot):
    # Build a list template to process
    tmplList = []
    for dirPath, _, fileNames in os.walk(tree[_SRC_], topdown=True, onerror=None, followlinks=False):
        srcDirPath = dirPath
        dstDirPath = os.path.join(targetRoot, dirPath[len(tree[_SRC_]):])
        for fn in fileNames:
            x = {}
            x[FSRC] = os.path.join(srcDirPath, fn)
            x['dst'] = os.path.join(dstDirPath, fn)
            tmplList.append(x)
    tree['_tmplList'] = tmplList


def groomNodeToHdfsTrees(tree, model):
    groomNodeToHdfsFilesOrTrees(tree, model)
    tree[_TSRC_] = tree[_SRC_] #  _src for testing
    if tree[_TSRC_].endswith("/"):
        tree[_TSRC_] = tree[_TSRC_][:-1]
    if not tree[_SRC_].endswith("/"):
        tree[_SRC_] = tree[_SRC_] + "/"


# --------------------------------- Maven stuff    

def groomMavenRepositories(context):
    model = context.model
    misc.ensureObjectInMaps(model[DATA], [MAVEN_REPO_BY_NAME], {} )
    if MAVEN_REPOSITORIES in model[SRC]:
        for repo in model[SRC][MAVEN_REPOSITORIES]:
            model[DATA][MAVEN_REPO_BY_NAME][repo["name"]] = repo
            misc.setDefaultInMap(repo, VALIDATE_CERTS, True)
            misc.setDefaultInMap(repo, TIMEOUT, 10)
            

def groomMavenFiles(f, model):
    path = f[FSRC][len('mvn://'):]
    src = path.split("/")
    if len(src) < 4 or len(src) > 6:
        misc.ERROR("'{0}' is not a valid maven path. Must be in the form mvn://maven_repo/group_id/artifact_id/version[classifier[/extension]]".format(f[SRC]))
    if src[0] not in model[DATA][MAVEN_REPO_BY_NAME]:
        misc.ERROR("'{0}' is not a defined maven repository".format(src[0]))
    else:
        repository = model[DATA][MAVEN_REPO_BY_NAME][src[0]]
    f[_REPO_] = src[0]
    f[_GROUP_ID_] = src[1]
    f[_ARTIFACT_ID_] = src[2]
    f[_VERSION_] = src[3]
    if len(src) >= 5:
        if len(src[4]) > 0:
            f[_CLASSIFIER_] = src[4]
        if len(src) >= 6:
            f[_EXTENSION_] = src[5]
        else:
            f[_EXTENSION_] = "jar"
    else:
        f[_EXTENSION_] = "jar"
    # Fixup _repoUrl_ based on version
    if f[_VERSION_] == "latest":
        if LASTEST_URL in repository:
            f[_REPO_URL_] = repository[LASTEST_URL]
        elif URL in repository:
            f[_REPO_URL_] = repository[URL]
        else:
            misc.ERROR("Maven artifact '{0}': No 'latest_url' nor 'url' defined in repository '{1}'".format(src, repository[NAME]))
    elif f[_VERSION_].find("SNAPSHOT") != -1:
        if SNAPSHOTS_URL in repository:
            f[_REPO_URL_] = repository[SNAPSHOTS_URL]
        elif URL in repository:
            f[_REPO_URL_] = repository[URL]
        else:
            misc.ERROR("Maven artifact '{0}': No 'snapshots_url' nor 'url' defined in repository '{1}'".format(src, repository[NAME]))
    else:
        if RELEASES_URL in repository:
            f[_REPO_URL_] = repository[RELEASES_URL]
        elif URL in repository:
            f[_REPO_URL_] = repository[URL]
        else:
            misc.ERROR("Maven artifact '{0}': No 'releases_url' nor 'url' defined in repository '{1}'".format(src, repository[NAME]))
    misc.setDefaultInMap(f, DEST_NAME, "{0}-{1}{2}.{3}".format(f[_ARTIFACT_ID_], f[_VERSION_], ("-" + f[_CLASSIFIER_]) if _CLASSIFIER_ in f else "", f[_EXTENSION_]))
    f[_TARGET_] = os.path.normpath(os.path.join(f[DEST_FOLDER], f[DEST_NAME]))

    

# This is not used in file, by in systemd and supervisor plugins

def lookupSrc(model, src):
    if src.startswith("file://"):
        path = src[len('file://'):] 
        displaySrc = path
        if not path.startswith("/"):
            path = lookupInLocalFiles(path, model)
        else:
            if not os.path.exists(path):
                return (None, None, "'{0}' does not exists".format(path))
        if os.path.isdir(path):
            return (None, None, "'{0}' can't be a folder!".format(src))
        return (path, displaySrc, None)
    elif src.startswith("tmpl://"):
        path = src[len('tmpl://'):] 
        displaySrc = path
        if not path.startswith("/"):
            path = lookupInLocalTemplates(path, model)
        else:
            if not os.path.exists(path):
                misc.ERROR("'{0}' does not exists".format(path))
        if os.path.isdir(path):
            misc.ERROR("Unit_file '{0}' can't be a folder!".format(src))
        return(path, displaySrc, None)
    else:
        return (None, None, "{0} is not a valid form. Unknown scheme.".format(src))



    