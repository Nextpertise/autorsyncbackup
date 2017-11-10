import glob, os, re, time, datetime, shutil
from models.job import job
from models.config import config
from models.jobrunhistory import jobrunhistory
from lib.rsync import rsync
from lib.logger import logger
from lib.command import command,  CommandException
from lib.statusemail import statusemail

class director():

    regexp_backupdirectory = r".*?(\d{4}-\d{2}-\d{2}_\d{2}-\d{2}-\d{2}_backup)\.(\d+)$"

    def getJobArray(self, jobpath=None):
        jobArray = []
        if jobpath is None:
            directory= config().jobconfigdirectory.rstrip('/')
            if(os.path.exists(directory)):
                os.chdir(directory)
                for filename in glob.glob("*.job"):
                    jobArray.append(job(directory + "/" + filename))
            else:
                logger().error("Job directory (%s) doesn't exists, exiting (1)" % directory)
        else:
            jobArray.append(job(jobpath))

        return jobArray

    def checkRemoteHost(self, job):
        return rsync().checkRemoteHost(job)

    def executeJobs(self,  job,  commands):
        comm = command()
        for c in commands:
            if c['local']:
                logger().debug('Running local command %s' % c['script'])
                c['returncode'],  c['stdout'],  c['stderr'] = comm.executeLocalCommand(job,  c['script'])
                logger().debug('command %s' % ('succeeded' if c['returncode'] == 0 else 'failed'))
            else:
                logger().debug('Running remote command %s' % c['script'])
                c['returncode'],  c['stdout'],  c['stderr'] =  comm.executeRemoteCommand(job,  c['script'])
                logger().debug('command %s' % ('succeeded' if c['returncode'] == 0 else 'failed'))
            if c['returncode'] != 0 and c['continueonerror'] == False:
                logger().debug('command failed and continueonerror = false: exception')
                raise CommandException('Hook %s failed to execute' % c['script'])

    def executeRsync(self, job, latest):
        job.backupstatus['startdatetime'] = 0
        job.backupstatus['enddatetime'] = 0
        try:
            self.executeJobs(job, job.beforeLocalHooks)
            self.executeJobs(job, job.beforeRemoteHooks)
        except CommandException as e:
            logger().error("Required command failed (%s), skipping remainder of job" % e)
            job.backupstatus['rsync_backup_status'] = 0
            job.backupstatus['rsync_stdout'] = "No output due to failed required 'Before' command"
            return 0;
        job.backupstatus['startdatetime'] = int(time.time())
        ret = rsync().executeRsync(job, latest)
        job.backupstatus['enddatetime'] = int(time.time())
        try:
            self.executeJobs(job, job.afterRemoteHooks)
            self.executeJobs(job, job.afterLocalHooks)
        except CommandException as e:
            logger().error("Required command failed (%s), skipping remainder of job" % e)
            return 0;
        return ret

    def checkBackupEnvironment(self, job):
        backupdir = job.backupdir.rstrip('/')
        try:
            if not os.path.exists(backupdir):
                os.makedirs(backupdir)
                logger().info("Backup path (%s) created" % backupdir)

            directory = backupdir + "/" + job.hostname + "/daily"
            if not os.path.exists(directory):
                os.makedirs(directory)

            directory = backupdir + "/" + job.hostname + "/weekly"
            if not os.path.exists(directory):
                os.makedirs(directory)

            directory = backupdir + "/" + job.hostname + "/monthly"
            if not os.path.exists(directory):
                os.makedirs(directory)

            self._moveLastBackupToCurrentBackup(job)

            directory = backupdir + "/" + job.hostname + "/current"
            if not os.path.exists(directory):
                os.makedirs(directory)
        except Exception as e:
            logger().error("Error creating backup directory (%s) for host (%s)" % (directory, job.hostname))
            statusemail().sendSuddenDeath(e)
            return False

    def checkForPreviousBackup(self, job):
        latest = job.backupdir.rstrip('/') + "/" + job.hostname + "/latest"
        if os.path.exists(latest):
            return latest
        else:
            return False

    def getBackups(self, job, directory=''):
        retlist = []
        if directory == '':
            directory = self.getWorkingDirectory()
        directory = job.backupdir.rstrip('/') + "/" + job.hostname + "/" + directory
        try:
            dirlist = os.listdir(directory)
            for l in dirlist:
                if re.match(self.regexp_backupdirectory, l):
                    retlist.append(l)
        except:
            logger().error("Error while listing working directory (%s) for host (%s)" % (directory, job.hostname))
        return retlist

    def getBackupsSize(self, job):
        size = 0
        values = []
        latest = os.path.realpath(job.backupdir.rstrip('/') + "/" + job.hostname + "/latest")
        daily_path = job.backupdir.rstrip('/') + "/" + job.hostname + "/daily"
        jrh = jobrunhistory(check = True)
        for interval in ['daily', 'weekly', 'monthly']:
            dirlist = self.getBackups(job, interval)
            for directory in dirlist:
                jobRow = jrh.identifyJob(job, directory)
                if not jobRow:
                    continue
                if interval == 'daily':
                    values.append(jobRow[3] or 0)
                if latest == daily_path + "/" + directory:
                    size += jobRow[2] or 0
                else:
                    size += jobRow[3] or 0
        jrh.closeDbHandler()
        avg = sum(values) / len(values) if values else 0
        return size, avg

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

    def getOldestBackupId(self, job):
        dirlist = self.getBackups(job)
        ret = False
        backup_id = 0
        for l in dirlist:
            if self.getIdfromBackupInstance(l) >= backup_id:
                ret = backup_id = self.getIdfromBackupInstance(l)
        return ret

    def backupRotate(self, job, moveCurrent = True):
        # Check if we need to remove the oldest backup(s)
        self._unlinkExpiredBackups(job)

        # Rotate backups
        if(self._rotateBackups(job)):
            latest = self._moveCurrentBackup(job)
            if latest:
                if(self._updateLatestSymlink(job, latest)):
                    pass
                else:
                    logger().error("Error updating current symlink for host: %s" % job.hostname)
            else:
                logger().error("Error moving current backup failed for host: %s" % job.hostname)
        else:
            logger().error("Error rotating backups for host: %s" % job.hostname)

    def _unlinkExpiredBackups(self, job):
        workingDirectory = self.getWorkingDirectory()

        """Unlink oldest backup(s) if applicable"""
        directory = job.backupdir.rstrip('/') + "/" + job.hostname + "/" + workingDirectory

        if not self.checkWorkingDirectory(workingDirectory):
            logger().error("Error working directory not found (%s)" % directory)
            return False

        backupRetention = int(getattr(job, workingDirectory + "rotation"))

        for l in self.getBackups(job):
            if self.getIdfromBackupInstance(l):
                if self.getIdfromBackupInstance(l) > (backupRetention - 1):
                    self._unlinkExpiredBackup(job, directory + "/" + l)
        return True

    def _unlinkExpiredBackup(self, job, backupdirectory):
        ret = True
        logger().debug("Unlink expired backup (rm -rf %s)" % backupdirectory)
        try:
            shutil.rmtree(backupdirectory)
        except:
            logger().error("Error while removing (%s)" % backupdirectory)
            ret = False
        return ret

    def _rotateBackups(self, job):
        """Rotate backups"""
        ret = True
        directory = job.backupdir.rstrip('/') + "/" + job.hostname + "/" + self.getWorkingDirectory()
        backup_id = self.getOldestBackupId(job)
        while id >= 0:
            cur = "%s/*.%s" % (directory, backup_id)
            cur = glob.glob(cur)
            if cur:
                cur = os.path.basename(cur[0])
                cur = self.getNamefromBackupInstance(cur)
                if cur is not False:
                    src = "%s/%s.%s" % (directory, cur, backup_id)
                    dest = "%s/%s.%s" % (directory, cur, (backup_id + 1))

                    try:
                        os.rename(src, dest)
                    except:
                        ret = False

                    logger().debug("mv %s %s" % (src, dest))
                    backup_id = backup_id - 1
                else:
                    ret = False
            else:
                return ret
        return ret

    def _moveCurrentBackup(self, job):
        """Move current backup"""
        src = job.backupdir.rstrip('/') + "/" + job.hostname + "/current"

        # BackupDirectoryInstance format: 2015-10-27_04-56-59_backup.0
        folder = datetime.datetime.today().strftime("%Y-%m-%d_%H-%M-%S_backup.0")
        ret = self.getWorkingDirectory() + "/" + folder
        dest = job.backupdir.rstrip('/') + "/" + job.hostname + "/" + ret

        try:
            os.rename(src, dest)
        except:
            ret = False

        logger().debug("mv %s %s " % (src, dest))
        return ret

    def _updateLatestSymlink(self, job, latest):
        ret = True
        symlinkfile = job.backupdir.rstrip('/') + "/" + job.hostname + "/latest"
        logger().debug("Create symlink to latest backup (ln -s %s %s" % (latest, symlinkfile))
        try:
            os.unlink(symlinkfile)
        except:
            pass
        try:
            os.symlink(latest, symlinkfile)
        except:
            ret = False
        return ret

    def _moveLastBackupToCurrentBackup(self, job):
        """Move last backup (expired) backup instance to current directory"""
        workingDirectory = self.getWorkingDirectory()
        rotation = 0
        try:
            rotation = getattr(job, workingDirectory + 'rotation')
        except:
            pass

        oldestId = self.getOldestBackupId(job)
        if rotation > 0 and oldestId >= rotation:
            src = job.backupdir.rstrip('/') + "/" + job.hostname + "/" + workingDirectory + "/*." + str(oldestId)
            dest = job.backupdir.rstrip('/') + "/" + job.hostname + "/current"
            g = glob.glob(src)
            if not len(g) == 1:
                errorMsg = "More than one directory matching on glob(%s)" % src
                logger().error(errorMsg)
                raise Exception(errorMsg)
            if os.path.exists(dest):
                logger().info("Do not move oldest backup (%s) because current directory already exists")
                return True
            ret = True
            try:
                os.rename(g[0], dest)
                logger().info("mv %s %s" % (g[0], dest))
            except:
                ret = False
            return ret

    def getWorkingDirectory(self):
        """Check in which folder we place the backup today"""
        ret = "daily"
        if(int(datetime.datetime.today().strftime("%w")) == config().weeklybackup):
            ret = "weekly"
        if(int(datetime.datetime.today().strftime("%d")) == config().monthlybackup):
            ret = "monthly"
        return ret

    def sanityCheckWorkingDirectory(self, job):
        src = job.backupdir.rstrip('/') + "/" + job.hostname + "/" + self.getWorkingDirectory() + "/*.*"
        dirlist = glob.glob(src)
        found_ids = []
        ret = True

        # Check for duplicate id's
        for l in dirlist:
            backup_id = self.getIdfromBackupInstance(l)
            if backup_id in found_ids:
                ret = False
            found_ids.append(backup_id)

        # Check sequence
        for backup_id in range(0, self.getOldestBackupId(job)):
            if backup_id not in found_ids:
                ret = False

        if ret:
            logger().debug("Sanity check passed for: %s in folder: %s" % (job.hostname, self.getWorkingDirectory()))
        else:
            logger().error("Sanity check failed for: %s in folder: %s" % (job.hostname, self.getWorkingDirectory()))
        job.backupstatus['sanity_check'] = int(ret)
        return ret

    # Checks
    def checkWorkingDirectory(self, workingDirectory):
        """Check if workingDirectory is daily/weekly/monthly"""
        check = ["daily", "weekly", "monthly"]
        return workingDirectory in check

    def processBackupStatus(self, job):
        job.backupstatus['hostname'] = job.hostname
        if(job.ssh):
            ssh = 'True'
            job.backupstatus['username'] = job.sshusername
        else:
            ssh = 'False'
            job.backupstatus['username'] = job.rsyncusername
        job.backupstatus['ssh'] = ssh
        job.backupstatus['share'] = job.rsyncshare
        job.backupstatus['include'] = ':'.join(job.include)
        job.backupstatus['exclude'] = ':'.join(job.exclude)
        job.backupstatus['backupdir'] = job.backupdir
        job.backupstatus['speedlimitkb'] = job.speedlimitkb
        job.backupstatus['type'] = self.getWorkingDirectory()
        self.parseRsyncOutput(job)
        jrh = jobrunhistory(check = True)
        jrh.insertJob(job.backupstatus,  job.hooks)
        jrh.closeDbHandler()

    def parseRsyncOutput(self, job):
        regexps = {
            'rsync_number_of_files'             : r"^.*Number of files: (\d[\d,]*).*$",
            'rsync_number_of_files_transferred' : r"^.*Number of .*files transferred: (\d[\d,]*).*$",
            'rsync_total_file_size'             : r"^.*Total file size: (\d[\d,]*).*$",
            'rsync_total_transferred_file_size' : r"^.*Total transferred file size: (\d[\d,]*).*$",
            'rsync_literal_data'                : r"^.*Literal data: (\d[\d,]*).*$",
            'rsync_matched_data'                : r"^.*Matched data: (\d[\d,]*).*$",
            'rsync_file_list_size'              : r"^.*File list size: (\d[\d,]*).*$",
            'rsync_file_list_generation_time'   : r"^.*File list generation time: (\d+\.\d*).*$",
            'rsync_file_list_transfer_time'     : r"^.*File list transfer time: (\d+\.\d*).*$",
            'rsync_total_bytes_sent'            : r"^.*Total bytes sent: (\d[\d,]*).*$",
            'rsync_total_bytes_received'        : r"^.*Total bytes received: (\d[\d,]*).*$"
        }
        strings = job.backupstatus['rsync_stdout']
        job.backupstatus['rsync_stdout'] = strings[:10000]
        for key in regexps.keys():
            try:
                logger().debug("matching %s for %s" % (regexps[key], key))
                m = re.match(regexps[key],  strings,  re.MULTILINE | re.DOTALL)
                if m:
                    job.backupstatus[key] = m.group(1).replace(',',  '')
                else:
                    job.backupstatus[key] = ''
                    logger().debug("no match!")
            except:
                job.backupstatus[key] = ''
                logger().debug("FAILING regexp[%s] %s" % (key, regexps[key]))
