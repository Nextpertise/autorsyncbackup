import glob, os, re, time, datetime, shutil
from models.job import job
from models.config import config
from models.jobrunhistory import jobrunhistory
from lib.rsync import rsync

class director():
    
    regexp_backupdirectory = r"^(\d{4}-\d{2}-\d{2}_\d{2}-\d{2}-\d{2}_backup)\.(\d+)$"

    def getJobArray(self, jobpath):
        jobArray = []
        if jobpath is None:
            dir = config().jobconfigdirectory.rstrip('/')
            if(os.path.exists(dir)):
                os.chdir(dir)
                for file in glob.glob("*.job"):
                    jobArray.append(job(dir + "/" + file))
            else:
                print "Job directory (%s) doesn't exists, exiting (1)" % dir
        else:
            jobArray.append(job(jobpath))
            
        return jobArray
        
    def checkRemoteHost(self, job):
        return rsync().checkRemoteHost(job)
        
    def executeRsync(self, job, latest):
        job.backupstatus['startdatetime'] = int(time.time())
        ret = rsync().executeRsync(job, latest)
        job.backupstatus['enddatetime'] = int(time.time())
        return ret
        
    def checkBackupEnvironment(self, job):
        backupdir = job.backupdir.rstrip('/')
        if not os.path.exists(backupdir):
            print "Backup path (%s) doesn't exists" % backupdir
            return False
        try:
            dir = backupdir + "/" + job.hostname + "/current"
            if not os.path.exists(dir):
                os.makedirs(dir)
            dir = backupdir + "/" + job.hostname + "/daily"
            if not os.path.exists(dir):
                os.makedirs(dir)
            dir = backupdir + "/" + job.hostname + "/weekly"
            if not os.path.exists(dir):
                os.makedirs(dir)
            dir = backupdir + "/" + job.hostname + "/monthly"
            if not os.path.exists(dir):
                os.makedirs(dir)
        except:
            print "Error creating backup directory (%s) for host (%s)" % (dir, job.hostname)
            return False
    
    def checkForPreviousBackup(self, job):
        latest = job.backupdir.rstrip('/') + "/" + job.hostname + "/latest"
        if os.path.exists(latest):
            return latest
        else:
            return False
            
    def getBackups(self, job, workingDirectory):
        dir = job.backupdir.rstrip('/') + "/" + job.hostname + "/" + workingDirectory
        try:
            list = os.listdir(dir)
        except:
            print "Error while listing working directory (%s) for host (%s)" % (dir, job.hostname)
            retlist = False
        retlist = []
        if(list):
            for l in list:
                if re.match(self.regexp_backupdirectory, l):
                    retlist.append(l)
        return retlist
        
    def getIdfromBackupInstance(self, backupDirectoryInstance):
        ret = False
        p = re.compile(self.regexp_backupdirectory)
        m = p.match(backupDirectoryInstance)
        if m:
            ret = int(m.group(2))
        return ret
        
    def getNamefromBackupInstance(self, backupDirectoryInstance):
        ret = False
        p = re.compile(self.regexp_backupdirectory)
        m = p.match(backupDirectoryInstance)
        if m:
            ret = m.group(1)
        return ret  
        
    def getOldestBackupId(self, job, workingDirectory):
        list = self.getBackups(job, workingDirectory)
        ret = False
        id = 0
        for l in list:
            if self.getIdfromBackupInstance(l) >= id:
                ret = id = self.getIdfromBackupInstance(l)
        return ret            
            
    def backupRotate(self, job, moveCurrent = True):
        workingDirectory = self.getWorkingDirectory()
        
        # Check if we need to remove the oldest backup(s)
        self._unlinkExpiredBackups(job, workingDirectory)
        
        # Rotate backups
        if(self._rotateBackups(job, workingDirectory)):
            latest = self._moveCurrentBackup(job, workingDirectory)
            if latest:
                if(self._updateLatestSymlink(job, latest)):
                    pass
                else:
                    print "Error updating current symlink for host: %s" % job.hostname
            else:
                print "Error moving current backup failed for host: %s" % job.hostname
        else:
            print "Error rotating backups for host: %s" % job.hostname
        
    def _unlinkExpiredBackups(self, job, workingDirectory):
        """Unlink oldest backup(s) if applicable"""
        dir = job.backupdir.rstrip('/') + "/" + job.hostname + "/" + workingDirectory
        
        if not self.checkWorkingDirectory(workingDirectory):
          print "Error working directory not found (%s)" % dir
          return False

        backupRetention = int(getattr(job, workingDirectory + "rotation"))
        
        for l in self.getBackups(job, workingDirectory):
            if self.getIdfromBackupInstance(l):
                if self.getIdfromBackupInstance(l) > (backupRetention - 1):
                    self._unlinkExpiredBackup(job, dir + "/" + l)
        return True
        
    def _unlinkExpiredBackup(self, job, backupdirectory):
        ret = True
        if config().debug:
            print "DEBUG: Unlink expired backup (rm -rf %s)" % backupdirectory
        try:
            shutil.rmtree(backupdirectory)
        except:
            print "Error while removing (%s)" % backupdirectory
            ret = False
        return ret
        
    def _rotateBackups(self, job, workingDirectory):
        """Rotate backups"""
        ret = True
        dir = job.backupdir.rstrip('/') + "/" + job.hostname + "/" + workingDirectory
        id = self.getOldestBackupId(job, workingDirectory)
        while id >= 0:
            cur = "%s/*.%s" % (dir, id)
            cur = glob.glob(cur)
            if cur:
                cur = os.path.basename(cur[0])
                cur = self.getNamefromBackupInstance(cur)
                if cur is not False:
                    src = "%s/%s.%s" % (dir, cur, id)
                    dest = "%s/%s.%s" % (dir, cur, (id + 1))
                    
                    try:
                        os.rename(src, dest)
                    except:
                        ret = False
                    
                    if config().debug:
                        print "DEBUG: mv %s %s" % (src, dest) 
                    id = id - 1
                else:
                    ret = False
            else:
                return ret
        return ret
        
    def _moveCurrentBackup(self, job, workingDirectory):
        """Move current backup"""
        src = job.backupdir.rstrip('/') + "/" + job.hostname + "/current"
        
        # BackupDirectoryInstance format: 2015-10-27_04-56-59_backup.0
        folder = datetime.datetime.today().strftime("%Y-%m-%d_%H-%M-%S_backup.0")
        ret = workingDirectory + "/" + folder
        dest = job.backupdir.rstrip('/') + "/" + job.hostname + "/" + ret
        
        try:
            os.rename(src, dest)
        except:
            ret = False
        
        if config().debug:
            print "DEBUG: mv %s %s " % (src, dest)
        return ret
    
    def _updateLatestSymlink(self, job, latest):
        ret = True
        symlinkfile = job.backupdir.rstrip('/') + "/" + job.hostname + "/latest"
        if config().debug:
            print "DEBUG: Create symlink to latest backup (ln -s %s %s" % (latest, symlinkfile)
        try:
            os.unlink(symlinkfile)
        except:
            pass
        try:
            os.symlink(latest, symlinkfile)
        except:
            ret = false
        return ret

    def getWorkingDirectory(self):
        """Check in which folder we place the backup today"""
        ret = "daily"
        if(int(datetime.datetime.today().strftime("%w")) == config().weeklybackup):
            ret = "weekly"
        if(int(datetime.datetime.today().strftime("%d")) == config().monthlybackup):
            ret = "monthly"
        return ret
    
    # Checks
    def checkWorkingDirectory(self, workingDirectory):
        """Check if workingDirectory is daily/weekly/monthly"""
        check = ["daily", "weekly", "monthly"]
        return workingDirectory in check
        
    def processBackupStatus(self, job):
        job.backupstatus['hostname'] = job.hostname
        job.backupstatus['username'] = job.username
        if(job.ssh):
            ssh = 'True'
        else:
            ssh = 'False'
        job.backupstatus['ssh'] = ssh
        job.backupstatus['share'] = job.share
        job.backupstatus['fileset'] = ':'.join(job.fileset)
        job.backupstatus['backupdir'] = job.backupdir
        job.backupstatus['type'] = self.getWorkingDirectory()
        p = re.compile(r"^\s*?Number of files: (\d+)\s*Number of files transferred: (\d+)\s*Total file size: (\d+) bytes\s*Total transferred file size: (\d+)\s* bytes\s*Literal data: (\d+) bytes\s*Matched data: (\d+) bytes\s*File list size: (\d+)\s*File list generation time: (\S+)\s* seconds?\s*File list transfer time: (\S+)\s*seconds?\s*Total bytes sent: (\d+)\s*Total bytes received: (\d+)(\s|\S)*$")
        m = p.match(job.backupstatus['rsync_stdout'])
        if m:
            job.backupstatus['rsync_number_of_files'] = m.group(1)
            job.backupstatus['rsync_number_of_files_transferred'] =  m.group(2)
            job.backupstatus['rsync_total_file_size'] =  m.group(3)
            job.backupstatus['rsync_total_transferred_file_size'] =  m.group(4)
            job.backupstatus['rsync_literal_data'] =  m.group(5)
            job.backupstatus['rsync_matched_data'] =  m.group(6)
            job.backupstatus['rsync_file_list_size'] =  m.group(7)
            job.backupstatus['rsync_file_list_generation_time'] =  float(m.group(8))
            job.backupstatus['rsync_file_list_transfer_time'] =  float(m.group(9))
            job.backupstatus['rsync_total_bytes_sent'] =  m.group(10)
            job.backupstatus['rsync_total_bytes_received'] =  m.group(11)
            
        jobrunhistory().insertJob(job.backupstatus)