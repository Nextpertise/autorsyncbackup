from models.config import config
from models.jobrunhistory import jobrunhistory

class statusemail():
    
    def sendStatusEmail(self, jobs):
        # TODO: produce a nice e-mail from this shizzle
        #query_result = jobrunhistory().getJobHistory(self.getBackupHosts(jobs))
        print "--stats--"
        print self.getStats(jobs)
        print "--overall_backup_state--"
        print self.getOverallBackupState(jobs)
        print "--missing_hosts--"
        print self.getMissingHosts(jobs)
        
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
        ret['total_backup_duration'] = 0
        ret['total_number_of_files'] = 0
        ret['total_backup_duration'] = 0
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
        
        ret['average_backup_duration'] = ret['total_backup_duration'] / ret['total_host_count']
        ret['average_speed_limit_kb'] = ret['total_speed_limit_kb'] / ret['total_host_count']
        return ret