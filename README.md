AutoRsyncbackup
---------------

AutoRsyncBackup is a backup solution written in Python as wrapper around Rsync.
Currently it's only tested for **Debian Jessie**, but it should work on any other Linux distribution.
Please create an issue if you find any problem.

    @author: Teun Ouwehand (teun@nextpertise.nl)
    @company: Nextpertise B.V.

Install AutoRsyncbackup (Server):
-----------

Export for example to: `/usr/local/share/autorsyncbackup`

```
cd /usr/local/share/
git clone git@github.com:Nextpertise/autorsyncbackup.git
```

Install dependencies:

`apt-get install python python-yaml python-jinja2 python-mailer python-paramiko python-prettytable`
    
Create symlink:

`ln -s /usr/local/share/autorsyncbackup/src/autorsyncbackup.py /usr/local/bin/autorsyncbackup`

Create a job directory, this directory will contain .job files with rsync hosts:

`mkdir /etc/autorsyncbackup`

The job files are written in YAML syntax and will only apply with the `.job` file extension, config example: `/etc/autorsyncbackup/host.domain.tld.job`
```
hostname: host.domain.tld
username: rsyncuser
password: rsyncpassword
share: rsyncshare
backupdir: /var/data/backups_rsync
speedlimitkb: 1600
dailyrotation: 8
weeklyrotation: 5
monthlyrotation: 13
include: #formerly fileset
  - /etc/
  - /home/
exclude:
  - "*.bak"
  - ".cache/*"
hooks:
  - script: /bin/false
    local: true
    runtime: before
    continueonerror: true

  - script: /bin/ls -l
    local: false
    runtime: after
    continueonerror: true
```

Define the main config at: `/etc/autorsyncbackup/main.yaml`, config example:
```
debuglevel: 2
weeklybackup: 6
monthlybackup: 1
backupmailrecipients:
    - your@mail.com
```

Note: The backupdir will be postfixed with the hostname, by example: `/var/data/backups_rsync/host.domain.tld/`

Create a directory which contain the backups:

`mkdir -p /var/data/backups_rsync`

Create the directory where the SqLite database file will be stored:

`mkdir /var/spool/autorsyncbackup`

Finally execute the backup (you can cron this command):

`/usr/local/bin/autorsyncbackup`
    
Install rsync as deamon (Client)
-----------------------
    
Install the debian package:

`apt-get install rsync`
    
Enable deamon in `/etc/default/rsync`:
    
`RSYNC_ENABLE=true`
    
Configure rsync for accepting connections (Change `1.2.3.4` ip-adres to backup server):
```
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
```

Configure a password in `/etc/rsyncd.secrets`:
    
`backup:VerySecretPasswordHere`
    
Adjust permissions on `/etc/rsyncd.secrets`:
    
`chmod 500 /etc/rsyncd.secrets`

Start the rsync daemon with the init script:

`/etc/init.d/rsync start`

Command line options
--------------------
* `-c, --main-config <configfile>   `Defines the main config file, default is `/etc/autorsyncbackup/main.yaml`.
* `-d, --dry-run                    `Dry run, do try to login on host but do not invoke rsync or hook scripts.
* `-v, --verbose                    `Write logoutput also to stdout
* `--version                        `Show version number
* `-j, --single-job <jobfile>       `Run only the given job file
* `-s, --status <hostname>          `Get status of last backup run of the given hostname. The exit code will be set (0 for success, 1 for error)
* `-l, --list-jobs total|average    `Get list of jobs, sorted by total disk usage (total) or by average backup size increase (average)

Config file options
-------------------
(showing default values)

```yaml
rsyncpath:          "/usr/bin/rsync"                                # path to the rsync executable file
lockfile:           "/var/run/autorsyncbackup.pid"                  # path to the run/pid file on your system
jobconfigdirectory: "/etc/autorsyncbackup/"                         # location where .job files are kept
jobspooldirectory:  "/var/spool/autorsyncbackup"                    # location of the spool directory
backupdir:          "/var/data/backups/autorsyncbackup/"            # where the backups are stored
logfile:            "/var/log/autorsyncbackup/autorsyncbackup.log"  # records the actions taken by autorsyncbackup
speedlimitkb:       0                                               # maximize datatransfer speed in KB
dailyrotation:      8                                               # how many 'daily' backups to keep
weeklyrotation:     5                                               # how many 'weekly' backups to keep
monthlyrotation:    13                                              # how many 'monthly' backups to keep
weeklybackup:       6                                               # the day of the week (0 = sunday) on which to make a weekly backup
monthlybackup:      1                                               # the day of the month on which to make a monthly backup
include	     														# list of dirs and files to backup; formerly fileset 
  - /etc/
  - /home/
exclude:															# exclude files matching PATTERN
  - "*.bak"
  - ".cache/*"                                               
backupmailfrom:     ""                                              # email from address
jobworkers:         3                                               # number of concurrent jobs
debuglevel:         0                                               # sets the verbosity of the logfile
databaseretention:  540                                             # how many days the backup status records are kept
smtphost:           _no default value_                              # where to send email to (port 25 is implied)
recipients:                                                         # list of status email recipients
  - maintainer@yourcompany.com
  - another@nodefault.example.com
```

Job file options
----------------
(showing default values)

```yaml
enabled:          True                                     # (en/dis)able this entry
hostname:         _no_default_value_                       # fully qualified domain name of the host being backedup
ssh:              False                                    # whether to use rsync over ssh (True) or plain rsync (False)
rsync_username:   _no_default_value_                       # rsync user account
rsync_password:   _no_default_value_                       # rsync password
rsync_share:      _no_default_value_                       # rsync share
ssh_username:     _no_default_value_                       # ssh username
ssh_publickey:    _no_default_value_                       # ssh private key file (public key on client)
port:             22 or 873                                # defaults to either ssh or rsync port depending on the value of the ssh entry
backupdir:        _taken_from_main_config_file_            # see Config file options
speedlimitkb:     _taken_from_main_config_file_            # see Config file options
dailyrotation:    _taken_from_main_config_file_            # see Config file options
weeklyrotation:   _taken_from_main_config_file_            # see Config file options
monthlyrotation:  _taken_from_main_config_file_            # see Config file options
weeklybackup:     _taken_from_main_config_file_            # see Config file options
monthlybackup:    _taken_from_main_config_file_            # see Config file options
include	     														# list of dirs and files to backup; formerly fileset 
  - /etc/
  - /home/
exclude:															# exclude files matching PATTERN
  - "*.bak:"
  - ".cache/*"                                             
hooks:                                                     # list of pre/post backup scripts (no defaults)
  - script:       name_and_full_path_of_executable         # full path to executable
    local:        False                                    # whether the script runs locally on the server or remote on the client
    runtime:      before                                   # whether the script runs "before" or "after" the backup
    continueonerror: False                                 # abort backup run when script fails
```
