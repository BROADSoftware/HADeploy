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
from templator import Templator


logger = logging.getLogger("hadeploy.main")


def handleSourceFiles(srcFileList, context):
    parser = Parser(context)
    for src in srcFileList:
        parser.parse(src)



def main():
    mydir =  os.path.dirname(os.path.realpath(__file__)) 
    parser = argparse.ArgumentParser()
    parser.add_argument('--src', nargs='*', required=True)
    parser.add_argument('--yamlLoggingConf', help="Logging configuration as a yaml file", required=False)
    parser.add_argument('--workingFolder', help="Where to store working context", required=True)

    param = parser.parse_args()

    if param.yamlLoggingConf != None:
        loggingConfFile = param.yamlLoggingConf
    else:
        loggingConfFile = os.path.join(mydir, "conf/logging.yml")
        
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
    if 'include' in context.model[SRC]:
        del(context.model[SRC]['include'])  # Must remove, as not part of the schema

    # Now, build the schema for source validation, by merge of all schema plugin
    theSchema = context.getSchema()
    dump.dumpSchema(context, theSchema)
    dump.dumpModel(context)
    # And validate against this schema
    schema.validate(context.model[SRC], theSchema)

    # And groom all plugins
    context.groom()

    context.buildInstallTemplate()
    context.buildRemoveTemplate()
    context.builRolesPath()

    #dump.dumpModel(context)

    context.generatePrivateTemplate()

    templator = Templator([os.path.join(mydir, './templates'), context.workingFolder], context.model)
    templator.generate("inventory.jj2", os.path.join(context.workingFolder, "inventory"))
    templator.generate("ansible.cfg.jj2", os.path.join(context.workingFolder, "ansible.cfg"))
    templator.generate("install.yml.jj2", os.path.join(context.workingFolder, "install.yml"))
    templator.generate("remove.yml.jj2", os.path.join(context.workingFolder, "remove.yml"))
    misc.ensureFolder(os.path.join(context.workingFolder, "group_vars"))
    templator.generate("group_vars_all.jj2", os.path.join(context.workingFolder, "group_vars/all"))
    

if __name__ == "__main__":
    main()


