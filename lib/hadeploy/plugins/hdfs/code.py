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


from hadeploy.core.plugin import Plugin
from hadeploy.core.const import SRC,DATA


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
KEYTAB_PATH="keytab_path"
SCOPE_BY_NAME="scopeByName"          


HOST="host"
HOST_BY_NAME="hostByName"
INVENTORY="inventory"


class FilesPlugin(Plugin):
    
    def __init__(self, name, path, context):
        Plugin.__init__(self, name, path, context)

    def getGroomingDependencies(self):
        return ['files']

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
            if KEYTAB_PATH not in model[SRC][HDFS_RELAY]:
                misc.ERROR("hdfs_relay: Please provide a 'keytab_path' if you want to use a Kerberos 'principal'")
            if USER in model[SRC][HDFS_RELAY]:
                misc.ERROR("hdfs_relay: If a 'principal' is defined, then no 'user' should be defined, as all operations will be performed on behalf of the 'principal'")
            model[SRC][HDFS_RELAY][KERBEROS] = True
            model[SRC][HDFS_RELAY][USER] = "KERBEROS"
            misc.setDefaultInMap(model[SRC][HDFS_RELAY], KDEBUG, False)
        else:
            if KEYTAB_PATH in model[SRC][HDFS_RELAY]:
                misc.ERROR("hdfs_relay: Please, provide a 'principal' if you need to use a keytab")
            model[SRC][HDFS_RELAY][KERBEROS] = False
            model[SRC][HDFS_RELAY][KDEBUG] = False
            misc.setDefaultInMap(model[SRC][HDFS_RELAY], USER,  "hdfs")



def groomSourceHostCredentials(model):
    misc.ensureObjectInMaps(model[DATA], [HDFS, CREDENTIAL_BY_HOST], {})
    if SOURCE_HOST_CREDENTIALS in model[SRC]:
        for h in model[SRC][SOURCE_HOST_CREDENTIALS]:
            key = h[HOST]
            model[DATA][HDFS][CREDENTIAL_BY_HOST][key] = h
            del model[DATA][HDFS][CREDENTIAL_BY_HOST][key][HOST]  # No need to keep hostname, as it is the key
            misc.setDefaultInMap(model[DATA][HDFS][CREDENTIAL_BY_HOST][key], KDEBUG, False)





