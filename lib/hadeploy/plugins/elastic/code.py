# Copyright (C) 2018 BROADSoftware
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
from hadeploy.core.plugin import Plugin
from hadeploy.core.const import SRC,DATA,ACTION_DEPLOY,ACTION_REMOVE,SCOPE_ELASTIC
from sets import Set
#import json


logger = logging.getLogger("hadeploy.plugins.kafka")

ELASTICSEARCH_SERVERS="elasticsearch_servers"
ELASTICSEARCH_INDICES="elasticsearch_indices"
ELASTICSEARCH_TEMPLATES="elasticsearch_templates"
NAME="name"
SERVER="server"
NO_REMOVE="no_remove"
RECREATE="recreate"
DEFINITION="definition"


ELASTIC="elastic"
SERVER_BY_NAME="serverByName"
INDEX_BY_SERVER="indexByServer"
INDICES="indices"
TEMPLATES="templates"
_DEFINITION_="_definition_"

class ElasticsearchPlugin(Plugin):
    
    def __init__(self, name, path, context):
        Plugin.__init__(self, name, path, context)

    def onNewSnippet(self, snippetPath):
        pass

    def getGroomingPriority(self):
        return 3000

    def getSupportedScopes(self):
        return [SCOPE_ELASTIC]        

    def getSupportedActions(self):
        if self.context.toExclude(SCOPE_ELASTIC):
            return []
        else:
            return [ACTION_DEPLOY, ACTION_REMOVE]

    def getPriority(self, action):
        return 2700 if action == ACTION_DEPLOY else 5000 if action == ACTION_REMOVE else misc.ERROR("Plugin 'elasticsearch' called with invalid action: '{0}'".format(action))

    def onGrooming(self):
        misc.applyWhenOnList(self.context.model[SRC], ELASTICSEARCH_SERVERS)
        misc.applyWhenOnList(self.context.model[SRC], ELASTICSEARCH_INDICES)
        misc.applyWhenOnList(self.context.model[SRC], ELASTICSEARCH_TEMPLATES)
        if self.context.toExclude(SCOPE_ELASTIC):
            return
        misc.ensureObjectInMaps(self.context.model[DATA], [ELASTIC], {})
        groomElasticServers(self.context.model)
        groomElasticIndices(self.context.model)
        groomElasticTemplates(self.context.model)


def groomElasticServers(model):
    misc.ensureObjectInMaps(model[DATA][ELASTIC], [SERVER_BY_NAME], {})
    if ELASTICSEARCH_SERVERS in model[SRC]:
        for server in model[SRC][ELASTICSEARCH_SERVERS]:
            if server[NAME] in model[DATA][ELASTIC][SERVER_BY_NAME]:
                misc.ERROR("Elasticsearch server '{}' is defined twice!".format(server[NAME]))
            misc.ensureObjectInMaps(server, [INDICES], [])
            misc.ensureObjectInMaps(server, [TEMPLATES], [])
            model[DATA][ELASTIC][SERVER_BY_NAME][server[NAME]] = server
    
def groomElasticIndices(model):
    nameChecker = Set()
    if ELASTICSEARCH_INDICES in model[SRC]:
        for index in model[SRC][ELASTICSEARCH_INDICES]:
            key = index[SERVER] + "." + index[NAME]
            if key in nameChecker:
                misc.ERROR("Elastic search index '{}' is defined twice in server '{}'".format(index[NAME], index[SERVER]))
            nameChecker.add(key)
            misc.setDefaultInMap(index, NO_REMOVE, False)
            misc.setDefaultInMap(index, RECREATE, False)
            if isinstance(index[DEFINITION], basestring):
                #index[_DEFINITION_] = json.loads(index[DEFINITION])
                index[_DEFINITION_] = index[DEFINITION]
            else:
                index[_DEFINITION_] = index[DEFINITION]
            if not index[SERVER] in model[DATA][ELASTIC][SERVER_BY_NAME]:
                misc.ERROR("Elastic search index '{}' refers to a non existing server '{}'".format(index[NAME], index[SERVER]))
            else:
                model[DATA][ELASTIC][SERVER_BY_NAME][index[SERVER]][INDICES].append(index)
            

def groomElasticTemplates(model):
    nameChecker = Set()
    if ELASTICSEARCH_TEMPLATES in model[SRC]:
        for template in model[SRC][ELASTICSEARCH_TEMPLATES]:
            key = template[SERVER] + "." + template[NAME]
            if key in nameChecker:
                misc.ERROR("Elastic search template '{}' is defined twice in server '{}'".format(template[NAME], template[SERVER]))
            nameChecker.add(key)
            misc.setDefaultInMap(template, NO_REMOVE, False)
            if isinstance(template[DEFINITION], basestring):
                #template[_DEFINITION_] = json.loads(template[DEFINITION])
                template[_DEFINITION_] = template[DEFINITION]
            else:
                template[_DEFINITION_] = template[DEFINITION]
            if not template[SERVER] in model[DATA][ELASTIC][SERVER_BY_NAME]:
                misc.ERROR("Elastic search template '{}' refers to a non existing server '{}'".format(template[NAME], template[SERVER]))
            else:
                model[DATA][ELASTIC][SERVER_BY_NAME][template[SERVER]][TEMPLATES].append(template)
            
   
    
    
