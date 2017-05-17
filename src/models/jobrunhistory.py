import sqlite3
from config import config
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
        except:
            exitcode = 1
            logger().error("Error while opening db (%s) due to unexisting directory or permission error, exiting (%d)" % (path, exitcode))
            exit(exitcode)
            
    def closeDbHandler(self):
        path = "%s/autorsyncbackup.db" % self.dbdirectory
        try:
            self.conn.close()
            logger().debug("close db [%s]" % path)
        except:
            pass
            
    def checkTables(self):
        logger().debug("Check for table `jobrunhistory`")
        c = self.conn.cursor()
        c.execute("SELECT name FROM sqlite_master WHERE type='table' AND name='jobrunhistory'")
        if c.fetchone() is None:
            self.createTableJobrunhistoryTable()
        
        logger().debug("Check for table jobcommandhistory")
        c.execute("select name from sqlite_master where type='table' and name='jobcommandhistory'")
        if c.fetchone() is None:
            self.createTableJobcommandhistoryTable()
      
        
    def createTableJobrunhistoryTable(self):
        jobrunhistoryTable = 'CREATE TABLE IF NOT EXISTS jobrunhistory \
                                ( \
                                    id INTEGER PRIMARY KEY  AUTOINCREMENT, \
                                    hostname TEXT, \
                                    startdatetime INTEGER, \
                                    enddatetime INTEGER, \
                                    username TEXT, \
                                    ssh INTEGER, \
                                    share TEXT, \
                                    fileset TEXT, \
                                    backupdir TEXT, \
                                    speedlimitkb INTEGER, \
                                    filesrotate TEXT, \
                                    type TEXT, \
                                    rsync_backup_status INTEGER, \
                                    rsync_return_code INTEGER, \
                                    rsync_pre_stdout TEXT, \
                                    rsync_stdout TEXT, \
                                    rsync_number_of_files INTEGER, \
                                    rsync_number_of_files_transferred INTEGER, \
                                    rsync_total_file_size INTEGER, \
                                    rsync_total_transferred_file_size INTEGER, \
                                    rsync_literal_data INTEGER, \
                                    rsync_matched_data INTEGER, \
                                    rsync_file_list_size INTEGER, \
                                    rsync_file_list_generation_time NUMERIC, \
                                    rsync_file_list_transfer_time NUMERIC, \
                                    rsync_total_bytes_sent INTEGER, \
                                    rsync_total_bytes_received INTEGER, \
                                    sanity_check INTEGER \
                                );'
        logger().debug("create table `jobrunhistory`")
        logger().debug("%s" % jobrunhistoryTable.replace("\n",""))
        c = self.conn.cursor()
        c.execute(jobrunhistoryTable)
        
    def createTableJobcommandhistoryTable(self):
        sql = '''
            create table if not exists jobcommandhistory(
                id integer primary key autoincrement,
                jobrunid integer not null,
                local integer,
                before integer,
                returncode integer,
                continueonerror integer,
                script text,
                stdout text,
                stderr text);
        '''
        logger().debug('create table jobcommandhistory')
        logger().debug("%s" % sql.replace("\n",  ""))
        c = self.conn.cursor()
        c.execute(sql)
        
    def insertJob(self, backupstatus,  hooks):
        """Insert job run details into the database"""
        try:
            columns = ', '.join(backupstatus.keys())
            placeholders = ', '.join(['?'] * len(backupstatus))
            query = "INSERT INTO jobrunhistory ( %s ) VALUES ( %s )" % (columns, placeholders)
            c = self.conn.cursor()
            c.execute(query, backupstatus.values())

            jobid = c.lastrowid
            if hooks != None:
                for hook in hooks:
                    sql = "insert into jobcommandhistory (jobrunid, local, before, returncode, continueonerror, script, stdout, stderr) values (%d, %d, %d, %d, %d, '%s', '%s', '%s')" % (
                        jobid,
                        hook['local'],
                        hook['runtime'] == 'before',
                        hook['returncode'],
                        int(hook['continueonerror'] == True),
                        hook['script'], 
                        hook['stdout'],
                        hook['stderr'])
                    logger().debug(sql)
                    c.execute(sql)

            self.conn.commit()
            logger().debug("Commited job history to database")
        except Exception as e:
            logger().error("Could not insert job details for host (%s) into the database (%s): %s" % (backupstatus['hostname'], self.dbdirectory + "/autorsyncbackup.db", e))
            
    def getJobHistory(self, hosts):
        ret = []
        if hosts:
            try:
                c = self.conn.cursor()
                c.row_factory = self.dict_factory
                placeholders = ', '.join(['?'] * len(hosts))
                # Get last run history of given hosts
                query = "SELECT * FROM jobrunhistory WHERE hostname in (%s) GROUP BY hostname;" % placeholders
                c.execute(query, hosts)
                ret = c.fetchall()
                
                for row in ret:
                    query = "select * from jobcommandhistory where jobrunid = %d" % row['id']
                    c.execute(query)
                    row['commands'] = c.fetchall()
            except Exception as e:
                logger().error(e)
        return ret

    def deleteHistory(self):
        try:
            c = self.conn.cursor()
            c.execute("select id from jobrunhistory where startdatetime < strftime('%s','now','-%d days')" % ('%s', config().databaseretention))
            result = c.fetchall()
            for row in result:
                c.execute("delete from jobcommandhistory where jobrunid = %d" % row['id'])
                c.execute("delete from jobrunhistory where id = %d" % row['id'])
        except Exception as e:
            logger().error(e)

    def dict_factory(self, cursor, row):
        d = {}
        for idx, col in enumerate(cursor.description):
            d[col[0]] = row[idx]
        return d

