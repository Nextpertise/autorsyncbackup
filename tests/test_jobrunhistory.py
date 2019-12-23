import datetime
import os
import re
import sqlite3
import time
import uuid

import pytest

from lib.logger import logger
from models.job import job
from models.jobrunhistory import jobrunhistory


tables = [
           'jobrunhistory',
           'jobcommandhistory',
         ]


def get_table_sql(c, name):
    query = """
            SELECT sql
              FROM sqlite_master
             WHERE type = 'table'
               AND name = :name
            """
    param = {
              'name': name
            }

    c.execute(query, param)

    row = c.fetchone()

    if row is not None:
        return row[0]

    return None


def get_record_count(c, table):
    query = """
            SELECT COUNT(id)
              FROM %s
            """ % table
    param = {}

    c.execute(query, param)

    row = c.fetchone()

    if row is not None:
        return row[0]

    return None


def test_init(tmp_path):
    jrh = jobrunhistory(str(tmp_path))

    db_file = os.path.join(tmp_path, 'autorsyncbackup.db')

    assert os.path.exists(db_file)

    c = jrh.conn.cursor()

    for table in tables:
        assert get_table_sql(c, table) is None


def test_init_check(tmp_path):
    jrh = jobrunhistory(str(tmp_path), check=True)

    db_file = os.path.join(tmp_path, 'autorsyncbackup.db')

    assert os.path.exists(db_file)

    c = jrh.conn.cursor()

    for table in tables:
        sql = get_table_sql(c, table)

        assert sql is not None
        assert re.search(r' %s ' % table, sql)


def test_openDbHandler(tmp_path):
    jrh = jobrunhistory(str(tmp_path), check=True)

    assert jrh.conn.in_transaction is False


def test_openDbHandler_exception():
    path = '/non-existent'

    with pytest.raises(SystemExit) as e:
        jobrunhistory(path, check=True)

    assert e.type == SystemExit
    assert e.value.code == 1


def test_closeDbHandler(tmp_path):
    jrh = jobrunhistory(str(tmp_path), check=True)

    assert jrh.closeDbHandler() is None

    with pytest.raises(sqlite3.ProgrammingError) as e:
        jrh.conn.in_transaction

    assert e.type == sqlite3.ProgrammingError
    assert 'Cannot operate on a closed database' in str(e.value)


def test_checkTables(tmp_path):
    jrh = jobrunhistory(str(tmp_path), check=False)

    jrh.checkTables()

    c = jrh.conn.cursor()

    for table in tables:
        sql = get_table_sql(c, table)

        assert sql is not None
        assert re.search(r' %s ' % table, sql)


def test_checkTables_twice(tmp_path):
    jrh = jobrunhistory(str(tmp_path), check=True)

    jrh.checkTables()

    c = jrh.conn.cursor()

    for table in tables:
        sql = get_table_sql(c, table)

        assert sql is not None
        assert re.search(r' %s ' % table, sql)


def test_createTableJobrunhistoryTable(tmp_path):
    jrh = jobrunhistory(str(tmp_path), check=False)

    jrh.createTableJobrunhistoryTable()

    c = jrh.conn.cursor()

    table = 'jobrunhistory'

    sql = get_table_sql(c, table)

    assert sql is not None
    assert re.search(r' %s ' % table, sql)


def test_createTableJobcommandhistoryTable(tmp_path):
    jrh = jobrunhistory(str(tmp_path), check=False)

    jrh.createTableJobcommandhistoryTable()

    c = jrh.conn.cursor()

    table = 'jobcommandhistory'

    sql = get_table_sql(c, table)

    assert sql is not None
    assert re.search(r' %s ' % table, sql)


def test_insertJob(tmp_path):
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

    c = jrh.conn.cursor()

    query = """
            SELECT id
              FROM jobrunhistory
             WHERE integrity_id = :integrity_id
            """
    param = {
              'integrity_id': backupstatus['integrity_id'],
            }

    c.execute(query, param)

    row = c.fetchone()

    assert row is not None
    assert row[0] >= 1

    query = """
            SELECT c.id
              FROM jobcommandhistory AS c,
                   jobrunhistory AS h
             WHERE c.jobrunid = h.id
               AND h.integrity_id = :integrity_id
            """

    c.execute(query, param)

    row = c.fetchone()

    assert row is not None
    assert row[0] >= 1


def test_insertJob_exception(tmp_path, caplog):
    logger().debuglevel = 3

    jrh = jobrunhistory(str(tmp_path), check=True)

    backupstatus = {
                     'hostname':            'localhost',
                     'non_existing_column': None,
                   }

    jrh.insertJob(backupstatus, None)

    assert 'Could not insert job details for host' in caplog.text
    assert (
            'table jobrunhistory has no column'
            ' named non_existing_column'
           ) in caplog.text


def test_insertJob_none_hooks(tmp_path, caplog):
    logger().debuglevel = 3

    jrh = jobrunhistory(str(tmp_path), check=True)

    backupstatus = {
                     'hostname':      'localhost',
                     'startdatetime': time.time(),
                   }

    jrh.insertJob(backupstatus, None)

    c = jrh.conn.cursor()

    for table in tables:
        count = get_record_count(c, table)

        assert count is not None

        if table == 'jobrunhistory':
            assert count == 1
        elif table == 'jobcommandhistory':
            assert count == 0


def test_identifyJob(tmp_path, caplog):
    logger().debuglevel = 3

    jrh = jobrunhistory(str(tmp_path), check=True)

    backupstatus = {
                     'hostname':              'localhost',
                     'startdatetime':         time.time() - 1,
                     'rsync_total_file_size': 1337,
                     'rsync_literal_data':    42,
                   }

    hooks = []

    jrh.insertJob(backupstatus, hooks)

    path = os.path.join(
                         os.path.dirname(__file__),
                         'etc/localhost.job',
                       )

    j = job(path)

    directory = datetime.datetime.today().strftime(
                "%Y-%m-%d_%H-%M-%S_backup.0")

    i = jrh.identifyJob(j, directory)

    for record in caplog.records:
        assert 'cannot identify job for' not in record.msg
        assert 'large time difference for job' not in record.msg
        assert 'invalid values for job' not in record.msg

    assert i is not None
    assert i[0] >= 1
    assert i[1] == backupstatus['startdatetime']
    assert i[2] == backupstatus['rsync_total_file_size']
    assert i[3] == backupstatus['rsync_literal_data']


def test_identifyJob_error(tmp_path, caplog):
    logger().debuglevel = 3

    jrh = jobrunhistory(str(tmp_path), check=True)

    backupstatus = {
                     'hostname':              'localhost',
                     'startdatetime':         time.time(),
                     'rsync_total_file_size': 1337,
                     'rsync_literal_data':    42,
                   }

    hooks = []

    jrh.insertJob(backupstatus, hooks)

    path = os.path.join(
                         os.path.dirname(__file__),
                         'etc/localhost.job',
                       )

    j = job(path)

    directory = datetime.datetime.today().strftime(
                "%Y-%m-%d_%H-%M-%S_backup.0")

    i = jrh.identifyJob(j, directory)

    assert 'cannot identify job for' in caplog.text

    assert i is None


def test_identifyJob_large_time_difference(tmp_path, caplog):
    logger().debuglevel = 3

    jrh = jobrunhistory(str(tmp_path), check=True)

    backupstatus = {
                     'hostname':              'localhost',
                     'startdatetime':         time.time() - 86400,
                     'rsync_total_file_size': 1337,
                     'rsync_literal_data':    42,
                   }

    hooks = []

    jrh.insertJob(backupstatus, hooks)

    path = os.path.join(
                         os.path.dirname(__file__),
                         'etc/localhost.job',
                       )

    j = job(path)

    directory = datetime.datetime.today().strftime(
                "%Y-%m-%d_%H-%M-%S_backup.0")

    i = jrh.identifyJob(j, directory)

    # Warnings are not logged by default
    if len(caplog.records) > 0:
        assert 'large time difference for job' in caplog.text

    assert i is not None
    assert i[0] >= 1
    assert i[1] == backupstatus['startdatetime']
    assert i[2] == backupstatus['rsync_total_file_size']
    assert i[3] == backupstatus['rsync_literal_data']


def test_identifyJob_invalid_values(tmp_path, caplog):
    logger().debuglevel = 3

    jrh = jobrunhistory(str(tmp_path), check=True)

    backupstatus = {
                     'hostname':              'localhost',
                     'startdatetime':         time.time() - 86400,
                     'rsync_total_file_size': '',
                     'rsync_literal_data':    None,
                   }

    hooks = []

    jrh.insertJob(backupstatus, hooks)

    path = os.path.join(
                         os.path.dirname(__file__),
                         'etc/localhost.job',
                       )

    j = job(path)

    directory = datetime.datetime.today().strftime(
                "%Y-%m-%d_%H-%M-%S_backup.0")

    i = jrh.identifyJob(j, directory)

    # Warnings are not logged by default
    if len(caplog.records) > 0:
        assert 'invalid values for job' in caplog.text

    assert i is not None
    assert i[0] >= 1
    assert i[1] == backupstatus['startdatetime']
    assert i[2] == backupstatus['rsync_total_file_size']
    assert i[3] == backupstatus['rsync_literal_data']


def test_getJobHistory(tmp_path):
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

    history = jrh.getJobHistory([backupstatus['hostname']])

    assert history is not None
    assert len(history) == 1
    assert history[0]['hostname'] == backupstatus['hostname']

    assert history[0]['commands'] is not None
    assert len(history[0]['commands']) == 1
    assert history[0]['commands'][0]['script'] == 'uptime'


def test_getJobHistory_exception(tmp_path, caplog):
    logger().debuglevel = 3

    jrh = jobrunhistory(str(tmp_path), check=True)

    jrh.closeDbHandler()

    history = jrh.getJobHistory(['localhost'])

    assert 'Cannot operate on a closed database' in caplog.text

    assert history is not None
    assert history == []


def test_getJobHistory_none_hosts(tmp_path):
    jrh = jobrunhistory(str(tmp_path), check=True)

    history = jrh.getJobHistory(None)

    assert history is not None
    assert history == []


def test_deleteHistory(tmp_path):
    jrh = jobrunhistory(str(tmp_path), check=True)

    backupstatus = {
                     'hostname':      'localhost',
                     'startdatetime': time.time() - (86400 * 600)
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

    jrh.deleteHistory()

    c = jrh.conn.cursor()

    for table in tables:
        count = get_record_count(c, table)

        assert count is not None
        assert count == 0


def test_deleteHistory_exception(tmp_path, caplog):
    logger().debuglevel = 3

    jrh = jobrunhistory(str(tmp_path), check=True)

    jrh.closeDbHandler()

    jrh.deleteHistory()

    assert 'Cannot operate on a closed database' in caplog.text
