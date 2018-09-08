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
from hadeploy.core.const import SRC,DATA,DEFAULT_TOOLS_FOLDER,SCOPE_KAFKA,ACTION_DEPLOY,ACTION_REMOVE

logger = logging.getLogger("hadeploy.plugins.kafka")

HELPER="helper"
KAFKA="kafka"
DIR="dir"
JDCTOPIC_JAR="jdctopic_jar"

HOST_GROUP_BY_NAME="hostGroupByName"
INVENTORY="inventory"
KAFKA_RELAY="kafka_relay"
ZK_HOST_GROUP="zk_host_group"
ZK_PORT="zk_port"
BROKER_ID_MAP="broker_id_map"
KAFKA_VERSION="kafka_version"
TOOLS_FOLDER="tools_folder"
ZK_PATH="zk_path"

        
KAFKA_TOPICS="kafka_topics"
ASSIGNMENTS="assignments"
PROPERTIES="properties"
NO_REMOVE="no_remove"

BECOME_USER="become_user"
LOGS_USER="logsUser"

class KafkaPlugin(Plugin):
    
    def __init__(self, name, path, context):
        Plugin.__init__(self, name, path, context)

    def getGroomingPriority(self):
        return 5000

    def getSupportedScopes(self):
        return [SCOPE_KAFKA]        

    def getSupportedActions(self):
        if self.context.toExclude(SCOPE_KAFKA):
            return []
        else:
            return [ACTION_DEPLOY, ACTION_REMOVE]

    def getPriority(self, action):
        return 5000 if action == ACTION_DEPLOY else 2000 if action == ACTION_REMOVE else misc.ERROR("Plugin 'kafka' called with invalid action: '{0}'".format(action))

    def onGrooming(self):
        misc.applyWhenOnSingle(self.context.model[SRC], KAFKA_RELAY)
        misc.applyWhenOnList(self.context.model[SRC], KAFKA_TOPICS)
        if self.context.toExclude(SCOPE_KAFKA):
            return
        self.buildHelper()
        misc.ensureObjectInMaps(self.context.model[DATA], [KAFKA], {})
        groomKafkaRelay(self.context.model)
        groomKafkaTopics(self.context.model)
    
    def buildAuxTemplates(self, action, priority):
        if self.context.toExclude(SCOPE_KAFKA):
            return
        if KAFKA_TOPICS in self.context.model[SRC] and len(self.context.model[SRC][KAFKA_TOPICS]) > 0 :
            templator = Templator([os.path.join(self.path, './helpers/jdctopic')], self.context.model)
            if action == ACTION_DEPLOY:
                templator.generate("desc_topics.yml.jj2", os.path.join(self.context.workingFolder, "desc_topics.yml.j2"))
            elif action == ACTION_REMOVE:
                templator.generate("desc_untopics.yml.jj2", os.path.join(self.context.workingFolder, "desc_untopics.yml.j2"))
            else:
                pass
    
    def getTemplateAsFile(self, action, priority):
        if self.context.toExclude(SCOPE_KAFKA):
            return []
        else:
            return [os.path.join(self.path, "install_kafka_relay.yml.jj2"), os.path.join(self.path, "{0}.yml.jj2".format(action))]
    
    def buildHelper(self):
        if KAFKA_RELAY in self.context.model[SRC]:
            helper = {}
            helper[DIR] = os.path.normpath(os.path.join(self.path, "helpers"))
            jarPattern = "jdctopic/jdctopic.{}-*-uber.jar".format(self.context.model[SRC][KAFKA_RELAY][KAFKA_VERSION])
            jdctopicjars = glob.glob(os.path.join(helper[DIR], jarPattern))
            if len(jdctopicjars) < 1:
                misc.ERROR("Unable to find helper for Kafka.Please, refer to the documentation about Installation")
            if len(jdctopicjars) > 1:
                misc.ERROR("Several version of kafka helper jar in {}. Please, cleanup.".format(helper[DIR]))
            helper[JDCTOPIC_JAR] = os.path.basename(jdctopicjars[0])
            
            misc.ensureObjectInMaps(self.context.model, [HELPER, KAFKA], helper)
        
# ------------------------------------------- Static function

def groomKafkaRelay(model):
    if KAFKA_RELAY in model[SRC]:
        if not KAFKA_TOPICS in model[SRC] or len(model[SRC][KAFKA_TOPICS]) == 0:
            del(model[SRC][KAFKA_RELAY])
        else:
            hg = model[SRC][KAFKA_RELAY][ZK_HOST_GROUP]
            if hg not in model[DATA][INVENTORY][HOST_GROUP_BY_NAME]:
                misc.ERROR("kafka_relay: host_group '{0}' does not exists!".format(hg))
            misc.setDefaultInMap(model[SRC][KAFKA_RELAY], ZK_PORT, 2181)
            if BROKER_ID_MAP in model[SRC][KAFKA_RELAY]:
                for brokerId in model[SRC][KAFKA_RELAY][BROKER_ID_MAP].itervalues():
                    if not isinstance(brokerId, int):
                        misc.ERROR("kafka_relay: BrokerId ({0}) must be integer".format(brokerId))
            misc.setDefaultInMap(model[SRC][KAFKA_RELAY], ZK_PATH, '/')
            if BECOME_USER in model[SRC][KAFKA_RELAY]:
                model[SRC][KAFKA_RELAY][LOGS_USER] = model[SRC][KAFKA_RELAY][BECOME_USER]
                misc.setDefaultInMap(model[SRC][KAFKA_RELAY], TOOLS_FOLDER, "/tmp/hadeploy_{}".format(model[SRC][KAFKA_RELAY][BECOME_USER]))
            else:
                model[SRC][KAFKA_RELAY][LOGS_USER] = "{{ansible_user}}"
                misc.setDefaultInMap(model[SRC][KAFKA_RELAY], TOOLS_FOLDER, DEFAULT_TOOLS_FOLDER)

            
def groomKafkaTopics(model):
    if KAFKA_TOPICS in model[SRC] and len(model[SRC][KAFKA_TOPICS]) > 0 :
        if not KAFKA_RELAY in model[SRC]:
            misc.ERROR("A kafka_relay must be defined if at least one kafka_topic is defined")
        for topic in model[SRC][KAFKA_TOPICS]:
            if ASSIGNMENTS in topic:
                if len(topic[ASSIGNMENTS]) == 0:
                    misc.ERROR("Topic '{0}': At least one partition must be defined".format(topic['name']))
                listPart = []
                nbrRep = None
                for part in topic[ASSIGNMENTS]:
                    if not part.isdigit():
                        misc.ERROR("Topic '{0}': Partition ID must be integer".format(topic['name']))
                    listPart.append(int(part))
                    rep = topic[ASSIGNMENTS][part]
                    if not isinstance(rep, list):
                        misc.ERROR("Topic '{0}: Each partition must be defined by an array of brokerId': ".format(topic['name']))
                    if nbrRep == None:
                        nbrRep = len(rep)
                    else:
                        if nbrRep != len(rep):
                            misc.ERROR("Topic '{0}' All partition must have the same number of replicas: ".format(topic['name']))
                    if BROKER_ID_MAP in model[SRC][KAFKA_RELAY]:
                        # Must translate broker_id
                        rep2 = []
                        for brokerId in rep:
                            if not str(brokerId) in model[SRC][KAFKA_RELAY][BROKER_ID_MAP]:
                                misc.ERROR("Topic '{0}': BrokerId {1} must be defined in kafka_relay.broker_id_map".format(topic['name'], brokerId))
                            rep2.append(model[SRC][KAFKA_RELAY][BROKER_ID_MAP][str(brokerId)])
                        topic[ASSIGNMENTS][part] = rep2
                    else :
                        for brokerId in rep:
                            if not isinstance(brokerId, int):
                                misc.ERROR("Topic '{0}': BrokerId must be digit! Or may be you forget to define a 'broker_id_map' in your 'kafka_relay'?".format(topic['name']))
                x = set(listPart)
                if len(x) != len(listPart):
                    misc.ERROR("Topic '{0}': There is duplicated partition ID".format(topic['name']))
                listPart = sorted(listPart)
                if listPart[0] != 0 or listPart[len(listPart) - 1] != len(listPart) -1:
                    misc.ERROR("Topic '{0}': Partition ID must be consecutive numbers, from 0 to number of partition".format(topic['name']))
            else:
                if not 'replication_factor' in topic or not 'partition_factor' in topic:
                    misc.ERROR("Topic '{0}': If partitions layout is not explicit (using assignment), both replication_factor and partition_factor must be defined".format(topic['name']))
            if PROPERTIES in topic:
                if not isinstance(topic[PROPERTIES], dict):
                    misc.ERROR("Topic '{0}': properties: must be a map!".format(topic['name']))
                if len(topic[PROPERTIES]) == 0:
                    del(topic[PROPERTIES])
            misc.setDefaultInMap(topic, NO_REMOVE, False)

    
