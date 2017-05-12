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
import misc
import os
import glob
from templator import Templator


from plugin import Plugin
from const import SRC,DATA,DEFAULT_TOOLS_FOLDER

logger = logging.getLogger("hadeploy.plugins.hive")

HIVE="hive"
HIVE_DATABASES="hive_databases"

HIVE_TABLES="hive_tables"

HELPER="helper"
DIR="dir"
JDCHIVE_JAR="jdchive_jar"
PRINCIPAL="principal"
KEYTAB_PATH="keytab_path"
KERBEROS="kerberos"
DEBUG="debug"


HIVE_RELAY="hive_relay"
TOOLS_FOLDER="tools_folder"
REPORT_FILE="report_file"

class HBasePlugin(Plugin):
    
    def __init__(self, name, path, context):
        Plugin.__init__(self, name, path, context)

    def onNewSnippet(self, snippetPath):
        model = self.context.model
        if HIVE_RELAY in model[SRC] and REPORT_FILE in model[SRC][HIVE_RELAY]:
            if not os.path.isabs( model[SRC][HIVE_RELAY][REPORT_FILE]):
                model[SRC][HIVE_RELAY][REPORT_FILE] = os.path.normpath(os.path.join(snippetPath, model[SRC][HIVE_RELAY][REPORT_FILE]))                
            
            
    def onGrooming(self):
        self.buildHelper()
        misc.ensureObjectInMaps(self.context.model[DATA], [HIVE], {})
        groomHiveRelay(self.context.model)
        groomHiveDatabases(self.context.model)
        
    
    def onTemplateGeneration(self):
        pass
        if (HIVE_DATABASES in self.context.model[SRC] and len(self.context.model[SRC][HIVE_DATABASES]) > 0) or (HIVE_TABLES in self.context.model[SRC] and len(self.context.model[SRC][HIVE_TABLES]) > 0):
            templator = Templator([os.path.join(self.path, './helpers/jdchive')], self.context.model)
            templator.generate("desc_hive.yml.jj2", os.path.join(self.context.workingFolder, "desc_hive.yml.j2"))
            templator.generate("desc_unhive.yml.jj2", os.path.join(self.context.workingFolder, "desc_unhive.yml.j2"))
    
    def getInstallTemplates(self):
        return [os.path.join(self.path, "install_hive_relay.yml.jj2"), os.path.join(self.path, "install.yml.jj2")]

    def getRemoveTemplates(self):
        return [os.path.join(self.path, "install_hive_relay.yml.jj2"), os.path.join(self.path, "remove.yml.jj2")]

    def buildHelper(self):
        helper = {}
        helper[DIR] = os.path.normpath(os.path.join(self.path, "helpers"))
        jdchivejars = glob.glob(os.path.join(helper[DIR], "jdchive/jdchive_uber*.jar"))
        if len(jdchivejars) < 1:
            misc.ERROR("Unable to find helper for Hive.Please, refer to the documentation about Installation")
        helper[JDCHIVE_JAR] = os.path.basename(jdchivejars[0])
        misc.ensureObjectInMaps(self.context.model, [HELPER, HIVE], helper)
        
  
        
# ---------------------------------------------------- Static functions

HIVE_DATABASES="hive_databases"
NAME="name"
NO_REMOVE="no_remove"

def groomHiveRelay(model):
    if HIVE_RELAY in model[SRC]:
        if (not HIVE_DATABASES in model[SRC] or len(model[SRC][HIVE_DATABASES]) == 0) and (not HIVE_TABLES in model[SRC] or len(model[SRC][HIVE_TABLES]) == 0):
            # Optimization for execution
            del (model[SRC][HIVE_RELAY])
        else:
            if not TOOLS_FOLDER in model[SRC][HIVE_RELAY]:
                model[SRC][HIVE_RELAY][TOOLS_FOLDER] = DEFAULT_TOOLS_FOLDER
            if PRINCIPAL in  model[SRC][HIVE_RELAY]:
                if KEYTAB_PATH not in model[SRC][HIVE_RELAY]:
                    misc.ERROR("hive_relay: Please provide a 'keytab_path' if you want to use a Kerberos 'principal'")
                model[SRC][HIVE_RELAY][KERBEROS] = True
            else:
                if KEYTAB_PATH in model[SRC][HIVE_RELAY]:
                    misc.ERROR("hive_relay: Please, provide a 'principal' if you need to use a keytab")
                model[SRC][HIVE_RELAY][KERBEROS] = False
            misc.setDefaultInMap( model[SRC][HIVE_RELAY], DEBUG, False)
                
def groomHiveDatabases(model):
    if HIVE_DATABASES in model[SRC] and len(model[SRC][HIVE_DATABASES]) > 0 :
        if not HIVE_RELAY in model[SRC]:
            misc.ERROR('A hive_relay must be defined if at least one hbase_namespace is defined')
        #databaseByName = {}    
        for db in model[SRC][HIVE_DATABASES]:
            misc.setDefaultInMap(db, NO_REMOVE, False)
            if db[NAME] == 'default':
                if not db[NO_REMOVE]:
                    misc.ERROR("HIVE database 'default' can't be removed. Please set no_remove: True")
            #databaseByName[db[NAME]] = db
        #model[DATA][HIVE][DATABASE_BY_NAME] = databaseByName
    
                    
        