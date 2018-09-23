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
module: elasticsearch_index
short_description: Manage elasticsearch index
description:
     - Allow to create ES indices in an idempotent way.
notes:
    - All operations are performed using elasticsearch REST API 
requirements: [ ]
author: 
    - "Serge ALEXANDRE"
options:
  name:
    description:
      - 'Index name'
    required: true
    default: None
  elasticsearch_url:
    description:
      - The Elasticsearch server base URL to access API. Typically http://elastic1.myserver.com:9200  
    required: true
    default: None
  username:
    description:
      - The user name to log on the elasticsearch cluster. Must have enough rights to create indices
    required: false
    default: None
    aliases: []
  password:
    description:
      - The password associated with the username
    required: false
    default: None
    aliases: []
  validate_certs:
    description:
      - Useful if elasticsearch connection is using SSL. If no, SSL certificates will not be validated. This should only be used on personally controlled sites using self-signed certificates.
    required: false
    default: True
    aliases: []
  ca_bundle_file:
    description:
      - Useful if elasticsearch connection is using SSL. Allow to specify a CA_BUNDLE file, a file that contains root and intermediate certificates to validate the server certificate.
      - In its simplest case, it could be a file containing the server certificate in .pem format.
      - This file will be looked up on the remote system, on which this module will be executed. 
    required: false
    default: None
    aliases: []
  definition:
    description:
      - Index definition as a json string or as a YAML definition
    required: true
    default: None
  state:
    description:
      - Whether to create (present) or remove (absent) this index. Also accept 'get' value, which return index definition
    required: false
    default: present
    choices: [ present, absent, get ]
'''

EXAMPLES = '''

- hosts: elastic1
  roles:
  - elastic_modules
  tasks:
  - name: Create index
    elasticsearch_index:
      name: index1
      elasticsearch_url: "http://elastic1.mydomain.com:9200"
      definition: |
        {
            "settings" : {
                "index": {
                    "number_of_shards" : 1
                }
            },
            "mappings" : {
                "type1" : {
                    "properties" : {
                        "field1" : { "type" : "text" }
                    }
                }
            }
        }
      state: present

# One can also use a pure YAML notation. 

  - name: Create index
    elasticsearch_index:
      name: test1
      elasticsearch_url: "http://elastic1.mydomain.com:9200"
      definition:
        settings:
          index:
            number_of_shards: 1
        mappings:
          type1:
            properties:
              field1:
                type: text
      state: present
   
      

'''

import json 
import pprint
import ansible.module_utils.six as six



HAS_REQUESTS = False

try:
    import requests
    from requests.auth import HTTPBasicAuth
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
    

# Some token in index definition which are of interest 
SETTINGS="settings"
MAPPINGS="mappings"

class EsApi:
    
    def __init__(self, endpoint, username, password, verify):
        self.endpoint = endpoint
        self.username = username
        self.password = password
        self.verify = verify
        self.auth = HTTPBasicAuth(self.username, self.password)
        
       
    def get(self, path, okStatus=[200], noneStatus=[]):
        url = self.endpoint + path
        resp = requests.get(url, auth = self.auth, verify = self.verify)
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
        resp = requests.put(url, json=json, headers={'content-type': 'application/json'}, auth = self.auth, verify = self.verify)
        debug("HTTP PUT({})  --> {}".format(url, resp.status_code))        
        if resp.status_code != 200:
            error("Invalid returned http code '{0}' when calling PUT on '{1}' : {2}\nPAYLOAD:\n{3}".format(resp.status_code, url, resp.text, pp.pformat(json)))
        else:
            result = resp.json()
            return result

    def getIndex(self ,name):
        r = self.get(name, noneStatus=[404])
        if r and name in r:
            return r[name]
        else:
            return None

    def deleteIndex(self, name):
        url = self.endpoint + name
        resp = requests.delete(url, auth = self.auth, verify = self.verify)
        debug("HTTP DELETE({})  --> {}".format(url, resp.status_code))        
        if resp.status_code == 200:
            return True
        elif resp.status_code == 404:
            return False
        else:
            error("Invalid returned http code '{0}' when calling DELETE on '{1}: {2}'".format(resp.status_code, url, resp.text))

    def updateIndexSetting(self, indexName, settings):
        r = self.put("{}/_settings".format(indexName), settings)
        return r
        
    def setMapping(self, indexName, typeName, mappings):
        r = self.put("{}/_mapping/{}".format(indexName, typeName), mappings)
        return r
        
        
    def createIndex(self, name, definition):
        existing = self.getIndex(name)
        if existing == None:
            # Must create it
            r2 = self.put(name, definition)
            # Will fetch back to ensure all parameters was taken in account
            existing = self.getIndex(name)
            missing = diffDefinition(definition, existing)
            if len(missing) == 0:
                return True
            else:
                error("Unable to create index '{}'. Would need to handle {}".format(name, missing ))
        else:
            #debug("ALREADY EXIST:\nEXISTING:\n{}\nNEW:\n{}\n".format(pp.pformat(existing), pp.pformat(definition)) )
            missing = diffDefinition(definition, existing)
            if len(missing) == 0:
                return False
            else:
                # Check if we have a chance to being able to modify
                debug("Adjusting index '{}'. Missing/changed values: {}".format(name, missing))
                for key in missing:
                    if key != SETTINGS and key != MAPPINGS:
                        error("Unable to modify index '{}' definition. Changing attribute '{}' is not supported".format(name, key))
                if SETTINGS in missing:
                    self.updateIndexSetting(name, missing[SETTINGS])
                if MAPPINGS in missing:
                    for key in missing[MAPPINGS]:
                        self.setMapping(name, key, missing[MAPPINGS][key])
                # Now, after potential adjustment, check again
                existing = self.getIndex(name)
                #debug("FINAL CHECK:\nEXISTING:\n{}\nNEW:\n{}\n".format(pp.pformat(existing), pp.pformat(definition)) )
                missing = diffDefinition(definition, existing)
                if len(missing) == 0:
                    return True
                else:
                    error("Unable to adjust index '{}'. Would need to handle {}".format(name, missing ))
      
      
      
      
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
            username = dict(required=False, type='str'),
            password = dict(required=False, type='str'),
            validate_certs = dict(required=False, type='bool', default=True),
            ca_bundle_file = dict(required=False, type='str'),
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
    p.username = module.params['username']
    p.password = module.params['password']
    p.validateCerts = module.params['validate_certs']
    p.ca_bundleFile = module.params['ca_bundle_file']
    p.definition = module.params['definition']
    p.state = module.params['state']
    p.logLevel = module.params['log_level']
    p.checkMode = module.check_mode
    p.changed = False
    
    
    global  logLevel
    logLevel = p.logLevel
    
    if not p.elasticsearchUrl.endswith("/"):
        p.elasticsearchUrl = p.elasticsearchUrl + "/"
        
    if (p.username != None) != (p.password != None):
        error("'username' and 'password' must be defined both or not at all")
    
    if p.ca_bundleFile != None:
        verify = p.ca_bundleFile
    else:
        verify = p.validateCerts

    api = EsApi(p.elasticsearchUrl, p.username, p.password, verify)
    
    if p.state == ABSENT:
        p.changed = api.deleteIndex(p.name)
        module.exit_json(changed=p.changed, logs=logs)
    elif p.state == PRESENT:
        if p.definition == None:
            error("'definition' attribute must be provided when state == 'present'")
        # From ansible module.net_tools.basic.uri 
        if not isinstance(p.definition, six.string_types):
            p.definition = json.dumps(p.definition)
        definition = json.loads(p.definition)
        p.changed = api.createIndex(p.name, definition)
        module.exit_json(changed=p.changed, logs=logs)
    elif p.state == GET:
        definition = api.getIndex(p.name)
        if definition != None:
            module.exit_json(changed=False, name=p.name, state="present", definition=definition, logs=logs)
        else:
            module.exit_json(changed=False, name=p.name, state="absent", logs=logs)
    else:
        error("Invalid state: '{}'".format(p.state))



from ansible.module_utils.basic import *
if __name__ == '__main__':
    main()

