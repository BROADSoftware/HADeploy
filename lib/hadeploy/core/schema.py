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
import misc
from pykwalify.core import Core as kwalify


"""
From http://stackoverflow.com/questions/7204805/dictionaries-of-dictionaries-merge
Modified for mergin sequence, which are only one elements. So, must merge inner (mapping) items
"""
class YamlReaderError(Exception):
    pass

def schemaMerge(a, b):
    """merges b into a and return merged result

    NOTE: tuples and arbitrary objects are not handled as it is totally ambiguous what should happen"""
    key = None
    # ## debug output
    # sys.stderr.write("DEBUG: %s to %s\n" %(b,a))
    try:
        if a is None or isinstance(a, str) or isinstance(a, unicode) or isinstance(a, int) or isinstance(a, long) or isinstance(a, float):
            # border case for first run or if a is a primitive
            a = b
        elif isinstance(a, list):
            # lists can be only appended
            if isinstance(b, list):
                # merge lists
                #a.extend(b)
                # Specific to kwalify schema description: Sequence are alwoys on item.
                schemaMerge(a[0], b[0]) 
            else:
                # append to list
                a.append(b)
        elif isinstance(a, dict):
            # dicts must be merged
            if isinstance(b, dict):
                for key in b:
                    if key in a:
                        a[key] = schemaMerge(a[key], b[key])
                    else:
                        a[key] = b[key]
            else:
                raise YamlReaderError('Cannot merge non-dict "%s" into dict "%s"' % (b, a))
        else:
            raise YamlReaderError('NOT IMPLEMENTED "%s" into "%s"' % (b, a))
    except TypeError, e:
        raise YamlReaderError('TypeError "%s" in key "%s" when merging "%s" into "%s"' % (e, key, b, a))
    return a





def validate(model, schema):
    k = kwalify(source_data = model, schema_data=schema)
    try:
        k.validate(raise_exception=False)
        if len(k.errors) != 0:
            misc.ERROR("Problem {0}".format(k.errors))
    except Exception as e:          # Need to catch, as, despite raise_exeception=False, some cases still generate exception (ie map/list mismatch)
        misc.ERROR("Problem {0}".format(e))
    
