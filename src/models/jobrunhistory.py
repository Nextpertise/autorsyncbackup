import datetime
import sqlite3
import time

from .config import config
from lib.logger import logger


class jobrunhistory():
    # Default config values
    dbdirectory = None
    conn = None

    def __init__(self, dbdirectory=None, check=False):
        self.dbdirectory = config().jobspooldirectory
        if dbdirectory:
            self.dbdirectory = dbdirectory
        self.openDbHandler()
        if check:
            self.checkTables()

    def openDbHandler(self):
        path = "%s/autorsyncbackup.db" % self.dbdirectory
        try:
            self.conn = sqlite3.connect(path)
            logger().debug("open db [%s]" % path)
        except Exception:
            exitcode = 1
            logger().error(("Error while opening db (%s)"
                            " due to unexisting directory"
                            " or permission error,"
                            " exiting (%d)") % (path, exitcode))
            exit(exitcode)

    def closeDbHandler(self):
        path = "%s/autorsyncbackup.db" % self.dbdirectory
        try:
            self.conn.close()
            logger().debug("close db [%s]" % path)
        except Exception:
            pass

    def checkTables(self):
        logger().debug("Check for table `jobrunhistory`")
        c = self.conn.cursor()
        c.execute(("SELECT name FROM sqlite_master"
                   " WHERE type='table' AND name='jobrunhistory'"))
        if c.fetchone() is None:
            self.createTableJobrunhistoryTable()

        logger().debug("Check for table jobcommandhistory")
        c.execute(("SELECT name FROM sqlite_master"
                   " WHERE type='table' AND name='jobcommandhistory'"))
        if c.fetchone() is None:
            self.createTableJobcommandhistoryTable()

    def createTableJobrunhistoryTable(self):
        jobrunhistoryTable = '''
                             CREATE TABLE IF NOT EXISTS jobrunhistory (
                                 id INTEGER PRIMARY KEY  AUTOINCREMENT,
                                 integrity_id TEXT,
                                 hostname TEXT,
                                 startdatetime INTEGER,
                                 enddatetime INTEGER,
                                 username TEXT,
                                 ssh INTEGER,
                                 share TEXT,
                                 include TEXT,
                                 exclude TEXT,
                                 backupdir TEXT,
                                 speedlimitkb INTEGER,
                                 filesrotate TEXT,
                                 type TEXT,
                                 rsync_backup_status INTEGER,
                                 rsync_return_code INTEGER,
                                 rsync_pre_stdout TEXT,
                                 rsync_stdout TEXT,
                                 rsync_number_of_files INTEGER,
                                 rsync_number_of_files_transferred INTEGER,
                                 rsync_total_file_size INTEGER,
                                 rsync_total_transferred_file_size INTEGER,
                                 rsync_literal_data INTEGER,
                                 rsync_matched_data INTEGER,
                                 rsync_file_list_size INTEGER,
                                 rsync_file_list_generation_time NUMERIC,
                                 rsync_file_list_transfer_time NUMERIC,
                                 rsync_total_bytes_sent INTEGER,
                                 rsync_total_bytes_received INTEGER,
                                 sanity_check INTEGER
                             );
                             '''
        logger().debug("create table `jobrunhistory`")
        logger().debug("%s" % jobrunhistoryTable.replace("\n", ""))
        c = self.conn.cursor()
        c.execute(jobrunhistoryTable)

    def createTableJobcommandhistoryTable(self):
        sql = '''
              CREATE TABLE IF NOT EXISTS jobcommandhistory (
                  id INTEGER PRIMARY KEY AUTOINCREMENT,
                  jobrunid INTEGER NOT NULL,
                  local INTEGER,
                  before INTEGER,
                  returncode INTEGER,
                  continueonerror INTEGER,
                  script TEXT,
                  stdout TEXT,
                  stderr TEXT
              );
              '''
        logger().debug('create table `jobcommandhistory`')
        logger().debug("%s" % sql.replace("\n",  ""))
        c = self.conn.cursor()
        c.execute(sql)

    def insertJob(self, backupstatus,  hooks):
        """Insert job run details into the database"""
        try:
            columns = ', '.join(backupstatus.keys())
            placeholders = ', '.join(['?'] * len(backupstatus))
            query = "INSERT INTO jobrunhistory (%s) VALUES (%s)" % (
                    columns, placeholders)
            c = self.conn.cursor()
            c.execute(query, list(backupstatus.values()))

            jobid = c.lastrowid
            if hooks is not None:
                for hook in hooks:
                    sql = """
                          INSERT INTO jobcommandhistory (
                              jobrunid,
                              local,
                              before,
                              returncode,
                              continueonerror,
                              script,
                              stdout,
                              stderr
                          ) VALUES (
                              ?, ?, ?, ?, ?, ?, ?, ?
                          )
                          """
                    logger().debug("%s" % sql.replace("\n",  ""))
                    c.execute(
                        sql,
                        (
                            jobid,
                            hook['local'],
                            hook['runtime'] == 'before',
                            hook.get('returncode', -1),
                            int(hook['continueonerror'] is True),
                            hook['script'],
                            hook.get('stdout', 'not run'),
                            hook.get('stderr', 'not run')
                        )
                    )

            self.conn.commit()
            logger().debug("Committed job history to database")
        except Exception as e:
            logger().debug(columns)
            logger().debug(backupstatus.values())
            logger().error(("Could not insert job details for host (%s)"
                            " into the database (%s): %s") % (
                            backupstatus['hostname'],
                            self.dbdirectory + "/autorsyncbackup.db",
                            e))

    def identifyJob(self, job, directory):
        c = self.conn.cursor()
        query = """
                SELECT id,
                       startdatetime,
                       rsync_total_file_size,
                       rsync_literal_data
                  FROM jobrunhistory
                 WHERE hostname = ?
                   AND startdatetime <= ?
              ORDER BY startdatetime DESC
                 LIMIT 1
                """
        dt = datetime.datetime.strptime(directory[:19], '%Y-%m-%d_%H-%M-%S')
        sec = int(time.mktime(dt.timetuple()))
        c.execute(query, (job.hostname, sec))
        ret = c.fetchall()
        if not ret:
            logger().error('cannot identify job for %s,%s'
                           % (job.hostname, sec))
            return None
        j = ret[0]
        d = abs(sec-j[1])
        if d > 8:
            logger().warning('large time difference for job %s,%s: %s'
                             % (job.hostname, sec, d))
        if j[2] is None or j[2] == '' or j[3] is None or j[3] == '':
            logger().warning(('invalid values for job %s,'
                              ' id %s, total %s, average %s')
                             % (job.hostname, j[0], j[2], j[3]))
        return j

    def getJobHistory(self, hosts):
        ret = []
        if hosts:
            for host in hosts:
                try:
                    c = self.conn.cursor()
                    c.row_factory = self.dict_factory
                    # Get last run history of given hosts
                    query = """
                            SELECT *
                              FROM jobrunhistory
                             WHERE hostname = ?
                          ORDER BY startdatetime DESC
                             LIMIT 1
                            """
                    c.execute(query, [host])
                    rows = c.fetchall()

                    for row in rows:
                        query = """
                                SELECT *
                                  FROM jobcommandhistory
                                 WHERE jobrunid = ?
                                """
                        c.execute(query, [row['id']])
                        row['commands'] = c.fetchall()

                        ret.append(row)
                except Exception as e:
                    logger().error(e)
        return ret

    def deleteHistory(self):
        try:
            c = self.conn.cursor()
            c.row_factory = self.dict_factory
            query = """
                    SELECT id
                      FROM jobrunhistory
                     WHERE startdatetime < strftime('%s','now','-%d days')
                    """ % ('%s', config().databaseretention)
            c.execute(query)
            result = c.fetchall()
            for row in result:
                c.execute(("DELETE FROM jobcommandhistory"
                           " WHERE jobrunid = %d") % row['id'])
                c.execute(("DELETE FROM jobrunhistory"
                           " WHERE id = %d") % row['id'])
        except Exception as e:
            logger().error(e)

    def dict_factory(self, cursor, row):
        d = {}
        for idx, col in enumerate(cursor.description):
            d[col[0]] = row[idx]
        return d
