import yaml, socket

class config():
    
    class __impl:
        """ Implementation of the singleton interface """
        
        # Default config values
        mainconfigpath = "/etc/autorsyncbackup/main.yaml"
        rsyncpath = "/usr/bin/rsync"
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
        debug = True
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
            print "Reading main config from %s" % self.mainconfigpath
            with open(self.mainconfigpath, 'r') as stream:
                config = yaml.load(stream)
        except:
            exitcode = 1
            print "ERROR: %s: Error while reading main config, exiting (%d)" % (self.mainconfigpath, exitcode)
            exit(exitcode)

        try:
            self.debug = config['debug']
        except:
            pass
            
        try:
            self.rsyncpath = config['rsyncpath']
        except:
            if self.debug:
                self.debugmessages.append("DEBUG: %s: No rsyncpath is set, using default value: %s" % (self.mainconfigpath, self.rsyncpath))

        try:
            self.jobconfigdirectory = config['jobconfigdirectory']
        except:
            if self.debug:
                self.debugmessages.append("DEBUG: %s: No jobconfigdirectory is set, using default value: %s" % (self.mainconfigpath, self.jobconfigdirectory))
                
        try:
            self.jobspooldirectory = config['jobspooldirectory']
        except:
            if self.debug:
                self.debugmessages.append("DEBUG: %s: No jobspooldirectory is set, using default value: %s" % (self.mainconfigpath, self.jobspooldirectory))

        try:
            self.backupdir = config['backupdir']
        except:
            if self.debug:
                self.debugmessages.append("DEBUG: %s: No backupdir is set, using default value: %s" % (self.mainconfigpath, self.backupdir))
                
        try:
            self.logfile = config['logfile']
        except:
            print "Writing to logfile %s" % self.logfile
            if self.debug:
                self.debugmessages.append("DEBUG: %s: No logfile is set, using default value: %s" % (self.mainconfigpath, self.logfile))
            
        try:
            self.speedlimitkb = config['speedlimitkb']
        except:
            if self.debug:
                self.debugmessages.append("DEBUG: %s: No speedlimitkb is set, using default value: %d" % (self.mainconfigpath, self.speedlimitkb))
            
        try:
            self.dailyrotation = config['dailyrotation']
        except:
            if self.debug:
                self.debugmessages.append("DEBUG: %s: No dailyrotation is set, using default value: %d" % (self.mainconfigpath, self.dailyrotation))
            
        try:
            self.weeklyrotation = config['weeklyrotation']
        except:
            if self.debug:
                self.debugmessages.append("DEBUG: %s: No weeklyrotation is set, using default value: %d" % (self.mainconfigpath, self.weeklyrotation))
            
        try:
            self.monthlyrotation = config['monthlyrotation']
        except:
            if self.debug:
                self.debugmessages.append("DEBUG: %s: No monthlyrotation is set, using default value: %d" % (self.mainconfigpath, self.monthlyrotation))
                
        try:
            self.weeklybackup = config['weeklybackup']
        except:
            if self.debug:
                self.debugmessages.append("DEBUG: %s: No weeklybackup is set, using default value: %d" % (self.mainconfigpath, self.weeklybackup))
                
        try:
            self.monthlybackup = config['monthlybackup']
        except:
            if self.debug:
                self.debugmessages.append("DEBUG: %s: No monthlybackup is set, using default value: %d" % (self.mainconfigpath, self.monthlybackup))
                
        try:
            self.smtphost = config['smtphost']
        except:
            self.smtphost = 'localhost'
            if self.debug:
                self.debugmessages.append("DEBUG: %s: No smtphost is set, using default value: %s" % (self.mainconfigpath, self.smtphost))

        try:
            self.backupmailfrom = config['backupmailfrom']
        except:
            defaultPrefix = "backup@"
            fqdn = socket.getfqdn()
            self.backupmailfrom = "%s%s" % (defaultPrefix, fqdn)
            if self.debug:
                self.debugmessages.append("DEBUG: %s: No backupmailfrom is set, using default value: %s" % (self.mainconfigpath, self.monthlybackup))
                
        try:
            if type(config['backupmailrecipients']) is list:
                self.backupmailrecipients = config['backupmailrecipients']
        except:
            if self.debug:
                self.debugmessages.append("DEBUG: %s: No backupmailrecipient(s) are set, there will no backup report be sent" % self.mainconfigpath)