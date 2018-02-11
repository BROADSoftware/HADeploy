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
import yaml
import copy


from hadeploy.core.plugin import Plugin
from hadeploy.core.const import SRC,DATA,DEFAULT_TOOLS_FOLDER,SCOPE_HIVE,ACTION_DEPLOY,ACTION_REMOVE

logger = logging.getLogger("hadeploy.plugins.hive")

RANGER_POLICY="ranger_policy"

HIVE="hive"
HIVE_DATABASES="hive_databases"

HIVE_TABLES="hive_tables"

HELPER="helper"
DIR="dir"
JDCHIVE_JAR="jdchive_jar"
PRINCIPAL="principal"
KERBEROS="kerberos"
DEBUG="debug"
LOCAL_KEYTAB_PATH="local_keytab_path"
RELAY_KEYTAB_PATH="relay_keytab_path"
_RELAY_KEYTAB_FOLDER_="_relayKeytabFolder_"        


HIVE_DATABASES="hive_databases"
NAME="name"
NO_REMOVE="no_remove"

    
INPUT_FORMAT="input_format"
OUTPUT_FORMAT="output_format"
STORED_AS="stored_as"
DELIMITED="delimited"
SERDE="serde"

LOCATION="location"
DATABASE="database"
OWNER="owner"
OWNER_TYPE="owner_type"
               

HIVE_RELAY="hive_relay"
TOOLS_FOLDER="tools_folder"
REPORT_FILE="report_file"

BECOME_USER="become_user"
LOGS_USER="logsUser"


class HBasePlugin(Plugin):
    
    def __init__(self, name, path, context):
        Plugin.__init__(self, name, path, context)

    def onNewSnippet(self, snippetPath):
        model = self.context.model
        if HIVE_RELAY in model[SRC]: 
            if REPORT_FILE in model[SRC][HIVE_RELAY]:
                model[SRC][HIVE_RELAY][REPORT_FILE] = misc.snippetRelocate(snippetPath, model[SRC][HIVE_RELAY][REPORT_FILE])
            if LOCAL_KEYTAB_PATH in model[SRC][HIVE_RELAY]:
                model[SRC][HIVE_RELAY][LOCAL_KEYTAB_PATH] = misc.snippetRelocate(snippetPath, model[SRC][HIVE_RELAY][LOCAL_KEYTAB_PATH])
            

    def getGroomingPriority(self):
        return 4500

    def getSupportedScopes(self):
        return [SCOPE_HIVE]        

    def getSupportedActions(self):
        if self.context.toExclude(SCOPE_HIVE):
            return []
        else:
            return [ACTION_DEPLOY, ACTION_REMOVE]

    def getPriority(self, action):
        return 4500 if action == ACTION_DEPLOY else 2500 if action == ACTION_REMOVE else misc.ERROR("Plugin 'hive' called with invalid action: '{0}'".format(action))

            
    def onGrooming(self):
        misc.applyWhenOnSingle(self.context.model[SRC], HIVE_RELAY)
        misc.applyWhenOnList(self.context.model[SRC], HIVE_DATABASES)
        misc.applyWhenOnList(self.context.model[SRC], HIVE_TABLES)
        if self.context.toExclude(SCOPE_HIVE):
            return
        self.buildHelper()
        misc.ensureObjectInMaps(self.context.model[DATA], [HIVE], {})
        groomHiveRelay(self.context.model)
        groomHiveDatabases(self.context.model)
        groomHiveTables(self.context.model)
        
    
    def buildAuxTemplates(self, action, priority):
        if self.context.toExclude(SCOPE_HIVE):
            return
        model = self.context.model
        if HIVE_RELAY in model[SRC]:
            if action == ACTION_DEPLOY:
                # -------------------------------------------- For Deploy
                tgt = { "databases": [], "tables": []}
                if HIVE_DATABASES in model[SRC]:
                    for db in model[SRC][HIVE_DATABASES]:
                        db2 = copy.deepcopy(db)
                        del(db2[NO_REMOVE])
                        del(db2[misc.WHEN])
                        if RANGER_POLICY in db2:
                            del(db2[RANGER_POLICY])
                        tgt["databases"].append(db2)
                if HIVE_TABLES in model[SRC]:
                    for tbl in model[SRC][HIVE_TABLES]:
                        tbl2 = copy.deepcopy(tbl)
                        del(tbl2[NO_REMOVE])
                        del(tbl2[misc.WHEN])
                        if RANGER_POLICY in tbl2:
                            del(tbl2[RANGER_POLICY])
                        tgt["tables"].append(tbl2)
                f = open(os.path.join(self.context.workingFolder, "desc_hive.yml.j2"), "w")
                yaml.dump(tgt, f)
                f.close()
            elif action == ACTION_REMOVE:
                # -------------------------------------------- For REMOVE
                tgt = { "databases": [], "tables": []}
                if HIVE_DATABASES in model[SRC]:
                    for db in model[SRC][HIVE_DATABASES]:
                        if not db[NO_REMOVE]:
                            tgt["databases"].append({ NAME: db[NAME], "state": "absent" })
                if HIVE_TABLES in model[SRC]:
                    for tbl in model[SRC][HIVE_TABLES]:
                        if not tbl[NO_REMOVE]:
                            tgt["tables"].append({ NAME: tbl[NAME], DATABASE: tbl[DATABASE], "state": "absent" })
                f = open(os.path.join(self.context.workingFolder, "desc_unhive.yml.j2"), "w")
                yaml.dump(tgt, f)
                f.close()
            else:
                pass
                
    def getTemplateAsFile(self, action, priority):
        if self.context.toExclude(SCOPE_HIVE):
            return []
        else:
            return [os.path.join(self.path, "install_hive_relay.yml.jj2"), os.path.join(self.path, "{0}.yml.jj2".format(action))]
    
    def buildHelper(self):
        helper = {}
        helper[DIR] = os.path.normpath(os.path.join(self.path, "helpers"))
        jdchivejars = glob.glob(os.path.join(helper[DIR], "jdchive/jdchive_uber*.jar"))
        if len(jdchivejars) < 1:
            misc.ERROR("Unable to find helper for Hive.Please, refer to the documentation about Installation")
        helper[JDCHIVE_JAR] = os.path.basename(jdchivejars[0])
        misc.ensureObjectInMaps(self.context.model, [HELPER, HIVE], helper)

# ---------------------------------------------------- Static functions

def groomHiveRelay(model):
    if HIVE_RELAY in model[SRC]:
        if (not HIVE_DATABASES in model[SRC] or len(model[SRC][HIVE_DATABASES]) == 0) and (not HIVE_TABLES in model[SRC] or len(model[SRC][HIVE_TABLES]) == 0):
            # Optimization for execution
            del (model[SRC][HIVE_RELAY])
        else:
            if not TOOLS_FOLDER in model[SRC][HIVE_RELAY]:
                model[SRC][HIVE_RELAY][TOOLS_FOLDER] = DEFAULT_TOOLS_FOLDER
            misc.setDefaultInMap( model[SRC][HIVE_RELAY], DEBUG, False)
            if PRINCIPAL in  model[SRC][HIVE_RELAY]:
                if LOCAL_KEYTAB_PATH not in model[SRC][HIVE_RELAY] and RELAY_KEYTAB_PATH not in model[SRC][HIVE_RELAY]:
                    misc.ERROR("hive_relay: Please provide a 'local_keytab_path' and/or a 'relay_keytab_path' if you want to use a Kerberos 'principal'")
                model[SRC][HIVE_RELAY][KERBEROS] = True
                if LOCAL_KEYTAB_PATH in model[SRC][HIVE_RELAY]:
                    if not os.path.exists(model[SRC][HIVE_RELAY][LOCAL_KEYTAB_PATH]):
                        misc.ERROR("hive_relay: local_keytab_file '{0}' does not exists!".format(model[SRC][HIVE_RELAY][LOCAL_KEYTAB_PATH]))
                if RELAY_KEYTAB_PATH not in model[SRC][HIVE_RELAY]:
                    model[SRC][HIVE_RELAY][_RELAY_KEYTAB_FOLDER_] = os.path.join(model[SRC][HIVE_RELAY][TOOLS_FOLDER], "keytabs")
                    model[SRC][HIVE_RELAY][RELAY_KEYTAB_PATH] = os.path.join( model[SRC][HIVE_RELAY][_RELAY_KEYTAB_FOLDER_], os.path.basename(model[SRC][HIVE_RELAY][LOCAL_KEYTAB_PATH]))
                if BECOME_USER in model[SRC][HIVE_RELAY]:
                    misc.ERROR("hive_relay: become_user and principal can't be defined both!")
                model[SRC][HIVE_RELAY][LOGS_USER] = "{{ansible_user}}"
            else:
                if LOCAL_KEYTAB_PATH in model[SRC][HIVE_RELAY] or RELAY_KEYTAB_PATH in model[SRC][HIVE_RELAY]:
                    misc.ERROR("hive_relay: Please, provide a 'principal' if you need to use a keytab")
                model[SRC][HIVE_RELAY][KERBEROS] = False
                if BECOME_USER in model[SRC][HIVE_RELAY]:
                    model[SRC][HIVE_RELAY][LOGS_USER] = model[SRC][HIVE_RELAY][BECOME_USER]
                else:
                    model[SRC][HIVE_RELAY][LOGS_USER] = "{{ansible_user}}"
                
def groomHiveDatabases(model):
    if HIVE_DATABASES in model[SRC] and len(model[SRC][HIVE_DATABASES]) > 0 :
        if not HIVE_RELAY in model[SRC]:
            misc.ERROR('A hive_relay must be defined if at least one hive database is defined')
        for db in model[SRC][HIVE_DATABASES]:
            misc.setDefaultInMap(db, NO_REMOVE, False)
            if db[NAME] == 'default':
                misc.ERROR("HIVE database 'default' can't be altered")
            if (LOCATION in db) and (not db[LOCATION].startswith("/")):
                misc.ERROR("Database '{0}': Location must be absolute!".format(db[NAME]))
            if (OWNER in db) != (OWNER_TYPE in db):
                misc.ERROR("Database '{0}': If an owner is defined, then owner_type (USER|GROUP|ROLE) must be also!".format(db[NAME]))
                    
def groomHiveTables(model):
    if HIVE_TABLES in model[SRC] and len(model[SRC][HIVE_TABLES]) > 0 :
        if not HIVE_RELAY in model[SRC]:
            misc.ERROR('A hive_relay must be defined if at least one hive table is defined')
        for tbl in model[SRC][HIVE_TABLES]:
            misc.setDefaultInMap(tbl, NO_REMOVE, False)
            # We detect some miss configuration at this level (Instead of letting jdchive failing), as user report will be far better
            if (INPUT_FORMAT in tbl) != (OUTPUT_FORMAT in tbl):
                misc.ERROR("HIVE table '{0}:{1}': Both 'input_format' and 'output_format' must be defined together!".format(tbl[DATABASE], tbl[NAME]))
            if (STORED_AS in tbl) and (INPUT_FORMAT in tbl):
                misc.ERROR("HIVE table '{0}:{1}': Both 'stored_as' and 'input/output_format' can't be defined together!".format(tbl[DATABASE], tbl[NAME]))
            if (DELIMITED in tbl) and (SERDE in tbl):
                misc.ERROR("HIVE table '{0}:{1}': Both 'delimited' and 'serde' can't be defined together!".format(tbl[DATABASE], tbl[NAME]))
            if (LOCATION in tbl) and (not tbl[LOCATION].startswith("/")):
                misc.ERROR("HIVE table '{0}:{1}': Location must be absolute!".format(tbl[DATABASE], tbl[NAME]))
                
            