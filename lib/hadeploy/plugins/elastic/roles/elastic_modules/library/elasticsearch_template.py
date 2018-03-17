#!/usr/bin/python
# -*- coding: utf-8 -*-

# (c) 2018, BROADSoftware
#
# This software is free software: you can redistribute it and/or modify
# it under the terms of the GNU General Public License as published by
# the Free Software Foundation, either version 3 of the License, or
# (at your option) any later version.
#
# This software is distributed in the hope that it will be useful,
# but WITHOUT ANY WARRANTY; without even the implied warranty of
# MERCHANTABILITY or FITNESS FOR A PARTICULAR PURPOSE.  See the
# GNU General Public License for more details.
#
# You should have received a copy of the GNU General Public License
# along with this software. If not, see <http://www.gnu.org/licenses/>.




DOCUMENTATION = '''
---
module: elasticsearch_template
short_description: Manage elasticsearch index templates
description:
     - Allow to create ES templates in an idempotent way.
notes:
    - All operations are performed using elasticsearch REST API 
requirements: [ ]
author: 
    - "Serge ALEXANDRE"
options:
  name:
    description:
      - 'Template name'
    required: true
    default: None
  elasticsearch_url:
    description:
      - The Elasticsearch server base URL to access API. Typically http://elastic1.myserver.com:9200  
    required: true
    default: None
  definition:
    description:
      - Template definition as a json string or as a YAML definition
    required: true
    default: None
  state:
    description:
      - Whether to create (present) or remove (absent) this template. Also accept 'get' value, which return the template definition
    required: false
    default: present
    choices: [ present, absent, get ]

'''

EXAMPLES = '''


- hosts: elastic1
  roles:
  - elastic_modules
  tasks:
  - name: Create template
    elasticsearch_template:
      name: tmpl1
      elasticsearch_url: "http://elastic1.mydomain.com:9200"
      definition: |
        {
          "index_patterns": ["xte*", "bar*"],
          "settings": {    
            "index": {
                "number_of_shards": 1
            }
          },
          "mappings": {
            "type1": {
              "_source": {
                "enabled": false
              },
              "properties": {
                "host_name": {
                  "type": "keyword"
                },
                "created_at": {
                  "type": "date",
                  "format": "EEE MMM dd HH:mm:ss Z YYYY"
                }
              }
            }
          }
        }      
      state: present

# One can also use a pure YAML notation. 

  - name: Create template
    elasticsearch_template:
      name: tmpl1
      elasticsearch_url: "http://elastic1.mydomain.com:9200"
      definition:
        index_patterns: 
        - "xte*"
        - "bar*"
        settings:
          index:
            number_of_shards: 1
        mappings:
          type1:
            _source:
              enabled: False
            properties:
              host_name:
                type: keyword
              created_at:
                type: date
                format: "EEE MMM dd HH:mm:ss Z YYYY"
      state: present
    

'''

import json 
import pprint
import ansible.module_utils.six as six



HAS_REQUESTS = False

try:
    import requests
    HAS_REQUESTS = True
except ImportError, AttributeError:
    # AttributeError if __version__ is not present
    pass


# Global, to allow access from error
module = None
logs = []
logLevel = 'None'

pp = pprint.PrettyPrinter(indent=2)

    
def log(level, message):
    logs.append(level + ':' + message)
        
def debug(message):
    if logLevel == 'debug' or logLevel == "info":
        log("DEBUG", message)

def info(message):
    if logLevel == "info" :
        log("INFO", message)

def error(message):
    module.fail_json(msg = message, logs=logs)    



class Parameters:
    pass


def diffDefinition(target, current, missing=None):
    """ Lookup missing values of 'target' object in 'current' object.
    Add all missing stuff in a returned 'missing' object
    """
    if missing is None: # See http://effbot.org/zone/default-values.htm for explaination
        missing = {}
    for key in target:
        targetObj = target[key]
        if key in current:
            currentObj = current[key]
            if isinstance(targetObj, str) or isinstance(targetObj, unicode) or isinstance(targetObj, int) or isinstance(targetObj, long) or isinstance(targetObj, float):
                if str(targetObj) == str(currentObj):
                    return missing # Normally, not used, as only called in recursing
                else:
                    missing[key] = targetObj
            elif isinstance(targetObj, list):
                if isinstance(currentObj, list):
                    missingItems = []
                    currentSet = set(currentObj)
                    for item in targetObj:
                        if not item in currentObj:
                            missingItems.append(item)
                    if len(missingItems) > 0:
                        missing[key] = missingItems
                else:
                    missing[key] = targetObj
            elif isinstance(targetObj, dict):
                if isinstance(currentObj, dict):
                    missing[key] = {}
                    diffDefinition(targetObj, currentObj, missing[key])
                    if len(missing[key]) == 0:
                        del(missing[key])
                else:
                    missing[key] = targetObj
            else:
                missing[key] = targetObj
        else:
            missing[key] = targetObj
    return missing
    


class EsApi:
    
    def __init__(self, endpoint):
        self.endpoint = endpoint
       
    def get(self, path, okStatus=[200], noneStatus=[]):
        url = self.endpoint + path
        resp = requests.get(url)
        debug("HTTP GET({})  --> {}".format(url, resp.status_code))
        if resp.status_code in okStatus:
            result = resp.json()
            return result
        elif resp.status_code in noneStatus:
          return None  
        else:
            error("Invalid returned http code '{0}' when calling GET on '{1}'".format(resp.status_code, url))
            
         
    def put(self, path, json):
        url = self.endpoint + path
        resp = requests.put(url, json=json, headers={'content-type': 'application/json'})
        debug("HTTP PUT({})  --> {}".format(url, resp.status_code))        
        if resp.status_code != 200:
            error("Invalid returned http code '{0}' when calling PUT on '{1}' : {2}\nPAYLOAD:\n{3}".format(resp.status_code, url, resp.text, pp.pformat(json)))
        else:
            result = resp.json()
            return result


    def getTemplate(self, name):
        r = self.get("_template/{}".format(name), noneStatus=[404])
        if r and name in r:
            return r[name]
        else:
            return None
        
    def deleteTemplate(self, name):
        url = self.endpoint + "_template/{}".format(name)
        resp = requests.delete(url)
        debug("HTTP DELETE({})  --> {}".format(url, resp.status_code))        
        if resp.status_code == 200:
            return True
        elif resp.status_code == 404:
            return False
        else:
            error("Invalid returned http code '{0}' when calling DELETE on '{1}: {2}'".format(resp.status_code, url, resp.text))

  
    def createTemplate(self, name, definition):
        existing = self.getTemplate(name)
        if existing == None:
            # Must create it
            self.put("_template/{}".format(name), definition)
            # Will fetch back to ensure all parameters was taken in account
            existing = self.getTemplate(name)
            missing = diffDefinition(definition, existing)
            if len(missing) == 0:
                return True
            else:
                error("Unable to create template '{}'. Would need to handle {}".format(name, missing ))
        else:
            #debug("ALREADY EXIST:\nEXISTING:\n{}\nNEW:\n{}\n".format(pp.pformat(existing), pp.pformat(definition)) )
            missing = diffDefinition(definition, existing)
            if len(missing) == 0:
                return False
            else:
                debug("Recreating template '{}'. Missing/changed values: {}".format(name, missing))
                self.put("_template/{}".format(name), definition)
                existing = self.getTemplate(name)
                missing = diffDefinition(definition, existing)
                if len(missing) == 0:
                    return True
                else:
                    error("Unable to adjust template '{}'. Would need to handle {}".format(name, missing ))

      
      
      
# Possible states                
PRESENT="present"
ABSENT="absent"
GET="get"

            
def main():
    
    global module
    module = AnsibleModule(
        argument_spec = dict(
            name = dict(type='str', required=True),
            elasticsearch_url = dict(type='str', required=True),
            definition = dict(type='raw', required=False),    # Not required if state is not 'present'
            state = dict(type='str', required=False, choices=[PRESENT, ABSENT,GET], default=PRESENT),
            log_level = dict(type='str', required=False, default="None")
            
        ),
        supports_check_mode=True
    )
    
    if not HAS_REQUESTS:
        error(msg="python-requests package is not installed")    
    
    p = Parameters()
    p.name = module.params['name']
    p.elasticsearchUrl = module.params['elasticsearch_url']
    p.definition = module.params['definition']
    p.state = module.params['state']
    p.logLevel = module.params['log_level']
    p.checkMode = module.check_mode
    p.changed = False
    
    
    global  logLevel
    logLevel = p.logLevel
    
    if not p.elasticsearchUrl.endswith("/"):
        p.elasticsearchUrl = p.elasticsearchUrl + "/"

    api = EsApi(p.elasticsearchUrl)
    
    if p.state == ABSENT:
        p.changed = api.deleteTemplate(p.name)
        module.exit_json(changed=p.changed, logs=logs)
    elif p.state == PRESENT:
        if p.definition == None:
            error("'definition' attribute must be provided when state == 'present'")
        # From ansible module.net_tools.basic.uri 
        if not isinstance(p.definition, six.string_types):
            p.definition = json.dumps(p.definition)
        definition = json.loads(p.definition)
        p.changed = api.createTemplate(p.name, definition)
        module.exit_json(changed=p.changed, logs=logs)
    elif p.state == GET:
        definition = api.getTemplate(p.name)
        if definition != None:
            module.exit_json(changed=False, name=p.name, state="present", definition=definition, logs=logs)
        else:
            module.exit_json(changed=False, name=p.name, state="absent", logs=logs)
    else:
        error("Invalid state: '{}'".format(p.state))



from ansible.module_utils.basic import *
if __name__ == '__main__':
    main()

