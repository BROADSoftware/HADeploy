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
from const import PLUGINS, PLUGINS_PATHS, SRC, VARS
from templator import Templator


logger = logging.getLogger("hadeploy.main")

INCLUDED_SCOPES="included_scopes"
EXCLUDED_SCOPES="excluded_scopes"


def handleSourceFiles(srcFileList, context, fileByVariable):
    parser = Parser(context, fileByVariable)
    for src in srcFileList:
        parser.parse(src)

# We allow both --scope sc1 --scope sc2,sc3
def handleCliScopes(scopeList):
    scp = []
    if scopeList != None:
        for sc in scopeList:
            scp.extend(sc.split(","))
    return set(scp)   # A set will be more efficient
        
def main():
    mydir =  os.path.dirname(os.path.realpath(__file__)) 
    parser = argparse.ArgumentParser()
    parser.add_argument('--src', nargs='*', required=True)
    parser.add_argument('--action', required=True)
    parser.add_argument('--scope', nargs='*', required=False)
    parser.add_argument('--noScope', nargs='*', required=False)
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
    handleSourceFiles(param.src, context, None)
    context.groom()
    
    # --------------------------------------------- included scope handling
    context.includedScopes = handleCliScopes(param.scope)
    if len(context.includedScopes) == 0 and INCLUDED_SCOPES in context.model[SRC]:
        context.includedScopes = set(context.model[SRC][INCLUDED_SCOPES])
    if len(context.includedScopes) > 0:
        print("Scope limited to  {0}".format(str(list(context.includedScopes))))
    # -------------------------------------------- Excluded scope handling
    context.excludedScopes = handleCliScopes(param.noScope)
    if EXCLUDED_SCOPES in context.model[SRC]:
        context.excludedScopes = context.excludedScopes.union(context.model[SRC][EXCLUDED_SCOPES])
    if len(context.excludedScopes) > 0:
        print("Scope excluded: {0}".format(str(list(context.excludedScopes))))
    
    # Now, we must have the effective PLUGINS list and PLUGINS_PATHS in the context. We can load all plugins
    for plName in context.model[SRC][PLUGINS]:
            context.loadPlugin(plName, context.model[SRC][PLUGINS_PATHS])
    # And reload source files, with now all plugins activated
    fileByVariable = {} if param.action == "dumpvars" else None        
    handleSourceFiles(param.src, context, fileByVariable)
    if 'include' in context.model[SRC]:
        del(context.model[SRC]['include'])  # Must remove, as not part of the schema

    # Now, build the schema for source validation, by merge of all schema plugin
    theSchema = context.getSchema()
    dump.dumpSchema(context, theSchema)
    #dump.dumpModel(context)
    # And validate against this schema
    schema.validate(context.model[SRC], theSchema)

    # And groom all plugins
    context.groom()

    dump.dumpModel(context)

    # Check scopes validity
    # NB: We perform this after grooming, even if grooming can rely on scope. Aims is only to detect scopes with typo. 
    supportedScopes = context.getAllSupportedScopes()
    scopesToTest = context.excludedScopes.union(context.includedScopes)
    for scope in scopesToTest:
        if scope != "all" and scope != "none" and not context.checkScope(scope) and scope not in supportedScopes:   # checkScope(): Scope for target file/folders (hosts and hostgroups)
            misc.ERROR("Scope '{0}' is not supported!".format(scope))
    
    templator = Templator([os.path.join(mydir, './templates'), context.workingFolder], context.model)
    actions = context.getAllSupportedActions()
    logger.debug("Supported actions: {0}".format(actions))
    action = param.action
    if action == "none":
        for action in actions:
            pluginExts = context.getPluginExtForAction(action)
            logger.debug("Action: {0} -> plugins: {1}".format(action, pluginExts))
            context.buildTemplate(action, pluginExts)
            context.builRolesPath(action, pluginExts)
            context.generateAuxTemplates(action, pluginExts)
            templator.generate("{0}.yml.jj2".format(action), os.path.join(context.workingFolder, "{0}.yml".format(action)))
    elif action == "dumpvars":
        if SRC in context.model and VARS in context.model[SRC]:
            print("---")
            variables = context.model[SRC][VARS]
            for name in sorted(variables):
                x = yaml.dump(variables[name], default_flow_style=True, default_style=None, explicit_end=False)
                p = x.find("\n...\n")
                if p > 0:
                    x = x[:-5]
                p = x.find("\n")
                if p > 0:
                    x = x[:-1]
                print("{}: {}   ({})".format(name, x, fileByVariable[name] if name in fileByVariable else "??"))
            print("---")
            #txt = yaml.dump(context.model[SRC][VARS], default_flow_style=False, default_style=None)
            return
    else: 
        if not action in actions:
            misc.ERROR("Action {0} not supported. Current configuration only supports {1}".format(action, str(actions)))
        pluginExts = context.getPluginExtForAction(action)
        logger.debug("Action: {0} -> plugins: {1}".format(action, pluginExts))
        context.buildTemplate(action, pluginExts)
        context.builRolesPath(action, pluginExts)
        context.generateAuxTemplates(action, pluginExts)
        templator.generate("{0}.yml.jj2".format(action), os.path.join(context.workingFolder, "{0}.yml".format(action)))
        

    templator.generate("inventory.jj2", os.path.join(context.workingFolder, "inventory"))
    templator.generate("ansible.cfg.jj2", os.path.join(context.workingFolder, "ansible.cfg"))
    misc.ensureFolder(os.path.join(context.workingFolder, "group_vars"))
    templator.generate("group_vars_all.jj2", os.path.join(context.workingFolder, "group_vars/all"))
    

if __name__ == "__main__":
    main()


