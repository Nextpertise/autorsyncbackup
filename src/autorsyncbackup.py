#!/usr/bin/python

from director import director
from models.config import config

import pprint

if __name__ == "__main__":
    # Welcome message
    print "Starting autoRsyncBackup"
    
    # Run director
    director = director()
    jobs = director.getJobArray()
    
    job = jobs[0]
    director.checkRemoteHost(job)
    director.checkBackupEnvironment(job)
    latest = director.checkForPreviousBackup(job)
    director.executeRsync(job, latest)