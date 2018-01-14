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

import pprint
import os
import errno


prettyPrinter = pprint.PrettyPrinter(indent=2)

def pprint(obj):
    prettyPrinter.pprint(obj)
                

def ERROR(err):
    if type(err) is str:
        message = err
    else:
        message = err.__class__.__name__ + ": " + str(err)
    print "* * * * ERROR: " + str(message)
    #raise Exception("xx")
    exit(1)



def ensureFolder(path):
    try:
        os.makedirs(path)
    except OSError as exception:
        if exception.errno != errno.EEXIST:
            raise
        else:
            pass
                
def ensureObjectInMaps(root, keys, defaultObj):
    for key in keys[:-1]:
        if not key in root:
            root[key] = {}
        root = root[key]
    key = keys[-1:][0]
    if not key in root:
        root[key] = defaultObj

def setDefaultInMap(root, key, defaultValue):
    if not key in root:
        root[key] = defaultValue
         
def snippetRelocate(snippetPath, varPath):
    if os.path.isabs(varPath):
        return varPath
    elif varPath.startswith("~"):
        return os.path.expanduser(varPath)
    else:
        return os.path.normpath(os.path.join(snippetPath,varPath))




WHEN="when"

#def removeOnNotWhen(l):
#    l2 = []
#    for item in l:
#        setDefaultInMap(item, WHEN, True)
#        if item[WHEN]:
#            l2.append(item)
#    return l2

#def checkWhen(o):
#    setDefaultInMap(o, WHEN, True)
#    return o[WHEN]
                   
def applyWhenOnSingle(root, token):
    if token in root:
        setDefaultInMap(root[token], WHEN, True)
        if not root[token][WHEN]:
            del root[token]

def applyWhenOnList(root, token):
    if token in root:
        l2 = []
        for item in root[token]:
            setDefaultInMap(item, WHEN, True)
            if item[WHEN]:
                l2.append(item)
        root[token] = l2
        
        
