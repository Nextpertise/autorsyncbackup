import base64
import email
import os
import time
import uuid

import mailer

from lib.statusemail import statusemail
from models.config import config
from models.job import job
from models.jobrunhistory import jobrunhistory


def test_init():
    se = statusemail()

    assert se.jobrunhistory is not None


def test_sendStatusEmail(tmp_path, monkeypatch):
    email_path = os.path.join(str(tmp_path), 'status.eml')

    def mock_send(self, message):
        with open(email_path, 'w') as f:
            f.write(message.as_string())

        return True

    monkeypatch.setattr(mailer.Mailer, 'send', mock_send)

    config().jobspooldirectory = str(tmp_path)
    config().backupmailrecipients = ['foo@example.com']

    path = os.path.join(
               os.path.dirname(__file__),
               'etc/localhost.job',
           )

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

    j = job(path)

    jobs = [
             j,
           ]

    durationstats = {
                      'backupstartdatetime':       int(time.time()) - 40,
                      'backupenddatetime':         int(time.time()) - 30,
                      'housekeepingstartdatetime': int(time.time()) - 20,
                      'housekeepingenddatetime':   int(time.time()) - 10,
                    }

    se = statusemail()

    se.sendStatusEmail(jobs, durationstats)

    assert se.history is not None
    assert se.history != []

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

    assert 'Integrity:' in text_body
    assert '>Integrity</td>' in html_body


def test_sendSuddenDeath(tmp_path, monkeypatch):
    email_path = os.path.join(str(tmp_path), 'sudden-death.eml')

    def mock_send(self, message):
        with open(email_path, 'w') as f:
            f.write(message.as_string())

        return True

    monkeypatch.setattr(mailer.Mailer, 'send', mock_send)

    config().jobspooldirectory = str(tmp_path)
    config().backupmailrecipients = ['foo@example.com']

    exc = 'Mock: There was much rejoicing'

    se = statusemail()

    se.sendSuddenDeath(exc)

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


def test_getOverallBackupState_error(tmp_path):
    config().jobspooldirectory = str(tmp_path)
    config().backupmailrecipients = ['foo@example.com']

    se = statusemail()

    se.history = [
                   {
                     'rsync_backup_status': 1,
                     'sanity_check':        1,
                     'integrity_confirmed': True,
                     'commands':            [],
                   },
                 ]

    (ret, good, warning, bad) = se.getOverallBackupState([])

    assert ret == 'error'
    assert len(good) == 0
    assert len(warning) == 0
    assert len(bad) == 0

    se.history = []

    (ret, good, warning, bad) = se.getOverallBackupState([])

    assert ret == 'error'
    assert len(good) == 0
    assert len(warning) == 0
    assert len(bad) == 0


def test_getOverallBackupState_good(tmp_path):
    config().jobspooldirectory = str(tmp_path)
    config().backupmailrecipients = ['foo@example.com']

    se = statusemail()

    se.history = [
                   {
                     'rsync_backup_status': 1,
                     'sanity_check':        1,
                     'integrity_confirmed': True,
                     'commands':            [],
                   },
                 ]

    (ret, good, warning, bad) = se.getOverallBackupState(se.history)

    assert ret == 'ok'
    assert len(good) == 1
    assert len(warning) == 0
    assert len(bad) == 0


def test_getOverallBackupState_bad(tmp_path):
    config().jobspooldirectory = str(tmp_path)
    config().backupmailrecipients = ['foo@example.com']

    se = statusemail()

    se.history = [
                   {
                     'rsync_backup_status': 0,
                     'sanity_check':        1,
                     'integrity_confirmed': True,
                     'commands':            [],
                   },
                 ]

    (ret, good, warning, bad) = se.getOverallBackupState(se.history)

    assert ret == 'error'
    assert len(good) == 0
    assert len(warning) == 0
    assert len(bad) == 1

    se.history = [
                   {
                     'rsync_backup_status': 1,
                     'sanity_check':        0,
                     'integrity_confirmed': True,
                     'commands':            [],
                   },
                 ]

    (ret, good, warning, bad) = se.getOverallBackupState(se.history)

    assert ret == 'error'
    assert len(good) == 0
    assert len(warning) == 0
    assert len(bad) == 1

    se.history = [
                   {
                     'rsync_backup_status': 1,
                     'sanity_check':        1,
                     'integrity_confirmed': False,
                     'commands':            [],
                   },
                 ]

    (ret, good, warning, bad) = se.getOverallBackupState(se.history)

    assert ret == 'error'
    assert len(good) == 0
    assert len(warning) == 0
    assert len(bad) == 1

    se.history = [
                   {
                     'rsync_backup_status': 1,
                     'sanity_check':        1,
                     'integrity_confirmed': False,
                     'commands':            [
                                              {
                                                'returncode':      1,
                                                'continueonerror': True,
                                              },
                                            ],
                   },
                 ]

    (ret, good, warning, bad) = se.getOverallBackupState(se.history)

    assert ret == 'error'
    assert len(good) == 0
    assert len(warning) == 0
    assert len(bad) == 1

    se.history = [
                   {
                     'rsync_backup_status': 1,
                     'sanity_check':        1,
                     'integrity_confirmed': True,
                     'commands':            [
                                              {
                                                'returncode':      1,
                                                'continueonerror': False,
                                              },
                                            ],
                   },
                 ]

    (ret, good, warning, bad) = se.getOverallBackupState(se.history)

    assert ret == 'error'
    assert len(good) == 0
    assert len(warning) == 0
    assert len(bad) == 1


def test_getOverallBackupState_warning(tmp_path):
    config().jobspooldirectory = str(tmp_path)
    config().backupmailrecipients = ['foo@example.com']

    se = statusemail()

    se.history = [
                   {
                     'rsync_backup_status': 1,
                     'sanity_check':        1,
                     'integrity_confirmed': True,
                     'commands':            [
                                              {
                                                'returncode':      1,
                                                'continueonerror': True,
                                              },
                                            ],
                   },
                 ]

    (ret, good, warning, bad) = se.getOverallBackupState(se.history)

    assert ret == 'warning'
    assert len(good) == 0
    assert len(warning) == 1
    assert len(bad) == 0


def test_getBackupHosts(tmp_path):
    config().jobspooldirectory = str(tmp_path)
    config().backupmailrecipients = ['foo@example.com']

    se = statusemail()

    # no jobs
    ret = se.getBackupHosts([])

    assert ret == []

    # disabled job
    path = os.path.join(
               os.path.dirname(__file__),
               'etc/hostname-only.job',
           )

    j = job(path)

    ret = se.getBackupHosts([j])

    assert ret == []

    # enabled job
    path = os.path.join(
               os.path.dirname(__file__),
               'etc/localhost.job',
           )

    j = job(path)

    ret = se.getBackupHosts([j])

    assert ret == ['localhost']


def test_getMissingHosts(tmp_path):
    config().jobspooldirectory = str(tmp_path)
    config().backupmailrecipients = ['foo@example.com']

    se = statusemail()

    # no jobs nor history
    se.history = []

    hosts = se.getMissingHosts([])

    assert hosts == []

    # enabled job, no history
    path = os.path.join(
               os.path.dirname(__file__),
               'etc/localhost.job',
           )

    j = job(path)

    se.history = []

    hosts = se.getMissingHosts([j])

    assert len(hosts) == 1
    assert 'localhost' in hosts

    # enabled job, job in history
    se.history = [
                   {
                     'hostname': 'localhost',
                   },
                 ]

    hosts = se.getMissingHosts([j])

    assert hosts == []

    # disabled job, no history
    path = os.path.join(
               os.path.dirname(__file__),
               'etc/hostname-only.job',
           )

    j = job(path)

    se.history = []

    hosts = se.getMissingHosts([j])

    assert hosts == []


def test_getStats(tmp_path):
    config().jobspooldirectory = str(tmp_path)
    config().backupmailrecipients = ['foo@example.com']

    se = statusemail()

    se.history = [
                   {
                     'rsync_backup_status':               1,
                     'commanderror':                      'ok',
                     'startdatetime':                     time.time() - 10,
                     'enddatetime':                       time.time(),
                     'rsync_number_of_files':             8086,
                     'rsync_number_of_files_transferred': 42,
                     'rsync_total_file_size':             6800,
                     'rsync_total_transferred_file_size': 314,
                     'rsync_literal_data':                42,
                     'rsync_matched_data':                42,
                     'rsync_file_list_size':              386,
                     'rsync_file_list_generation_time':   0.007,
                     'rsync_file_list_transfer_time':     0.016,
                     'rsync_total_bytes_sent':            486,
                     'rsync_total_bytes_received':        586,
                     'speedlimitkb':                      686,
                     'sanity_check':                      0,
                   },
                 ]

    ret = se.getStats([])

    keys = [
             'total_host_count',
             'total_backups_failed',
             'total_rsync_duration',
             'total_number_of_files',
             'total_number_of_files_transferred',
             'total_file_size',
             'total_transferred_file_size',
             'total_literal_data',
             'total_matched_data',
             'total_file_list_size',
             'total_file_list_generation_time',
             'total_file_list_transfer_time',
             'total_bytes_sent',
             'total_bytes_received',
             'total_speed_limit_kb',
             'average_backup_duration',
             'average_speed_limit_kb',
             'total_backups_success',
           ]

    for key in keys:
        assert key in ret

    assert ret['total_backups_failed'] == 1
    assert ret['total_backups_success'] == 0
    assert ret['average_backup_duration'] == 0
    assert ret['average_speed_limit_kb'] == 0

    se.history = [
                   {
                     'rsync_backup_status':               0,
                     'commanderror':                      'ok',
                     'startdatetime':                     time.time() - 10,
                     'enddatetime':                       time.time(),
                     'rsync_number_of_files':             8086,
                     'rsync_number_of_files_transferred': 42,
                     'rsync_total_file_size':             6800,
                     'rsync_total_transferred_file_size': 314,
                     'rsync_literal_data':                42,
                     'rsync_matched_data':                42,
                     'rsync_file_list_size':              386,
                     'rsync_file_list_generation_time':   0.007,
                     'rsync_file_list_transfer_time':     0.016,
                     'rsync_total_bytes_sent':            486,
                     'rsync_total_bytes_received':        586,
                     'speedlimitkb':                      686,
                     'sanity_check':                      1,
                   },
                 ]

    ret = se.getStats([])

    assert ret['total_backups_failed'] == 1
    assert ret['total_backups_success'] == 0
    assert ret['average_backup_duration'] == 0
    assert ret['average_speed_limit_kb'] == 0

    se.history = [
                   {
                     'rsync_backup_status':               1,
                     'commanderror':                      'ok',
                     'startdatetime':                     time.time() - 10,
                     'enddatetime':                       time.time(),
                     'rsync_number_of_files':             8086,
                     'rsync_number_of_files_transferred': 42,
                     'rsync_total_file_size':             6800,
                     'rsync_total_transferred_file_size': 314,
                     'rsync_literal_data':                42,
                     'rsync_matched_data':                42,
                     'rsync_file_list_size':              386,
                     'rsync_file_list_generation_time':   0.007,
                     'rsync_file_list_transfer_time':     0.016,
                     'rsync_total_bytes_sent':            486,
                     'rsync_total_bytes_received':        586,
                     'speedlimitkb':                      0,
                     'sanity_check':                      1,
                   },
                 ]

    ret = se.getStats([])

    assert ret['total_backups_failed'] == 0
    assert ret['total_backups_success'] == 1
    assert ret['average_backup_duration'] > 0
    assert ret['average_speed_limit_kb'] == 0

    se.history = [
                   {
                     'rsync_backup_status':               1,
                     'commanderror':                      'ok',
                     'startdatetime':                     time.time() - 10,
                     'enddatetime':                       time.time(),
                     'rsync_number_of_files':             8086,
                     'rsync_number_of_files_transferred': 42,
                     'rsync_total_file_size':             6800,
                     'rsync_total_transferred_file_size': 314,
                     'rsync_literal_data':                42,
                     'rsync_matched_data':                42,
                     'rsync_file_list_size':              386,
                     'rsync_file_list_generation_time':   0.007,
                     'rsync_file_list_transfer_time':     0.016,
                     'rsync_total_bytes_sent':            486,
                     'rsync_total_bytes_received':        586,
                     'speedlimitkb':                      686,
                     'sanity_check':                      1,
                   },
                 ]

    ret = se.getStats([])

    assert ret['total_backups_failed'] == 0
    assert ret['total_backups_success'] == 1
    assert ret['average_backup_duration'] > 0
    assert ret['average_speed_limit_kb'] > 0
