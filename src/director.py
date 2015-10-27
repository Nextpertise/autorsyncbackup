import glob, os
from models.job import job
from models.config import config

import subprocess

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
        print job.ssh
        print job.hostname
        
        try:
          output = subprocess.check_output("ls -l; sleep 4; exit 255", stderr=subprocess.STDOUT, shell=True)
        except subprocess.CalledProcessError as exc:
          print "error code", exc.returncode, exc.output
          output = exc.output