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
    
    director.checkRemoteHost(jobs[0])