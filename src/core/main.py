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
import schema
import dump

from context import Context
from parser import Parser
from const import PLUGINS, PLUGINS_PATHS, SRC


logger = logging.getLogger("hadeploy.main")



def handleSourceFiles(srcFileList, context):
    parser = Parser()
    for src in srcFileList:
        base = os.path.dirname(os.path.abspath(src))
        parser.parse(src)
        # Adjust some environment variable, as they are relative to source file path
        context.model['src'] = parser.getResult()
        for plugin in context.plugins:
            plugin.onNewSnippet(context, base)



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
    
    # ----- We must make a first read of the file, with only the 'master' plugin to fetch plugins list and path
    masterPluginPath = os.path.abspath(os.path.join(mydir, "."))
    context = Context(workingFolder)
    context.loadPlugin("master", [masterPluginPath])
    handleSourceFiles(param.src, context)
    context.groom()

    # Now, we must have the effective PLUGINS list and PLUGINS_PATHS in the context. We can load all plugins
    for plName in context.model[SRC][PLUGINS]:
            context.loadPlugin(plName, context.model[SRC][PLUGINS_PATHS])
    # And reload source files, with now all plugins activated
    handleSourceFiles(param.src, context)
    # And groom all plugins
    context.groom()

    dump.dumpModel(context)
    
    # Now, build the schema for source validation, by merge of all schema plugin
    theSchema = context.getSchema()
    dump.dumpSchema(context, theSchema)
    
    schema.validate(context.model[SRC], theSchema)




"""
    test1Plugin = loadPlugin("test1", [builtinPath])
    context.addPlugin(test1Plugin)

    test2Plugin = loadPlugin("test2", [builtinPath])
    context.addPlugin(test2Plugin)
    
    masterPlugin.onNewSnippet(context)
    test1Plugin.onNewSnippet(context)
    test2Plugin.onNewSnippet(context)
"""

if __name__ == "__main__":
    main()


