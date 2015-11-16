import yaml
from config import config

class job():
    enabled = True
    filepath = None
    hostname = None
    username = None
    password = None
    ssh = False
    share = None
    backupdir = None
    speedlimitkb = None
    dailyrotation = None
    weeklyrotation = None
    monthlyrotation = None
    fileset = None
    backupstatus = None
    
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
            print "Error while reading %s, skiping job" % self.filepath
            self.enabled = False
            return False

        try:
            self.hostname = jobconfig['hostname']
        except:
            print "%s: No hostname, skipping job." % self.filepath
            self.enabled = False
            return False

        try:
            self.ssh = jobconfig['ssh']
        except:
            if config().debug:
                print "DEBUG: %s: No SSH jobconfig variable set." % self.filepath
        
        try:
            self.username = jobconfig['username']
        except:
            print "%s: No username is set, skipping job." % self.filepath
            self.enabled = False
            return False

        try:
            if not self.ssh:
                self.password = jobconfig['password']
        except:
            print "%s: No password is set while not using SSH, skipping job." % self.filepath
            self.enabled = False
            return False
            
        try:
            self.share = jobconfig['share']
        except:
            print "%s: No share is set, skipping job." % self.filepath
            self.enabled = False
            return False
            
        try:
            self.backupdir = jobconfig['backupdir']
        except:
            self.backupdir = config().backupdir
            if config().debug:
                print "DEBUG: %s: No backupdir is set, using default" % self.filepath
            
        try:
            self.speedlimitkb = int(jobconfig['speedlimitkb'])
        except:
            self.speedlimitkb = config().speedlimitkb
            if config().debug:
                print "DEBUG: %s: No or invalid speedlimitkb is set, using default" % self.filepath
            
        try:
            self.dailyrotation = jobconfig['dailyrotation']
        except:
            self.dailyrotation = config().dailyrotation
            if config().debug:
                print "DEBUG: %s: No dailyrotation is set, using default" % self.filepath
            
        try:
            self.weeklyrotation = jobconfig['weeklyrotation']
        except:
            self.weeklyrotation = config().weeklyrotation
            if config().debug:
                print "DEBUG: %s: No weeklyrotation is set, using default" % self.filepath
            
        try:
            self.monthlyrotation = jobconfig['monthlyrotation']
        except:
            self.monthlyrotation = config().monthlyrotation
            if config().debug:
                print "DEBUG: %s: No monthlyrotation is set, using default" % self.filepath
                
        try:
            self.weeklybackup = jobconfig['weeklybackup']
        except:
            self.weeklybackup = config().weeklybackup
            if config().debug:
                print "DEBUG: %s: No weeklybackup is set, using default" % self.filepath
                
        try:
            self.monthlybackup = jobconfig['monthlybackup']
        except:
            self.monthlybackup = config().monthlybackup
            if config().debug:
                print "DEBUG: %s: No monthlybackup is set, using default" % self.filepath
            
        try:
            self.fileset = jobconfig['fileset']
        except:
            print "%s: No fileset is set, skipping job." % self.filepath
            self.enabled = False
            return False