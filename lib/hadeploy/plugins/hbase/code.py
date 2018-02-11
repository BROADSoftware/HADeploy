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
import glob
from hadeploy.core.templator import Templator


from hadeploy.core.plugin import Plugin
from hadeploy.core.const import SRC,DATA,DEFAULT_TOOLS_FOLDER,SCOPE_HBASE,ACTION_DEPLOY,ACTION_REMOVE

logger = logging.getLogger("hadeploy.plugins.hbase")

HBASE="hbase"    
    
HBASE_RELAY="hbase_relay"
TOOLS_FOLDER="tools_folder"
PRINCIPAL="principal"
DEBUG="debug"
HBASE_NAMESPACES="hbase_namespaces"
NO_REMOVE="no_remove"
MANAGED="managed"
TABLES="tables"
KERBEROS="kerberos"
LOCAL_KEYTAB_PATH="local_keytab_path"
RELAY_KEYTAB_PATH="relay_keytab_path"
_RELAY_KEYTAB_FOLDER_="_relayKeytabFolder_"        

HBASE_TABLES="hbase_tables"
NAMESPACE_BY_NAME="namespaceByName"
PRESPLIT="presplit"
SPLITS="splits"
START_KEY="start_key"
END_KEY="end_key"
NUM_REGION="num_region"
NAME="name"
NAMESPACE="namespace"

    
    
HBASE_DATASETS="hbase_datasets"
DEL_ROWS="delRows"  
DEL_VALUES="delValues"
DONT_ADD_ROW="dontAddRow"
DONT_ADD_VALUE="dontAddValue"
UPD_VALUES="updValues"

HELPER="helper"
DIR="dir"
JDCHTABLE_JAR="jdchtable_jar"
HBLOAD_JAR="hbload_jar"

BECOME_USER="become_user"
LOGS_USER="logsUser"


class HBasePlugin(Plugin):
    
    def __init__(self, name, path, context):
        Plugin.__init__(self, name, path, context)


    def onNewSnippet(self, snippetPath):
        model = self.context.model
        if HBASE_RELAY in model[SRC]: 
            if LOCAL_KEYTAB_PATH in model[SRC][HBASE_RELAY]:
                model[SRC][HBASE_RELAY][LOCAL_KEYTAB_PATH] = misc.snippetRelocate(snippetPath, model[SRC][HBASE_RELAY][LOCAL_KEYTAB_PATH])
            

    def getGroomingPriority(self):
        return 4000

    def getSupportedScopes(self):
        return [SCOPE_HBASE]        

    def getSupportedActions(self):
        if self.context.toExclude(SCOPE_HBASE):
            return []
        else:
            return [ACTION_DEPLOY, ACTION_REMOVE]

    def getPriority(self, action):
        return 4000 if action == ACTION_DEPLOY else 3000 if action == ACTION_REMOVE else misc.ERROR("Plugin 'hbase' called with invalid action: '{0}'".format(action))

    def onGrooming(self):
        misc.applyWhenOnSingle(self.context.model[SRC], HBASE_RELAY)
        misc.applyWhenOnList(self.context.model[SRC], HBASE_NAMESPACES)
        misc.applyWhenOnList(self.context.model[SRC], HBASE_TABLES)
        misc.applyWhenOnList(self.context.model[SRC], HBASE_DATASETS)
        if self.context.toExclude(SCOPE_HBASE):
            return
        self.buildHelper()
        misc.ensureObjectInMaps(self.context.model[DATA], [HBASE], {})
        groomHbaseRelay(self.context.model)
        groomHBaseNamespaces(self.context.model)
        groomHBaseTables(self.context.model)
        groomHBaseDatasets(self.context.model)

    
    def buildAuxTemplates(self, action, priority):
        if not self.context.toExclude(SCOPE_HBASE):
            if HBASE_NAMESPACES in self.context.model[SRC] and len(self.context.model[SRC][HBASE_NAMESPACES]) > 0:
                templator = Templator([os.path.join(self.path, './helpers/jdchtable')], self.context.model)
                if action == ACTION_DEPLOY:
                    templator.generate("desc_htables.yml.jj2", os.path.join(self.context.workingFolder, "desc_htables.yml.j2"))
                elif action == ACTION_REMOVE:
                    templator.generate("desc_unhtables.yml.jj2", os.path.join(self.context.workingFolder, "desc_unhtables.yml.j2"))
                else:
                    pass
    

    def getTemplateAsFile(self, action, priority):
        if self.context.toExclude(SCOPE_HBASE):
            return []
        else:
            return [os.path.join(self.path, "install_hbase_relay.yml.jj2"), os.path.join(self.path, "{0}.yml.jj2".format(action))]

    def buildHelper(self):
        helper = {}
        helper[DIR] = os.path.normpath(os.path.join(self.path, "helpers"))
        jdchtablejars = glob.glob(os.path.join(helper[DIR], "jdchtable/jdchtable_uber*.jar"))
        if len(jdchtablejars) < 1:
            misc.ERROR("Unable to find helper for HBase.Please, refer to the documentation about Installation")
        helper[JDCHTABLE_JAR] = os.path.basename(jdchtablejars[0])
        
        hbloadjars = glob.glob(os.path.join(helper[DIR], "hbload/hbload_uber*.jar"))
        if len(hbloadjars) < 1:
            misc.ERROR("Unable to find helper for HBase datasets loader. Please, refer to the documentation about Installation")
        helper[HBLOAD_JAR] = os.path.basename(hbloadjars[0])
        misc.ensureObjectInMaps(self.context.model, [HELPER, HBASE], helper)
        
        
        
# ---------------------------------------------------- Static functions
  
def groomHbaseRelay(model):
    if HBASE_RELAY in model[SRC]:
        if (not HBASE_NAMESPACES in model[SRC] or len(model[SRC][HBASE_NAMESPACES]) == 0) and  (not HBASE_TABLES in model[SRC] or len(model[SRC][HBASE_TABLES]) == 0):
            # Optimization on execution time
            del(model[SRC][HBASE_RELAY])
        else:
            if not TOOLS_FOLDER in model[SRC][HBASE_RELAY]:
                model[SRC][HBASE_RELAY][TOOLS_FOLDER] = DEFAULT_TOOLS_FOLDER
            misc.setDefaultInMap(model[SRC][HBASE_RELAY], DEBUG, False)
            if PRINCIPAL in  model[SRC][HBASE_RELAY]:
                if LOCAL_KEYTAB_PATH not in model[SRC][HBASE_RELAY] and  RELAY_KEYTAB_PATH not in model[SRC][HBASE_RELAY]:
                    misc.ERROR("hbase_relay: Please provide a 'local_keytab_path' and/or a 'relay_keytab_path' if you want to use a Kerberos 'principal'")
                model[SRC][HBASE_RELAY][KERBEROS] = True
                if LOCAL_KEYTAB_PATH in model[SRC][HBASE_RELAY]:
                    if not os.path.exists(model[SRC][HBASE_RELAY][LOCAL_KEYTAB_PATH]):
                        misc.ERROR("hbase_relay: local_keytab_file '{0}' does not exists!".format(model[SRC][HBASE_RELAY][LOCAL_KEYTAB_PATH]))
                if RELAY_KEYTAB_PATH not in model[SRC][HBASE_RELAY]:
                    model[SRC][HBASE_RELAY][_RELAY_KEYTAB_FOLDER_] = os.path.join(model[SRC][HBASE_RELAY][TOOLS_FOLDER], "keytabs")
                    model[SRC][HBASE_RELAY][RELAY_KEYTAB_PATH] = os.path.join( model[SRC][HBASE_RELAY][_RELAY_KEYTAB_FOLDER_], os.path.basename(model[SRC][HBASE_RELAY][LOCAL_KEYTAB_PATH]))
                if BECOME_USER in model[SRC][HBASE_RELAY]:
                    misc.ERROR("hbase_relay: become_user and principal can't be defined both!")
                model[SRC][HBASE_RELAY][LOGS_USER] = "{{ansible_user}}"
            else:
                if LOCAL_KEYTAB_PATH in model[SRC][HBASE_RELAY] or RELAY_KEYTAB_PATH in model[SRC][HBASE_RELAY]:
                    misc.ERROR("hbase_relay: Please, provide a 'principal' if you need to use a keytab")
                model[SRC][HBASE_RELAY][KERBEROS] = False
                if BECOME_USER in model[SRC][HBASE_RELAY]:
                    model[SRC][HBASE_RELAY][LOGS_USER] = model[SRC][HBASE_RELAY][BECOME_USER]
                else:
                    model[SRC][HBASE_RELAY][LOGS_USER] = "{{ansible_user}}"
            
def groomHBaseNamespaces(model):
    if HBASE_NAMESPACES in model[SRC] and len(model[SRC][HBASE_NAMESPACES]) > 0 :
        if not HBASE_RELAY in model[SRC]:
            misc.ERROR('A hbase_relay must be defined if at least one hbase_namespace is defined')
        namespaceByName = {}    
        for ns in model[SRC][HBASE_NAMESPACES]:
            misc.setDefaultInMap(ns, NO_REMOVE, False)
            misc.setDefaultInMap(ns, MANAGED, True)
            if ns[NAME] == 'default':
                if not ns[NO_REMOVE]:
                    misc.ERROR("HBase namespace 'default' can't be removed. Please set no_remove: True")
                if ns[MANAGED]:
                    misc.ERROR("HBase namespace 'default' can't be managed. Please set managed: False")
            namespaceByName[ns[NAME]] = ns
            ns[TABLES] = []
        model[DATA][HBASE][NAMESPACE_BY_NAME] = namespaceByName
        
        
def groomHBaseTables(model):
    if HBASE_TABLES in model[SRC] and len(model[SRC][HBASE_TABLES]) > 0 :
        if not HBASE_RELAY in model[SRC]:
            misc.ERROR('A hbase_relay must be defined if at least one hbase_tables is defined')
        for table in model[SRC][HBASE_TABLES]:        
            if PRESPLIT in table:
                ps = table[PRESPLIT]
                if SPLITS in ps:
                    if START_KEY in ps or END_KEY in ps or NUM_REGION in ps:
                        misc.ERROR("HBase table '{0}': Invalid presplit definition (1)".format(table[NAME]))
                elif START_KEY in ps:
                    if not END_KEY in ps or not NUM_REGION in ps:
                        misc.ERROR("HBase table '{0}': Invalid presplit definition (3)".format(table[NAME]))
                    if SPLITS in ps:
                        misc.ERROR("HBase table '{0}': Invalid presplit definition (4)".format(table[NAME]))
                else:
                    misc.ERROR("HBase table '{0}': Invalid presplit definition (5)".format(table[NAME]))
            if not NO_REMOVE in table:
                table[NO_REMOVE] = False
            if not NAMESPACE_BY_NAME in model[DATA][HBASE]:
                model[DATA][HBASE][NAMESPACE_BY_NAME] = {}
                model[SRC][HBASE_NAMESPACES] = []
            if not table[NAMESPACE] in model[DATA][HBASE][NAMESPACE_BY_NAME]:
                if table[NAMESPACE] == "default":
                    ns = { NAME: table[NAMESPACE], MANAGED: False, NO_REMOVE: True, TABLES: [] }
                    model[DATA][HBASE][NAMESPACE_BY_NAME][ns[NAME]] = ns
                    model[SRC][HBASE_NAMESPACES].append(ns)
                else:
                    misc.ERROR("HBase table '{0}': Namespace '{1}' is not defined!".format(table[NAME], table[NAMESPACE]))
            #print model[DATA][HBASE][NAMESPACE_BY_NAME]
                
            myNamespace = model[DATA][HBASE][NAMESPACE_BY_NAME][table[NAMESPACE]]
            myNamespace[TABLES].append(table)
            if table[NO_REMOVE] and not myNamespace[NO_REMOVE]:
                misc.ERROR("HBase table '{0}' is not removable while its namespace '{1}' is!".format(table[NAME], table[NAMESPACE]))
                

def groomHBaseDatasets(model):
    if HBASE_DATASETS in model[SRC] and len(model[SRC][HBASE_DATASETS]) > 0 :
        if not HBASE_RELAY in model[SRC]:
            misc.ERROR('A hbase_relay must be defined if at least one hbase_datasets is defined')
        for ds in model[SRC][HBASE_DATASETS]:
            if ds[SRC].startswith('file://'):
                groomFileFiles(ds, model)
            elif ds[SRC].startswith('http://') or  ds[SRC].startswith('https://'):
                groomHttpFiles(ds, model)
            elif ds[SRC].startswith('tmpl://'):
                groomTmplFiles(ds, model)
            else:
                misc.ERROR('Invalid src scheme for hbase_dataset (table:{0}:{1})'.format(ds[NAMESPACE], ds['table']))
            misc.setDefaultInMap(ds, DEL_ROWS, False)
            misc.setDefaultInMap(ds, DEL_VALUES, False)
            misc.setDefaultInMap(ds, DONT_ADD_ROW, False)
            misc.setDefaultInMap(ds, DONT_ADD_VALUE, False)
            misc.setDefaultInMap(ds, UPD_VALUES, False)
            misc.setDefaultInMap(ds, NO_REMOVE, False)

# Copied from 'files' plugin

FSRC="src"
_DISPLAY_SRC_="_displaySrc_"
_SRC_="_src_"
VALIDATE_CERTS="validate_certs"
FORCE_BASIC_AUTH="force_basic_auth"
LOCAL_FILES_FOLDERS="local_files_folders"
LOCAL_TEMPLATES_FOLDERS="local_templates_folders"

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


