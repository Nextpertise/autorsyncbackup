from models.config import config
import subprocess

class rsync():
    
    def checkRemoteHost(self, job):
        "Determine if we should use the SSH or Rsync protocol"
        if job.ssh:
            ret = self.checkRemoteHostViaSshProtocol(job)
        else:
            ret = self.checkRemoteHostViaRsyncProtocol(job)
        return ret
    
    def checkRemoteHostViaRsyncProtocol(self, job):
        """Check if remote host is up and able to accept connections with our credentials"""
        command = "export RSYNC_PASSWORD=\"%s\"; rsync --contimeout=5 rsync://%s@%s/%s" % (job.password, job.username, job.hostname, job.share)
        
        # TODO: Move command execution to seperate function, return errorcode, stdout
        try:
            output = subprocess.check_output(command, stderr=subprocess.STDOUT, shell=True)
        except subprocess.CalledProcessError as exc:
            print "Error while connecting to host (%s) - %s" % (exc.returncode, exc.output)
            return False
        if config().debug:
            print "DEBUG: Succesfully connected to host via rsync protocol (%s)" % job.hostname
        return True
          
    def checkRemoteHostViaSshProtocol(self, job):
        """TODO: Needs to be implemented"""
        print "checkRemoteHostViaSshProtocol - Needs to be implemented"
        return False
        
    def executeRsync(self, job, latest):
        "Determine if we should use the SSH or Rsync protocol"
        if job.ssh:
            ret = self.executeRsyncViaSshProtocol(job, latest)
        else:
            ret = self.executeRsyncViaRsyncProtocol(job, latest)
        return ret
        
    def executeRsyncViaRsyncProtocol(self, job, latest):
        dir = job.backupdir.rstrip('/') + "/" + job.hostname + "/current"
        options = "--contimeout=5 -aR --delete --stats"
        rsyncpath = "/usr/bin/rsync"
        
        if(latest):
            command = "export RSYNC_PASSWORD=\"%s\"; %s %s --link-dest=%s %s %s" % (job.password, rsyncpath, options, latest, self.generateFileset(job), dir)
        else:
            command = "export RSYNC_PASSWORD=\"%s\"; %s %s %s %s" % (job.password, rsyncpath, options, self.generateFileset(job), dir)
        print command
    
    def executeRsyncViaSshProtocol(self, job, latest):
        """TODO: Needs to be implemented"""
        # rsync -aR --delete --stats -e ssh root@stage1.netwerven.nl:/etc root@stage1.netwerven.nl:/var/spool/cron/crontabs /var/data/backups/autorsyncbackup/stage1.netwerven.nl/current/
        print "executeRsyncViaSshProtocol - Needs to be implemented"
        return False
        
    def generateFileset(self, job):
        if not job.fileset:
            print "ERROR: No fileset specified"
            return False
        fileset = ""
        for fs in job.fileset:
            if job.ssh:
                fileset = fileset + " %s@%s:%s" % (job.username, job.hostname, fs)
            else:
                fileset = fileset + " rsync://%s@%s:/%s%s" % (job.username, job.hostname, job.share, fs)
        return fileset