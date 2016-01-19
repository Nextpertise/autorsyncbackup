AutoRsyncbackup
---------------

AutoRsyncBackup is a backup solution written in Python as wrapper around Rsync.
Currently it's only tested for Debian Wheezy, but it should work on any other Linux distribution.
Please create an issue if you find any problem.

    @author: Teun Ouwehand (teun@nextpertise.nl)
    @company: Nextpertise B.V.

Install AutoRsyncbackup (Server):
-----------

Export by example to: `/usr/local/share/autorsyncbackup`

    $ cd /usr/local/share/
    $ git clone git@github.com:Nextpertise/autorsyncbackup.git

Install dependencies:

    $ apt-get install python python-yaml python-jinja2 python-mailer python-paramiko python-prettytable
    
Create symlink:

    $ ln -s /usr/local/share/autorsyncbackup/src/autorsyncbackup.py /usr/local/bin/autorsyncbackup

Create a job directory, this directory will contain .job files with rsync hosts:

    $ mkdir /etc/autorsyncbackup

The job files are written in YAML syntax and will only apply with the `.job` file extension, config example: `/etc/autorsyncbackup/host.domain.tld.job`

    ---
    hostname: host.domain.tld
    username: rsyncuser
    password: rsyncpassword
    share: rsyncshare
    backupdir: /var/data/backups_rsync
    speedlimitkb: 1600
    dailyrotation = 8
    weeklyrotation = 5
    monthlyrotation = 13
    fileset:
      - /etc/
      - /home/
    hooks:
      - script: /bin/false
        local: true
        runtime: before
        continueonerror: true
    
      - script: /bin/ls -l
        local: false
        runtime: after
        continueonerror: true

Define the main config at: `/etc/autorsyncbackup/main.yaml`, config example:

    ---
    debug: True
    weeklybackup: 7
    monthlybackup: 1
    backupmailrecipients:
        - your@mail.com
    
Note: The backupdir will be postfixed with the hostname, by example: `/var/data/backups_rsync/host.domain.tld/`

Create a directory which contain the backups:

    $ mkdir /var/data/backups_rsync

Create the directory where the SqLite database file will be stored:

    $ mkdir /var/lib/autorsyncbackup

Finally execute the backup (you can cron this command):

    $ /usr/local/bin/autorsyncbackup
    
Install rsync as deamon (Client)
-----------------------
    
Install the debian package:

    $ apt-get install rsync
    
Enable deamon in `/etc/default/rsync`:
    
    RSYNC_ENABLE=true
    
Configure rsync for accepting connections (Change `1.2.3.4` ip-adres to backup server):
    
    uid = root
    gid = root
    pid file = /var/run/rsyncd.pid
    log file = /var/log/rsync.log
    hosts allow = 1.2.3.4
    max connections = 2
    
    [backup]
            comment = backup share
            path = /
            read only = yes
            auth users= backup
            secrets file = /etc/rsyncd.secrets
    
Configure a password in `/etc/rsyncd.secrets`:
    
    backup:VerySecretPasswordHere
    
Adjust permissions on `/etc/rsyncd.secrets`:
    
    chmod 500 /etc/rsyncd.secrets

Start the rsync daemon with the init script:

    $ /etc/init.d/rsync start

Command line options
--------------------
* -c, --main-config <configfile>    Defines the main config file, default is `/etc/autorsyncbackup/main.yaml`.
* -d, --dry-run                     Dry run, do try to login on host but do not invoke rsync or hook scripts.
* -v, --verbose                     Write logoutput also to stdout
* --version                         Show version number
* -j, --single-job <jobfile>        Run only the given job file
* -s, --status <hostname>           Get status of last backup run of the given hostname. The exit code will be set (0 for success, 1 for error)

Config file options
-------------------

Job file options
----------------
