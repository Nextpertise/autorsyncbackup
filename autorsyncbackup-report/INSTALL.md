#Autorsync Backup Report

First clone autorsyncbackup-report in autorsyncbackup subfolder:

    cd /usr/local/share/autorsyncbackup
    git clone https://github.com/ivodvb/AutoRsyncBackup-Report.git autorsyncbackup-report

Install dependecies:

    cd /usr/local/share/autorsyncbackup/autorsyncbackup-report
    ./composer.phar self-update
    ./composer.phar install
 
Start configuration, change e-mail addres(ses) and update hosts in `hostsToBackup` which are obligatory for succesfull backups:

    cp config.yaml.dist config.yaml
 
Autorsyncbackup-report will investigate the latest .log files in the spool directory and can inform you with a daily report. Cron the following command for daily reports:

    php /usr/local/share/autorsyncbackup/autorsyncbackup-report/mail.php
