import time
import uuid

from lib.statuscli import statuscli
from models.config import config
from models.jobrunhistory import jobrunhistory


def test_init():
    sc = statuscli()

    assert sc.jobrunhistory is not None


def test_getList(test_config, tmp_path):
    config().jobspooldirectory = str(tmp_path)

    jrh = jobrunhistory(str(tmp_path), check=True)

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

    hooks = [
              {
                'local':           1,
                'runtime':         'before',
                'returncode':      0,
                'continueonerror': True,
                'script':          'uptime',
                'stdout':          (
                                    ' 12:11:51 up  2:40, 13 users, '
                                    ' load average: 0.84, 0.71, 0.71\n'
                                   ),
                'stderr':          '',
              },
            ]

    jrh.insertJob(backupstatus, hooks)

    sc = statuscli()

    history = sc.getList(backupstatus['hostname'])

    assert history is not None
    assert history != []


def test_printOutput(test_config, tmp_path, capsys):
    config().jobspooldirectory = str(tmp_path)

    jrh = jobrunhistory(str(tmp_path), check=True)

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

    sc = statuscli()

    sc.printOutput(backupstatus['hostname'])

    captured = capsys.readouterr()

    assert 'localhost' in captured.out
    assert 'Ok' in captured.out


def test_printOutput_rsync_failed(test_config, tmp_path, capsys):
    config().jobspooldirectory = str(tmp_path)

    jrh = jobrunhistory(str(tmp_path), check=True)

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
                     'rsync_backup_status':               0,
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

    sc = statuscli()

    sc.printOutput(backupstatus['hostname'])

    captured = capsys.readouterr()

    assert 'localhost' in captured.out
    assert 'Failed' in captured.out


def test_printOutput_no_history(test_config, tmp_path, capsys):
    config().jobspooldirectory = str(tmp_path)

    jobrunhistory(str(tmp_path), check=True)

    sc = statuscli()

    sc.printOutput('localhost')

    captured = capsys.readouterr()

    assert 'Could not find hostname' in captured.out
