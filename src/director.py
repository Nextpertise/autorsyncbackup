import glob, os
from models.job import job
from models.configparser import configparser

class director():

    def getJobArray(self):
        
        jobArray = []
        dir = configparser().jobconfigdirectory.rstrip('/')
        os.chdir(dir)
        for file in glob.glob("*.job"):
            jobArray.append(job(dir + "/" + file))
            
        return jobArray