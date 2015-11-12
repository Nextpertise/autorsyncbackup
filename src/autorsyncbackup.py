#!/usr/bin/python

from optparse import OptionParser
from director import director
from models.config import config

def setupCliArguments():
    parser = OptionParser()
    parser.add_option("-c", "--main-config", dest="mainconfig", metavar="path_to_main.yaml",
        help="set different main config file, default value = /etc/autorsyncbackup/main.yaml", 
        default="/etc/autorsyncbackup/main.yaml")
    parser.add_option("-d", "--dry-run", action="store_true", dest="dryrun", default=False,
        help="do not invoke rsync, only perform a login attempt on remote host")
    parser.add_option("-j", "--single-job", metavar="path_to_jobfile.job", dest="job", 
        help="run only the given job file")

    (options, args) = parser.parse_args()    
    return options

if __name__ == "__main__":
    # Welcome message
    print "Starting autoRsyncBackup"
    
    options = setupCliArguments()
    config(options.mainconfig)
    
    # Run director
    director = director()
    jobs = director.getJobArray(options.job)
    
    # TODO: Run multiple jobs at the same time
    # TODO: Create logfile, write debug always to log?
    # TODO: Create status mail
    
    for job in jobs:
        if(job.enabled):
            director.checkRemoteHost(job)
            if not options.dryrun:
                director.checkBackupEnvironment(job)
                latest = director.checkForPreviousBackup(job)
                director.executeRsync(job, latest)
                director.backupRotate(job)
                director.processBackupStatus(job)