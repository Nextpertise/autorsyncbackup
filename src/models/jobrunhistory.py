from config import config
import sqlite3

class jobrunhistory():
    class __impl:
        """ Implementation of the singleton interface """
        
        # Default config values
        dbdirectory = "/var/lib/autorsyncbackup"
        conn = None

        def spam(self):
            """ Test method, return singleton id """
            return id(self)

    # storage for the instance reference
    __instance = None
    
    def __init__(self, dbdirectory=None):
        """ Create singleton instance """
        # Check whether we already have an instance
        if jobrunhistory.__instance is None:
            # Create and remember instance
            jobrunhistory.__instance = jobrunhistory.__impl()
            
            if(dbdirectory):
                self.dbdirectory = dbdirectory
            self.openDbHandler()
            self.checkTables()
            self.init = False

        # Store instance reference as the only member in the handle
        self.__dict__['_jobrunhistory__instance'] = jobrunhistory.__instance

    def __getattr__(self, attr):
        """ Delegate access to implementation """
        return getattr(self.__instance, attr)

    def __setattr__(self, attr, value):
        """ Delegate access to implementation """
        return setattr(self.__instance, attr, value)
            
    def openDbHandler(self):
        path = "%s/autorsyncbackup.db" % self.dbdirectory
        try:
            self.conn = sqlite3.connect(path)
            if config().debug:
                print "DEBUG: open %s" % path
        except:
            print "Error while opening db (%s) due to unexisting directory or permission error" % path
            exit(1)
            
    def checkTables(self):
        print "DEBUG: Check for table `jobrunhistory`"
        c = self.conn.cursor()
        c.execute("SELECT name FROM sqlite_master WHERE type='table' AND name='jobrunhistory'")
        if c.fetchone() is None:
          self.createTableJobrunhistoryTable()
        
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
                                    rsync_total_bytes_received INTEGER \
                                );'
        if config().debug:
            print "DEBUG: create table `jobrunhistory`"
            print jobrunhistoryTable
        c = self.conn.cursor()
        c.execute(jobrunhistoryTable)
        
    def insertJob(self, backupstatus):
        """Insert job run details into the database"""
        try:
            columns = ', '.join(backupstatus.keys())
            placeholders = ', '.join(['?'] * len(backupstatus))
            query = "INSERT INTO jobrunhistory ( %s ) VALUES ( %s )" % (columns, placeholders)
            c = self.conn.cursor()
            c.execute(query, backupstatus.values())
            self.conn.commit()
        except:
            print "ERROR: Could not insert job details for host (%s) into the database (%s)" % (backupstatus['hostname'], self.dbdirectory + "/autorsyncbackup.db")
            
    def getJobHistory(self, hosts):
        ret = None
        if hosts:
            try:
                c = self.conn.cursor()
                c.row_factory = self.dict_factory
                placeholders = ', '.join(['?'] * len(hosts))
                # TODO: Only report backups of last 24h / make this variabel in config
                query = "SELECT * FROM jobrunhistory WHERE hostname in (%s) GROUP BY hostname;" % placeholders
                c.execute(query, hosts)
                ret = c.fetchall()
            except:
                pass
        return ret
        
    def dict_factory(self, cursor, row):
        d = {}
        for idx, col in enumerate(cursor.description):
            d[col[0]] = row[idx]
        return d