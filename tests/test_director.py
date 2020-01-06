import base64
import email
import glob
import io
import os
import re
import time

import mailer
import paramiko
import pytest

from lib.command import CommandException
from lib.director import director
from lib.logger import logger
from models.config import config
from models.job import job
from models.jobrunhistory import jobrunhistory


def create_job(dir):
    path = os.path.join(
                         dir,
                         'localhost.job',
                       )

    backup_path = os.path.join(
                                dir,
                                'backups',
                              )

    options = {
                'hostname':       'localhost',
                'rsync_username': 'autorsyncbackup',
                'rsync_password': 'fee-fi-fo-fum',
                'rsync_share':    'backup',
                'backupdir':      backup_path,
                'include':        ['/etc'],
              }

    with open(path, 'w') as f:
        for key in options:
            if key == 'include':
                f.write("%s:\n" % key)
                for item in options[key]:
                    f.write("  - %s\n" % item)
            else:
                f.write("%s: %s\n" % (key, options[key]))

    return path


def test_getJobArray(test_config, tmp_path):
    config().jobconfigdirectory = os.path.join(
                                                os.path.dirname(__file__),
                                                'etc/director',
                                              )
    config().jobspooldirectory = str(tmp_path)

    d = director()

    jobs = d.getJobArray()

    assert type(jobs) is list
    assert len(jobs) == 2


def test_getJobArray_error(test_config, tmp_path, caplog):
    path = '/non-existent'

    config().jobconfigdirectory = path
    config().jobspooldirectory = str(tmp_path)

    logger().debuglevel = 3

    d = director()

    jobs = d.getJobArray()

    assert type(jobs) is list
    assert len(jobs) == 0

    assert "Job directory (%s) doesn't exists, exiting" % path in caplog.text


def test_getJobArray_jobpath(test_config, tmp_path):
    config().jobspooldirectory = str(tmp_path)

    path = os.path.join(
                         os.path.dirname(__file__),
                         'etc/localhost.job',
                       )

    d = director()

    jobs = d.getJobArray(path)

    assert type(jobs) is list
    assert len(jobs) == 1


def test_checkRemoteHost(test_config, tmp_path):
    config().jobspooldirectory = str(tmp_path)
    config().rsyncpath = os.path.join(
                                       os.path.dirname(__file__),
                                       'bin/mock-rsync-ok.sh',
                                     )

    path = os.path.join(
                         os.path.dirname(__file__),
                         'etc/rsync.job',
                       )

    j = job(path)

    d = director()

    ret = d.checkRemoteHost(j)

    assert ret is True
    assert j.backupstatus['rsync_backup_status'] == int(ret)


def test_executeJobs_local(test_config, tmp_path):
    config().jobspooldirectory = str(tmp_path)

    path = os.path.join(
                         os.path.dirname(__file__),
                         'etc/localhost.job',
                       )

    j = job(path)

    commands = [
                 {
                   'local':           True,
                   'script':          'uptime',
                   'runtime':         'before',
                   'continueonerror': True,
                 },
               ]

    d = director()

    d.executeJobs(j, commands)

    assert commands[0]['returncode'] == 0
    assert 'load average' in commands[0]['stdout']
    assert commands[0]['stderr'] == ''


def test_executeJobs_remote(test_config, tmp_path, monkeypatch):
    def mock_connect(self, hostname, username=None, key_filename=None):
        return True

    def mock_exec_command(self, command):
        stdin = io.StringIO('')
        stdout = io.StringIO('Mock STDOUT\n0')
        stderr = io.StringIO('')

        return stdin, stdout, stderr

    monkeypatch.setattr(paramiko.SSHClient, 'connect', mock_connect)
    monkeypatch.setattr(paramiko.SSHClient, 'exec_command', mock_exec_command)

    config().jobspooldirectory = str(tmp_path)

    path = os.path.join(
                         os.path.dirname(__file__),
                         'etc/localhost.job',
                       )

    j = job(path)

    commands = [
                 {
                   'local':           False,
                   'script':          'uptime',
                   'runtime':         'before',
                   'continueonerror': True,
                 },
               ]

    d = director()

    d.executeJobs(j, commands)

    assert commands[0]['returncode'] == 0
    assert commands[0]['stdout'] == 'Mock STDOUT\n'
    assert commands[0]['stderr'] == ''


def test_executeJobs_exception(test_config, tmp_path):
    config().jobspooldirectory = str(tmp_path)

    path = os.path.join(
                         os.path.dirname(__file__),
                         'etc/localhost.job',
                       )

    j = job(path)

    commands = [
                 {
                   'local':           True,
                   'script':          'false',
                   'runtime':         'before',
                   'continueonerror': False,
                 },
               ]

    d = director()

    with pytest.raises(CommandException) as e:
        d.executeJobs(j, commands)

    assert commands[0]['returncode'] == 1
    assert commands[0]['stdout'] == ''
    assert commands[0]['stderr'] == ''

    assert 'Hook %s failed to execute' % commands[0]['script'] in str(e)


def test_executeRsync(test_config, tmp_path):
    config().jobspooldirectory = str(tmp_path)
    config().rsyncpath = os.path.join(
                                       os.path.dirname(__file__),
                                       'bin/mock-rsync-ok.sh',
                                     )

    path = os.path.join(
                         os.path.dirname(__file__),
                         'etc/rsync.job',
                       )

    j = job(path)

    d = director()

    ret = d.executeRsync(j, None)

    assert ret == 1

    assert j.backupstatus['rsync_return_code'] == 0
    assert j.backupstatus['rsync_backup_status'] == 1
    assert 'startdatetime' in j.backupstatus
    assert 'enddatetime' in j.backupstatus


def test_executeRsync_local_before_fail(test_config, tmp_path, caplog):
    config().jobspooldirectory = str(tmp_path)

    logger().debuglevel = 3

    path = os.path.join(
                         os.path.dirname(__file__),
                         'etc/hooks-local-before-fail.job',
                       )

    j = job(path)

    d = director()

    ret = d.executeRsync(j, None)

    assert ret == 0

    assert 'Required command failed' in caplog.text

    assert j.backupstatus['rsync_backup_status'] == 0
    assert j.backupstatus['rsync_stdout'] == (
                                               "No output due to failed"
                                               " required 'Before' command"
                                             )


def test_executeRsync_remote_before_fail(
                                          test_config,
                                          tmp_path,
                                          caplog,
                                          monkeypatch
                                        ):
    def mock_connect(self, hostname, username=None, key_filename=None):
        return True

    def mock_exec_command(self, command):
        stdin = io.StringIO('')
        stdout = io.StringIO('1')
        stderr = io.StringIO('')

        return stdin, stdout, stderr

    monkeypatch.setattr(paramiko.SSHClient, 'connect', mock_connect)
    monkeypatch.setattr(paramiko.SSHClient, 'exec_command', mock_exec_command)

    config().jobspooldirectory = str(tmp_path)

    logger().debuglevel = 3

    path = os.path.join(
                         os.path.dirname(__file__),
                         'etc/hooks-remote-before-fail.job',
                       )

    j = job(path)

    d = director()

    ret = d.executeRsync(j, None)

    assert ret == 0

    assert 'Required command failed' in caplog.text

    assert j.backupstatus['rsync_backup_status'] == 0
    assert j.backupstatus['rsync_stdout'] == (
                                               "No output due to failed"
                                               " required 'Before' command"
                                             )


def test_executeRsync_local_after_fail(test_config, tmp_path, caplog):
    config().jobspooldirectory = str(tmp_path)
    config().rsyncpath = os.path.join(
                                       os.path.dirname(__file__),
                                       'bin/mock-rsync-ok.sh',
                                     )

    logger().debuglevel = 3

    path = os.path.join(
                         os.path.dirname(__file__),
                         'etc/hooks-local-after-fail.job',
                       )

    j = job(path)

    d = director()

    ret = d.executeRsync(j, None)

    assert ret == 0

    assert 'Required command failed' in caplog.text

    assert j.backupstatus['rsync_return_code'] == 0
    assert j.backupstatus['rsync_backup_status'] == 1
    assert 'startdatetime' in j.backupstatus
    assert 'enddatetime' in j.backupstatus


def test_executeRsync_remote_after_fail(
                                         test_config,
                                         tmp_path,
                                         caplog,
                                         monkeypatch
                                       ):
    def mock_connect(self, hostname, username=None, key_filename=None):
        return True

    def mock_exec_command(self, command):
        stdin = io.StringIO('')
        stdout = io.StringIO('1')
        stderr = io.StringIO('')

        return stdin, stdout, stderr

    monkeypatch.setattr(paramiko.SSHClient, 'connect', mock_connect)
    monkeypatch.setattr(paramiko.SSHClient, 'exec_command', mock_exec_command)

    config().jobspooldirectory = str(tmp_path)
    config().rsyncpath = os.path.join(
                                       os.path.dirname(__file__),
                                       'bin/mock-rsync-ok.sh',
                                     )

    logger().debuglevel = 3

    path = os.path.join(
                         os.path.dirname(__file__),
                         'etc/hooks-remote-after-fail.job',
                       )

    j = job(path)

    d = director()

    ret = d.executeRsync(j, None)

    assert ret == 0

    assert 'Required command failed' in caplog.text

    assert j.backupstatus['rsync_return_code'] == 0
    assert j.backupstatus['rsync_backup_status'] == 1
    assert 'startdatetime' in j.backupstatus
    assert 'enddatetime' in j.backupstatus


def test_checkBackupEnvironment(tmp_path):
    path = create_job(str(tmp_path))

    j = job(path)

    d = director()

    d.checkBackupEnvironment(j)

    for subdir in [
                    'daily',
                    'weekly',
                    'monthly',
                    'current',
                  ]:
        subdir_path = os.path.join(
                                    j.backupdir,
                                    j.hostname,
                                    subdir,
                                  )

        assert os.path.exists(subdir_path) is True
        assert os.path.isdir(subdir_path) is True


def test_checkBackupEnvironment_twice(tmp_path):
    path = create_job(str(tmp_path))

    j = job(path)

    d = director()

    d.checkBackupEnvironment(j)

    d.checkBackupEnvironment(j)

    for subdir in [
                    'daily',
                    'weekly',
                    'monthly',
                    'current',
                  ]:
        subdir_path = os.path.join(
                                    j.backupdir,
                                    j.hostname,
                                    subdir,
                                  )

        assert os.path.exists(subdir_path) is True
        assert os.path.isdir(subdir_path) is True


def test_checkBackupEnvironment_exception(
                                           test_config,
                                           tmp_path,
                                           monkeypatch,
                                           caplog,
                                         ):
    config().backupmailrecipients = ['root@localhost']

    exc = 'Mock makedirs failure'

    def mock_makedirs(path):
        raise IOError(exc)

    monkeypatch.setattr(os, 'makedirs', mock_makedirs)

    email_path = os.path.join(str(tmp_path), 'sudden-death.eml')

    def mock_send(self, message):
        with open(email_path, 'w') as f:
            f.write(message.as_string())

        return True

    monkeypatch.setattr(mailer.Mailer, 'send', mock_send)

    path = create_job(str(tmp_path))

    j = job(path)

    d = director()

    d.checkBackupEnvironment(j)

    assert 'Error creating backup directory' in caplog.text

    assert os.path.exists(email_path)

    text_body = None
    html_body = None

    with open(email_path) as f:
        msg = email.message_from_file(f)

        assert msg is not None
        assert msg.is_multipart() is True

        for part in msg.walk():
            content_type = part.get_content_type()

            assert content_type in [
                                     'multipart/alternative',
                                     'text/plain',
                                     'text/html',

                                   ]

            if content_type == 'multipart/alternative':
                continue

            body = part.get_payload()

            assert body is not None

            encoding = part.get('Content-Transfer-Encoding')

            if encoding is not None and encoding == 'base64':
                body = base64.b64decode(body)

            if content_type == 'text/plain':
                text_body = body.decode()
            elif content_type == 'text/html':
                html_body = body.decode()

    assert text_body is not None
    assert html_body is not None

    assert exc in text_body
    assert '<p>%s</p>' % exc in html_body


def test_checkForPreviousBackup(tmp_path):
    path = create_job(str(tmp_path))

    j = job(path)

    d = director()

    d.checkBackupEnvironment(j)

    latest = os.path.join(
                           j.backupdir,
                           j.hostname,
                           'daily',
                           time.strftime("%Y-%m-%d_%H-%M-%S_backup.0"),
                         )

    os.makedirs(latest)

    symlink = os.path.join(
                            j.backupdir,
                            j.hostname,
                            'latest',
                          )

    os.symlink(latest, symlink)

    ret = d.checkForPreviousBackup(j)

    assert ret == symlink


def test_checkForPreviousBackup_fail(tmp_path):
    path = create_job(str(tmp_path))

    j = job(path)

    d = director()

    ret = d.checkForPreviousBackup(j)

    assert ret is False


def test_getBackups(tmp_path):
    path = create_job(str(tmp_path))

    j = job(path)

    d = director()

    d.checkBackupEnvironment(j)

    subdir = time.strftime("%Y-%m-%d_%H-%M-%S_backup.0")

    daily_path = os.path.join(
                               j.backupdir,
                               j.hostname,
                               'daily',
                               subdir,
                             )

    os.makedirs(daily_path)

    ret = d.getBackups(j, 'daily')

    assert ret == [subdir]


def test_getBackups_no_match(tmp_path):
    path = create_job(str(tmp_path))

    j = job(path)

    d = director()

    d.checkBackupEnvironment(j)

    subdir = time.strftime("%Y-%m-%d_%H-%M-%S_backup.0")

    daily_path = os.path.join(
                               j.backupdir,
                               j.hostname,
                               'daily',
                               subdir,
                             )

    os.makedirs(daily_path)

    bak_path = os.path.join(
                               j.backupdir,
                               j.hostname,
                               'daily',
                               "%s.bak" % subdir,
                             )

    os.makedirs(bak_path)

    ret = d.getBackups(j, 'daily')

    assert ret == [subdir]


def test_getBackups_exception(tmp_path, caplog):
    path = create_job(str(tmp_path))

    j = job(path)

    d = director()

    ret = d.getBackups(j)

    assert 'Error while listing working directory' in caplog.text

    assert ret == []


def test_getBackupsSize(test_config, tmp_path):
    config().jobspooldirectory = str(tmp_path)

    path = create_job(str(tmp_path))

    j = job(path)

    d = director()

    d.checkBackupEnvironment(j)

    for interval in [
                      'daily',
                      'weekly',
                      'monthly',
                    ]:
        subdir = time.strftime("%Y-%m-%d_%H-%M-%S_backup.0")

        interval_path = os.path.join(
                                      j.backupdir,
                                      j.hostname,
                                      interval,
                                      subdir,
                                    )

        os.makedirs(interval_path)

        if interval == 'daily':
            symlink = os.path.join(
                                    j.backupdir,
                                    j.hostname,
                                    'latest',
                                  )

            os.symlink(interval_path, symlink)

    jrh = jobrunhistory(check=True)

    backupstatus = {
                     'hostname':              j.hostname,
                     'startdatetime':         time.time() - 1,
                     'rsync_total_file_size': 1337,
                     'rsync_literal_data':    42,
                   }

    hooks = []

    jrh.insertJob(backupstatus, hooks)

    time.sleep(0.1)

    (size, avg) = d.getBackupsSize(j)

    assert size != 0
    assert avg == float(backupstatus['rsync_literal_data'])


def test_getBackupsSize_no_history(test_config, tmp_path):
    config().jobspooldirectory = str(tmp_path)

    path = create_job(str(tmp_path))

    j = job(path)

    d = director()

    d.checkBackupEnvironment(j)

    subdir = time.strftime("%Y-%m-%d_%H-%M-%S_backup.0")

    daily_path = os.path.join(
                               j.backupdir,
                               j.hostname,
                               'daily',
                               subdir,
                             )

    os.makedirs(daily_path)

    symlink = os.path.join(
                            j.backupdir,
                            j.hostname,
                            'latest',
                          )

    os.symlink(daily_path, symlink)

    (size, avg) = d.getBackupsSize(j)

    assert size == 0
    assert avg == 0


def test_getBackupsSize_not_latest(test_config, tmp_path):
    config().jobspooldirectory = str(tmp_path)

    path = create_job(str(tmp_path))

    j = job(path)

    d = director()

    d.checkBackupEnvironment(j)

    subdir = time.strftime("%Y-%m-%d_%H-%M-%S_backup.0")

    daily_path = os.path.join(
                               j.backupdir,
                               j.hostname,
                               'daily',
                               subdir,
                             )

    os.makedirs(daily_path)

    jrh = jobrunhistory(check=True)

    backupstatus = {
                     'hostname':              j.hostname,
                     'startdatetime':         time.time() - 1,
                     'rsync_total_file_size': 1337,
                     'rsync_literal_data':    42,
                   }

    hooks = []

    jrh.insertJob(backupstatus, hooks)

    time.sleep(0.1)

    (size, avg) = d.getBackupsSize(j)

    assert size != 0
    assert avg != 0


def test_getIdfromBackupInstance(test_config, tmp_path):
    config().jobspooldirectory = str(tmp_path)

    d = director()

    directory = time.strftime("%Y-%m-%d_%H-%M-%S_backup.0")

    ret = d.getIdfromBackupInstance(directory)

    assert ret == 0


def test_getIdfromBackupInstance_fail(test_config, tmp_path):
    config().jobspooldirectory = str(tmp_path)

    d = director()

    ret = d.getIdfromBackupInstance('foo')

    assert ret is False


def test_getNamefromBackupInstance(test_config, tmp_path):
    config().jobspooldirectory = str(tmp_path)

    d = director()

    name = time.strftime("%Y-%m-%d_%H-%M-%S_backup")

    directory = "%s.0" % name

    ret = d.getNamefromBackupInstance(directory)

    assert ret == name


def test_getNamefromBackupInstance_fail(test_config, tmp_path):
    config().jobspooldirectory = str(tmp_path)

    d = director()

    ret = d.getNamefromBackupInstance('foo')

    assert ret is False


def test_getOldestBackupId(test_config, tmp_path):
    config().jobspooldirectory = str(tmp_path)

    path = create_job(str(tmp_path))

    j = job(path)

    d = director()

    d.checkBackupEnvironment(j)

    subdir = time.strftime("%Y-%m-%d_%H-%M-%S_backup.0")

    daily_path = os.path.join(
                               j.backupdir,
                               j.hostname,
                               'daily',
                               subdir,
                             )

    os.makedirs(daily_path)

    ret = d.getOldestBackupId(j)

    assert ret == 0


def test_backupRotate(test_config, tmp_path, caplog):
    config().jobspooldirectory = str(tmp_path)
    config().weeklybackup = int(time.strftime("%w")) + 1
    config().monthlybackup = int(time.strftime("%d")) + 2

    logger().debuglevel = 3

    path = create_job(str(tmp_path))

    j = job(path)

    d = director()

    d.checkBackupEnvironment(j)

    subdir = time.strftime("%Y-%m-%d_%H-%M-%S_backup.0")

    daily_path = os.path.join(
                               j.backupdir,
                               j.hostname,
                               'daily',
                               subdir,
                             )

    os.makedirs(daily_path)

    d.backupRotate(j)

    assert 'Error updating current symlink' not in caplog.text
    assert 'Error moving current backup failed' not in caplog.text
    assert 'Error rotating backups for host' not in caplog.text
    assert 'Error working directory not found' not in caplog.text


def test_backupRotate_symlink_error(
                                     test_config,
                                     tmp_path,
                                     caplog,
                                     monkeypatch,
                                   ):
    def mock_updateLatestSymlink(self, job, latest):
        return False

    monkeypatch.setattr(
                         director,
                         '_updateLatestSymlink',
                         mock_updateLatestSymlink
                       )

    config().jobspooldirectory = str(tmp_path)
    config().weeklybackup = int(time.strftime("%w")) + 1
    config().monthlybackup = int(time.strftime("%d")) + 2
    config().dailyrotation = 1

    logger().debuglevel = 3

    path = create_job(str(tmp_path))

    j = job(path)

    d = director()

    d.checkBackupEnvironment(j)

    subdir = time.strftime("%Y-%m-%d_%H-%M-%S_backup.0")

    daily_path = os.path.join(
                               j.backupdir,
                               j.hostname,
                               'daily',
                               subdir,
                             )

    os.makedirs(daily_path)

    d.backupRotate(j)

    assert 'Error updating current symlink' in caplog.text
    assert 'Error moving current backup failed' not in caplog.text
    assert 'Error rotating backups for host' not in caplog.text
    assert 'Error working directory not found' not in caplog.text


def test_backupRotate_move_error(test_config, tmp_path, caplog, monkeypatch):
    def mock_moveCurrentBackup(self, job):
        return False

    monkeypatch.setattr(director, '_moveCurrentBackup', mock_moveCurrentBackup)

    config().jobspooldirectory = str(tmp_path)
    config().weeklybackup = int(time.strftime("%w")) + 1
    config().monthlybackup = int(time.strftime("%d")) + 2
    config().dailyrotation = 1

    logger().debuglevel = 3

    path = create_job(str(tmp_path))

    j = job(path)

    d = director()

    d.checkBackupEnvironment(j)

    subdir = time.strftime("%Y-%m-%d_%H-%M-%S_backup.0")

    daily_path = os.path.join(
                               j.backupdir,
                               j.hostname,
                               'daily',
                               subdir,
                             )

    os.makedirs(daily_path)

    d.backupRotate(j)

    assert 'Error updating current symlink' not in caplog.text
    assert 'Error moving current backup failed' in caplog.text
    assert 'Error rotating backups for host' not in caplog.text
    assert 'Error working directory not found' not in caplog.text


def test_backupRotate_rotate_error(test_config, tmp_path, caplog, monkeypatch):
    def mock_rotateBackups(self, job):
        return False

    monkeypatch.setattr(director, '_rotateBackups', mock_rotateBackups)

    config().jobspooldirectory = str(tmp_path)
    config().weeklybackup = int(time.strftime("%w")) + 1
    config().monthlybackup = int(time.strftime("%d")) + 2
    config().dailyrotation = 1

    logger().debuglevel = 3

    path = create_job(str(tmp_path))

    j = job(path)

    d = director()

    d.checkBackupEnvironment(j)

    subdir = time.strftime("%Y-%m-%d_%H-%M-%S_backup.0")

    daily_path = os.path.join(
                               j.backupdir,
                               j.hostname,
                               'daily',
                               subdir,
                             )

    os.makedirs(daily_path)

    d.backupRotate(j)

    assert 'Error updating current symlink' not in caplog.text
    assert 'Error moving current backup failed' not in caplog.text
    assert 'Error rotating backups for host' in caplog.text
    assert 'Error working directory not found' not in caplog.text


def test_unlinkExpiredBackups(test_config, tmp_path):
    config().jobspooldirectory = str(tmp_path)
    config().weeklybackup = int(time.strftime("%w")) + 1
    config().monthlybackup = int(time.strftime("%d")) + 2
    config().dailyrotation = 1

    path = create_job(str(tmp_path))

    j = job(path)

    d = director()

    d.checkBackupEnvironment(j)

    subdir = time.strftime("%Y-%m-%d_%H-%M-%S_backup.1")

    daily_path1 = os.path.join(
                                j.backupdir,
                                j.hostname,
                                'daily',
                                subdir,
                              )

    os.makedirs(daily_path1)

    subdir = time.strftime("%Y-%m-%d_%H-%M-%S_backup.0")

    daily_path0 = os.path.join(
                                j.backupdir,
                                j.hostname,
                                'daily',
                                subdir,
                              )

    os.makedirs(daily_path0)

    assert os.path.exists(daily_path1) is True

    ret = d._unlinkExpiredBackups(j)

    assert ret is True

    assert os.path.exists(daily_path1) is False


def test_unlinkExpiredBackups_nop(test_config, tmp_path):
    config().jobspooldirectory = str(tmp_path)
    config().weeklybackup = int(time.strftime("%w")) + 1
    config().monthlybackup = int(time.strftime("%d")) + 2
    config().dailyrotation = 2

    path = create_job(str(tmp_path))

    j = job(path)

    d = director()

    d.checkBackupEnvironment(j)

    subdir = time.strftime("%Y-%m-%d_%H-%M-%S_backup.1")

    daily_path1 = os.path.join(
                                j.backupdir,
                                j.hostname,
                                'daily',
                                subdir,
                              )

    os.makedirs(daily_path1)

    subdir = time.strftime("%Y-%m-%d_%H-%M-%S_backup.0")

    daily_path0 = os.path.join(
                                j.backupdir,
                                j.hostname,
                                'daily',
                                subdir,
                              )

    os.makedirs(daily_path0)

    assert os.path.exists(daily_path1) is True

    ret = d._unlinkExpiredBackups(j)

    assert ret is True

    assert os.path.exists(daily_path1) is True


def test_unlinkExpiredBackups_fail(test_config, tmp_path, monkeypatch, caplog):
    def mock_checkWorkingDirectory(self, path):
        return False

    monkeypatch.setattr(
                         director,
                         'checkWorkingDirectory',
                         mock_checkWorkingDirectory,
                       )

    config().jobspooldirectory = str(tmp_path)
    config().weeklybackup = int(time.strftime("%w")) + 1
    config().monthlybackup = int(time.strftime("%d")) + 2
    config().dailyrotation = 1

    path = create_job(str(tmp_path))

    j = job(path)

    d = director()

    ret = d._unlinkExpiredBackups(j)

    assert ret is False

    assert 'Error working directory not found' in caplog.text


def test_unlinkExpiredBackup(test_config, tmp_path):
    config().jobspooldirectory = str(tmp_path)
    config().weeklybackup = int(time.strftime("%w")) + 1
    config().monthlybackup = int(time.strftime("%d")) + 2

    path = create_job(str(tmp_path))

    j = job(path)

    d = director()

    d.checkBackupEnvironment(j)

    subdir = time.strftime("%Y-%m-%d_%H-%M-%S_backup.0")

    daily_path = os.path.join(
                               j.backupdir,
                               j.hostname,
                               'daily',
                               subdir,
                             )

    os.makedirs(daily_path)

    assert os.path.exists(daily_path) is True

    ret = d._unlinkExpiredBackup(j, daily_path)

    assert ret is True

    assert os.path.exists(daily_path) is False


def test_unlinkExpiredBackup_exception(
                                        test_config,
                                        tmp_path,
                                        monkeypatch,
                                        caplog,
                                      ):
    config().jobspooldirectory = str(tmp_path)
    config().weeklybackup = int(time.strftime("%w")) + 1
    config().monthlybackup = int(time.strftime("%d")) + 2

    path = create_job(str(tmp_path))

    j = job(path)

    d = director()

    ret = d._unlinkExpiredBackup(j, 'foo')

    assert ret is False

    assert 'Error while removing' in caplog.text


def test_rotateBackups(test_config, tmp_path):
    config().jobspooldirectory = str(tmp_path)
    config().weeklybackup = int(time.strftime("%w")) + 1
    config().monthlybackup = int(time.strftime("%d")) + 2

    path = create_job(str(tmp_path))

    j = job(path)

    d = director()

    d.checkBackupEnvironment(j)

    subdir = time.strftime("%Y-%m-%d_%H-%M-%S_backup.0")

    daily_path = os.path.join(
                               j.backupdir,
                               j.hostname,
                               'daily',
                               subdir,
                             )

    os.makedirs(daily_path)

    ret = d._rotateBackups(j)

    assert ret is True


def test_rotateBackups_exception(test_config, tmp_path, monkeypatch):
    def mock_rename(src, dst):
        raise IOError('Mock rename failure')

    monkeypatch.setattr(os, 'rename', mock_rename)

    config().jobspooldirectory = str(tmp_path)
    config().weeklybackup = int(time.strftime("%w")) + 1
    config().monthlybackup = int(time.strftime("%d")) + 2

    path = create_job(str(tmp_path))

    j = job(path)

    d = director()

    d.checkBackupEnvironment(j)

    subdir = time.strftime("%Y-%m-%d_%H-%M-%S_backup.0")

    daily_path = os.path.join(
                               j.backupdir,
                               j.hostname,
                               'daily',
                               subdir,
                             )

    os.makedirs(daily_path)

    ret = d._rotateBackups(j)

    assert ret is False


def test_rotateBackups_getNamefromBackupInstance_fail(
                                                       test_config,
                                                       tmp_path,
                                                       monkeypatch,
                                                     ):
    def mock_getNamefromBackupInstance(self, path):
        return False

    monkeypatch.setattr(
                         director,
                         'getNamefromBackupInstance',
                         mock_getNamefromBackupInstance,
                       )

    config().jobspooldirectory = str(tmp_path)
    config().weeklybackup = int(time.strftime("%w")) + 1
    config().monthlybackup = int(time.strftime("%d")) + 2

    path = create_job(str(tmp_path))

    j = job(path)

    d = director()

    d.checkBackupEnvironment(j)

    subdir = time.strftime("%Y-%m-%d_%H-%M-%S_backup.0")

    daily_path = os.path.join(
                               j.backupdir,
                               j.hostname,
                               'daily',
                               subdir,
                             )

    os.makedirs(daily_path)

    ret = d._rotateBackups(j)

    assert ret is False


def test_rotateBackups_glob_fail(test_config, tmp_path, monkeypatch):
    def mock_glob(path):
        return None

    monkeypatch.setattr(glob, 'glob', mock_glob)

    config().jobspooldirectory = str(tmp_path)
    config().weeklybackup = int(time.strftime("%w")) + 1
    config().monthlybackup = int(time.strftime("%d")) + 2

    path = create_job(str(tmp_path))

    j = job(path)

    d = director()

    d.checkBackupEnvironment(j)

    subdir = time.strftime("%Y-%m-%d_%H-%M-%S_backup.0")

    daily_path = os.path.join(
                               j.backupdir,
                               j.hostname,
                               'daily',
                               subdir,
                             )

    os.makedirs(daily_path)

    ret = d._rotateBackups(j)

    assert ret is True


def test_moveCurrentBackup(test_config, tmp_path):
    config().jobspooldirectory = str(tmp_path)
    config().weeklybackup = int(time.strftime("%w")) + 1
    config().monthlybackup = int(time.strftime("%d")) + 2

    path = create_job(str(tmp_path))

    j = job(path)

    d = director()

    d.checkBackupEnvironment(j)

    ret = d._moveCurrentBackup(j)

    assert ret == time.strftime('daily/%Y-%m-%d_%H-%M-%S_backup.0')


def test_moveCurrentBackup_exception(test_config, tmp_path, monkeypatch):
    def mock_rename(src, dst):
        raise IOError('Mock rename failure')

    monkeypatch.setattr(os, 'rename', mock_rename)

    config().jobspooldirectory = str(tmp_path)
    config().weeklybackup = int(time.strftime("%w")) + 1
    config().monthlybackup = int(time.strftime("%d")) + 2

    path = create_job(str(tmp_path))

    j = job(path)

    d = director()

    d.checkBackupEnvironment(j)

    ret = d._moveCurrentBackup(j)

    assert ret is False


def test_updateLatestSymlink(test_config, tmp_path):
    config().jobspooldirectory = str(tmp_path)

    path = create_job(str(tmp_path))

    j = job(path)

    d = director()

    d.checkBackupEnvironment(j)

    subdir = time.strftime("%Y-%m-%d_%H-%M-%S_backup.0")

    daily_path = os.path.join(
                               j.backupdir,
                               j.hostname,
                               'daily',
                               subdir,
                             )

    os.makedirs(daily_path)

    ret = d._updateLatestSymlink(j, daily_path)

    assert ret is True


def test_updateLatestSymlink_exception(test_config, tmp_path, monkeypatch):
    def mock_symlink(src, dst):
        raise IOError('Mock symlink failure')

    monkeypatch.setattr(os, 'symlink', mock_symlink)

    config().jobspooldirectory = str(tmp_path)

    path = create_job(str(tmp_path))

    j = job(path)

    d = director()

    d.checkBackupEnvironment(j)

    subdir = time.strftime("%Y-%m-%d_%H-%M-%S_backup.0")

    daily_path = os.path.join(
                               j.backupdir,
                               j.hostname,
                               'daily',
                               subdir,
                             )

    os.makedirs(daily_path)

    ret = d._updateLatestSymlink(j, daily_path)

    assert ret is False


def test_moveLastBackupToCurrentBackup(test_config, tmp_path):
    config().jobspooldirectory = str(tmp_path)
    config().weeklybackup = int(time.strftime("%w")) + 1
    config().monthlybackup = int(time.strftime("%d")) + 2
    config().dailyrotation = 1

    logger().debuglevel = 3

    path = create_job(str(tmp_path))

    j = job(path)

    d = director()

    subdir = time.strftime("%Y-%m-%d_%H-%M-%S_backup.1")

    daily_path = os.path.join(
                               j.backupdir,
                               j.hostname,
                               'daily',
                               subdir,
                             )

    os.makedirs(daily_path)

    subdir = time.strftime("%Y-%m-%d_%H-%M-%S_backup.0")

    daily_path = os.path.join(
                               j.backupdir,
                               j.hostname,
                               'daily',
                               subdir,
                             )

    os.makedirs(daily_path)

    current_path = os.path.join(
                                 j.backupdir,
                                 j.hostname,
                                 'current',
                               )

    assert os.path.exists(current_path) is False

    ret = d._moveLastBackupToCurrentBackup(j)

    assert ret is True


def test_moveLastBackupToCurrentBackup_current_exists(
                                                       test_config,
                                                       tmp_path,
                                                       caplog,
                                                     ):
    config().jobspooldirectory = str(tmp_path)
    config().weeklybackup = int(time.strftime("%w")) + 1
    config().monthlybackup = int(time.strftime("%d")) + 2
    config().dailyrotation = 1

    logger().debuglevel = 3

    path = create_job(str(tmp_path))

    j = job(path)

    d = director()

    d.checkBackupEnvironment(j)

    subdir = time.strftime("%Y-%m-%d_%H-%M-%S_backup.1")

    daily_path = os.path.join(
                               j.backupdir,
                               j.hostname,
                               'daily',
                               subdir,
                             )

    os.makedirs(daily_path)

    subdir = time.strftime("%Y-%m-%d_%H-%M-%S_backup.0")

    daily_path = os.path.join(
                               j.backupdir,
                               j.hostname,
                               'daily',
                               subdir,
                             )

    os.makedirs(daily_path)

    current_path = os.path.join(
                                 j.backupdir,
                                 j.hostname,
                                 'current',
                               )

    assert os.path.exists(current_path) is True

    ret = d._moveLastBackupToCurrentBackup(j)

    assert ret is True


def test_moveLastBackupToCurrentBackup_getattr_exception(
                                                          test_config,
                                                          tmp_path,
                                                        ):
    config().jobspooldirectory = str(tmp_path)
    config().weeklybackup = int(time.strftime("%w")) + 1
    config().monthlybackup = int(time.strftime("%d")) + 2
    config().dailyrotation = 1

    path = create_job(str(tmp_path))

    j = job(path)

    delattr(j, 'dailyrotation')

    d = director()

    d.checkBackupEnvironment(j)

    subdir = time.strftime("%Y-%m-%d_%H-%M-%S_backup.1")

    daily_path = os.path.join(
                               j.backupdir,
                               j.hostname,
                               'daily',
                               subdir,
                             )

    os.makedirs(daily_path)

    subdir = time.strftime("%Y-%m-%d_%H-%M-%S_backup.0")

    daily_path = os.path.join(
                               j.backupdir,
                               j.hostname,
                               'daily',
                               subdir,
                             )

    os.makedirs(daily_path)

    ret = d._moveLastBackupToCurrentBackup(j)

    assert ret is None


def test_moveLastBackupToCurrentBackup_exception(test_config, tmp_path):
    config().jobspooldirectory = str(tmp_path)
    config().weeklybackup = int(time.strftime("%w")) + 1
    config().monthlybackup = int(time.strftime("%d")) + 2
    config().dailyrotation = 1

    path = create_job(str(tmp_path))

    j = job(path)

    d = director()

    d.checkBackupEnvironment(j)

    subdir = time.strftime(
                            "%Y-%m-%d_%H-%M-%S_backup.1",
                            time.localtime(time.time() - 856400)
                          )

    daily_path = os.path.join(
                               j.backupdir,
                               j.hostname,
                               'daily',
                               subdir,
                             )

    os.makedirs(daily_path)

    subdir = time.strftime("%Y-%m-%d_%H-%M-%S_backup.1")

    daily_path = os.path.join(
                               j.backupdir,
                               j.hostname,
                               'daily',
                               subdir,
                             )

    os.makedirs(daily_path)

    subdir = time.strftime("%Y-%m-%d_%H-%M-%S_backup.0")

    daily_path = os.path.join(
                               j.backupdir,
                               j.hostname,
                               'daily',
                               subdir,
                             )

    os.makedirs(daily_path)

    with pytest.raises(Exception) as e:
        ret = d._moveLastBackupToCurrentBackup(j)

        assert ret is None

    assert 'More than one directory matching on glob' in str(e)


def test_moveLastBackupToCurrentBackup_rename_exception(
                                                         test_config,
                                                         tmp_path,
                                                         monkeypatch,
                                                       ):
    def mock_rename(src, dst):
        raise IOError('Mock rename failure')

    monkeypatch.setattr(os, 'rename', mock_rename)

    config().jobspooldirectory = str(tmp_path)
    config().weeklybackup = int(time.strftime("%w")) + 1
    config().monthlybackup = int(time.strftime("%d")) + 2
    config().dailyrotation = 1

    logger().debuglevel = 3

    path = create_job(str(tmp_path))

    j = job(path)

    d = director()

    subdir = time.strftime("%Y-%m-%d_%H-%M-%S_backup.1")

    daily_path = os.path.join(
                               j.backupdir,
                               j.hostname,
                               'daily',
                               subdir,
                             )

    os.makedirs(daily_path)

    subdir = time.strftime("%Y-%m-%d_%H-%M-%S_backup.0")

    daily_path = os.path.join(
                               j.backupdir,
                               j.hostname,
                               'daily',
                               subdir,
                             )

    os.makedirs(daily_path)

    ret = d._moveLastBackupToCurrentBackup(j)

    assert ret is False


def test_moveLastBackupToCurrentBackup_nop(test_config, tmp_path):
    config().jobspooldirectory = str(tmp_path)
    config().weeklybackup = int(time.strftime("%w")) + 1
    config().monthlybackup = int(time.strftime("%d")) + 2

    path = create_job(str(tmp_path))

    j = job(path)

    d = director()

    ret = d._moveLastBackupToCurrentBackup(j)

    assert ret is None


def test_getWorkingDirectory_daily(test_config, tmp_path):
    config().jobspooldirectory = str(tmp_path)
    config().weeklybackup = int(time.strftime("%w")) + 1
    config().monthlybackup = int(time.strftime("%d")) + 2

    d = director()

    ret = d.getWorkingDirectory()

    assert ret == 'daily'


def test_getWorkingDirectory_weekly(test_config, tmp_path):
    config().jobspooldirectory = str(tmp_path)
    config().weeklybackup = int(time.strftime("%w"))
    config().monthlybackup = int(time.strftime("%d")) + 2

    d = director()

    ret = d.getWorkingDirectory()

    assert ret == 'weekly'


def test_getWorkingDirectory_monthly(test_config, tmp_path):
    config().jobspooldirectory = str(tmp_path)
    config().monthlybackup = int(time.strftime("%w")) + 1
    config().monthlybackup = int(time.strftime("%d"))

    d = director()

    ret = d.getWorkingDirectory()

    assert ret == 'monthly'


def test_sanityCheckWorkingDirectory(test_config, tmp_path, caplog):
    config().jobspooldirectory = str(tmp_path)
    config().weeklybackup = int(time.strftime("%w")) + 1
    config().monthlybackup = int(time.strftime("%d")) + 2

    logger().debuglevel = 3

    path = create_job(str(tmp_path))

    j = job(path)

    d = director()

    d.checkBackupEnvironment(j)

    subdir = time.strftime(
                            "%Y-%m-%d_%H-%M-%S_backup.1",
                            time.localtime(time.time() - 86400)
                          )

    daily_path = os.path.join(
                               j.backupdir,
                               j.hostname,
                               'daily',
                               subdir,
                             )

    os.makedirs(daily_path)

    subdir = time.strftime(
                            "%Y-%m-%d_%H-%M-%S_backup.0",
                            time.localtime(time.time())
                          )

    daily_path = os.path.join(
                               j.backupdir,
                               j.hostname,
                               'daily',
                               subdir,
                             )

    os.makedirs(daily_path)

    ret = d.sanityCheckWorkingDirectory(j)

    assert ret is True

    assert j.backupstatus['sanity_check'] == int(True)

    assert 'Sanity check failed for' not in caplog.text


def test_sanityCheckWorkingDirectory_duplicate_id(
                                                   test_config,
                                                   tmp_path,
                                                   caplog,
                                                 ):
    config().jobspooldirectory = str(tmp_path)
    config().weeklybackup = int(time.strftime("%w")) + 1
    config().monthlybackup = int(time.strftime("%d")) + 2

    logger().debuglevel = 3

    path = create_job(str(tmp_path))

    j = job(path)

    d = director()

    d.checkBackupEnvironment(j)

    subdir = time.strftime("%Y-%m-%d_%H-%M-%S_backup.0")

    daily_path = os.path.join(
                               j.backupdir,
                               j.hostname,
                               'daily',
                               subdir,
                             )

    os.makedirs(daily_path)

    subdir = time.strftime(
                            "%Y-%m-%d_%H-%M-%S_backup.0",
                            time.localtime(time.time() - 86400)
                          )

    daily_path = os.path.join(
                               j.backupdir,
                               j.hostname,
                               'daily',
                               subdir,
                             )

    os.makedirs(daily_path)

    ret = d.sanityCheckWorkingDirectory(j)

    assert ret is False

    assert j.backupstatus['sanity_check'] == int(False)

    assert 'Sanity check failed for' in caplog.text


def test_sanityCheckWorkingDirectory_invalid_sequence(
                                                       test_config,
                                                       tmp_path,
                                                       caplog,
                                                     ):
    config().jobspooldirectory = str(tmp_path)
    config().weeklybackup = int(time.strftime("%w")) + 1
    config().monthlybackup = int(time.strftime("%d")) + 2

    logger().debuglevel = 3

    path = create_job(str(tmp_path))

    j = job(path)

    d = director()

    d.checkBackupEnvironment(j)

    subdir = time.strftime("%Y-%m-%d_%H-%M-%S_backup.0")

    daily_path = os.path.join(
                               j.backupdir,
                               j.hostname,
                               'daily',
                               subdir,
                             )

    os.makedirs(daily_path)

    subdir = time.strftime(
                            "%Y-%m-%d_%H-%M-%S_backup.2",
                            time.localtime(time.time() - 86400)
                          )

    daily_path = os.path.join(
                               j.backupdir,
                               j.hostname,
                               'daily',
                               subdir,
                             )

    os.makedirs(daily_path)

    ret = d.sanityCheckWorkingDirectory(j)

    assert ret is False

    assert j.backupstatus['sanity_check'] == int(False)

    assert 'Sanity check failed for' in caplog.text


def test_checkWorkingDirectory(test_config, tmp_path):
    config().jobspooldirectory = str(tmp_path)

    d = director()

    for directory in [
                       'daily',
                       'weekly',
                       'monthly',
                     ]:
        assert d.checkWorkingDirectory(directory) is True

    assert d.checkWorkingDirectory('foo') is False


def test_processBackupStatus(test_config, tmp_path):
    config().jobspooldirectory = str(tmp_path)
    config().rsyncpath = os.path.join(
                                       os.path.dirname(__file__),
                                       'bin/mock-rsync-ok.sh',
                                     )

    logger().debuglevel = 3

    path = create_job(str(tmp_path))

    j = job(path)

    d = director()

    d.executeRsync(j, None)

    d.processBackupStatus(j)

    for key in [
                 'hostname',
                 'username',
                 'ssh',
                 'share',
                 'include',
                 'exclude',
                 'backupdir',
                 'speedlimitkb',
                 'type',
                 'integrity_id',
               ]:
        assert key in j.backupstatus


def test_processBackupStatus_ssh(test_config, tmp_path):
    config().jobspooldirectory = str(tmp_path)
    config().rsyncpath = os.path.join(
                                       os.path.dirname(__file__),
                                       'bin/mock-rsync-ok.sh',
                                     )

    logger().debuglevel = 3

    path = create_job(str(tmp_path))

    j = job(path)

    j.ssh = True

    d = director()

    d.executeRsync(j, None)

    d.processBackupStatus(j)

    for key in [
                 'hostname',
                 'username',
                 'ssh',
                 'share',
                 'include',
                 'exclude',
                 'backupdir',
                 'speedlimitkb',
                 'type',
                 'integrity_id',
               ]:
        assert key in j.backupstatus


def test_parseRsyncOutput(test_config, tmp_path):
    config().jobspooldirectory = str(tmp_path)
    config().rsyncpath = os.path.join(
                                       os.path.dirname(__file__),
                                       'bin/mock-rsync-ok.sh',
                                     )

    logger().debuglevel = 3

    path = create_job(str(tmp_path))

    j = job(path)

    d = director()

    d.executeRsync(j, None)

    d.parseRsyncOutput(j)

    for key in [
                 'rsync_number_of_files',
                 'rsync_number_of_files_transferred',
                 'rsync_total_file_size',
                 'rsync_total_transferred_file_size',
                 'rsync_literal_data',
                 'rsync_matched_data',
                 'rsync_file_list_size',
                 'rsync_file_list_generation_time',
                 'rsync_file_list_transfer_time',
                 'rsync_total_bytes_sent',
                 'rsync_total_bytes_received',
               ]:
        assert key in j.backupstatus

        assert j.backupstatus[key] != ''


def test_parseRsyncOutput_no_match(test_config, tmp_path, monkeypatch):
    def mock_match(pattern, string, flags=None):
        return False

    monkeypatch.setattr(re, 'match', mock_match)

    config().jobspooldirectory = str(tmp_path)
    config().rsyncpath = os.path.join(
                                       os.path.dirname(__file__),
                                       'bin/mock-rsync-ok.sh',
                                     )

    logger().debuglevel = 3

    path = create_job(str(tmp_path))

    j = job(path)

    d = director()

    d.executeRsync(j, None)

    d.parseRsyncOutput(j)

    for key in [
                 'rsync_number_of_files',
                 'rsync_number_of_files_transferred',
                 'rsync_total_file_size',
                 'rsync_total_transferred_file_size',
                 'rsync_literal_data',
                 'rsync_matched_data',
                 'rsync_file_list_size',
                 'rsync_file_list_generation_time',
                 'rsync_file_list_transfer_time',
                 'rsync_total_bytes_sent',
                 'rsync_total_bytes_received',
               ]:
        assert key in j.backupstatus

        assert j.backupstatus[key] == ''


def test_parseRsyncOutput_exception(test_config, tmp_path, monkeypatch):
    def mock_match(pattern, string, flags=None):
        return Exception('Mock match failure')

    monkeypatch.setattr(re, 'match', mock_match)

    config().jobspooldirectory = str(tmp_path)
    config().rsyncpath = os.path.join(
                                       os.path.dirname(__file__),
                                       'bin/mock-rsync-ok.sh',
                                     )

    logger().debuglevel = 3

    path = create_job(str(tmp_path))

    j = job(path)

    d = director()

    d.executeRsync(j, None)

    d.parseRsyncOutput(j)

    for key in [
                 'rsync_number_of_files',
                 'rsync_number_of_files_transferred',
                 'rsync_total_file_size',
                 'rsync_total_transferred_file_size',
                 'rsync_literal_data',
                 'rsync_matched_data',
                 'rsync_file_list_size',
                 'rsync_file_list_generation_time',
                 'rsync_file_list_transfer_time',
                 'rsync_total_bytes_sent',
                 'rsync_total_bytes_received',
               ]:
        assert key in j.backupstatus

        assert j.backupstatus[key] == ''
