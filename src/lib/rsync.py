from models.config import config
from lib.logger import logger
import subprocess, paramiko, time, socket;

class rsync():

    def checkRemoteHost(self, job):
        """Determine if we should use the SSH or Rsync protocol"""
        if job.ssh:
            ret = self.checkRemoteHostViaSshProtocol(job)
        else:
            ret = self.checkRemoteHostViaRsyncProtocol(job)
        job.backupstatus['rsync_backup_status'] = int(ret)
        return ret

    def checkRemoteHostViaRsyncProtocol(self, job):
        """Check if remote host is up and able to accept connections with our credentials"""
        password = "export RSYNC_PASSWORD=\"%s\"" % job.rsyncpassword
        rsyncCommand = "rsync --contimeout=5 rsync://%s@%s:%s/%s" % (job.rsyncusername, job.hostname, job.port, job.rsyncshare)
        command = "%s; %s" % (password, rsyncCommand)
        logger().info("Executing rsync check (%s)" % rsyncCommand)
        errcode, stdout = self.executeCommand(command)

        if errcode != 0:
            logger().error("Error while connecting to host (%s) - %s" % (job.hostname, stdout))
            job.backupstatus['startdatetime'] = int(time.time())
            job.backupstatus['enddatetime'] = int(time.time())
            job.backupstatus['hostname'] = job.hostname
            job.backupstatus['rsync_stdout'] = "Error while connecting to host (%s) - %s" % (job.hostname, stdout)
            ret = False
        else:
            ret = True
            logger().info("Succesfully connected to host via rsync protocol (%s)" % job.hostname)

        return ret

    def checkRemoteHostViaSshProtocol(self, job, initial_wait=0, interval=0, retries=1):
        status = None
        ssh = paramiko.SSHClient()
        ssh.set_missing_host_key_policy(paramiko.AutoAddPolicy())
        time.sleep(initial_wait)
        for x in range(retries):
            try:
                ssh.connect(job.hostname, username=job.sshusername, key_filename=job.sshprivatekey)
                logger().info("Succesfully connected to host via ssh protocol (%s)" % job.hostname)
                return True
            except (paramiko.BadHostKeyException, paramiko.AuthenticationException, paramiko.SSHException, socket.error, IOError) as e:
                status = "Error while connecting to host (%s) - %s" % (job.hostname, e)
                logger().error(status)
                time.sleep(interval)
        job.backupstatus['startdatetime'] = int(time.time())
        job.backupstatus['enddatetime'] = int(time.time())
        job.backupstatus['hostname'] = job.hostname
        job.backupstatus['rsync_stdout'] = status
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
            password = "export RSYNC_PASSWORD=\"%s\"" % job.rsyncpassword
            rsyncCommand = "%s %s %s %s %s" % (config().rsyncpath, options, latest, fileset, dir)
            command = "%s; %s" % (password, rsyncCommand)
            logger().info("Executing rsync command (%s)" % rsyncCommand)
            errcode, stdout = self.executeCommand(command)
        else:
            stdout = "Fileset is missing, Rsync is never invoked"
            errcode = 9

        job.backupstatus['rsync_stdout'] = stdout
        job.backupstatus['rsync_return_code'] = errcode
        return errcode, stdout

    def executeRsyncViaSshProtocol(self, job, latest):
        dir = job.backupdir.rstrip('/') + "/" + job.hostname + "/current"
        sshoptions = "-e 'ssh -p%d -i %s -o \"PasswordAuthentication no\"'" % (job.port, job.sshprivatekey)
        options = "-aR %s --delete --stats --bwlimit=%d" % (sshoptions, job.speedlimitkb)
        fileset = self.generateFileset(job)

        # Link files to the same inodes as last backup to save disk space and boost backup performance
        if(latest):
            latest = "--link-dest=%s" % latest
        else:
            latest = ""

        # Generate rsync CLI command and execute it
        if(fileset):
            command = "%s %s %s %s %s" % (config().rsyncpath, options, latest, fileset, dir)
            logger().info("Executing rsync command (%s)" % command)
            errcode, stdout = self.executeCommand(command)
        else:
            stdout = "Fileset is missing, Rsync is never invoked"
            errcode = 9

        job.backupstatus['rsync_stdout'] = stdout
        job.backupstatus['rsync_return_code'] = errcode
        return errcode, stdout

    def generateFileset(self, job):
        """Create fileset string"""
        if not job.fileset:
            logger().error("No fileset specified")
            return False
        fileset = ""
        for fs in job.fileset:
            if job.ssh:
                fileset = fileset + " %s@%s:%s" % (job.sshusername, job.hostname, fs)
            else:
                fileset = fileset + " rsync://%s@%s:%s/%s%s" % (job.rsyncusername, job.hostname, job.port, job.rsyncshare, fs)
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
