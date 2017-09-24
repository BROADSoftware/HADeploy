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
import os
import hadeploy.core.misc as misc


from hadeploy.core.plugin import Plugin
from hadeploy.core.const import SRC,DATA,HOST_BY_NAME,INVENTORY,SSH_USER,DEFAULT_HDFS_KEYTABS_FOLDER,ACTION_DEPLOY,ACTION_REMOVE


"""
This module is designed to works in cooperation with file modules, just by adding HDFS target.

It is far more easy to let the files modules handle data model even for HDFS targeted files.

"""


logger = logging.getLogger("hadeploy.plugins.hdfs")


HDFS="hdfs"
HDFS_RELAY="hdfs_relay"
SOURCE_HOST_CREDENTIALS="source_host_credentials"
CACHE_FOLDER="cache_folder"
USER="user"
KERBEROS="kerberos"
KDEBUG="kdebug"
CREDENTIAL_BY_HOST="credentialByHost"
PRINCIPAL="principal"
SCOPE_BY_NAME="scopeByName"          
LOCAL_KEYTAB_PATH="local_keytab_path"
RELAY_KEYTAB_PATH="relay_keytab_path"
_RELAY_KEYTAB_FOLDER_="_relayKeytabFolder_"        
NODE_KEYTAB_PATH="node_keytab_path"
_NODE_KEYTAB_FOLDER_="_nodeKeytabFolder_"        

HOST="host"

class HdfsPlugin(Plugin):
    
    def __init__(self, name, path, context):
        Plugin.__init__(self, name, path, context)


    def onNewSnippet(self, snippetPath):
        model = self.context.model
        if HDFS_RELAY in model[SRC]: 
            if LOCAL_KEYTAB_PATH in model[SRC][HDFS_RELAY]:
                model[SRC][HDFS_RELAY][LOCAL_KEYTAB_PATH] = misc.snippetRelocate(snippetPath, model[SRC][HDFS_RELAY][LOCAL_KEYTAB_PATH])
        if SOURCE_HOST_CREDENTIALS in model[SRC]:
            for h in model[SRC][SOURCE_HOST_CREDENTIALS]:
                if LOCAL_KEYTAB_PATH in h:
                    h[LOCAL_KEYTAB_PATH] = misc.snippetRelocate(snippetPath, h[LOCAL_KEYTAB_PATH])
                

         
    def getGroomingPriority(self):
        return 3500     
 
    def getSupportedActions(self):
        return [ACTION_DEPLOY, ACTION_REMOVE]

    def getPriority(self, action):
        return 3500 if action == ACTION_DEPLOY else 3500 if action == ACTION_REMOVE else misc.ERROR("Plugin 'hdfs' called with invalid action: '{0}'".format(action))


    def onGrooming(self):
        #misc.ensureObjectInMaps(self.context.model[DATA], [HDFS, SCOPE_BY_NAME], {})  # Also performed in file plugin if HDFS_RELAY is defined.
        groomHdfsRelay(self.context.model)
        groomSourceHostCredentials(self.context.model)
        
# ---------------------------------------------------- Static functions

def groomHdfsRelay(model):
    if HDFS_RELAY in model[SRC]:
        if model[SRC][HDFS_RELAY][HOST] not in model[DATA][INVENTORY][HOST_BY_NAME]:
            misc.ERROR("hdfs_relay: hosts '{0}' is undefined".format(model[SRC][HDFS_RELAY][HOST]))
        # misc.setDefaultInMap(model[SRC][HDFS_RELAY], CACHE_FOLDER, DEFAULT_HDFS_RELAY_CACHE_FOLDER) # Also performed in file plugin
        if PRINCIPAL in  model[SRC][HDFS_RELAY]:
            if USER in model[SRC][HDFS_RELAY]:
                misc.ERROR("hdfs_relay: If a 'principal' is defined, then no 'user' should be defined, as all operations will be performed on behalf of the 'principal'")
            if LOCAL_KEYTAB_PATH not in model[SRC][HDFS_RELAY] and  RELAY_KEYTAB_PATH not in model[SRC][HDFS_RELAY]:
                misc.ERROR("hdfs_relay: Please provide a 'local_keytab_path' and/or a 'relay_keytab_path' if you want to use a Kerberos 'principal'")
            if LOCAL_KEYTAB_PATH in model[SRC][HDFS_RELAY]:
                if not os.path.exists(model[SRC][HDFS_RELAY][LOCAL_KEYTAB_PATH]):
                    misc.ERROR("hdfs_relay: local_keytab_file '{0}' does not exists!".format(model[SRC][HDFS_RELAY][LOCAL_KEYTAB_PATH]))
                if RELAY_KEYTAB_PATH not in model[SRC][HDFS_RELAY]:
                    model[SRC][HDFS_RELAY][_RELAY_KEYTAB_FOLDER_] = DEFAULT_HDFS_KEYTABS_FOLDER
                    model[SRC][HDFS_RELAY][RELAY_KEYTAB_PATH] = os.path.join( model[SRC][HDFS_RELAY][_RELAY_KEYTAB_FOLDER_], os.path.basename(model[SRC][HDFS_RELAY][LOCAL_KEYTAB_PATH]))
            model[SRC][HDFS_RELAY][KERBEROS] = True
            model[SRC][HDFS_RELAY][USER] = "KERBEROS"
            misc.setDefaultInMap(model[SRC][HDFS_RELAY], KDEBUG, False)
        else:
            if LOCAL_KEYTAB_PATH in model[SRC][HDFS_RELAY] or RELAY_KEYTAB_PATH in model[SRC][HDFS_RELAY]:
                misc.ERROR("hdfs_relay: Please, provide a 'principal' if you need to use a keytab")
            model[SRC][HDFS_RELAY][KERBEROS] = False
            model[SRC][HDFS_RELAY][KDEBUG] = False
            sshUser =  model[DATA][INVENTORY][HOST_BY_NAME][model[SRC][HDFS_RELAY][HOST]][SSH_USER]
            misc.setDefaultInMap(model[SRC][HDFS_RELAY], USER,  "hdfs" if sshUser == "root" else sshUser)


def groomSourceHostCredentials(model):
    misc.ensureObjectInMaps(model[DATA], [HDFS, CREDENTIAL_BY_HOST], {})
    if SOURCE_HOST_CREDENTIALS in model[SRC]:
        for hcredential in model[SRC][SOURCE_HOST_CREDENTIALS]:
            key = hcredential[HOST]
            model[DATA][HDFS][CREDENTIAL_BY_HOST][key] = hcredential
            del model[DATA][HDFS][CREDENTIAL_BY_HOST][key][HOST]  # No need to keep hostname, as it is the key
            misc.setDefaultInMap(hcredential, KDEBUG, False)
            if LOCAL_KEYTAB_PATH not in hcredential and  NODE_KEYTAB_PATH not in hcredential:
                misc.ERROR("source_host_credential for host {0}: Please provide a 'local_keytab_path' and/or a 'node_keytab_path'".format(key))
            if LOCAL_KEYTAB_PATH in hcredential:
                if not os.path.exists(hcredential[LOCAL_KEYTAB_PATH]):
                    misc.ERROR("source_host_credential for host {0}: local_keytab_file '{1}' does not exists!".format(key, hcredential[LOCAL_KEYTAB_PATH]))
                if NODE_KEYTAB_PATH not in hcredential:
                    hcredential[_NODE_KEYTAB_FOLDER_] = DEFAULT_HDFS_KEYTABS_FOLDER
                    hcredential[NODE_KEYTAB_PATH] = os.path.join( hcredential[_NODE_KEYTAB_FOLDER_], os.path.basename(hcredential[LOCAL_KEYTAB_PATH]))




