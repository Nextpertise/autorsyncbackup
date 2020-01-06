import os
import time
import uuid

from _version import __version__
from autorsyncbackup import (
    setupCliArguments,
    getVersion,
    listJobs,
    checkRemoteHost,
    getLastBackupStatus,
)
from models.config import config
from models.jobrunhistory import jobrunhistory


def test_setupCliArguments():
    options = setupCliArguments()

    assert options.mainconfig == '/etc/autorsyncbackup/main.yaml'
    assert options.dryrun is False
    assert options.verbose is False
    assert options.version is False
    assert options.job is None
    assert options.sort is None
    assert options.hostname is None


def test_getVersion():
    assert getVersion() == __version__


def test_listJobs(test_config, tmp_path, capsys):
    config().lockfile = os.path.join(
                                      str(tmp_path),
                                      'autorsyncbackup.pid',
                                    )
    config().jobconfigdirectory = os.path.join(
                                                os.path.dirname(__file__),
                                                'etc/list',
                                              )
    config().jobspooldirectory = str(tmp_path)
    config().backupdir = os.path.join(
                                       str(tmp_path),
                                       'backups',
                                     )

    for subdir in [
                    'daily',
                    'weekly',
                    'monthly',
                  ]:
        path = os.path.join(
                             config().backupdir,
                             'localhost',
                             subdir,
                           )

        os.makedirs(path)

    listJobs('total')

    captured = capsys.readouterr()

    for title in [
                   'Hostname',
                   'Estimated total backup size',
                   'Average backup size increase',
                 ]:
        assert title in captured.out

    assert 'localhost' in captured.out
    assert '0 Bytes' in captured.out

    listJobs('average')

    captured = capsys.readouterr()

    for title in [
                   'Hostname',
                   'Estimated total backup size',
                   'Average backup size increase',
                 ]:
        assert title in captured.out

    assert 'localhost' in captured.out
    assert '0 Bytes' in captured.out


def test_checkRemoteHost(test_config, tmp_path):
    config().jobspooldirectory = str(tmp_path)
    config().rsyncpath = os.path.join(
                                       os.path.dirname(__file__),
                                       'bin/mock-rsync-ok.sh',
                                     )

    path = os.path.join(
                         os.path.dirname(__file__),
                         'etc/rsync.sh',
                       )

    ret = checkRemoteHost(path)

    assert ret is False


def test_checkRemoteHost_fail(test_config, tmp_path):
    config().jobspooldirectory = str(tmp_path)
    config().rsyncpath = os.path.join(
                                       os.path.dirname(__file__),
                                       'bin/mock-rsync-fail.sh',
                                     )

    path = os.path.join(
                         os.path.dirname(__file__),
                         'etc/rsync.sh',
                       )

    ret = checkRemoteHost(path)

    assert ret is True


def test_getLastBackupStatus(test_config, tmp_path, capsys):
    config().jobspooldirectory = str(tmp_path)

    jrh = jobrunhistory(check=True)

    backupstatus = {
                     'integrity_id':                      str(uuid.uuid1()),
                     'hostname':                          'localhost',
                     'startdatetime':                     time.time(),
                     'enddatetime':                       time.time(),
                     'username':                          'autorsyncbackup',
                     'ssh':                               'False',
                     'share':                             'backup',
                     'include':                           '/etc',
                     'exclude':                           '*.bak:.cache/*',
                     'backupdir':                         '/tmp',
                     'speedlimitkb':                      1600,
                     'filesrotate':                       None,
                     'type':                              'daily',
                     'rsync_backup_status':               1,
                     'rsync_return_code':                 0,
                     'rsync_pre_stdout':                  None,
                     'rsync_stdout':                      'foo\nbar\n',
                     'rsync_number_of_files':             3278,
                     'rsync_number_of_files_transferred': 1790,
                     'rsync_total_file_size':             6249777,
                     'rsync_total_transferred_file_size': 6213437,
                     'rsync_literal_data':                6213437,
                     'rsync_matched_data':                0,
                     'rsync_file_list_size':              80871,
                     'rsync_file_list_generation_time':   0.001,
                     'rsync_file_list_transfer_time':     0,
                     'rsync_total_bytes_sent':            39317,
                     'rsync_total_bytes_received':        6430608,
                     'sanity_check':                      1,
                   }

    hooks = []

    jrh.insertJob(backupstatus, hooks)

    getLastBackupStatus('localhost')

    captured = capsys.readouterr()

    assert 'localhost' in captured.out
    assert 'Ok' in captured.out
