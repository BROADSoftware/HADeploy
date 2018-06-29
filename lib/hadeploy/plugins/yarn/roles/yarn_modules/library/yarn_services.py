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
module: yarn_services
short_description: Manage long running yarn jobs status. 
description:
     - Allow to fetch yarn jobs status, to wait for up or down state and to kill jobs, based on jobs name.
notes:
    - All operations are performed using Ressource Manager web REST API 
    - This module is intended to manage a list of jobs as a whole.
requirements: [ ]
author: 
    - "Serge ALEXANDRE"
options:
  names:
    description:
      - 'A comma separated list of job names to control'
    required: true
    default: None
  state:
    description:
      - 'target job state: C(RUNNING), C(killed), C(nonexistent), C(existing), C(get)'
      - 'C(RUNNING): Wait for all jobs to be in RUNNING state. Also, can exit on timeout, or when detecting a failing job.'
      - 'C(killed): Issue a kill command if yarn job is RUNNING (or starting). If not, or already in C(killed) state, do nothing. Exit immediately.' 
      - 'C(nonexistent): Wait for all jobs to be not RUNNING.' 
      - 'C(get): Do nothing. Return current jobs status' 
    required: true
    default: None
  kerberos:
    description:
      - 'Boolean. Storm UI access require kerberos authentication'
    required: false
    default: false
  timeout:
    description:
      - 'Timeout value when waiting a target state' 
    required: false
    default: 120
  hadoop_conf_dir:
    description:
      - Where to find Hadoop configuration file, specially yarn-site.xml, 
        in order to lookup ressource manager web endpoint (C(yarn.resourcemanager.webapp.address[.rm1|.rm2]))
        Used only if rm_endpoints is not defined
    required: false
    default: "/etc/hadoop/conf"
  rm_endpoint:
    description:
      - Provide Yarn REST API entry point. Typically C(<namenodeHost>:8088). 
        It could also be a comma separated list of entry point, which will be checked up to a valid one. This will allow resource manager H.A. handling. 
        If not defined, will be looked up in local yarn-site.xml
    required: false
    default: None
'''

EXAMPLES = '''
'''

import time
from sets import Set as XSet
from xml.dom import minidom
import copy
import traceback

HAS_REQUESTS = False

try:
    import requests
    HAS_REQUESTS = True
except ImportError, AttributeError:
    # AttributeError if __version__ is not present
    pass

HAS_KERBEROS = False
try:
    from requests_kerberos import HTTPKerberosAuth
    HAS_KERBEROS = True
except ImportError:
    pass


# Global, to allow access from error
module = None
logs = []
logLevel = 'None'

       
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

class YarnState:
    NEW="NEW" 
    NEW_SAVING="NEW_SAVING" 
    SUBMITTED="SUBMITTED" 
    ACCEPTED="ACCEPTED" 
    RUNNING="RUNNING" 
    FINISHED="FINISHED" 
    FAILED="FAILED" 
    KILLED="KILLED" 

# Used both in parameters and result
class State:
    STARTING="starting"
    RUNNING="RUNNING"
    NONEXISTENT="nonexistent"
    KILLED="killed"
    GET="get"

startingSet = XSet([YarnState.NEW, YarnState.NEW_SAVING, YarnState.SUBMITTED, YarnState.ACCEPTED])
doneSet = XSet([YarnState.FINISHED, YarnState.FAILED, YarnState.KILLED])

class Errno:
    OK=0
    TIMEOUT=1
    ERROR=2
                            
class YarnAPI:
    
    def __init__(self, endpoint, kerberos):
        if endpoint.endswith("/"):
            self.endpoint = endpoint[:-1]
        else:
            self.endpoint = endpoint
        if not self.endpoint.startswith("http"):
            self.endpoint = "http://" + self.endpoint
        if kerberos:
            if not HAS_KERBEROS:
                error("'python-requests-kerberos' package is not installed while Kerberos is activated")
            else:
                self.kerberos_auth = HTTPKerberosAuth()
                self.kerberos = True
        else:
            self.kerberos_auth = None
            self.kerberos = False
            
    def test(self):
        try:
            url = self.endpoint + "/ws/v1/cluster/apps?states=RUNNING"
            resp = requests.get(url)
            if resp.status_code == 200:
                return (True, "")
            elif resp.status_code == 401:
                if self.kerberos:
                    return (False, "{0}  =>  Response code: {1} (May be you need to perform 'kinit' on the remote host)".format(url, resp.status_code))
                else:
                    return (False, "{0}  =>  Response code: {1} (May be KERBEROS authentication must be used)".format(url, resp.status_code))
            else: 
                return (False, "{0}  =>  Response code: {1}".format(url, resp.status_code))
        except Exception as e:
            if self.kerberos:
                return (False, "{0}  =>  Error: {1}. Are you sure this cluster is secured by Kerberos ?".format(url, str(e)))
            else:
                return (False, "{0}  =>  Error: {1}".format(url, str(e)))
            
    
    def get(self, path):
        url = self.endpoint + path
        resp = requests.get(url, auth=self.kerberos_auth)
        if resp.status_code == 200:
            result = resp.json()
            debug("GET on '{}' => {}".format(url, result))
            return result
        else:
            error("Invalid returned http code '{0}' when calling GET on '{1}'".format(resp.status_code, url))
  
    def initStatus(self, names):
        status = {}
        for name in names:
            status[name] = {}
            status[name]["state"] = State.NONEXISTENT
            status[name]["ids"] = {}
        return status
                        
                            
    def updateStatus(self, status):
        body = self.get("/ws/v1/cluster/apps?states=NEW,NEW_SAVING,SUBMITTED,ACCEPTED,RUNNING")
        activeYarnApps = XSet()
        if "apps" in body and body["apps"] != None and "app" in body["apps"]:
            for yarnApp in body["apps"]["app"]:
                activeYarnApps.add(yarnApp["name"])
                if yarnApp["name"] in status:
                    app = status[yarnApp["name"]]
                    if yarnApp["state"] in startingSet:
                        # Found an instance in "starting" state. 
                        if app["state"] == State.NONEXISTENT:
                            app["state"] = State.STARTING
                        app["ids"][yarnApp["id"]] = yarnApp["state"]
                    elif yarnApp["state"] == YarnState.RUNNING:
                        app["state"] = State.RUNNING
                        app["ids"][yarnApp["id"]] = yarnApp["state"]
                    else:
                        error("Unknown Yarn State:{}".format(yarnApp["state"]))
        for appName in status:
            if appName not in activeYarnApps:
                if status[appName]["state"] != State.NONEXISTENT:
                    status[appName]["state"] = State.KILLED
                    status[appName]["ids"] = {}
        return status
                        
    def kill(self, appId):
        url = "{}/ws/v1/cluster/apps/{}/state".format(self.endpoint, appId)
        state = { "state": "KILLED" }
        resp = requests.put(url, json=state, headers={'content-type': 'application/json'}, auth=self.kerberos_auth)
        debug("HTTP PUT({})  --> {}".format(url, resp.status_code))        
        if resp.status_code < 200 or resp.status_code > 299: 
            error("Invalid returned http code '{0}' when calling PUT on '{1}': {2}".format(resp.status_code, url, resp.text))
    
    def killAll(self, names, p):
        status = self.initStatus(names)
        self.updateStatus(status)
        before = copy.deepcopy(status)
        #pprint(status)
        for _, app in status.iteritems():
            for appId in app["ids"]:
                self.kill(appId)
                p.changed = True
        self.updateStatus(status)
        return (Errno.OK, before, status)
        
    def waitUndefined(self, names, timeout):
        startTime = time.time()
        status = self.initStatus(names)
        self.updateStatus(status)
        before = copy.deepcopy(status)
        while True:
            stillRunning = False 
            #pprint(status)
            print
            for _, app in status.iteritems():
                if app["state"] != State.NONEXISTENT and app["state"] != State.KILLED:
                    stillRunning = True 
            if time.time() > startTime + timeout:
                debug("waitUndefined({}, {}) exited on timeout!".format(names, timeout))
                return(Errno.TIMEOUT, before, status) 
            if stillRunning:
                time.sleep(0.5)
                self.updateStatus(status)
            else:
                return(Errno.OK, before, status) 
            
    def waitRunning(self, names, timeout):
        startTime = time.time()
        status = self.initStatus(names)
        self.updateStatus(status)
        before = copy.deepcopy(status)
        while True:
            stillStarting = False 
            #pprint(status)
            print
            for name, app in status.iteritems():
                if app["state"] == State.NONEXISTENT or app["state"] == State.STARTING:
                    stillStarting = True 
                if app["state"] == State.KILLED:
                    debug("waitRunning({}, {}) -> Application {}[{}] failed to start!".format(names, timeout, name, app["ids"]))
                    return(Errno.ERROR, before, status) 
            if time.time() > startTime + timeout:
                debug("waitUndefined({}, {}) exited on timeout!".format(names, timeout))
                return(Errno.TIMEOUT, before, status) 
            if stillStarting:
                time.sleep(0.5)
                self.updateStatus(status)
            else:
                return(Errno.OK, before, status) 
            
          
def lookupYarnApi(p):                
    if p.rmEndpoint == None:
        if not os.path.isdir(p.hadoopConfDir):
            error("{0} must be an existing folder, or hadoop_conf_dir  or rm_endpoint provided as parameter.".format(p.hadoopConfDir))
        candidates = []
        hspath = os.path.join(p.hadoopConfDir, "yarn-site.xml")
        if os.path.isfile(hspath):
            doc = minidom.parse(hspath)
            properties = doc.getElementsByTagName("property")
            for prop in properties :
                name = prop.getElementsByTagName("name")[0].childNodes[0].data
                if name.startswith("yarn.resourcemanager.webapp.address") :
                    candidates.append(prop.getElementsByTagName("value")[0].childNodes[0].data)
            if not candidates:
                error("Unable to find yarn.resourcemanager.webapp.address* in yarn-site.yml. Provide explicit 'rm_endpoint'")
            errors = []
            for endpoint in candidates:
                yarnAPI= YarnAPI(endpoint, p.kerberos)
                (x, err) = yarnAPI.test()
                if x:
                    p.rmEndpoint = yarnAPI.endpoint
                    return yarnAPI
                else:
                    errors.append(err)
            error("Unable to find a valid 'rm_endpoint' in yarn-site.xml:" + str(errors))
        else:
            error("Unable to find file {0}. Provide 'rm_endpoint' or 'hadoop_conf_dir' parameter".format(hspath))
    else:
        candidates = p.rmEndpoint.split(",")
        errors = []
        for endpoint in candidates:
            yarnAPI= YarnAPI(endpoint, p.kerberos)
            (x, err) = yarnAPI.test()
            if x:
                p.rmEndpoint = yarnAPI.endpoint
                return yarnAPI
            else:
                errors.append(err)
        error("Unable to find a valid 'rm_endpoint' in: " + p.rmEndpoint + " (" + str(errors) + ")")


            
def main():
    
    global module
    module = AnsibleModule(
        argument_spec = dict(
            names = dict(required=True),
            state = dict(required=True, choices=['RUNNING','killed','nonexistent','get']),
            kerberos = dict(required=False, type='bool', default=False),
            timeout = dict(required=False, type='int', default=120),
            hadoop_conf_dir = dict(required=False, default="/etc/hadoop/conf"),
            rm_endpoint = dict(required=False, default=None),
            log_level = dict(required=False, default="None")
        ),
        supports_check_mode=True
    )
    
    if not HAS_REQUESTS:
        error(msg="python-requests package is not installed")    
    
    p = Parameters()
    p.names = module.params['names']
    p.state = module.params['state']
    p.kerberos = module.params['kerberos']
    p.timeout = module.params['timeout']
    p.hadoopConfDir = module.params['hadoop_conf_dir']
    p.rmEndpoint = module.params['rm_endpoint']
    p.logLevel = module.params['log_level']
    p.checkMode = module.check_mode
    p.changed = False
    
    global  logLevel
    logLevel = p.logLevel
    
    yarnAPI = lookupYarnApi(p)
    
    names = p.names.split(",")
    
    debug("yarn_service: Debug enabled")
    
    try:
        if p.state == State.GET:
            status = yarnAPI.initStatus(names)
            yarnAPI.updateStatus(status)
            module.exit_json(changed=p.changed, status=status, logs=logs)
        elif p.state == State.KILLED:
            (errno, before, after) = yarnAPI.killAll(names, p)
            module.exit_json(changed=p.changed, status_before=before, logs=logs)    # After is not returned as may be confusing (Jobs are still running right after)
        elif p.state == State.NONEXISTENT:
            (errno, before, after) = yarnAPI.waitUndefined(names, p.timeout)
            if errno == Errno.OK:
                module.exit_json(changed=p.changed, status_before=before, status_after=after, logs=logs)
            else:
                module.fail_json(msg = "waitNonexistent() exit on timeout!", status_before=before, status_after=after, logs=logs)
        elif p.state == State.RUNNING:
            (errno, before, after) = yarnAPI.waitRunning(names, p.timeout)
            if errno == Errno.OK:
                module.exit_json(changed=p.changed, status_before=before, status_after=after, logs=logs)
            elif errno == Errno.TIMEOUT:
                module.fail_json(msg = "waitRunning() exit on timeout!", status_before=before, status_after=after, logs=logs)
            else:
                module.fail_json(msg = "waitRunning(): A least one og the jobs failed to start", status_before=before, status_after=after, logs=logs)
        else:
            error("Unknown state '{}'".format(p.state))
    except Exception as e:  # Do not trap BaseException, as it seems module.exit_json() throw some
        module.fail_json(msg = "Unexpected error: {}  {}".format(e, traceback.format_exc()), logs=logs)
    

from ansible.module_utils.basic import *
if __name__ == '__main__':
    main()

    
