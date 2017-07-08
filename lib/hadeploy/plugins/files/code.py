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
from hadeploy.core.const import SRC,DATA,DEFAULT_HDFS_RELAY_CACHE_FOLDER,INVENTORY,HOST_BY_NAME,SCOPE_FILES,SCOPE_HDFS,ACTION_DEPLOY,ACTION_REMOVE

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
        if HDFS_RELAY in model[SRC]:
            misc.setDefaultInMap(model[SRC][HDFS_RELAY], CACHE_FOLDER, DEFAULT_HDFS_RELAY_CACHE_FOLDER)
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
        
    

# ---------------------------------------------------- Static functions

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
            misc.setDefaultInMap(f, DEST_NAME,  os.path.basename(f[FSRC]))
            f[_TARGET_] = os.path.normpath(os.path.join(f[DEST_FOLDER], f[DEST_NAME]))
            if f[FSRC].startswith('file://'):
                groomFileFiles(f, model)
            elif f[FSRC].startswith('http://') or  f[FSRC].startswith('https://'):
                groomHttpFiles(f, model)
            elif f[FSRC].startswith('tmpl://'):
                groomTmplFiles(f, model)
            elif f[FSRC].startswith('node://'):
                groomNodeToHdfsFiles(f, model)
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
    path = f[FSRC][len('file://'):] 
    f[_DISPLAY_SRC_] = path
    if not path.startswith("/"):
        path = lookupInLocalFiles(path, model)
    if os.path.isdir(path):
        misc.ERROR("{0} is a folder. Use 'trees' block to copy a folder in a recursive way".format(f[FSRC]))
    f[_SRC_] = path

def groomHttpFiles(f, model):
    misc.setDefaultInMap(f, VALIDATE_CERTS, True)
    misc.setDefaultInMap(f, FORCE_BASIC_AUTH, False)

def groomTmplFiles(f, model):
    path = f[FSRC][len('tmpl://'):] 
    f[_DISPLAY_SRC_] = path
    if not path.startswith("/"):
        path = lookupInLocalTemplates(path, model)
    if os.path.isdir(path):
        misc.ERROR("Files: {0} is is a folder. Can't be a template source. Use 'trees' block to copy a folder in a recursive way".format(f[FSRC]))
    f[_SRC_] = path

def lookupInLocalFiles(path, model):
    if LOCAL_FILES_FOLDERS not in model[SRC]:
        misc.ERROR("Missing 'local_files_folders' definition while some files.src are not absolute")
    for ff in model[SRC][LOCAL_FILES_FOLDERS]:
        p = os.path.normpath(os.path.join(ff, path))
        if os.path.exists(p):
            return p
    misc.ERROR("Unable to find '{0}' in local_file_folders={1}".format(path, model[SRC][LOCAL_FILES_FOLDERS]))


def lookupInLocalTemplates(path, model):
    if LOCAL_TEMPLATES_FOLDERS not in model[SRC]:
        misc.ERROR("Missing 'local_templates_folders' definition while some templates are not absolute")
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
    

    