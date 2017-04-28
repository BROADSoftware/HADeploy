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

import os
import argparse 
import logging.config
import yaml

import misc

from plugin import Plugin
from context import Context

logger = logging.getLogger("hadeploy.main")


def main():
    mydir =  os.path.dirname(os.path.realpath(__file__)) 
    parser = argparse.ArgumentParser()
    parser.add_argument('--src', nargs='*', required=True)
    parser.add_argument('--yamlLoggingConf', help="Logging configuration as a yaml file", required=True)
    parser.add_argument('--workingFolder', help="Where to store working context", required=True)

    param = parser.parse_args()

    loggingConfFile = param.yamlLoggingConf
    if not os.path.isfile(loggingConfFile):
        misc.ERROR("'{0}' is not a readable file!".format(loggingConfFile))    

    logging.config.dictConfig(yaml.load(open(loggingConfFile)))
    
    logger.debug("mydir:" + mydir)
    logger.debug("param.src:" + str(param.src))
    
    workingFolder = param.workingFolder
    if not os.path.isdir(workingFolder):
        misc.ERROR("{0} must be an existing folder".format(workingFolder))
    if len(os.listdir(workingFolder)) > 0:
        misc.ERROR("{0} must be an existing EMPTY folder".format(workingFolder))
    
    # We must make a first read of the file, in a reduced context to fetch modules definition
    builtinPath = os.path.abspath(os.path.join(mydir, "../plugins"))
    context = Context()

    masterPlugin = Plugin("master", [builtinPath])
    context.addPlugin(masterPlugin)

    testPlugin = Plugin("test", [builtinPath])
    context.addPlugin(testPlugin)
    
    masterPlugin.onLoad(masterPlugin, context)
    testPlugin.onLoad(testPlugin, context)

if __name__ == "__main__":
    main()


