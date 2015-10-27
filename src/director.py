import glob, os
from models.job import job
from models.config import config
from lib.rsync import rsync

class director():

    def getJobArray(self):
        
        jobArray = []
        dir = config().jobconfigdirectory.rstrip('/')
        if(os.path.exists(dir)):
            os.chdir(dir)
            for file in glob.glob("*.job"):
                jobArray.append(job(dir + "/" + file))
        else:
            print "Job directory (%s) doesn't exists, exiting (1)" % dir
            
        return jobArray
        
    def checkRemoteHost(self, job):
        return rsync().checkRemoteHost(job)
        
    def executeRsync(self, job, latest):
        return rsync().executeRsync(job, latest)
        
    def checkBackupEnvironment(self, job):
        dir = job.backupdir.rstrip('/')
        if not os.path.exists(dir):
            print "Backup path (%s) doesn't exists" % job.backupdir
            return False
        try:
            dir = dir + "/" + job.hostname + "/current"
            if not os.path.exists(dir):
                os.makedirs(dir)
        except:
            print "Error creating backup directory (%s) for host (%s)" % (dir, job.hostname)
            return False
    
    def checkForPreviousBackup(self, job):
        latest = job.backupdir.rstrip('/') + "/" + job.hostname + "/latest"
        if os.path.exists(latest):
            return latest
        else:
            return False