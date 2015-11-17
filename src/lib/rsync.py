from models.config import config
from lib.logger import logger
import subprocess

class rsync():
    
    def checkRemoteHost(self, job):
        """Determine if we should use the SSH or Rsync protocol"""
        if job.ssh:
            ret = self.checkRemoteHostViaSshProtocol(job)
        else:
            ret = self.checkRemoteHostViaRsyncProtocol(job)
        return ret
    
    def checkRemoteHostViaRsyncProtocol(self, job):
        """Check if remote host is up and able to accept connections with our credentials"""
        command = "export RSYNC_PASSWORD=\"%s\"; rsync --contimeout=5 rsync://%s@%s/%s" % (job.password, job.username, job.hostname, job.share)
        errcode, stdout = self.executeCommand(command)
        
        if errcode != 0:
            logger().error("Error while connecting to host (%s) - %s" % (errcode, stdout))
            ret = False
        else:
            ret = True
            logger().info("INFO: Succesfully connected to host via rsync protocol (%s)" % job.hostname)
        
        return ret
          
    def checkRemoteHostViaSshProtocol(self, job):
        """TODO: Needs to be implemented"""
        logger().info("INFO: checkRemoteHostViaSshProtocol - Needs to be implemented")
        return False
        
    def executeRsync(self, job, latest):
        """Determine if we should use the SSH or Rsync protocol"""
        if job.ssh:
            ret = self.executeRsyncViaSshProtocol(job, latest)
        else:
            ret = self.executeRsyncViaRsyncProtocol(job, latest)
        ret = self.rsyncErrorCodeToBoolean(ret[0])
        job.backupstatus['rsync_backup_status'] = int(ret)
        return ret
        
    def executeRsyncViaRsyncProtocol(self, job, latest):
        """Execute rsync command via rsync protocol"""
        dir = job.backupdir.rstrip('/') + "/" + job.hostname + "/current"
        options = "--contimeout=5 -aR --delete --stats --bwlimit=%d" % job.speedlimitkb
        fileset = self.generateFileset(job)        
        
        # Link files to the same inodes as last backup to save disk space and boost backup performance
        if(latest):
            latest = "--link-dest=%s" % latest
        else:
            latest = ""
        
        # Generate rsync CLI command and execute it  
        if(fileset):  
            password = "export RSYNC_PASSWORD=\"%s\"" % job.password
            rsyncCommand = "%s %s %s %s %s" % (config().rsyncpath, options, latest, fileset, dir)
            command = "%s; %s" % (password, rsyncCommand)
            if config().debug:
                logger().debug("DEBUG: Executing rsync command (%s)" % rsyncCommand)
            errcode, stdout = self.executeCommand(command)
        else:
            stdout = "Fileset is missing, Rsync is never invoked"
            errcode = 9
        
        job.backupstatus['rsync_stdout'] = stdout
        job.backupstatus['rsync_return_code'] = errcode
        return errcode, stdout
    
    def executeRsyncViaSshProtocol(self, job, latest):
        """TODO: Needs to be implemented"""
        # rsync -aR --delete --stats -e ssh root@stage1.netwerven.nl:/etc root@stage1.netwerven.nl:/var/spool/cron/crontabs /var/data/backups/autorsyncbackup/stage1.netwerven.nl/current/
        logger().info("INFO: executeRsyncViaSshProtocol - Needs to be implemented")
        return False
        
    def generateFileset(self, job):
        """Create fileset string"""
        if not job.fileset:
            logger().error("ERROR: No fileset specified")
            return False
        fileset = ""
        for fs in job.fileset:
            if job.ssh:
                fileset = fileset + " %s@%s:%s" % (job.username, job.hostname, fs)
            else:
                fileset = fileset + " rsync://%s@%s:/%s%s" % (job.username, job.hostname, job.share, fs)
        return fileset
    
    def executeCommand(self, command):
        stdout = ""
        errcode = 0
        try:
            stdout = subprocess.check_output(command, stderr=subprocess.STDOUT, shell=True)
        except subprocess.CalledProcessError as exc:
            stdout = exc.output
            errcode = exc.returncode
        return errcode, stdout
        
    def rsyncErrorCodeToBoolean(self, errorCode):
        ret = False
        if errorCode == 0:
            ret = True
        elif errorCode == 23:
            ret = True
        elif errorCode == 24:
            ret = True
        return ret