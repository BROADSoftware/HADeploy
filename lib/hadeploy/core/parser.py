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

import yaml
import logging
import re
import misc
import jinja2
import os

from const import SRC

logger = logging.getLogger("hadeploy.parser")



class PathItem:
    """
        Limited YAML parser, based on pyyaml event generation.
        This parser is specific because:
        - It is able to merge several documents and file in one.
        - It merge MAP and SEQ. For example
        ---
        vars:
          x: "1111"        
          someitems:
          - item1
          - item2
          
        vars:
          z: "333"
        --- 
        vars:
          y: "2222"
          someitems:
          - item3
          - item4
        
        Gave same result as:
        vars:
          x: "1111"        
          y: "2222"
          z: "333"
          someitems:
          - item1
          - item2
          - item3
          - item4
        
        Also, able to handle variables, using jinj2 templating
        
    """
    
    # Type value
    UNKNOWN = 0
    SCALAR = 1
    MAP = 2
    SEQ = 3
    
    type2String = {
        UNKNOWN: "?",
        SCALAR: "X",
        MAP: "{}",
        SEQ: "[]"
    }
    
    def __init__(self, name, typ):
        self.name = name.encode('utf8')
        self.object = None
        self.setType(typ)
        
    def __repr__(self):
        return self.name + ":" + PathItem.type2String[self.type] 
    def __str__(self):
        return self.name 
    
    def setType(self, typ):
        self.type = typ
        if(self.type == PathItem.MAP):
            self.object = {}
        elif self.type == PathItem.SEQ:
            self.object = []
        else:
            self.object = None
        
    
class Path:
    def __init__(self):
        self.path = []
        self.add(PathItem("root", PathItem.UNKNOWN))
        
    def add(self, pathItem):
        self.path.append(pathItem)
        
    def __repr__(self):
        s = ""
        for p in self.path:
            s += "/" + repr(p)
        return s
    def __str__(self):
        s = ""
        for p in self.path[1:]:
            s += "/" + str(p)
        return s
    
    def len(self):
        return len(self.path)
    
    def top(self):
        return self.path[len(self.path) - 1]
    
    def reduce(self): 
        logger.debug("Will reduce path '{0}'".format(repr(self)))
        val = self.path.pop()
        container = self.top()
        if container.type == PathItem.MAP:
            ##logger.debug(container.object.__class__.__name__)
            container.object[val.name] = val.object
        elif container.type == PathItem.SEQ:
            container.object.append(val.object)
        else:
            raise Exception("Unable to reduce path '{0}'".format(repr(self)))

    def reduceWithAliasMap(self, aliasMap):
        logger.debug("Will reduceWithAliasMap path '{0}' with map '{1}'".format(repr(self), str(map)))
        self.path.pop() # Discard top value (Should be "<<")
        container = self.top()
        if container.type == PathItem.MAP:
            ##logger.debug(container.object.__class__.__name__)
            container.object.update(aliasMap)
        else:
            raise Exception("Unable to reduce path '{0} with an alias'".format(repr(self)))
        
        
            
            
    def setTopType(self, typ):
        self.top().setType(typ) 
        if self.len() > 1:
            container = self.path[self.len() - 2]
            if container.type == PathItem.MAP:
                if self.top().name in container.object:
                    target = container.object[self.top().name]
                    targetClassName = target.__class__.__name__
                    if self.top().type == PathItem.SEQ and targetClassName != "list":
                        raise Exception("Unable to merge SEQ with existing {0} (class: {1}) on path {2}".format(self.top().name, targetClassName, repr(self)))
                    if self.top().type == PathItem.MAP and targetClassName != "dict":
                        raise Exception("Unable to merge MAP with existing {0} (class: {1}) on path {2}".format(self.top().name, targetClassName, repr(self)))
                    logger.debug("MERGING on '{0}' (Path:'{1}')".format(self.top().name, repr(self)))
                    self.top().object = target
                

class State:
    BETWEEN_DOCS = 0
    WAITING_FOR_MAP_ENTRY = 1
    WAITING_FOR_SEQ_ENTRY = 2
    WAITING_FOR_TYPE = 3
    
    stateToString = {
        BETWEEN_DOCS: "BETWEEN_DOCS",
        WAITING_FOR_MAP_ENTRY: "WAITING_FOR_MAP_ENTRY",
        WAITING_FOR_SEQ_ENTRY: "WAITING_FOR_SEQ_ENTRY",
        WAITING_FOR_TYPE: "WAITING_FOR_TYPE"
    }

trueRegex = re.compile(r"^(?:y|Y|yes|Yes|YES|true|True|TRUE|on|On|ON)$")
falseRegex = re.compile(r"^(?:n|N|no|No|NO|false|False|FALSE|off|Off|OFF)$")

class Parser:
    def __init__(self, context, fileByVariable):
        self.context = context
        self.path = Path()
        self.state = State.WAITING_FOR_TYPE
        self.vars = None
        self.anchors = {}
        self.fileByVariable = fileByVariable
        self.parse(None)        # This to have an empty 'vars' dict. Otherwise, if no vars was defined at all, missing var error message was not explicit.

    def invalidEventError(self, event):
        raise Exception("Invalid event {0} in state {1} {2}".format(event, State.stateToString[self.state], event.start_mark))
    
    
    def setState(self, state):
        logger.debug("Switch state from {0} to {1}".format(State.stateToString[self.state], State.stateToString[state]))
        self.state = state
        
    def adjustStateFromTop(self):                    
        if self.path.top().type == PathItem.MAP:
            self.setState(State.WAITING_FOR_MAP_ENTRY)
        elif self.path.top().type == PathItem.SEQ:
            self.setState(State.WAITING_FOR_SEQ_ENTRY)
        else:
            raise Exception("Invalid top state for path {0}".format(repr(self.path)))

        
        
    def parse(self, fileName):
        if fileName == None:
            initVars = {}
            initVars["vars"] = {}
            stream = yaml.dump(initVars)
        elif "=" in fileName:
            clivars = {}
            clivars['vars'] = {}
            x = fileName.split("=")
            if len(x) != 2:
                misc.ERROR("Invalid variable syntax: '{0}'. Must be name=value (without space)".format(fileName))
            clivars['vars'][x[0]] = x[1]
            stream = yaml.dump(clivars)
        else:
            if not os.path.isfile(fileName):
                misc.ERROR("'{0}' is not a readable file!".format(fileName))    
            location =  os.path.dirname(os.path.realpath(fileName))             
            logger.debug("----------------------- Will parse file '{0}' (location:'{1}')".format(fileName, location))
            stream = open(fileName)
        
        for event in yaml.parse(stream):
            if isinstance(event, yaml.events.StreamStartEvent):
                logger.debug("--- StreamStartEvent")
                pass
            elif isinstance(event, yaml.events.DocumentStartEvent):
                logger.debug("--- DocumentStartEvent")
            elif isinstance(event, yaml.events.MappingStartEvent):
                logger.debug("--- MappingStartEvent:" + str(event))
                if self.state  == State.WAITING_FOR_TYPE:
                    self.path.setTopType(PathItem.MAP)
                    if self.path.len() == 2 and self.path.top().name == u'vars':
                        logger.debug("*** vars  ({0}) looked up!".format(self.path.top().object))
                        self.vars = self.path.top().object
                    if event.anchor != None:
                        logger.debug("************************************** ANCHOR {0}".format(event.anchor))
                        self.anchors[event.anchor] = self.path.top().object 
                    self.setState(State.WAITING_FOR_MAP_ENTRY)
                elif self.state  == State.BETWEEN_DOCS:
                    if self.path.top().type != PathItem.MAP:
                        misc.ERROR("Can't merge to document of different type (First is a MAP while other is a SEQ)")
                    else:
                        self.setState(State.WAITING_FOR_MAP_ENTRY)
                elif self.state  == State.WAITING_FOR_SEQ_ENTRY:
                    # A map in a sequence
                    self.path.add(PathItem("?", PathItem.MAP))
                    if event.anchor != None:
                        logger.debug("************************************** ANCHOR {0}".format(event.anchor))
                        self.anchors[event.anchor] = self.path.top().object 
                    self.setState(State.WAITING_FOR_MAP_ENTRY)
                else:
                    self.invalidEventError(event)
            elif isinstance(event, yaml.events.MappingEndEvent):
                logger.debug("--- MappingEndEvent")
                if self.state == State.WAITING_FOR_MAP_ENTRY:
                    if self.path.len() > 1:
                        self.register(fileName)
                        self.path.reduce()
                        self.adjustStateFromTop()
                    else:
                        logger.debug("Found MAP root")
                        self.setState(State.BETWEEN_DOCS)
                else: 
                    self.invalidEventError(event)
            elif isinstance(event, yaml.events.SequenceStartEvent):
                logger.debug("--- SequenceStartEvent:" + str(event))
                if self.state  == State.WAITING_FOR_TYPE:
                    self.path.setTopType(PathItem.SEQ)
                    self.setState(State.WAITING_FOR_SEQ_ENTRY)
                elif self.state  == State.WAITING_FOR_SEQ_ENTRY:
                    # A sequence in a sequence
                    self.path.add(PathItem("?", PathItem.SEQ))
                    self.setState(State.WAITING_FOR_SEQ_ENTRY)
                elif self.state  == State.BETWEEN_DOCS:
                    if self.path.top().type != PathItem.SEQ:
                        misc.ERROR("Can't merge to document of different type (First is a SEQ while other is a MAP)")
                    else:
                        self.setState(State.WAITING_FOR_SEQ_ENTRY)
                else:
                    self.invalidEventError(event)
            elif isinstance(event, yaml.events.SequenceEndEvent):
                logger.debug("--- SequenceEndEvent")
                if self.state == State.WAITING_FOR_SEQ_ENTRY:
                    if self.path.len() > 1:
                        self.register(fileName)
                        self.path.reduce()
                        self.adjustStateFromTop()
                    else:
                        logger.debug("Found SEQ root")
                        self.setState(State.BETWEEN_DOCS)
                else: 
                    self.invalidEventError(event)
            elif isinstance(event, yaml.events.ScalarEvent):
                logger.debug("--- ScalarEvent:" + str(event))
                if self.state == State.WAITING_FOR_MAP_ENTRY:
                    self.path.add(PathItem(event.value, PathItem.UNKNOWN))
                    self.setState(State.WAITING_FOR_TYPE)
                elif self.state == State.WAITING_FOR_SEQ_ENTRY:
                    self.path.add(PathItem("?", PathItem.SCALAR))
                    self.path.top().object = self.setScalar(event)
                    self.register(fileName)
                    if self.path.len() == 3 and self.path.path[1].name ==  "include":
                        included = os.path.join(location, self.path.top().object)
                        logger.debug("********************* Path:'{0}'  -> INCLUDE '{1}' from SEQ".format(repr(self.path), included))
                        self.setState(State.BETWEEN_DOCS)
                        self.path.reduce()
                        self.path.reduce()
                        self.adjustRelativePath(fileName)
                        self.parse(included)
                        self.path.add(PathItem("include", PathItem.SEQ))
                        logger.debug("********************* Path:'{0}' Back from include '{1}'".format(repr(self.path), included))
                        self.setState(State.WAITING_FOR_SEQ_ENTRY)  # No change
                    else: 
                        self.path.reduce()
                        self.setState(State.WAITING_FOR_SEQ_ENTRY)  # No change
                elif self.state == State.WAITING_FOR_TYPE:
                    self.path.top().type = PathItem.SCALAR
                    self.path.top().object = self.setScalar(event)
                    self.register(fileName)
                    if self.path.len() == 2 and self.path.path[1].name ==  "include":
                        included = os.path.join(location, self.path.top().object)
                        logger.debug("********************* Path:'{0}'  -> INCLUDE '{1}' from SINGLE".format(repr(self.path), included))
                        self.path.reduce()
                        self.setState(State.BETWEEN_DOCS)
                        self.adjustRelativePath(fileName)
                        self.parse(included)
                        logger.debug("********************* Path:{0} Back from include '{1}'".format(repr(self.path), included))
                        self.adjustStateFromTop()
                    elif self.path.len() == 2 and self.path.path[1].name ==  "vars":
                        misc.ERROR("'vars' entry must be a map!")       # Detect case where there is a vars: block without any entry. In such case, this is interpreted as a scalar and hide others variables
                    else:
                        self.path.reduce()
                        self.adjustStateFromTop()
                else:
                    self.invalidEventError(event)
            elif isinstance(event, yaml.events.AliasEvent):
                logger.debug("--- AliasEvent:"+ str(event))
                logger.debug("Path:'{0}'".format(repr(self.path)))
                if event.anchor not in self.anchors:
                    misc.ERROR("Alias &{0} not found ({1})".format(event.anchor, event.start_mark ))
                else:
                    self.path.reduceWithAliasMap(self.anchors[event.anchor])
                    self.adjustStateFromTop()
            elif isinstance(event, yaml.events.DocumentEndEvent):
                logger.debug("--- DocumentEndEvent")
                pass
            elif isinstance(event, yaml.events.StreamEndEvent):
                logger.debug("--- StreamEndEvent")
                pass
            else:
                raise Exception("Unknown event:" + repr(event))
        
        logger.debug("End or parsing: Anchors:{0}".format(str(self.anchors)))
        # Adjust some environment variable, as they are relative to source file path
        self.adjustRelativePath(fileName)

    def adjustRelativePath(self, fileName):
        if fileName != None:
            base = os.path.dirname(os.path.abspath(fileName))
            self.context.model[SRC] = self.getResult()
            for plugin in self.context.plugins:
                plugin.onNewSnippet(base)
        
        
    def getResult(self):
        return self.path.top().object



    def setScalar(self, event):
        logger.debug("setScalar({0}) start_mark:{1}  end_mark:{2}  style:{3}".format(event, event.start_mark, event.end_mark, event.style))
        value = event.value
        if '{' in value:
            thevars = self.vars
            #logger.debug("*********Will pass '{0}' through jinja2 with {1}".format(value, str(thevars)))
            try:
                value = jinja2.Template(value, 
                    undefined=jinja2.StrictUndefined,
                    trim_blocks = True,
                    block_start_string="%{",
                    block_end_string="}",
                    variable_start_string="${",
                    variable_end_string="}",
                    comment_start_string="#{",
                    comment_end_string="}"
                ).render(thevars)
            except Exception as e:
                misc.ERROR("{0} {1} (path:{2})".format(str(e), event.start_mark, str(self.path)))
            ##logger.debug("*********Result is {0}".format(value))
        if '>>' in value:
            thevars = self.vars
            #logger.debug("*********Will pass '{0}' through jinja2 with {1}".format(value, str(thevars)))
            try:
                value = jinja2.Template(value, 
                    undefined=jinja2.StrictUndefined,
                    trim_blocks = True,
                    block_start_string="%<",
                    block_end_string=">>",
                    variable_start_string="<<",
                    variable_end_string=">>",
                    comment_start_string="#<",
                    comment_end_string=">>"
                ).render(thevars)
            except Exception as e:
                misc.ERROR("{0} {1} (path:{2})".format(str(e), event.start_mark, str(self.path)))
            ##logger.debug("*********Result is {0}".format(value))
        value = value.encode('utf8')
        if event.style == u'"' or event.style == u'\'':
            return value
        else:
            try:
                return int(value)
            except:
                try:
                    return float(value)
                except:
                    if trueRegex.match(value):
                        return True
                    elif falseRegex.match(value):
                        return False
                    else:
                        return value
                    
                    
    def register(self, fileName):
        if self.fileByVariable != None:
            if self.path.len() == 3 and self.path.path[1].name ==  "vars":
                #print("{}: {}".format(self.path.top().name, os.path.relpath(fileName)))
                self.fileByVariable[self.path.top().name] = os.path.relpath(fileName)
            
