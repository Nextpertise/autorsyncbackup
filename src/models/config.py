import yaml, socket

class config():
    
    class __impl:
        """ Implementation of the singleton interface """
        
        # Default config values
        mainconfigpath = "/etc/autorsyncbackup/main.yaml"
        rsyncpath = "/usr/bin/rsync"
        lockfile = "/var/run/autorsyncbackup.pid"
        jobconfigdirectory = "/etc/autorsyncbackup/"
        jobspooldirectory = "/var/spool/autorsyncbackup/"
        backupdir = "/var/data/backups/autorsyncbackup/"
        logfile = "/var/log/autorsyncbackup/autorsyncbackup.log"
        speedlimitkb = 0
        dailyrotation = 8
        weeklyrotation = 5
        monthlyrotation = 13
        weeklybackup = 7
        monthlybackup = 1
        backupmailfrom = ""
        backupmailrecipients = []
        jobworkers = 3
        debuglevel = 0
        debugmessages = []

        def spam(self):
            """ Test method, return singleton id """
            return id(self)

    # storage for the instance reference
    __instance = None
    
    def __init__(self, mainconfigpath=None):
        """ Create singleton instance """
        # Check whether we already have an instance
        if config.__instance is None:
            # Create and remember instance
            config.__instance = config.__impl()
            
            if(mainconfigpath):
                self.mainconfigpath = mainconfigpath
            self.readConfig()
            self.init = False

        # Store instance reference as the only member in the handle
        self.__dict__['_config__instance'] = config.__instance

    def __getattr__(self, attr):
        """ Delegate access to implementation """
        return getattr(self.__instance, attr)

    def __setattr__(self, attr, value):
        """ Delegate access to implementation """
        return setattr(self.__instance, attr, value)
            
    def readConfig(self):
        try:
            self.debugmessages.append("Reading main config from %s" % self.mainconfigpath)
            with open(self.mainconfigpath, 'r') as stream:
                config = yaml.load(stream)
        except:
            exitcode = 1
            print "%s: Error while reading main config, exiting (%d)" % (self.mainconfigpath, exitcode)
            exit(exitcode)

        try:
            self.debuglevel = config['debuglevel']
        except:
            pass
            
        try:
            self.rsyncpath = config['rsyncpath']
        except:
            self.debugmessages.append("%s: No rsyncpath is set, using default value: %s" % (self.mainconfigpath, self.rsyncpath))
            
        try:
            self.lockfile = config['lockfile']
        except:
            self.debugmessages.append("%s: No lockfile path is set, using default value: %s" % (self.mainconfigpath, self.lockfile))

        try:
            self.jobconfigdirectory = config['jobconfigdirectory']
        except:
            self.debugmessages.append("%s: No jobconfigdirectory is set, using default value: %s" % (self.mainconfigpath, self.jobconfigdirectory))
                
        try:
            self.jobspooldirectory = config['jobspooldirectory']
        except:
            self.debugmessages.append("%s: No jobspooldirectory is set, using default value: %s" % (self.mainconfigpath, self.jobspooldirectory))

        try:
            self.backupdir = config['backupdir']
        except:
            self.debugmessages.append("%s: No backupdir is set, using default value: %s" % (self.mainconfigpath, self.backupdir))
                
        try:
            self.logfile = config['logfile']
        except:
            self.debugmessages.append("%s: No logfile is set, using default value: %s" % (self.mainconfigpath, self.logfile))
        self.debugmessages.append("Writing to logfile %s" % self.logfile)
            
        try:
            self.speedlimitkb = config['speedlimitkb']
        except:
            self.debugmessages.append("%s: No speedlimitkb is set, using default value: %d" % (self.mainconfigpath, self.speedlimitkb))
            
        try:
            self.dailyrotation = config['dailyrotation']
        except:
            self.debugmessages.append("%s: No dailyrotation is set, using default value: %d" % (self.mainconfigpath, self.dailyrotation))
            
        try:
            self.weeklyrotation = config['weeklyrotation']
        except:
            self.debugmessages.append("%s: No weeklyrotation is set, using default value: %d" % (self.mainconfigpath, self.weeklyrotation))
            
        try:
            self.monthlyrotation = config['monthlyrotation']
        except:
            self.debugmessages.append("%s: No monthlyrotation is set, using default value: %d" % (self.mainconfigpath, self.monthlyrotation))
                
        try:
            self.weeklybackup = config['weeklybackup']
        except:
            self.debugmessages.append("%s: No weeklybackup is set, using default value: %d" % (self.mainconfigpath, self.weeklybackup))
                
        try:
            self.monthlybackup = config['monthlybackup']
        except:
            self.debugmessages.append("%s: No monthlybackup is set, using default value: %d" % (self.mainconfigpath, self.monthlybackup))
                
        try:
            self.smtphost = config['smtphost']
        except:
            self.smtphost = 'localhost'
            self.debugmessages.append("%s: No smtphost is set, using default value: %s" % (self.mainconfigpath, self.smtphost))

        try:
            self.backupmailfrom = config['backupmailfrom']
        except:
            defaultPrefix = "backup@"
            fqdn = socket.getfqdn()
            self.backupmailfrom = "%s%s" % (defaultPrefix, fqdn)
            self.debugmessages.append("%s: No backupmailfrom is set, using default value: %s" % (self.mainconfigpath, self.monthlybackup))
                
        try:
            if type(config['backupmailrecipients']) is list:
                self.backupmailrecipients = config['backupmailrecipients']
        except:
            self.debugmessages.append("%s: No backupmailrecipient(s) are set, there will no backup report be sent" % self.mainconfigpath)
            
        try:
            self.jobworkers = config['jobworkers']
        except:
            self.debugmessages.append("%s: No jobworkers is set, using default value: %d" % (self.mainconfigpath, self.jobworkers))