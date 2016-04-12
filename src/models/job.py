import yaml
from config import config
from lib.logger import logger

class job():
    def __init__(self, filepath=None):
        self.enabled = None
        self.hostname = None
        self.ssh = None
        self.rsyncusername = None
        self.rsyncpassword = None
        self.rsyncshare = None
        self.sshusername = None
        self.sshprivatekey = None
        self.port = None
        self.backupdir = None
        self.speedlimitkb = None
        self.dailyrotation = None
        self.weeklyrotation = None
        self.monthlyrotation = None
        self.weeklybackup = None
        self.monthlybackup = None
        self.hooks = None
        self.beforeLocalHooks = []
        self.afterLocalHooks = []
        self.beforeRemoteHooks =[]
        self.afterRemoteHooks = []
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
            self.sshusername = jobconfig['ssh_username']
        except:
            if self.ssh:
                logger().info("%s: No ssh_username is set, skipping job." % self.filepath)
                self.enabled = False
                return False

        try:
            if not self.ssh:
                self.rsyncusername = jobconfig['rsync_username']
        except:
            logger().info("%s: No rsync_username is set, skipping job." % self.filepath)
            self.enabled = False
            return False

        try:
            if not self.ssh:
                self.rsyncpassword = jobconfig['rsync_password']
        except:
            logger().info("%s: No password is set while not using SSH, skipping job." % self.filepath)
            self.enabled = False
            return False
            
        try:
            self.sshprivatekey = jobconfig['ssh_privatekey']
        except:
            if self.ssh:
                logger().error("%s: SSH is set, but no ssh_privatekey is configured, disabling backup" % self.filepath)
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
            if not self.ssh:
                self.rsyncshare = jobconfig['rsync_share']
            else:
                self.rsyncshare = ''
        except:
            logger().info("%s: No rsync_share is set, skipping job." % self.filepath)
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
            if self.sshusername == None or self.sshprivatekey == None:
                logger().error('%s: Missing ssh username or keyfile, hooks disabled' % self.filepath)
            else:
                for hook in self.hooks:
                    try:
                        self.addhook(hook)
                    except KeyError as e:
                        logger().error("%s: Error in hook definition: %s" % (self.filepath,  e))
                        return False
        except Exception as e:
            logger().info("%s: No hooks defined, skipping hooks (exception: %s)." % (self.filepath,  e))
            
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
        
        hook['continueonerror'] = hook.get('continueonerror',  False)
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
    
    def showjob(self):
        print "Show job:"
        print "enabled: %s" % str(self.enabled)
        print "filepath: %s" % str(self.filepath)
        print "hostname: %s" % str(self.hostname)
        print "rsyncusername: %s" % str(self.rsyncusername)
        print "rsyncpassword: %s" % str(self.rsyncpassword)
        print "rsyncshare: %s" % str(self.rsyncshare)
        print "sshusername: %s" % str(self.sshusername)
        print "sshprivatekey: %s" % str(self.sshprivatekey)
        print "backupdir: %s" % str(self.backupdir)
        print "speedlimitkb: %s" % str(self.speedlimitkb)
        print "dailyrotation: %s" % str(self.dailyrotation)
        print "weeklyrotation: %s" % str(self.weeklyrotation)
        print "monthlyrotation: %s" % str(self.monthlyrotation)
        print "weeklybackup: %s" % str(self.weeklybackup)
        print "monthlybackup: %s" % str(self.monthlybackup)
        print "fileset: %s" % str(self.fileset)
        print "backupstatus: %s" % str(self.backupstatus)
        print "hooks: %s" % str(self.hooks)
        print "beforeLocalHooks: %s" % str(self.beforeLocalHooks)
        print "afterLocalHooks: %s" % str(self.afterLocalHooks)
        print "beforeRemoteHooks: %s" % str(self.beforeRemoteHooks)
        print "beforeRemoteHooks: %s" % str(self.beforeRemoteHooks)
        print "afterRemoteHooks: %s" % str(self.afterRemoteHooks)
