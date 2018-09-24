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
from hadeploy.core.const import SRC,DATA,SCOPE_RANGER,ACTION_DEPLOY,ACTION_REMOVE
import hadeploy.core.misc as misc
import os
from sets import Set
import yaml
import hadeploy.core.schema as schema
#from lib.hadeploy.plugins.ranger.code import HDFS_RANGER_POLICIES

logger = logging.getLogger("hadeploy.plugins.ranger")

DEFAULT_POLICY_NAME="_{0}_"
DEFAULT_HBASE_TABLE_POLICY_NAME="_{0}:{1}_"
DEFAULT_HIVE_TABLE_POLICY_NAME="_{0}.{1}_"


RANGER_RELAY="ranger_relay"
VALIDATE_CERTS="validate_certs"
CA_BUNDLE_LOCAL_FILE="ca_bundle_local_file"
CA_BUNDLE_RELAY_FILE="ca_bundle_relay_file"
POLICY_NAME_DECORATOR="policy_name_decorator"
CA_BUNDLE_RELAY_FOLDER="ca_bundle_relay_folder"

NAME="name"
RECURSIVE="recursive"
AUDIT="audit"
ENABLED="enabled"
NO_REMOVE="no_remove"
PERMISSIONS="permissions"
USERS="users"
GROUPS="groups"
DELEGATE_ADMIN="delegate_admin"
RANGER_POLICY="ranger_policy"
SCOPE="scope"
NO_LOG="no_log"

# -------------------- HDFS

HDFS_RANGER_POLICIES="hdfs_ranger_policies"
FOLDERS="folders"
PATH="path"
PATHS="paths"
HDFS="hdfs"
FILES="files"
TREES="trees"
DEST_FOLDER="dest_folder"
DEST_NAME="dest_name"
HDFS_RANGER_POLICIES_TO_REMOVE="hdfsRangerPoliciesToRemove"

# -------------------- HBASE
HBASE_NAMESPACES="hbase_namespaces"
HBASE_TABLES="hbase_tables"
TABLES="tables"
HBASE_RANGER_POLICIES="hbase_ranger_policies"
NAMESPACE="namespace"
COLUMNS="columns"
COLUMN_FAMILIES="column_families"
HBASE_RANGER_POLICIES_TO_REMOVE="hbaseRangerPoliciesToRemove"


# ------------------- Kafka

KAFKA_TOPICS="kafka_topics"
TOPICS="topics"
KAFKA_RANGER_POLICIES="kafka_ranger_policies"
IP_ADDRESSES="ip_addresses"
KAFKA_RANGER_POLICIES_TO_REMOVE="kafkaRangerPoliciesToRemove"

# ------------------------- hive

HIVE_DATABASES="hive_databases"
HIVE_TABLES="hive_tables"
DATABASES="databases"
DATABASE="database"
HIVE_RANGER_POLICIES="hive_ranger_policies"
HIVE_RANGER_POLICIES_TO_REMOVE="hiveRangerPoliciesToRemove"
UDFS="udfs"

# -------------------------------------- Yarn

YARN_RANGER_POLICIES="yarn_ranger_policies"
YARN_RANGER_POLICIES_TO_REMOVE="yarnRangerPoliciesToRemove"

# -------------------------------------- Storm

STORM_TOPOLOGIES="storm_topologies"        
TOPOLOGIES="topologies"
STORM_RANGER_POLICIES="storm_ranger_policies"
STORM_RANGER_POLICIES_TO_REMOVE="stormRangerPoliciesToRemove"

class RangerPlugin(Plugin):
    
    def __init__(self, name, path, context):
        Plugin.__init__(self, name, path, context)
        self.myHostGroups = []
    
    def onNewSnippet(self, snippetPath):
        if RANGER_RELAY in self.context.model[SRC]:
            if CA_BUNDLE_LOCAL_FILE in self.context.model[SRC][RANGER_RELAY]:
                self.context.model[SRC][RANGER_RELAY][CA_BUNDLE_LOCAL_FILE] = misc.snippetRelocate(snippetPath, self.context.model[SRC][RANGER_RELAY][CA_BUNDLE_LOCAL_FILE])
            

    def getGroomingPriority(self):
        return 8000

    def getSupportedScopes(self):
        return [SCOPE_RANGER]        

    def getSupportedActions(self):
        if self.context.toExclude(SCOPE_RANGER):
            return []
        else:
            return [ACTION_DEPLOY, ACTION_REMOVE]

    def getPriority(self, action):
        return 3200 if action == ACTION_DEPLOY else 3700 if action == ACTION_REMOVE else misc.ERROR("Plugin 'ranger' called with invalid action: '{0}'".format(action))

    def onGrooming(self):
        misc.applyWhenOnSingle(self.context.model[SRC], RANGER_RELAY)
        if 'hdfs' in self.context.pluginByName:
            misc.applyWhenOnList(self.context.model[SRC], HDFS_RANGER_POLICIES)
        if 'hbase' in self.context.pluginByName:
            misc.applyWhenOnList(self.context.model[SRC], HBASE_RANGER_POLICIES)
        if 'kafka' in self.context.pluginByName:
            misc.applyWhenOnList(self.context.model[SRC], KAFKA_RANGER_POLICIES)
        if 'hive' in self.context.pluginByName:
            misc.applyWhenOnList(self.context.model[SRC], HIVE_RANGER_POLICIES)
        if 'storm' in self.context.pluginByName:
            misc.applyWhenOnList(self.context.model[SRC], STORM_RANGER_POLICIES)
        misc.applyWhenOnList(self.context.model[SRC], YARN_RANGER_POLICIES)
        if self.context.toExclude(SCOPE_RANGER):
            return
        groomRangerRelay(self.context.model)
        if 'hdfs' in self.context.pluginByName:
            groomRangerHdfsPolicies(self.context.model)
        if 'hbase' in self.context.pluginByName:
            groomRangerHBasePolicies(self.context.model)
        if 'kafka' in self.context.pluginByName:
            groomRangerKafkaPolicies(self.context.model)
        if 'hive' in self.context.pluginByName:
            groomRangerHivePolicies(self.context.model)
        if 'storm' in self.context.pluginByName:
            groomRangerStormPolicies(self.context.model)
        groomRangerYarnPolicies(self.context.model)

    def getSchema(self):
        schemaFile = os.path.join(self.path, "schema_core.yml")
        theSchema=yaml.load(open(schemaFile))
        if 'hdfs' in self.context.pluginByName:
            schemaFile = os.path.join(self.path, "schema_hdfs.yml")
            schema.schemaMerge(theSchema, yaml.load(open(schemaFile)))
        if 'hbase' in self.context.pluginByName:
            schemaFile = os.path.join(self.path, "schema_hbase.yml")
            schema.schemaMerge(theSchema, yaml.load(open(schemaFile)))
        if 'kafka' in self.context.pluginByName:
            schemaFile = os.path.join(self.path, "schema_kafka.yml")
            schema.schemaMerge(theSchema, yaml.load(open(schemaFile)))
        if 'hive' in self.context.pluginByName:
            schemaFile = os.path.join(self.path, "schema_hive.yml")
            schema.schemaMerge(theSchema, yaml.load(open(schemaFile)))
        if 'storm' in self.context.pluginByName:
            schemaFile = os.path.join(self.path, "schema_storm.yml")
            schema.schemaMerge(theSchema, yaml.load(open(schemaFile)))
        return theSchema

    def getTemplateAsFile(self, action, priority):
        if self.context.toExclude(SCOPE_RANGER):
            return []
        else:
            return [os.path.join(self.path, "{0}.yml.jj2".format(action))]

# ---------------------------------------------------------------------------- Static function    

def groomRangerRelay(model):
    if RANGER_RELAY in model[SRC]:
        relay = model[SRC][RANGER_RELAY]
        misc.setDefaultInMap(relay, VALIDATE_CERTS, True)
        misc.setDefaultInMap(relay, NO_LOG, True)
        misc.setDefaultInMap(relay, POLICY_NAME_DECORATOR, 'HAD[{0}]')
        if CA_BUNDLE_LOCAL_FILE in relay:
            if not os.path.exists(relay[CA_BUNDLE_LOCAL_FILE]):
                misc.ERROR("ranger_relay.ca_bundle_local_file: {0} does not exists".format(relay[CA_BUNDLE_LOCAL_FILE]))
            if CA_BUNDLE_RELAY_FILE not in relay:
                misc.ERROR("ranger_relay: If a ca_bundle_local_file is defined, then a ca_bundle_relay_file must also be defined")
            if not os.path.isabs(relay[CA_BUNDLE_RELAY_FILE]):
                misc.ERROR("ranger_relay.ca_bundle_remote_file: {0}  must be absolute!".format(relay[CA_BUNDLE_RELAY_FILE]))
            relay[CA_BUNDLE_RELAY_FOLDER] = os.path.dirname(relay[CA_BUNDLE_RELAY_FILE] )
        
# -------------------------------------------------------------- HDFS

def groomRangerHdfsPolicies(model):
    grabHdfsRangerPoliciesFromFolders(model)
    grabHdfsRangerPoliciesFromTrees(model)
    grabHdfsRangerPoliciesFromFiles(model)
    if HDFS_RANGER_POLICIES in model[SRC] and len(model[SRC][HDFS_RANGER_POLICIES]) > 0:
        if RANGER_RELAY not in model[SRC]:
            misc.ERROR("There is at least one 'hdfs_ranger_policies', but no 'ranger_relay' was defined!")
        names = Set()
        toRemoveCount = 0
        for policy in model[SRC][HDFS_RANGER_POLICIES]:
            policy[NAME] = model[SRC][RANGER_RELAY][POLICY_NAME_DECORATOR].format(policy[NAME])
            if policy[NAME] in names:
                misc.ERROR("hdfs_ranger_policy.name: '{0}' is defined twice".format(policy[NAME])) 
            names.add(policy[NAME])
            misc.setDefaultInMap(policy, RECURSIVE, True)
            misc.setDefaultInMap(policy, AUDIT, True)
            misc.setDefaultInMap(policy, ENABLED, True)
            misc.setDefaultInMap(policy, NO_REMOVE, False)
            misc.setDefaultInMap(policy, PERMISSIONS, [])
            for perms in policy[PERMISSIONS]:
                misc.setDefaultInMap(perms, USERS, [])
                misc.setDefaultInMap(perms, GROUPS, [])
                misc.setDefaultInMap(perms, DELEGATE_ADMIN, False)
                if len(perms[USERS]) == 0 and len(perms[GROUPS]) == 0:
                    misc.ERROR("hdfs_ranger_policy.name: '{0}'. A permission has neither group or user defined.".format(policy[NAME]))
            if not policy[NO_REMOVE]:
                toRemoveCount = toRemoveCount + 1
        model[DATA][HDFS_RANGER_POLICIES_TO_REMOVE] = toRemoveCount
            
def grabHdfsRangerPoliciesFromFolders(model):
    if FOLDERS in model[SRC]:
        for folder in model[SRC][FOLDERS]:
            if RANGER_POLICY in folder:
                if folder[SCOPE] != HDFS:
                    misc.ERROR("Can't setup Apache Ranger policy on folder '{0}' as scope is not hdfs".format(folder[PATH]))
                policy = folder[RANGER_POLICY]
                policy[PATHS] = [ folder[PATH] ]
                policy[NO_REMOVE] = folder[NO_REMOVE]
                misc.setDefaultInMap(policy, NAME, DEFAULT_POLICY_NAME.format(folder[PATH]))
                misc.ensureObjectInMaps( model[SRC], [HDFS_RANGER_POLICIES], [])
                model[SRC][HDFS_RANGER_POLICIES].append(policy)

def grabHdfsRangerPoliciesFromTrees(model):
    if TREES in model[SRC]:
        for tree in model[SRC][TREES]:
            if RANGER_POLICY in tree:
                if tree[SCOPE] != HDFS:
                    misc.ERROR("Can't setup Apache Ranger policy on tree '{0}' as scope is not hdfs".format(tree[DEST_FOLDER]))
                policy = tree[RANGER_POLICY]
                policy[PATHS] = [ tree[DEST_FOLDER] ]
                policy[NO_REMOVE] = tree[NO_REMOVE]
                misc.setDefaultInMap(policy, NAME, DEFAULT_POLICY_NAME.format(tree[DEST_FOLDER]))
                misc.ensureObjectInMaps( model[SRC], [HDFS_RANGER_POLICIES], [])
                model[SRC][HDFS_RANGER_POLICIES].append(policy)
                

def grabHdfsRangerPoliciesFromFiles(model):
    if FILES in model[SRC]:
        for xfile in model[SRC][FILES]:
            if RANGER_POLICY in xfile:
                if xfile[SCOPE] != HDFS:
                    misc.ERROR("Can't setup Apache Ranger policy on file '{0}' as scope is not hdfs".format(os.path.join(xfile[DEST_FOLDER], xfile[DEST_NAME])))
                policy = xfile[RANGER_POLICY]
                misc.setDefaultInMap(policy, RECURSIVE, False)
                policy[PATHS] = [ os.path.join(xfile[DEST_FOLDER], xfile[DEST_NAME]) ]    # groomFiles should have been called before
                misc.setDefaultInMap(policy, NAME, DEFAULT_POLICY_NAME.format( policy[PATHS][0]))
                policy[NO_REMOVE] = xfile[NO_REMOVE]
                misc.ensureObjectInMaps( model[SRC], [HDFS_RANGER_POLICIES], [])
                model[SRC][HDFS_RANGER_POLICIES].append(policy)
            
            
# -------------------------------------------------------------- Hbase

def grabHBaseRangerPoliciesFromNamespaces(model):
    if HBASE_NAMESPACES in model[SRC]:
        for namespace in model[SRC][HBASE_NAMESPACES]:
            if RANGER_POLICY in namespace:
                policy = namespace[RANGER_POLICY]
                policy[TABLES] = [ namespace[NAME] + ":*" ]
                misc.setDefaultInMap(policy, NAME, DEFAULT_POLICY_NAME.format(namespace[NAME]))
                policy[NO_REMOVE] = namespace[NO_REMOVE]
                misc.ensureObjectInMaps( model[SRC], [HBASE_RANGER_POLICIES], [])
                model[SRC][HBASE_RANGER_POLICIES].append(policy)
            

def grabHBaseRangerPoliciesFromTables(model):
    if HBASE_TABLES in model[SRC]:
        for table in model[SRC][HBASE_TABLES]:
            if RANGER_POLICY in table:
                policy = table[RANGER_POLICY]
                policy[TABLES] = [ table[NAMESPACE] +':' + table[NAME] ]
                misc.setDefaultInMap(policy, NAME, DEFAULT_HBASE_TABLE_POLICY_NAME.format(table[NAMESPACE], table[NAME]))
                policy[NO_REMOVE] = table[NO_REMOVE]
                misc.ensureObjectInMaps( model[SRC], [HBASE_RANGER_POLICIES], [])
                model[SRC][HBASE_RANGER_POLICIES].append(policy)
            

def groomRangerHBasePolicies(model):
    grabHBaseRangerPoliciesFromNamespaces(model)
    grabHBaseRangerPoliciesFromTables(model)
    if HBASE_RANGER_POLICIES in model[SRC] and len(model[SRC][HBASE_RANGER_POLICIES]) > 0:
        if RANGER_RELAY not in model[SRC]:
            misc.ERROR("There is at least one 'hbase_ranger_policies', but no 'ranger_relay' was defined!")
        names = Set()
        toRemoveCount = 0
        for policy in model[SRC][HBASE_RANGER_POLICIES]:
            policy[NAME] = model[SRC][RANGER_RELAY][POLICY_NAME_DECORATOR].format(policy[NAME])
            if policy[NAME] in names:
                misc.ERROR("hbase_ranger_policy.name: '{0}' is defined twice".format(policy[NAME])) 
            names.add(policy[NAME])
            misc.setDefaultInMap(policy, AUDIT, True)
            misc.setDefaultInMap(policy, ENABLED, True)
            misc.setDefaultInMap(policy, NO_REMOVE, False)
            if COLUMNS not in policy or len(policy[COLUMNS]) == 0:
                policy[COLUMNS] = [ '*' ]
            if COLUMN_FAMILIES not in policy or len(policy[COLUMN_FAMILIES]) == 0:
                policy[COLUMN_FAMILIES] = [ '*' ]
            misc.setDefaultInMap(policy, PERMISSIONS, [])
            for perms in policy[PERMISSIONS]:
                misc.setDefaultInMap(perms, USERS, [])
                misc.setDefaultInMap(perms, GROUPS, [])
                misc.setDefaultInMap(perms, DELEGATE_ADMIN, False)
                if len(perms[USERS]) == 0 and len(perms[GROUPS]) == 0:
                    misc.ERROR("hbase_ranger_policy.name: '{0}'. A permission has neither group or user defined.".format(policy[NAME]))
            if not policy[NO_REMOVE]:
                toRemoveCount = toRemoveCount + 1
        model[DATA][HBASE_RANGER_POLICIES_TO_REMOVE] = toRemoveCount
            
# -------------------------------------------------------------- Kafka

def grabKafkaRangerPoliciesFromTopics(model):
    if KAFKA_TOPICS in model[SRC]:
        for topic in model[SRC][KAFKA_TOPICS]:
            if RANGER_POLICY in topic:
                policy = topic[RANGER_POLICY]
                policy[TOPICS] = [ topic[NAME] ]
                misc.setDefaultInMap(policy, NAME, DEFAULT_POLICY_NAME.format(topic[NAME]))
                policy[NO_REMOVE] = topic[NO_REMOVE]
                misc.ensureObjectInMaps( model[SRC], [KAFKA_RANGER_POLICIES], [])
                model[SRC][KAFKA_RANGER_POLICIES].append(policy)

def groomRangerKafkaPolicies(model):
    grabKafkaRangerPoliciesFromTopics(model)
    if KAFKA_RANGER_POLICIES in model[SRC] and len(model[SRC][KAFKA_RANGER_POLICIES]) > 0:
        if RANGER_RELAY not in model[SRC]:
            misc.ERROR("There is at least one 'kafka_ranger_policies', but no 'ranger_relay' was defined!")
        names = Set()
        toRemoveCount = 0
        for policy in model[SRC][KAFKA_RANGER_POLICIES]:
            policy[NAME] = model[SRC][RANGER_RELAY][POLICY_NAME_DECORATOR].format(policy[NAME])
            if policy[NAME] in names:
                misc.ERROR("kafka_ranger_policy.name: '{0}' is defined twice".format(policy[NAME])) 
            names.add(policy[NAME])
            misc.setDefaultInMap(policy, AUDIT, True)
            misc.setDefaultInMap(policy, ENABLED, True)
            misc.setDefaultInMap(policy, NO_REMOVE, False)
            misc.setDefaultInMap(policy, PERMISSIONS, [])
            for perms in policy[PERMISSIONS]:
                misc.setDefaultInMap(perms, USERS, [])
                misc.setDefaultInMap(perms, GROUPS, [])
                misc.setDefaultInMap(perms, IP_ADDRESSES, [])
                misc.setDefaultInMap(perms, DELEGATE_ADMIN, False)
                if len(perms[USERS]) == 0 and len(perms[GROUPS]) == 0:
                    misc.ERROR("kafka_ranger_policy.name: '{0}'. A permission has neither group or user defined.".format(policy[NAME]))
            if not policy[NO_REMOVE]:
                toRemoveCount = toRemoveCount + 1
        model[DATA][KAFKA_RANGER_POLICIES_TO_REMOVE] = toRemoveCount
            
# -------------------------------------------------------------- Hive

def grabHiveRangerPoliciesFromDatabase(model):
    if HIVE_DATABASES in model[SRC]:
        for database in model[SRC][HIVE_DATABASES]:
            if RANGER_POLICY in database:
                policy = database[RANGER_POLICY]
                policy[DATABASES] = [ database[NAME] ]
                policy[TABLES] = [ "*" ]
                policy[COLUMNS] = [ "*" ]
                misc.setDefaultInMap(policy, NAME, DEFAULT_POLICY_NAME.format(database[NAME]))
                policy[NO_REMOVE] = database[NO_REMOVE]
                misc.ensureObjectInMaps( model[SRC], [HIVE_RANGER_POLICIES], [])
                model[SRC][HIVE_RANGER_POLICIES].append(policy)
            

def grabHiveRangerPoliciesFromTables(model):
    if HIVE_TABLES in model[SRC]:
        for table in model[SRC][HIVE_TABLES]:
            if RANGER_POLICY in table:
                policy = table[RANGER_POLICY]
                policy[DATABASES] = [ table[DATABASE] ]
                policy[TABLES] = [ table[NAME] ]
                policy[COLUMNS] = [ "*" ]
                misc.setDefaultInMap(policy, NAME, DEFAULT_HIVE_TABLE_POLICY_NAME.format(table[DATABASE], table[NAME]))
                policy[NO_REMOVE] = table[NO_REMOVE]
                misc.ensureObjectInMaps( model[SRC], [HIVE_RANGER_POLICIES], [])
                model[SRC][HIVE_RANGER_POLICIES].append(policy)
            
def groomRangerHivePolicies(model):
    grabHiveRangerPoliciesFromDatabase(model)
    grabHiveRangerPoliciesFromTables(model)
    if HIVE_RANGER_POLICIES in model[SRC] and len(model[SRC][HIVE_RANGER_POLICIES]) > 0:
        if RANGER_RELAY not in model[SRC]:
            misc.ERROR("There is at least one 'hive_ranger_policies', but no 'ranger_relay' was defined!")
        names = Set()
        toRemoveCount = 0
        for policy in model[SRC][HIVE_RANGER_POLICIES]:
            policy[NAME] = model[SRC][RANGER_RELAY][POLICY_NAME_DECORATOR].format(policy[NAME])
            if policy[NAME] in names:
                misc.ERROR("hive_ranger_policy.name: '{0}' is defined twice".format(policy[NAME])) 
            names.add(policy[NAME])
            misc.setDefaultInMap(policy, AUDIT, True)
            misc.setDefaultInMap(policy, ENABLED, True)
            misc.setDefaultInMap(policy, NO_REMOVE, False)
            if UDFS in policy:
                if COLUMNS in policy or TABLES in policy:
                    misc.ERROR("hive_ranger_policy.name: '{0}' 'udfs' and 'tables' or 'columns' are exclusive".format(policy[NAME]))
            else:
                if COLUMNS not in policy or len(policy[COLUMNS]) == 0:
                    policy[COLUMNS] = [ '*' ]
                if TABLES not in policy or len(policy[TABLES]) == 0:
                    policy[TABLES] = [ '*' ]
            misc.setDefaultInMap(policy, PERMISSIONS, [])
            for perms in policy[PERMISSIONS]:
                misc.setDefaultInMap(perms, USERS, [])
                misc.setDefaultInMap(perms, GROUPS, [])
                misc.setDefaultInMap(perms, DELEGATE_ADMIN, False)
                if len(perms[USERS]) == 0 and len(perms[GROUPS]) == 0:
                    misc.ERROR("hive_ranger_policy.name: '{0}'. A permission has neither group or user defined.".format(policy[NAME]))
            if not policy[NO_REMOVE]:
                toRemoveCount = toRemoveCount + 1
        model[DATA][HIVE_RANGER_POLICIES_TO_REMOVE] = toRemoveCount
            
              
# -------------------------------------------------------------- Yarn
            
def groomRangerYarnPolicies(model):
    if YARN_RANGER_POLICIES in model[SRC] and len(model[SRC][YARN_RANGER_POLICIES]) > 0:
        if RANGER_RELAY not in model[SRC]:
            misc.ERROR("There is at least one 'yarn_ranger_policies', but no 'ranger_relay' was defined!")
        names = Set()
        toRemoveCount = 0
        for policy in model[SRC][YARN_RANGER_POLICIES]:
            policy[NAME] = model[SRC][RANGER_RELAY][POLICY_NAME_DECORATOR].format(policy[NAME])
            if policy[NAME] in names:
                misc.ERROR("yarn_ranger_policy.name: '{0}' is defined twice".format(policy[NAME])) 
            names.add(policy[NAME])
            misc.setDefaultInMap(policy, AUDIT, True)
            misc.setDefaultInMap(policy, ENABLED, True)
            misc.setDefaultInMap(policy, RECURSIVE, True)
            misc.setDefaultInMap(policy, NO_REMOVE, False)
            misc.setDefaultInMap(policy, PERMISSIONS, [])
            for perms in policy[PERMISSIONS]:
                misc.setDefaultInMap(perms, USERS, [])
                misc.setDefaultInMap(perms, GROUPS, [])
                misc.setDefaultInMap(perms, DELEGATE_ADMIN, False)
                if len(perms[USERS]) == 0 and len(perms[GROUPS]) == 0:
                    misc.ERROR("yarn_ranger_policy.name: '{0}'. A permission has neither group or user defined.".format(policy[NAME]))
            if not policy[NO_REMOVE]:
                toRemoveCount = toRemoveCount + 1
        model[DATA][YARN_RANGER_POLICIES_TO_REMOVE] = toRemoveCount
            
# -------------------------------------------------------------- Storm

def grabStormRangerPoliciesFromTopologies(model):
    if STORM_TOPOLOGIES in model[SRC]:
        for topology in model[SRC][STORM_TOPOLOGIES]:
            if RANGER_POLICY in topology:
                policy = topology[RANGER_POLICY]
                policy[TOPOLOGIES] = [ topology[NAME] ]
                misc.setDefaultInMap(policy, NAME, DEFAULT_POLICY_NAME.format(topology[NAME]))
                policy[NO_REMOVE] = topology[NO_REMOVE]
                misc.ensureObjectInMaps( model[SRC], [STORM_RANGER_POLICIES], [])
                model[SRC][STORM_RANGER_POLICIES].append(policy)

def groomRangerStormPolicies(model):
    grabStormRangerPoliciesFromTopologies(model)
    if STORM_RANGER_POLICIES in model[SRC] and len(model[SRC][STORM_RANGER_POLICIES]) > 0:
        if RANGER_RELAY not in model[SRC]:
            misc.ERROR("There is at least one 'storm_ranger_policies', but no 'ranger_relay' was defined!")
        names = Set()
        toRemoveCount = 0
        for policy in model[SRC][STORM_RANGER_POLICIES]:
            policy[NAME] = model[SRC][RANGER_RELAY][POLICY_NAME_DECORATOR].format(policy[NAME])
            if policy[NAME] in names:
                misc.ERROR("storm_ranger_policy.name: '{0}' is defined twice".format(policy[NAME])) 
            names.add(policy[NAME])
            misc.setDefaultInMap(policy, AUDIT, True)
            misc.setDefaultInMap(policy, ENABLED, True)
            misc.setDefaultInMap(policy, NO_REMOVE, False)
            misc.setDefaultInMap(policy, PERMISSIONS, [])
            for perms in policy[PERMISSIONS]:
                misc.setDefaultInMap(perms, USERS, [])
                misc.setDefaultInMap(perms, GROUPS, [])
                misc.setDefaultInMap(perms, DELEGATE_ADMIN, False)
                if len(perms[USERS]) == 0 and len(perms[GROUPS]) == 0:
                    misc.ERROR("storm_ranger_policy.name: '{0}'. A permission has neither group or user defined.".format(policy[NAME]))
            if not policy[NO_REMOVE]:
                toRemoveCount = toRemoveCount + 1
        model[DATA][STORM_RANGER_POLICIES_TO_REMOVE] = toRemoveCount
                 
