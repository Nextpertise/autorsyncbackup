import datetime
from models.config import config
from models.jobrunhistory import jobrunhistory
from mailer import Mailer, Message
from jinja2 import Environment, PackageLoader
from collections import OrderedDict

class statusemail():
    def sendStatusEmail(self, jobs):
        state = self.getOverallBackupState(jobs)
        hosts = self.getBackupHosts(jobs)
        missinghosts = self.getMissingHosts(jobs)
        stats = self.getStats(jobs)
        jrh = jobrunhistory().getJobHistory(self.getBackupHosts(jobs))
        
        subject = "%d jobs OK - %d jobs FAILED - %s" % (stats['total_backups_success'], stats['total_backups_failed'], datetime.datetime.today().strftime("%a, %d/%m/%Y"))
        body = self.getHtmlEmailBody(state, hosts, missinghosts, stats, jrh, jobs)
        self._send(subject=subject, htmlbody=body)
        
    def getHtmlEmailBody(self, state, hosts, missinghosts, stats, jobrunhistory, jobs):
        env = Environment(loader=PackageLoader('autorsyncbackup', 'templates'))
        env.filters['datetimeformat'] = self._epochToStrDate
        env.filters['bytesformat'] = self._bytesToReadableStr
        env.filters['secondsformat'] = self._secondsToReadableStr
        env.filters['numberformat'] = self._intToReadableStr
        template = env.get_template('email.tpl')
        return template.render(state=state, hosts=hosts, missinghosts=missinghosts, stats=stats, jobrunhistory=jobrunhistory, jobs=jobs)
        
    def getOverallBackupState(self, jobs):
        """Overall backup state = 'ok' unless there is at least one failed backup"""
        ret = "ok"
        for j in jobrunhistory().getJobHistory(self.getBackupHosts(jobs)):
            if j['rsync_backup_status'] != "1":
                ret = "error"        
        return ret
    
    def getBackupHosts(self, jobs):
        """Get all configured hosts"""
        ret = []
        for j in jobs:
            ret.append(j.hostname)
        return ret
        
    def getMissingHosts(self, jobs):
        """Add all configured hosts, remove all runned hosts, incase there are elements left we have 'missing' hosts"""
        hosts = []
        for i in jobs:
            hosts.append(i.hostname)
        for j in jobrunhistory().getJobHistory(self.getBackupHosts(jobs)):
            hosts.remove(j['hostname'])
        return hosts
        
    def getStats(self, jobs):
        """Produce total/average stats out database/jobs data"""
        result = jobrunhistory().getJobHistory(self.getBackupHosts(jobs))
        ret = {}
        ret['total_host_count'] = len(result)
        ret['total_backups_failed'] = 0
        ret['total_backup_duration'] = 0
        ret['total_number_of_files'] = 0
        ret['total_number_of_files_transferred'] = 0
        ret['total_file_size'] = 0
        ret['total_transferred_file_size'] = 0
        ret['total_literal_data'] = 0
        ret['total_matched_data'] = 0
        ret['total_file_list_size'] = 0
        ret['total_file_list_generation_time'] = 0
        ret['total_file_list_transfer_time'] = 0
        ret['total_bytes_sent'] = 0
        ret['total_bytes_received'] = 0
        ret['total_speed_limit_kb'] = 0
        
        for i in result:
            if i['rsync_backup_status'] == 1:
                ret['total_backup_duration'] = ret['total_backup_duration'] + (i['enddatetime'] - i['startdatetime'])
                ret['total_number_of_files'] = ret['total_number_of_files'] + i['rsync_number_of_files']
                ret['total_number_of_files_transferred'] = ret['total_number_of_files_transferred'] + i['rsync_number_of_files_transferred']
                ret['total_file_size'] = ret['total_file_size'] + i['rsync_total_file_size']
                ret['total_transferred_file_size'] = ret['total_transferred_file_size'] + i['rsync_total_transferred_file_size']
                ret['total_literal_data'] = ret['total_literal_data'] + i['rsync_literal_data']
                ret['total_matched_data'] = ret['total_matched_data'] + i['rsync_matched_data']
                ret['total_file_list_size'] = ret['total_file_list_size'] + i['rsync_file_list_size']
                ret['total_file_list_generation_time'] = ret['total_file_list_generation_time'] + i['rsync_file_list_generation_time']
                ret['total_file_list_transfer_time'] = ret['total_file_list_transfer_time'] + i['rsync_file_list_transfer_time']
                ret['total_bytes_sent'] = ret['total_bytes_sent'] + i['rsync_total_bytes_sent']
                ret['total_bytes_received'] = ret['total_bytes_received'] + i['rsync_total_bytes_received']
                if i['speedlimitkb']:
                    ret['total_speed_limit_kb'] = ret['total_speed_limit_kb'] + i['speedlimitkb']
            else:
                ret['total_backups_failed'] = ret['total_backups_failed'] + 1
        
        ret['total_backups_success'] = ret['total_host_count'] - ret['total_backups_failed']
        ret['average_backup_duration'] = ret['total_backup_duration'] / ret['total_host_count']
        ret['average_speed_limit_kb'] = ret['total_speed_limit_kb'] / ret['total_host_count']
        return ret
        
    def _send(self, subject, htmlbody):
        for to in config().backupmailrecipients:
            message = Message(From=config().backupmailfrom, To=to, charset="utf-8")
            message.Subject = subject
            message.Html = htmlbody
            message.Body = """This is an HTML e-mail with the backup overview, please use a HTML enabled e-mail client."""
            sender = Mailer(config().smtphost)
            sender.send(message)
        
    # Jinja filters
    def _epochToStrDate(self, epoch, strftime):
        return datetime.datetime.fromtimestamp(epoch).strftime(strftime)
        
    def _bytesToReadableStr(self, bytes):
        try:
          bytes = float(bytes)
        except:
          bytes = 0
        i = 0
        byteUnits = [' Bytes', ' KB', ' MB', ' GB', ' TB', ' PB', ' EB', ' ZB', ' YB']
        bytesStr = "%.0f" % bytes
        while bytes > 1024:
            bytes = bytes / 1024
            i = i + 1
            bytesStr = "%.1f" % bytes
        return bytesStr + byteUnits[i]
        
    def _secondsToReadableStr(self, seconds):
        try:
          seconds = int(seconds)
        except:
          seconds = 0
        if seconds == 0:
            return "0 seconds"
        ret = ""
        units = OrderedDict([('week', 7*24*3600), ('day', 24*3600), ('hour', 3600), ('minute', 60), ('second', 1)])
        for unit in units:
            quot = seconds / units[unit]
            if quot:
               ret = ret + str(quot) + " " + unit
               seconds = seconds - (quot * units[unit])
               if abs(quot) > 1:
                   ret = ret + "s"
               ret = ret + ", "
        return ret[:-2]
        
    def _intToReadableStr(self, x):
        try:
            x = int(x)
        except:
            x = 0
        if x < 0:
            return '-' + intWithCommas(-x)
        result = ''
        while x >= 1000:
            x, r = divmod(x, 1000)
            result = ".%03d%s" % (r, result)
        return "%d%s" % (x, result)