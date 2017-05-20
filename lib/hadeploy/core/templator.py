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

import jinja2
import logging
import yaml

logger = logging.getLogger("hadeploy.Templator")


def to_nice_yaml(a, **kw):
    '''Make verbose, human readable yaml'''
    #transformed = yaml.dump(a, Dumper=AnsibleDumper, indent=4, allow_unicode=True, default_flow_style=False, **kw)
    #return to_unicode(transformed)
    #return yaml.dump(a, width=120, default_flow_style=False,  canonical=False, default_style='"', tags=False, **kw)
    return yaml.dump(a, width=10240,  indent=4, allow_unicode=True, default_flow_style=False, **kw)


def to_yaml(a, **kw):
    '''Make yaml'''
    #transformed = yaml.dump(a, Dumper=AnsibleDumper, indent=4, allow_unicode=True, default_flow_style=False, **kw)
    #return to_unicode(transformed)
    #return yaml.dump(a, width=120, default_flow_style=False,  canonical=False, default_style='"', tags=False, **kw)
    #return yaml.dump(a, width=10240,  indent=2, allow_unicode=True, default_flow_style=True, **kw)
    return yaml.dump(a)



class Templator():

    def __init__(self, templatePaths, model):
        self.model = model
        self.env = jinja2.Environment(
            loader = jinja2.FileSystemLoader(templatePaths), 
            undefined = jinja2.StrictUndefined, 
            trim_blocks = True,
            block_start_string="{{%",
            block_end_string="%}}",
            variable_start_string="{{{",
            variable_end_string="}}}",
            comment_start_string="{{#",
            comment_end_string="#}}"
        )
        self.env.filters['to_nice_yaml'] = to_nice_yaml
        self.env.filters['to_yaml'] = to_yaml
   
        

    def generate(self, tmplName, targetFileName):
        tmpl = self.env.get_template(tmplName)
        logger.debug("Will generate '{0}'".format(targetFileName))
        f = open(targetFileName, 'w')
        x = tmpl.render(self.model)
        f.write(x)
        f.close()
