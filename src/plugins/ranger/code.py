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
from plugin import Plugin
from const import SRC,DATA
import misc
import os
from sets import Set
import yaml
import schema

logger = logging.getLogger("hadeploy.plugins.ranger")

DEFAULT_POLICY_NAME="_{0}_"
DEFAULT_HBASE_TABLE_POLICY_NAME="_{0}:{1}_"


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


class RangerPlugin(Plugin):
    
    def __init__(self, name, path, context):
        Plugin.__init__(self, name, path, context)
        self.myHostGroups = []
    
    def onNewSnippet(self, snippetPath):
        if 'ranger_relay' in self.context.model:
            if 'ca_bundle_local_file' in self.context.model['ranger_relay']:
                if not os.path.isabs(self.context.model['ranger_relay']['ca_bundle_local_file']):
                    self.context.model['ranger_relay']['ca_bundle_local_file'] = os.path.normpath(os.path.join(snippetPath, self.context.model['ranger_relay']['ca_bundle_local_file']))
            

    def onGrooming(self):
        groomRangerRelay(self.context.model)
        if 'hdfs' in self.context.pluginByName:
            groomRangerHdfsPolicies(self.context.model)
        if 'hbase' in self.context.pluginByName:
            groomRangerHBasePolicies(self.context.model)
        if 'kafka' in self.context.pluginByName:
            groomRangerKafkaPolicies(self.context.model)

    def getSchema(self):
        schemaFile = os.path.join(self.path, "schema_base.yml")
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
        return theSchema

# ---------------------------------------------------------------------------- Static function    

def groomRangerRelay(model):
    if RANGER_RELAY in model[SRC]:
        relay = model[SRC][RANGER_RELAY]
        misc.setDefaultInMap(relay, VALIDATE_CERTS, True)
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
    if HDFS_RANGER_POLICIES in model[SRC]:
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
                    misc.ERROR("hdfs_ranger_policy.name: '{0}'. A permission has neither group or user defined.")
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
    if HBASE_RANGER_POLICIES in model[SRC]:
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
                    misc.ERROR("hbase_ranger_policy.name: '{0}'. A permission has neither group or user defined.")
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
    if KAFKA_RANGER_POLICIES in model[SRC]:
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
                    misc.ERROR("kafka_ranger_policy.name: '{0}'. A permission has neither group or user defined.")
            if not policy[NO_REMOVE]:
                toRemoveCount = toRemoveCount + 1
        model[DATA][KAFKA_RANGER_POLICIES_TO_REMOVE] = toRemoveCount
            
                        
                
