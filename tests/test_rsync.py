import os

import paramiko

from lib.logger import logger
from lib.rsync import rsync
from models.config import config
from models.job import job


def test_checkRemoteHost_rsync(test_config, tmp_path):
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

    r = rsync()

    ret = r.checkRemoteHost(j)

    assert ret is True
    assert j.backupstatus['rsync_backup_status'] == int(ret)


def test_checkRemoteHost_rsync_fail(test_config, tmp_path):
    config().jobspooldirectory = str(tmp_path)
    config().rsyncpath = os.path.join(
                                       os.path.dirname(__file__),
                                       'bin/mock-rsync-fail.sh',
                                     )

    path = os.path.join(
                         os.path.dirname(__file__),
                         'etc/rsync.job',
                       )

    j = job(path)

    r = rsync()

    ret = r.checkRemoteHost(j)

    assert ret is False
    assert j.backupstatus['rsync_backup_status'] == int(ret)


def test_checkRemoteHost_ssh(test_config, tmp_path, monkeypatch):
    def mock_connect(self, hostname, username=None, key_filename=None):
        return True

    monkeypatch.setattr(paramiko.SSHClient, 'connect', mock_connect)

    config().jobspooldirectory = str(tmp_path)

    path = os.path.join(
                         os.path.dirname(__file__),
                         'etc/ssh.job',
                       )

    j = job(path)

    r = rsync()

    ret = r.checkRemoteHost(j)

    assert ret is True
    assert j.backupstatus['rsync_backup_status'] == int(ret)


def test_checkRemoteHost_ssh_fail(test_config, tmp_path, monkeypatch):
    def mock_connect(self, hostname, username=None, key_filename=None):
        raise IOError('Mock connection failed')

    monkeypatch.setattr(paramiko.SSHClient, 'connect', mock_connect)

    config().jobspooldirectory = str(tmp_path)

    path = os.path.join(
                         os.path.dirname(__file__),
                         'etc/ssh.job',
                       )

    j = job(path)

    r = rsync()

    ret = r.checkRemoteHost(j)

    assert ret is False
    assert j.backupstatus['rsync_backup_status'] == int(ret)


def test_executeRsync_rsync(test_config, tmp_path):
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

    r = rsync()

    ret = r.executeRsync(j, None)

    assert ret is True
    assert j.backupstatus['rsync_backup_status'] == int(ret)
    assert j.backupstatus['rsync_return_code'] == 0
    assert 'sending incremental file list' in j.backupstatus['rsync_stdout']


def test_executeRsync_rsync_latest(test_config, tmp_path):
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

    r = rsync()

    ret = r.executeRsync(j, 'foo')

    assert ret is True
    assert j.backupstatus['rsync_backup_status'] == int(ret)
    assert j.backupstatus['rsync_return_code'] == 0
    assert 'sending incremental file list' in j.backupstatus['rsync_stdout']


def test_executeRsync_rsync_no_include(test_config, tmp_path):
    config().jobspooldirectory = str(tmp_path)
    config().rsyncpath = os.path.join(
                                       os.path.dirname(__file__),
                                       'bin/mock-rsync-ok.sh',
                                     )

    path = os.path.join(
                         os.path.dirname(__file__),
                         'etc/rsync-no-include.job',
                       )

    j = job(path)

    r = rsync()

    ret = r.executeRsync(j, 'foo')

    assert ret is False
    assert j.backupstatus['rsync_backup_status'] == 0
    assert j.backupstatus['rsync_return_code'] == 9
    assert (
             'Include/Fileset is missing, Rsync is never invoked'
           ) in j.backupstatus['rsync_stdout']


def test_executeRsync_ssh(test_config, tmp_path):
    config().jobspooldirectory = str(tmp_path)
    config().rsyncpath = os.path.join(
                                       os.path.dirname(__file__),
                                       'bin/mock-rsync-ok.sh',
                                     )

    path = os.path.join(
                         os.path.dirname(__file__),
                         'etc/ssh.job',
                       )

    j = job(path)

    r = rsync()

    ret = r.executeRsync(j, None)

    assert ret is True
    assert j.backupstatus['rsync_backup_status'] == int(ret)
    assert j.backupstatus['rsync_return_code'] == 0
    assert 'sending incremental file list' in j.backupstatus['rsync_stdout']


def test_executeRsync_ssh_latest(test_config, tmp_path):
    config().jobspooldirectory = str(tmp_path)
    config().rsyncpath = os.path.join(
                                       os.path.dirname(__file__),
                                       'bin/mock-rsync-ok.sh',
                                     )

    path = os.path.join(
                         os.path.dirname(__file__),
                         'etc/ssh.job',
                       )

    j = job(path)

    r = rsync()

    ret = r.executeRsync(j, 'foo')

    assert ret is True
    assert j.backupstatus['rsync_backup_status'] == int(ret)
    assert j.backupstatus['rsync_return_code'] == 0
    assert 'sending incremental file list' in j.backupstatus['rsync_stdout']


def test_executeRsync_ssh_no_include(test_config, tmp_path):
    config().jobspooldirectory = str(tmp_path)
    config().rsyncpath = os.path.join(
                                       os.path.dirname(__file__),
                                       'bin/mock-rsync-ok.sh',
                                     )

    path = os.path.join(
                         os.path.dirname(__file__),
                         'etc/ssh-no-include.job',
                       )

    j = job(path)

    r = rsync()

    ret = r.executeRsync(j, 'foo')

    assert ret is False
    assert j.backupstatus['rsync_backup_status'] == 0
    assert j.backupstatus['rsync_return_code'] == 9
    assert (
             'Include/Fileset is missing, Rsync is never invoked'
           ) in j.backupstatus['rsync_stdout']


def test_executeRsyncViaRsyncProtocol(test_config, tmp_path):
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

    r = rsync()

    (status, stdout) = r.executeRsyncViaRsyncProtocol(j, None)

    assert status == 0
    assert 'sending incremental file list' in stdout


def test_executeRsyncViaSshProtocol(test_config, tmp_path):
    config().jobspooldirectory = str(tmp_path)
    config().rsyncpath = os.path.join(
                                       os.path.dirname(__file__),
                                       'bin/mock-rsync-ok.sh',
                                     )

    path = os.path.join(
                         os.path.dirname(__file__),
                         'etc/ssh.job',
                       )

    j = job(path)

    r = rsync()

    (status, stdout) = r.executeRsyncViaSshProtocol(j, None)

    assert status == 0
    assert 'sending incremental file list' in stdout


def test_generateInclude_rsync():
    path = os.path.join(
                         os.path.dirname(__file__),
                         'etc/rsync.job',
                       )

    j = job(path)

    r = rsync()

    include = r.generateInclude(j)

    assert include == " rsync://%s@%s:%s/%s%s" % (
                                                   j.rsyncusername,
                                                   j.hostname,
                                                   j.port,
                                                   j.rsyncshare,
                                                   '/etc',
                                                 )


def test_generateInclude_ssh():
    path = os.path.join(
                         os.path.dirname(__file__),
                         'etc/ssh.job',
                       )

    j = job(path)

    r = rsync()

    include = r.generateInclude(j)

    assert include == " %s@%s:%s" % (
                                      j.sshusername,
                                      j.hostname,
                                      '/etc',
                                    )


def test_generateInclude_error(caplog):
    logger().debuglevel = 3

    path = os.path.join(
                         os.path.dirname(__file__),
                         'etc/rsync-no-include.job',
                       )

    j = job(path)

    r = rsync()

    include = r.generateInclude(j)

    assert include is False
    assert 'No include/fileset specified' in caplog.text


def test_generateExclude():
    path = os.path.join(
                         os.path.dirname(__file__),
                         'etc/rsync.job',
                       )

    j = job(path)

    r = rsync()

    exclude = r.generateExclude(j)

    assert exclude == (
                        " --exclude '*.bak'"
                        " --exclude '.cache/*'"
                      )


def test_executeCommand():
    r = rsync()

    (status, stdout) = r.executeCommand('uptime')

    assert status == 0
    assert type(stdout) is not bytes
    assert 'load average' in stdout


def test_rsyncErrorCodeToBoolean():
    r = rsync()

    assert r.rsyncErrorCodeToBoolean(0) is True
    assert r.rsyncErrorCodeToBoolean(1) is False
    assert r.rsyncErrorCodeToBoolean(24) is True
