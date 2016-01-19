import yaml
from config import config
from lib.logger import logger

class job():
    enabled = None
    filepath = None
    hostname = None
    username = None
    password = None
    ssh = None
    sshpublickey = None
    port = None
    share = None
    backupdir = None
    speedlimitkb = None
    dailyrotation = None
    weeklyrotation = None
    monthlyrotation = None
    weeklybackup = None
    monthlybackup = None
    fileset = None
    backupstatus = None
    hooks = None
    beforeLocalHooks = []
    afterLocalHooks = []
    beforeRemoteHooks =[]
    afterRemoteHooks = []
    
    def __init__(self, filepath=None):
        self.filepath = filepath
        self.fileset = []
        self.backupstatus = {}
        self.readJob()
    
    def readJob(self):
        try:
            with open(self.filepath, 'r') as stream:
                jobconfig = yaml.load(stream)
        except:
            logger().error("Error while reading %s, skiping job" % self.filepath)
            self.enabled = False
            return False

        try:
            self.enabled = jobconfig['enabled']
        except:
            self.enabled = True
            logger().debug("%s: No enabled tag is set, using default value: True" % self.filepath)

        try:
            self.hostname = jobconfig['hostname']
        except:
            logger().info("%s: No hostname, skipping job." % self.filepath)
            self.enabled = False
            return False

        try:
            self.ssh = jobconfig['ssh']
        except:
            self.ssh = False
            logger().debug("%s: No SSH jobconfig variable set." % self.filepath)
        
        try:
            self.username = jobconfig['username']
        except:
            logger().info("%s: No username is set, skipping job." % self.filepath)
            self.enabled = False
            return False

        try:
            if not self.ssh:
                self.password = jobconfig['password']
        except:
            logger().info("%s: No password is set while not using SSH, skipping job." % self.filepath)
            self.enabled = False
            return False
            
        try:
            self.sshpublickey = jobconfig['sshpublickey']
        except:
            if self.ssh:
                logger().error("%s: SSH is set, but no sshpublickey is configured, disabling backup" % self.filepath)
                self.enabled = False
                return False
            
        try:
            self.port = jobconfig['port']
        except:
            if self.ssh:
                self.port = 22
                logger().debug("%s: No rsync+ssh port is set, using default." % self.filepath)
            else:
                self.port = 873
                logger().debug("%s: No rsync port is set, using default." % self.filepath)
            
        try:
            self.share = jobconfig['share']
        except:
            logger().info("%s: No share is set, skipping job." % self.filepath)
            self.enabled = False
            return False
            
        try:
            self.backupdir = jobconfig['backupdir']
        except:
            self.backupdir = config().backupdir
            logger().debug("%s: No backupdir is set, using default" % self.filepath)
            
        try:
            self.speedlimitkb = int(jobconfig['speedlimitkb'])
        except:
            self.speedlimitkb = config().speedlimitkb
            logger().debug("%s: No or invalid speedlimitkb is set, using default" % self.filepath)
            
        try:
            self.dailyrotation = jobconfig['dailyrotation']
        except:
            self.dailyrotation = config().dailyrotation
            logger().debug("%s: No dailyrotation is set, using default" % self.filepath)
            
        try:
            self.weeklyrotation = jobconfig['weeklyrotation']
        except:
            self.weeklyrotation = config().weeklyrotation
            logger().debug("%s: No weeklyrotation is set, using default" % self.filepath)
            
        try:
            self.monthlyrotation = jobconfig['monthlyrotation']
        except:
            self.monthlyrotation = config().monthlyrotation
            logger().debug("%s: No monthlyrotation is set, using default" % self.filepath)
                
        try:
            self.weeklybackup = jobconfig['weeklybackup']
        except:
            self.weeklybackup = config().weeklybackup
            logger().debug("%s: No weeklybackup is set, using default" % self.filepath)
                
        try:
            self.monthlybackup = jobconfig['monthlybackup']
        except:
            self.monthlybackup = config().monthlybackup
            logger().debug("%s: No monthlybackup is set, using default" % self.filepath)
            
        try:
            self.hooks = jobconfig['hooks']
            for hook in self.hooks:
                try:
                    self.addhook(hook)
                except KeyError as e:
                    logger.debug("%s: Error in hook definition: %s" % (self.filepath,  e))
                    return False
        except:
            logger().info("%s: No hooks defined, skipping hooks." % self.filepath)
            
        try:
            self.fileset = jobconfig['fileset']
        except:
            logger().info("%s: No fileset is set, skipping job." % self.filepath)
            self.enabled = False
            return False

    def addhook(self,  hook):
        if not 'script' in hook:
            raise KeyError("script not defined in hook")
        
        hook['local'] = hook.get('local',  False)
        if not hook['local'] in (False,  True):
            raise KeyError("local not one of True or False in hook")

        hook['runtime'] = hook.get('runtime',  'before')
        if not hook['runtime'] in ('before',  'after'):
            raise KeyError("runtime must be before or after in hook")
        
        hook['continueonerror'] = hook.get('continueOnError',  False)
        if not hook['continueonerror'] in (False,  True):
            raise KeyError("continueonerror must be True of False in hook")
        
        if hook['local']:
            if hook['runtime'] == 'before':
                self.beforeLocalHooks.append(hook)
            else:
                self.afterLocalHooks.append(hook)
        else:
            if hook['runtime'] == 'before':
                self.beforeRemoteHooks.append(hook)
            else:
                self.afterRemoteHooks.append(hook)
