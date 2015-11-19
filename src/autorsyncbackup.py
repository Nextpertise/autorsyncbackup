#!/usr/bin/python
import time
from optparse import OptionParser
from director import director
from models.config import config
from lib.statusemail import statusemail
from lib.logger import logger

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
    print "Starting AutoRsyncBackup"
    
    options = setupCliArguments()
    config(options.mainconfig)
    
    # Set logpath
    logger(config().logfile)
    for msg in config().debugmessages:
        logger().debug(msg)
    
    # Run director
    director = director()
    jobs = director.getJobArray(options.job)
    
    # Execute jobs
    durationstats = {}
    durationstats['backupstartdatetime'] = int(time.time())
    for job in jobs:
        if(job.enabled):
            director.checkRemoteHost(job)
            if not options.dryrun:
                director.checkBackupEnvironment(job)
                latest = director.checkForPreviousBackup(job)
                director.executeRsync(job, latest)
                director.processBackupStatus(job)
    durationstats['backupenddatetime'] = int(time.time())

    if not options.dryrun:
        # Do housekeeping
        durationstats['housekeepingstartdatetime'] = int(time.time())
        for job in jobs:
            if(job.enabled):
                if job.backupstatus['rsync_backup_status'] == 1:
                    director.backupRotate(job)
        durationstats['housekeepingenddatetime'] = int(time.time())
        
        # Sent status report
        statusemail().sendStatusEmail(jobs, durationstats)