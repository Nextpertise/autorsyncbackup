import datetime
from models.config import config
from models.jobrunhistory import jobrunhistory
from lib.jinjafilters import jinjafilters
from lib.logger import logger
from mailer import Mailer, Message
from jinja2 import Environment, PackageLoader

class statusemail():
    def sendStatusEmail(self, jobs, durationstats):
        state = self.getOverallBackupState(jobs)
        hosts = self.getBackupHosts(jobs)
        missinghosts = self.getMissingHosts(jobs)
        stats = self.getStats(jobs)
        jrh = jobrunhistory().getJobHistory(self.getBackupHosts(jobs))
        
        subject = "%d jobs OK - %d jobs FAILED - %s" % (stats['total_backups_success'], stats['total_backups_failed'], datetime.datetime.today().strftime("%a, %d/%m/%Y"))
        body = self.getHtmlEmailBody(state, hosts, missinghosts, stats, durationstats, jrh, jobs)
        self._send(subject=subject, htmlbody=body)
        
    def getHtmlEmailBody(self, state, hosts, missinghosts, stats, durationstats, jobrunhistory, jobs):
        env = Environment(loader=PackageLoader('autorsyncbackup', 'templates'))
        env.filters['datetimeformat'] = jinjafilters()._epochToStrDate
        env.filters['bytesformat'] = jinjafilters()._bytesToReadableStr
        env.filters['secondsformat'] = jinjafilters()._secondsToReadableStr
        env.filters['numberformat'] = jinjafilters()._intToReadableStr
        template = env.get_template('email.j2')
        return template.render(state=state, hosts=hosts, missinghosts=missinghosts, stats=stats, durationstats=durationstats, jobrunhistory=jobrunhistory, jobs=jobs)
        
    def getOverallBackupState(self, jobs):
        """Overall backup state = 'ok' unless there is at least one failed backup"""
        ret = "ok"
        for j in jobrunhistory().getJobHistory(self.getBackupHosts(jobs)):
            if j['rsync_backup_status'] != 1:
                ret = "error"        
        return ret
    
    def getBackupHosts(self, jobs):
        """Get all configured hosts"""
        ret = []
        for j in jobs:
            if j.enabled:
                ret.append(j.hostname)
        return ret
        
    def getMissingHosts(self, jobs):
        """Add all configured hosts, remove all runned hosts, incase there are elements left we have 'missing' hosts"""
        hosts = []
        for i in jobs:
            if i.enabled:
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
        ret['total_rsync_duration'] = 0
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
        ret['average_backup_duration'] = 0
        ret['average_speed_limit_kb'] = 0
        
        for i in result:
            if i['rsync_backup_status'] == 1:
                ret['total_rsync_duration'] = ret['total_rsync_duration'] + (i['enddatetime'] - i['startdatetime'])
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
        if ret['total_backups_success'] > 0:
            ret['average_backup_duration'] = ret['total_rsync_duration'] / ret['total_backups_success']
            ret['average_speed_limit_kb'] = ret['total_speed_limit_kb'] / ret['total_backups_success']
        return ret
        
    def _send(self, subject, htmlbody):
        for to in config().backupmailrecipients:
            logger().info("INFO: Sent backup report to [%s] via SMTP:%s" % (to, config().smtphost))
            message = Message(From=config().backupmailfrom, To=to, charset="utf-8")
            message.Subject = subject
            message.Html = htmlbody
            message.Body = """This is an HTML e-mail with the backup overview, please use a HTML enabled e-mail client."""
            sender = Mailer(config().smtphost)
            sender.send(message)