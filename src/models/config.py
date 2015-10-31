import yaml

class config():
    
    class __impl:
        """ Implementation of the singleton interface """
        
        # Default config values
        mainconfigpath = "/etc/autorsyncbackup/main.yaml"
        rsyncpath = "/usr/bin/rsync"
        jobconfigdirectory = "/etc/autorsyncbackup/"
        jobspooldirectory = "/var/spool/autorsyncbackup/"
        backupdir = "/var/data/backups/autorsyncbackup/"
        speedlimitkb = 0
        dailyrotation = 8
        weeklyrotation = 5
        monthlyrotation = 13
        weeklybackup = 7
        monthlybackup = 1
        debug = True

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
            print "DEBUG: %s: Error while reading main config" % self.mainconfigpath
            return False

        try:
            self.debug = config['debug']
        except:
            pass
            
        try:
            self.rsyncpath = config['rsyncpath']
        except:
            if self.debug:
                print "DEBUG: %s: No rsyncpath is set, using default value: %s" % (self.mainconfigpath, self.rsyncpath)

        try:
            self.jobconfigdirectory = config['jobconfigdirectory']
        except:
            if self.debug:
                print "DEBUG: %s: No jobconfigdirectory is set, using default value: %s" % (self.mainconfigpath, self.jobconfigdirectory)
                
        try:
            self.jobspooldirectory = config['jobspooldirectory']
        except:
            if self.debug:
                print "DEBUG: %s: No jobspooldirectory is set, using default value: %s" % (self.mainconfigpath, self.jobspooldirectory)

        try:
            self.backupdir = config['backupdir']
        except:
            if self.debug:
                print "DEBUG: %s: No backupdir is set, using default value: %s" % (self.mainconfigpath, self.backupdir)
            
        try:
            self.speedlimitkb = config['speedlimitkb']
        except:
            if self.debug:
                print "DEBUG: %s: No speedlimitkb is set, using default value: %d" % (self.mainconfigpath, self.speedlimitkb)
            
        try:
            self.dailyrotation = config['dailyrotation']
        except:
            if self.debug:
                print "DEBUG: %s: No dailyrotation is set, using default value: %d" % (self.mainconfigpath, self.dailyrotation)
            
        try:
            self.weeklyrotation = config['weeklyrotation']
        except:
            if self.debug:
                print "DEBUG: %s: No weeklyrotation is set, using default value: %d" % (self.mainconfigpath, self.weeklyrotation)
            
        try:
            self.monthlyrotation = config['monthlyrotation']
        except:
            if self.debug:
                print "DEBUG: %s: No monthlyrotation is set, using default value: %d" % (self.mainconfigpath, self.monthlyrotation)
                
        try:
            self.weeklybackup = config['weeklybackup']
        except:
            if self.debug:
                print "DEBUG: %s: No weeklybackup is set, using default value: %d" % (self.mainconfigpath, self.weeklybackup)
                
        try:
            self.monthlybackup = config['monthlybackup']
        except:
            if self.debug:
                print "DEBUG: %s: No monthlybackup is set, using default value: %d" % (self.mainconfigpath, self.monthlybackup)