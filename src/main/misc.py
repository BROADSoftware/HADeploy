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


