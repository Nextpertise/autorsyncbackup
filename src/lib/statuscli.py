from prettytable import PrettyTable

from models.jobrunhistory import jobrunhistory
from lib.jinjafilters import jinjafilters


class statuscli():
    jobrunhistory = None

    def __init__(self):
        self.jobrunhistory = jobrunhistory()

    def __del__(self):
        self.jobrunhistory.closeDbHandler()

    def getList(self, hostname):
        return self.jobrunhistory.getJobHistory([hostname])

    def printOutput(self, hostname):
        ret = 1
        history = self.getList(hostname)
        if history:
            x = PrettyTable(['Hostname',
                             'Backup status',
                             'Start time',
                             'Duration',
                             'Total number of files',
                             'Total filesize'])
            backupState = 'Failed'
            hostname = history[0]['hostname']
            totalNumberOfFiles = jinjafilters()._intToReadableStr(
                                 history[0]['rsync_number_of_files'])
            totalFileSize = jinjafilters()._bytesToReadableStr(
                            history[0]['rsync_total_file_size'])
            duration = jinjafilters()._secondsToReadableStr(
                       history[0]['enddatetime'] - history[0]['startdatetime']
                       + 1, True)
            starttime = jinjafilters()._epochToStrDate(
                        history[0]['startdatetime'], "%d-%m-%Y %H:%M:%S")
            if history[0]['rsync_backup_status'] == 1:
                backupState = 'Ok'
                ret = 0
            else:
                duration = '-'
                totalNumberOfFiles = '-'
                totalFileSize = '-'
            x.add_row([hostname,
                       backupState,
                       starttime,
                       duration,
                       totalNumberOfFiles,
                       totalFileSize])
            x.align = "l"
            x.padding_width = 1
            print(x)
        else:
            print("Could not find hostname: [%s]" % hostname)
        return ret
