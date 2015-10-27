#!/usr/bin/python

from director import director
from models.configparser import configparser

import pprint

if __name__ == "__main__":
    # Welcome message
    print "Starting autoRsyncBackup"
    
    # Run director
    director = director()
    director.getJobArray()