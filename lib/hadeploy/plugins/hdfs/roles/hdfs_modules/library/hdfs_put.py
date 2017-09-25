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


# TRICK:
# To debug exchange, on the namenode:
# ngrep -q -d eth0 -W normal  port 50070

DOCUMENTATION = '''
---
module: hdfs_put
version_added: "historical"
short_description: Copies files from remote locations up to HDFS
description:
     - The M(put) module copies a file or a folder from the remote box to HDFS. 
options:
  src:
    description:
      - Path on the remote box to a file to copy to HDFS. Can be absolute or relative.
        If path is a directory, it is copied recursively. In this case, if path ends
        with "/", only inside contents of that directory are copied to destination.
        Otherwise, if it does not end with "/", the directory itself with all contents
        is copied. This behavior is similar to Rsync.
        When a file is copied, target modification time is adjusted to the source value.
    required: true
    default: null
    aliases: []
  hdfs_dest:
    description:
      - HDFS absolute path where the file should be copied to.  
        If it is a directory, file will be copied into with its source name. 
        If not, this will be the target full path. In this case, dirname must exist
        If src is a directory, this must be a directory too.
    required: true
    default: null
  backup:
    description:
      - Create a backup file including the timestamp information so you can get
        the original file back if you somehow clobbered it incorrectly.
    required: false
    choices: [ "yes", "no" ]
    default: "no"
  force:
    description:
      - the default is C(yes), which will replace the target file when size or modification time is different from the source. 
        If C(no), the file will only be transferred if the destination does not exist.
    required: false
    choices: [ "yes", "no" ]
    default: "yes"
  force_ext:
    description:
      - the default is C(yes), which will adjust owner/group/mode on target files and directory with the provided value, if any. 
        If C(no), existing files and directories will not be modified.
    required: false
    choices: [ "yes", "no" ]
    default: "yes"
  directory_mode:
    description:
      - When doing a recursive copy set the mode for the directories. If this is not set we will use the system
        defaults. The mode is only set on directories which are newly created, and will not affect those that
        already existed.
    required: false
  owner:
    description:
      - Name of the user that will own the file, as would be fed by HDFS 'FileSystem.setOwner' 
    required: false
    default: None
  group:
    description:
      - Name of the group that will own the file, as would be fed by HDFS 'FileSystem.setOwner' 
    required: false
    default: None
  mode:
    description:
      - Mode (Permission) the file will be set, such as 0644 as would be fed by HDFS 'FileSystem.setPermission' 
    required: false
    default: None
  hadoop_conf_dir:
    description:
      - Where to find Hadoop configuration file, specially hdfs-site.xml, 
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
    - "Serge ALEXANDRE"

'''


EXAMPLES = '''

  # ------------------------- Directory copy
  # Let's say we have /tmp/file/tree/file1.txt on the remote node and /tmp/tree is an existing hdfs folder
  
  # The following will result in /tmp/tree/file1.txt in HDFS
  - hdfs_copy: src=/tmp/files/tree/ hdfs_dest=/tmp/tree
  
  # The following will result in /tmp/tree/tree/file1.txt in HDFS (/tmp/tree/tree is created if not existsing
  - hdfs_copy: src=/tmp/files/tree hdfs_dest=/tmp/tree
  

'''

from xml.dom import minidom

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
      

    def getPathTypeAndStatus(self, path):
        url = "http://{0}/webhdfs/v1{1}?{2}op=GETFILESTATUS".format(self.endpoint, path, self.auth)
        resp = requests.get(url)
        if resp.status_code == 200:
            result = resp.json()
            fs = {}
            fs['size'] = result['FileStatus']['length']
            fs['modificationTime'] = result['FileStatus']['modificationTime']/1000
            fs['mode'] = "0" + result['FileStatus']['permission']
            fs['owner'] = result['FileStatus']['owner']
            fs['group'] = result['FileStatus']['group']
            return (result['FileStatus']['type'], fs)
        elif resp.status_code == 404:
            return ("NOT_FOUND", None)
        elif resp.status_code == 403:
            return ("NO_ACCESS", None)
        else:
            error("Invalid returned http code '{0}' when calling '{1}'".format(resp.status_code, url))
     
            
    def put(self, url):
        resp = requests.put(url, allow_redirects=False)
        if resp.status_code != 200:  
            error("Invalid returned http code '{0}' when calling '{1}'", resp.status_code, url)

    def createFolder(self, path, permission):
        if permission != None:
            url = "http://{0}/webhdfs/v1{1}?{2}op=MKDIRS&permission={3}".format(self.endpoint, path, self.auth, permission)
        else:
            url = "http://{0}/webhdfs/v1{1}?{2}op=MKDIRS".format(self.endpoint, path, self.auth)
        self.put(url)

    def setOwner(self, path, owner):
        url = "http://{0}/webhdfs/v1{1}?{2}op=SETOWNER&owner={3}".format(self.endpoint, path, self.auth, owner)
        self.put(url)

    def setGroup(self, path, group):
        url = "http://{0}/webhdfs/v1{1}?{2}op=SETOWNER&group={3}".format(self.endpoint, path, self.auth, group)
        self.put(url)
    
    def setPermission(self, path, permission):
        url = "http://{0}/webhdfs/v1{1}?{2}op=SETPERMISSION&permission={3}".format(self.endpoint, path, self.auth, permission)
        self.put(url)

    def setModificationTime(self, hdfsPath, modTime):
        url = "http://{0}/webhdfs/v1{1}?{2}op=SETTIMES&modificationtime={3}".format(self.endpoint, hdfsPath, self.auth, long(modTime)*1000)
        self.put(url)

    def putFileToHdfs(self, localPath, hdfsPath, overwrite):
        url = "http://{0}/webhdfs/v1{1}?{2}op=CREATE&overwrite={3}".format(self.endpoint, hdfsPath, self.auth, "true" if overwrite else "false")
        resp = requests.put(url, allow_redirects=False)
        if not resp.status_code == 307:
            error("Invalid returned http code '{0}' when calling '{1}'".format(resp.status_code, url))
        url2 = resp.headers['location']    
        f = open(localPath, "rb")
        resp2 = requests.put(url2, data=f, headers={'content-type': 'application/octet-stream'})
        if not resp2.status_code == 201:
            error("Invalid returned http code '{0}' when calling '{1}'".format(resp2.status_code, url2))
           
    def rename(self, hdfsPath, newName):
        url = "http://{0}/webhdfs/v1{1}?{2}op=RENAME&destination={3}".format(self.endpoint, hdfsPath, self.auth, newName)
        self.put(url)
           
                            
    def getDirContent(self, path):
        url = "http://{0}/webhdfs/v1{1}?{2}op=LISTSTATUS".format(self.endpoint, path, self.auth)
        resp = requests.get(url)
        dirContent = {}
        dirContent['status'] = "OK"
        dirContent['files'] = []
        dirContent['directories'] = []
        if resp.status_code == 200:
            result = resp.json()
            for f in result['FileStatuses']['FileStatus']:
                if f['type'] == 'FILE':
                    fi = {}
                    fi['name'] = f['pathSuffix']
                    fi['size'] = f['length']
                    fi['modificationTime'] = f['modificationTime']/1000
                    fi['mode'] = "0" + f['permission']
                    fi['owner'] = f['owner']
                    fi['group'] = f['group']
                    dirContent['files'].append(fi)
                elif f['type'] == 'DIRECTORY':
                    di = {}
                    di['name'] = f['pathSuffix']
                    #di['modificationTime'] = f['modificationTime']/1000
                    di['mode'] = "0" + f['permission']
                    di['owner'] = f['owner']
                    di['group'] = f['group']
                    dirContent['directories'].append(di)
                else:
                    error("Unknown directory entry type: {0}".format(f['type']))
        elif resp.status_code == 404:
            dirContent['status'] = "NOT_FOUND"
        elif resp.status_code == 403:
            dirContent['status'] = "NO_ACCESS"
        else:
            error("Invalid returned http code '{0}' when calling '{1}'".format(resp.status_code, url))
        return dirContent
    

webHDFS = None

def cleanup():
    if webHDFS != None:
        webHDFS.close()
    

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
    

def checkParameters(p):
    if not os.path.exists(p.src):
        module.fail_json(msg="Source %s not found" % (p.src))
    if not os.access(p.src, os.R_OK):
        module.fail_json(msg="Source %s not readable" % (p.src))
    if p.mode != None:
        if not isinstance(p.mode, int):
            try:
                p.mode = int(p.mode, 8)
            except Exception:
                error("mode must be in octal form")
        p.mode = oct(p.mode)
    if p.directoryMode != None:
        if not isinstance(p.directoryMode, int):
            try:
                p.directoryMode = int(p.directoryMode, 8)
            except Exception:
                error("directoryMode must be in octal form")
        p.directoryMode = oct(p.directoryMode)
        #print '{ mode_type: "' + str(type(p.directoryMode)) + '",  directoryMode_value: "' + str(p.directoryMode) + '"}'

    if not p.hdfsDest.startswith("/"):
        error("hdfs_dest '{0}' is not absolute. Absolute path is required!", p.path)


def applyAttrOnNewFile(webhdfs, path, p):
    if p.owner != None:
        webhdfs.setOwner(path,p.owner)
    if p.group != None:
        webhdfs.setGroup(path, p.group)
    if p.mode != None:
        webhdfs.setPermission(path, p.mode)


def applyAttrOnNewDirectory(webhdfs, path, p):
    if p.owner != None:
        webhdfs.setOwner(path, p.owner)
    if p.group != None:
        webhdfs.setGroup(path, p.group)
    # Mode is defined at creation
    
    
def adjustAttrOnExistingFile(webhdfs, filePath, fileStatus, p):
    if p.owner != None and p.owner != fileStatus['owner']:
        webhdfs.setOwner(filePath, p.owner)
    if p.group != None and p.group != fileStatus['group']:
        webhdfs.setGroup(filePath, p.group)
    if(p.mode != None and fileStatus['mode'] != p.mode):
        webhdfs.setPermission(filePath, p.mode)


def adjustAttrOnExistingDir(webhdfs, dirPath, dirStatus, p):
    if p.owner != None and p.owner != dirStatus['owner']:
        webhdfs.setOwner(dirPath, p.owner)
    if p.group != None and p.group != dirStatus['group']:
        webhdfs.setGroup(dirPath, p.group)
    if(p.directoryMode != None and p.directoryMode != dirStatus['mode']):
        webhdfs.setPermission(dirPath, p.directoryMode)


def checkAttrOnExistingFile(fileStatus, p):
    if p.owner != None and p.owner != fileStatus['owner']:
        return True
    if p.group != None and p.group != fileStatus['group']:
        return True
    #print("p.mode:{0}   fileStatus['mode']:{1}".format(p.mode, fileStatus['mode']))
    if(p.mode != None and fileStatus['mode'] != p.mode):
        return True
    return False

def checkAttrOnExistingDir(dirStatus, p):
    if p.owner != None and p.owner != dirStatus['owner']:
        return True
    if p.group != None and p.group != dirStatus['group']:
        return True
    #print("p.directoryMode:{0}   dirStatus['mode']:{1}".format(p.directoryMode, dirStatus['mode']))
    if(p.directoryMode != None and p.directoryMode != dirStatus['mode']):
        return True
    return False



def backupHdfsFile(webhdfs, path):
    #ext = time.strftime("%Y-%m-%d@%H:%M:%S", time.localtime(time.time()))
    ext = time.strftime("%Y-%m-%d_%H_%M_%S~", time.localtime(time.time()))
    backupdest = '%s.%s' % (path, ext)
    webhdfs.rename(path, backupdest)
    


def buildLocalTree(rroot):
    tree = {}
    if rroot == "/":
        tree['slashTerminated'] = False
        prefLen = len(rroot) 
    else:
        if rroot.endswith("/"):
            rroot = rroot[:-1]
            tree['slashTerminated'] = True
        else :
            tree['slashTerminated'] = False
        prefLen = len(rroot) + 1
    tree['rroot'] = rroot
    fileMap = {}
    dirMap = {}
    for root, dirs, files in os.walk(rroot, topdown=True, onerror=None, followlinks=False):
        for fileName in files:
            key = os.path.join(root, fileName)[prefLen:]
            path = os.path.join(rroot, key)
            stat = os.stat(path)
            f = {}
            f['size'] = stat.st_size
            f['modificationTime'] = int(stat.st_mtime)
            f['mode'] = "0" + oct(stat.st_mode)[-3:]
            fileMap[key] = f
        for dirName in dirs:
            key = os.path.join(root, dirName)[prefLen:]
            path = os.path.join(rroot, key)
            stat = os.stat(path)
            f = {}
            f['mode'] = "0" + oct(stat.st_mode)[-3:]
            dirMap[key] = f
    tree['files'] = fileMap
    tree['directories'] = dirMap
    return tree
    
    
def buildHdfsTree(webHdfs, rroot):
    tree = {}
    if rroot == "/":
        tree['slashTerminated'] = False
        prefLen = len(rroot) 
    else:
        if rroot.endswith("/"):
            rroot = rroot[:-1]
            tree['slashTerminated'] = True
        else :
            tree['slashTerminated'] = False
        prefLen = len(rroot) + 1
    tree['rroot'] = rroot
    fileMap = {}
    dirMap = {}
    noAccess = []
    walkInHdfs(webHdfs, rroot, dirMap, fileMap, noAccess, prefLen)
    tree['files'] = fileMap
    tree['directories'] = dirMap
    tree['noAccess'] = noAccess
    return tree

def walkInHdfs(webHdfs, current, dirMap, fileMap, noAccess, prefLen):
    dirContent = webHdfs.getDirContent(current)
    #print misc.pprint2s(dirContent)
    if dirContent['status'] == "OK":
        for f in dirContent['files']:
            path = os.path.join(current, f['name'])[prefLen:]
            del f['name']
            fileMap[path] = f
        for d in dirContent['directories']:
            #print misc.pprint2s(d)
            path = os.path.join(current, d['name'])
            del d['name']
            dirMap[path[prefLen:]] = d
            walkInHdfs(webHdfs, path, dirMap, fileMap, noAccess, prefLen)
    elif dirContent['status'] == "NO_ACCESS":
        noAccess.append(current)
    else:
        error("Invalid DirContent status: {0} for path:'{1}'".format(dirContent.status, current)) 


def buildEmptyTree(rroot):
        tree = {}
        tree['files'] = {}
        tree['directories'] = {}
        tree['noAccess'] = []
        if rroot == "/":
            tree['slashTerminated'] = False
        else:
            if rroot.endswith("/"):
                rroot = rroot[:-1]
                tree['slashTerminated'] = True
            else :
                tree['slashTerminated'] = False
        tree['rroot'] = rroot
        return tree       
                
def main():
    
    global module
    module = AnsibleModule(
        argument_spec = dict(
            backup = dict(required=False, type='bool', default=False),
            directory_mode = dict(required=False, default=None),
            force = dict(required=False, type='bool', default=True),
            force_ext = dict(required=False, type='bool', default=True),
            group = dict(required=False, default=None),
            hadoop_conf_dir = dict(required=False, default="/etc/hadoop/conf"),
            hdfs_dest  = dict(required=True),
            hdfs_user = dict(required=False, default="hdfs"),
            mode = dict(required=False, default=None),
            owner = dict(required=False, default=None),
            src  = dict(required=True, default=None),
            webhdfs_endpoint = dict(required=False, default=None),
        ),
        supports_check_mode=True
    )
    
    if not HAS_REQUESTS:
        module.fail_json(msg="python-requests package is not installed")    

    p = Parameters()
    p.backup = module.params['backup']
    p.directoryMode = module.params['directory_mode']
    p.force = module.params['force']
    p.forceExt = module.params['force_ext']
    p.group = module.params['group']
    p.hadoopConfDir = module.params['hadoop_conf_dir']
    p.hdfsDest = module.params['hdfs_dest']
    p.hdfsUser = module.params['hdfs_user']
    p.mode = module.params['mode']
    p.owner = module.params['owner']
    p.src = module.params['src']
    p.webhdfsEndpoint = module.params['webhdfs_endpoint']

    p.checkMode = module.check_mode
    p.changed = False

    checkParameters(p)
    
    global webHDFS
    webHDFS = lookupWebHdfs(p)
    
    (destPathType,  destStatus) = webHDFS.getPathTypeAndStatus(p.hdfsDest)
    
    #print(destPathType)
            
    if not os.path.isdir(p.src):
        # -----------------------------------------------------------------------------------------------------Source is a simple file
        if destPathType == 'DIRECTORY':
            # Target is a directory. Recompute effective target
            p.hdfsDest = os.path.join(p.hdfsDest, os.path.basename(p.src))
            (destPathType,  destStatus) = webHDFS.getPathTypeAndStatus(p.hdfsDest)
            
        if destPathType == "NOT_FOUND":  # -------------------------------------------------------- Target does not exist
            # hdfs_dest does not exist. Ensure base dir exists
            destBasedir = os.path.dirname(p.hdfsDest)
            (destBaseDirType, _) = webHDFS.getPathTypeAndStatus(destBasedir)
            if destBaseDirType != 'DIRECTORY':
                error("Destination directory {0} does not exist", destBasedir)
            p.changed = True
            if not p.checkMode:
                webHDFS.putFileToHdfs(p.src, p.hdfsDest, False)
                webHDFS.setModificationTime(p.hdfsDest, int(os.stat(p.src).st_mtime))
                applyAttrOnNewFile(webHDFS, p.hdfsDest, p)
        elif destPathType == 'FILE':  # --------------------------------------------- Target already exists. Check if we need to overwrite.
            stat = os.stat(p.src)
            if p.force and (stat.st_size != destStatus['size'] or  int(stat.st_mtime) != destStatus['modificationTime']):
                #print("{{ statst_size: {0}, destStatus_length: {1}, int_stat_st_mtime: {2}, estStatus_modificationTime_1000: {3} }}".format(stat.st_size, destStatus['length'], int(stat.st_mtime), destStatus['modificationTime']/100))
                # File changed. Must be copied again
                p.changed = True
                if not p.checkMode:
                    if p.backup:
                        backupHdfsFile(webHDFS, p.hdfsDest)
                    webHDFS.putFileToHdfs(p.src, p.hdfsDest, True)
                    webHDFS.setModificationTime(p.hdfsDest, int(stat.st_mtime))
                    applyAttrOnNewFile(webHDFS, p.hdfsDest, p)
            else:
                if checkAttrOnExistingFile(destStatus, p) and p.forceExt:
                    p.changed = True
                    if not p.checkMode:
                        adjustAttrOnExistingFile(webHDFS, p.hdfsDest, destStatus, p)
        elif destPathType == 'DIRECTORY':
            error("hdfs_dest '{0}' is a directory. Must be a file or not existing", p.hdfsDest)
        else:
            error("Unknown type '{0}' for hdfs_dest '{1}'", destPathType, p.hdfsDest)
    else:
        # ----------------------------------------------------------------------------------------------- Source is a directory. Use copy by mirroring
        if destPathType == "NOT_FOUND":
            error("Path {0} non existing on HDFS", p.hdfsDest)
        if destPathType == "FILE":
            error("HDFS path {0} is a file. Must be a directory", p.hdfsDest)
        elif destPathType == "NO_ACCESS":
            error("HDFS path {0}: No access", p.hdfsDest)
        elif destPathType != "DIRECTORY":
            error("HDFS path {0}: Unknown type: '{1}'", p.hdfsDest, destPathType)
        
        handlePutByMirroring(webHDFS, p)

    cleanup()
    module.exit_json(changed=p.changed)






def handlePutByMirroring(webHDFS, p):    
    srcTree = buildLocalTree(p.src)

    directoriesToCreate = []
    directoriesToAdjust = []
    filesToCreate = []
    filesToReplace = []
    filesToAdjust = []

    # If source does not end with '/', its basename will be added to target path. And directory created if not existing
    if not srcTree['slashTerminated']:
        x = os.path.basename(srcTree['rroot'])
        p.hdfsDest = os.path.join(p.hdfsDest, x)
        (ft, dirStatus) = webHDFS.getPathTypeAndStatus(p.hdfsDest)
        if ft == "NOT_FOUND":
            directoriesToCreate.append(p.hdfsDest)
            destTree = buildEmptyTree(p.hdfsDest)
        elif ft == "DIRECTORY":
            destTree = buildHdfsTree(webHDFS, p.hdfsDest)
            destTree['directories'][p.hdfsDest] = dirStatus  # Will need to to apply modification later on
            if checkAttrOnExistingDir(dirStatus, p):
                directoriesToAdjust.append(p.hdfsDest)
        else:
            error("HDFS path {0}: Invalid type: '{1}'", p.hdfsDest, ft)
    else:
        destTree = buildHdfsTree(webHDFS, p.hdfsDest)
    
    # Lookup all folder to create on target
    for dirName in srcTree['directories']:
        if dirName in destTree['directories']:
            if checkAttrOnExistingDir(destTree['directories'][dirName], p):
                directoriesToAdjust.append(dirName)
        else:
            dirPath = os.path.join(destTree['rroot'], dirName)
            directoriesToCreate.append(dirPath)
               
    directoriesToAdjust.sort()
    directoriesToCreate.sort()

    for fileName in srcTree['files']:
        if fileName in destTree['files']:
            srcFilesStatus = srcTree['files'][fileName]
            destFilesStatus = destTree['files'][fileName]
            if srcFilesStatus['size'] != destFilesStatus['size'] or srcFilesStatus['modificationTime'] != destFilesStatus['modificationTime']:
                filesToReplace.append(fileName)
            elif checkAttrOnExistingFile(destTree['files'][fileName], p):
                filesToAdjust.append(fileName)
        else:
            filesToCreate.append(fileName)

    #print("directoriesToCreate:{0} filesToAdjust:{1} filesToCreate:{2} filesToReplace:{3}".format(directoriesToCreate, filesToAdjust, filesToCreate, filesToReplace))
    
    for f in directoriesToCreate:
        p.changed = True
        if not p.checkMode:
            webHDFS.createFolder(f, p.directoryMode)
            applyAttrOnNewDirectory(webHDFS, f, p)

    if p.forceExt:
        for f in directoriesToAdjust:
            p.changed = True
            if not p.checkMode:
                dirPath = os.path.join(destTree['rroot'], f)
                dirStatus = destTree['directories'][f]
                adjustAttrOnExistingDir(webHDFS, dirPath, dirStatus, p)
    
        for f in filesToAdjust:
            p.changed = True
            if not p.checkMode:
                filePath = os.path.join(destTree['rroot'], f)
                fileStatus = destTree['files'][f]
                adjustAttrOnExistingFile(webHDFS, filePath, fileStatus, p)

    for f in filesToCreate:
        p.changed = True
        if not p.checkMode:
            srcPath = os.path.join(srcTree['rroot'], f)
            destPath = os.path.join(destTree['rroot'], f)
            webHDFS.putFileToHdfs(srcPath, destPath, p.force)
            modTime = srcTree['files'][f]['modificationTime']
            webHDFS.setModificationTime(destPath, modTime)
            applyAttrOnNewFile(webHDFS, destPath, p)

    if p.force:
        for f in filesToReplace:
            p.changed = True
            if not p.checkMode:
                srcPath = os.path.join(srcTree['rroot'], f)
                destPath = os.path.join(destTree['rroot'], f)
                if p.backup:
                    backupHdfsFile(webHDFS, destPath)
                webHDFS.putFileToHdfs(srcPath, destPath, p.force)
                modTime = srcTree['files'][f]['modificationTime']
                webHDFS.setModificationTime(destPath, modTime)
                applyAttrOnNewFile(webHDFS, destPath, p)
    



from ansible.module_utils.basic import *

if __name__ == '__main__':
    main()

