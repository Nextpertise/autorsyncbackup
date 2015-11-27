#!/usr/bin/python
import time, threading, Queue
from optparse import OptionParser
from _version import __version__
from models.config import config
from lib.director import director
from lib.pidfile import *
from lib.statusemail import statusemail
from lib.logger import logger
from lib.jobthread import jobThread

def setupCliArguments():
    """ Parse CLI options """
    parser = OptionParser()
    parser.add_option("-c", "--main-config", dest="mainconfig", metavar="path_to_main.yaml",
        help="set different main config file, default value = /etc/autorsyncbackup/main.yaml", 
        default="/etc/autorsyncbackup/main.yaml")
    parser.add_option("-d", "--dry-run", action="store_true", dest="dryrun", default=False,
        help="do not invoke rsync, only perform a login attempt on the remote host, when applied with -j the exit code will be set (0 for success, 1 for error)")
    parser.add_option("-v", "--verbose", action="store_true", dest="verbose", default=False,
        help="Write logoutput also to stdout")
    parser.add_option("--version", action="store_true", dest="version", default=False,
        help="Show version number")
    parser.add_option("-j", "--single-job", metavar="path_to_jobfile.job", dest="job", 
        help="run only the given job file")

    (options, args) = parser.parse_args()    
    return options
        
def getVersion():
    return __version__

def runBackup(jobpath, dryrun):
    """ Start backup run """
    exitFlag = threading.Event()
    queueLock = threading.Lock()
    workQueue = Queue.Queue(0)

    try:
        with Pidfile(config().lockfile, logger().debug, logger().error):
            # Run director
            directorInstance = director()
            jobs = directorInstance.getJobArray(jobpath)
            
            # Start threads
            threads = []
            if not dryrun:
                for i in range(0, config().jobworkers):
                  thread = jobThread(i, exitFlag, queueLock, directorInstance, workQueue)
                  thread.start()
                  threads.append(thread)
            
            # Execute jobs
            queueLock.acquire()
            durationstats = {}
            durationstats['backupstartdatetime'] = int(time.time())
            for job in jobs:
                if(job.enabled):
                    if directorInstance.checkRemoteHost(job):
                        if not dryrun:
                            # Add to queue
                            workQueue.put(job)
            queueLock.release()            
            # Wait for queue to empty
            while not workQueue.empty():
                pass
            
            # Notify threads it's time to exit
            exitFlag.set()
            
            # Wait for all threads to complete
            for t in threads:
                t.join()
            durationstats['backupenddatetime'] = int(time.time())
        
            if not dryrun:
                # Do housekeeping
                durationstats['housekeepingstartdatetime'] = int(time.time())
                for job in jobs:
                    if(job.enabled):
                        if job.backupstatus['rsync_backup_status'] == 1:
                            directorInstance.backupRotate(job)
                durationstats['housekeepingenddatetime'] = int(time.time())
                
                # Sent status report
                statusemail().sendStatusEmail(jobs, durationstats)
    except ProcessRunningException as m:
        logger().error(m)
        
def checkRemoteHost(jobpath):
    """ Check remote host and exit with exitcode 0 (success) or 1 (error) """
    directorInstance = director()
    jobs = directorInstance.getJobArray(jobpath)
    checkRemoteHost = directorInstance.checkRemoteHost(jobs[0])
    exit(not checkRemoteHost)
        
if __name__ == "__main__":
    options = setupCliArguments()
    config(options.mainconfig)
    checkSingleHost = False
    
    # Welcome message
    if options.verbose:
        print "Starting AutoRsyncBackup"
    
    if options.job and options.dryrun:
        checkSingleHost = True
        options.verbose = True
        config().debuglevel = 2
    
    # Set logpath
    logger(config().logfile)
    logger().setDebuglevel(config().debuglevel)
    logger().setVerbose(options.verbose)
    for msg in config().debugmessages:
        logger().debug(msg)

    if options.version:
        print getVersion()
        exit(0)
    elif checkSingleHost:
        checkRemoteHost(options.job)
    else:
        runBackup(options.job, options.dryrun)