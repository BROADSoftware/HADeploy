#!/usr/bin/python
# -*- coding: utf-8 -*-

# (c) 2015, BROADSoftware
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


from xml.dom import minidom

DOCUMENTATION = '''
---
module: hdfs_info
version_added: "historical"
short_description: Grab information about an HDFS file or folder
description:
     - Allow testing of file/folder existence. And retrieve owner, group and mode of an existing file/folder on HDFS.
notes:
    - As HDFS is a distributed file system shared by all nodes of a cluster, 
      this module must be launched on one node only. Note there is no 
      protection against race condition (Same operation performed simultaneously
      from several nodes).
    - All HDFS operations are performed using WebHDFS REST API. 
requirements: [ ]
author: 
    - "Serge ALEXANDRE"
options:
  hdfs_path:
    description:
      - 'HDFS path to the file being managed.  Aliases: I(dest), I(name)'
    required: true
    default: None
  hadoop_conf_dir:
    description:
      - Where to find Haddop configuration file, specially hdfs-site.xml, 
        in order to lookup WebHDFS endpoint (C(dfs.namenode.http-address))
        Used only if webhdfs_endpoint is not defined
    required: false
    default: "/etc/hadoop/conf"
  webhdfs_endpoint:
    description:
      - Provide WebHDFS REST API entry point. Typically C(<namenodeHost>:50070). 
        It could also be a comma separated list of entry point, which will be checked up to a valid one. This will allow Namenode H.A. handling. 
        If not defined, will be looked up in local hdfs-site.xml
    required: false
    default: None
  hdfs_user:
    description: 
    - Define account to impersonate to perform required operation on HDFS through WebHDFS.
    - Also accepts the special value C(KERBEROS). In such case, a valid Kerberos ticket must exist for the ansible_user account. (A C(kinit) must be issued under this account). 
      Then HDFS operation will be performed on behalf of the user defined by the Kerberos ticket.
    required: false
    default: "hdfs"
author: 
    - Serge ALEXANDRE
    
    
'''

EXAMPLES = '''



'''
RETURN = '''
hdfs_path:
    description: file/path to grab info from
    returned: always
    type: string
    sample: "/path/to/file.txt"
exits:
    description: If the path exists
    returned: always
    type: boolean
    sample: True
type:
    description: 'file', 'directory' or 'absent'
    returned: always
    type: string
    sample: "directory"
owner:
    description: Owner of the file or directory
    returned: if exists
    type: string
    sample: "joe"
group:
    description: Group of the file or directory
    returned: if exists
    type: string
    sample: "users"
mode:
    description: Permission of the file or directory
    returned: if exists
    type: string
    sample: "0755"
int_mode:
    description: Permission of the file or directory
    returned: if exists
    type: int
    sample: 493
size:
    description: Size of the file
    returned: always
    type: integer
    sample: 2354
modificationTime:
    description: Last modification time, in second since Epoch
    returned: always
    type: integer
    sample: 1483097882
'''

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

class WebHDFS:
      
    def __init__(self, endpoint, hdfsUser):
        self.endpoint = endpoint
        self.delegationToken = None
        self.auth = None
        if hdfsUser == "KERBEROS":
            self.kerberos = True
            if not HAS_KERBEROS:
                error("'python-requests-kerberos' package is not installed")
        else :
            self.kerberos = False
            self.auth = "user.name=" + hdfsUser + "&"
        
         
    def test(self):
        try:
            if self.kerberos:
                kerberos_auth = HTTPKerberosAuth()
                url = "http://{0}/webhdfs/v1/?op=GETDELEGATIONTOKEN".format(self.endpoint)
                resp = requests.get(url, auth=kerberos_auth)
                if resp.status_code == 200:
                    result = resp.json()
                    self.delegationToken = result['Token']['urlString']
                    self.auth = "delegation=" + self.delegationToken + "&"
                    return (True, "")
                elif resp.status_code == 401:
                    return (False, "{0}  =>  Response code: {1} (May be you need to perform 'kinit' on the remote host)".format(url, resp.status_code))
                else: 
                    return (False, "{0}  =>  Response code: {1}".format(url, resp.status_code))
            else:
                url = "http://{0}/webhdfs/v1/?{1}op=GETFILESTATUS".format(self.endpoint, self.auth)
                resp = requests.get(url)
                if resp.status_code == 200:
                    return (True, "")
                elif resp.status_code == 401:
                    return (False, "{0}  =>  Response code: {1} (May be KERBEROS authentication must be used)".format(url, resp.status_code))
                else: 
                    return (False, "{0}  =>  Response code: {1}".format(url, resp.status_code))
        except Exception as e:
            if self.kerberos:
                return (False, "{0}  =>  Error: {1}. Are you sure this cluster is secured by Kerberos ?".format(url, str(e)))
            else:
                return (False, "{0}  =>  Error: {1}".format(url, str(e)))


    def close(self):
        if self.kerberos and self.delegationToken != None:
            url = "http://{0}/webhdfs/v1/?{1}op=CANCELDELEGATIONTOKEN&token={2}".format(self.endpoint, self.auth, self.delegationToken)
            self.put(url)
      
            
    def put(self, url):
        resp = requests.put(url, allow_redirects=False)
        if resp.status_code != 200:  
            error("Invalid returned http code '{0}' when calling '{1}'", resp.status_code, url)

        
    def getFileStatus(self, path):
        url = "http://{0}/webhdfs/v1{1}?{2}op=GETFILESTATUS".format(self.endpoint, path, self.auth)
        resp = requests.get(url)
        if resp.status_code == 200:
            #print content
            result = resp.json()
            return result['FileStatus']
        elif resp.status_code == 404:
            return None
        else:
            error("Invalid returned http code '{0}' when calling '{1}'",resp.status_code, url)
            
 
            
class State:
    FILE = "file"
    ABSENT = "absent"
    DIRECTORY = "directory"
    
class HdfsType:
    FILE = "FILE"
    DIRECTORY = "DIRECTORY"


webhdfs = None

def cleanup():
    if webhdfs != None:
        webhdfs.close()
        
def error(message, *args):
    x = "" + message.format(*args)
    cleanup()
    module.fail_json(msg = x)    


class Parameters:
    pass
     
def lookupWebHdfs(p):                
    if p.webhdfsEndpoint == None:
        if not os.path.isdir(p.hadoopConfDir):
            error("{0} must be an existing folder, or --hadoopConfDir  or --webhdfsEndpoint provided as parameter.".format(p.hadoopConfDir))
        candidates = []
        hspath = os.path.join(p.hadoopConfDir, "hdfs-site.xml")
        NN_HTTP_TOKEN1 = "dfs.namenode.http-address"
        NN_HTTP_TOKEN2 = "dfs.http.address"  # Deprecated
        if os.path.isfile(hspath):
            doc = minidom.parse(hspath)
            properties = doc.getElementsByTagName("property")
            for prop in properties :
                name = prop.getElementsByTagName("name")[0].childNodes[0].data
                if name.startswith(NN_HTTP_TOKEN1) or name.startswith(NN_HTTP_TOKEN2):
                    candidates.append(prop.getElementsByTagName("value")[0].childNodes[0].data)
            if not candidates:
                error("Unable to find {0}* or {1}* in {2}. Provide explicit 'webhdfs_endpoint'", NN_HTTP_TOKEN1, NN_HTTP_TOKEN2, hspath)
            errors = []
            for endpoint in candidates:
                webHDFS= WebHDFS(endpoint, p.hdfsUser)
                (x, err) = webHDFS.test()
                if x:
                    p.webhdfsEndpoint = webHDFS.endpoint
                    return webHDFS
                else:
                    errors.append(err)
            error("Unable to find a valid 'webhdfs_endpoint' in hdfs-site.xml:" + str(errors))
        else:
            error("Unable to find file {0}. Provide 'webhdfs_endpoint' or 'hadoop_conf_dir' parameter", hspath)
    else:
        candidates = p.webhdfsEndpoint.split(",")
        errors = []
        for endpoint in candidates:
            webHDFS= WebHDFS(endpoint, p.hdfsUser)
            (x, err) = webHDFS.test()
            if x:
                p.webhdfsEndpoint = webHDFS.endpoint
                return webHDFS
            else:
                errors.append(err)
        error("Unable to find a valid 'webhdfs_endpoint' in: " + p.webhdfsEndpoint + " (" + str(errors) + ")")
    
                
                
def main():
    
    global module
    module = AnsibleModule(
        argument_spec = dict(
            hdfs_path  = dict(required=True),
            hadoop_conf_dir = dict(required=False, default="/etc/hadoop/conf"),
            webhdfs_endpoint = dict(required=False, default=None),
            hdfs_user = dict(required=False, default="hdfs")
            
        )
    )
    
    if not HAS_REQUESTS:
        module.fail_json(msg="python-requests package is not installed")    

    
    p = Parameters()
    p.path = module.params['hdfs_path']
    p.hadoopConfDir = module.params['hadoop_conf_dir']
    p.webhdfsEndpoint = module.params['webhdfs_endpoint']
    p.hdfsUser = module.params['hdfs_user']
    p.changed = False


    if not p.path.startswith("/"):
        error("Path '{0}' is not absolute. Absolute path is required!", p.path)
  
    global webhdfs
    webhdfs = lookupWebHdfs(p)
    
    fileStatus = webhdfs.getFileStatus(p.path)
    # NB: Need to set hdfs_path. If setting 'path', module.exit_json will add a 'state' referring to local file status.
    cleanup()
    if fileStatus == None:
        module.exit_json(
            changed = False,
            hdfs_path = p.path,
            exists = False,
            type = "absent"
        )
    else:
        module.exit_json(
            changed = False,
            hdfs_path = p.path,
            exists = True,
            type = fileStatus['type'].lower(),
            owner = fileStatus['owner'],
            group = fileStatus['group'],
            mode = "0" + fileStatus['permission'],
            int_mode = int(fileStatus['permission'], 8),
            modificationTime = fileStatus['modificationTime']/1000,
            size = fileStatus['length']
        )

    

from ansible.module_utils.basic import *
if __name__ == '__main__':
    main()

