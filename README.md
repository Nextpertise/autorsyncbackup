`@author: Teun Ouwehand (teun@nextpertise.nl)`

`@company: Nextpertise B.V.`

autorsyncbackup is a backup solutuon completely written in bash as wrapper around rsync. currently it's only tested for Debian Wheezy. Please create a issue if you find any problem.

How to use:
-----------

copy both bash files to: /usr/share/autorsyncbackup

    $ mkdir /usr/share/autorsyncbackup`
    $ cp autorsyncbackup /usr/share/autorsyncbackup/
    $ cp rsync_lib.sh /usr/share/autorsyncbackup/

create a job directory, this directory will contain .yml files with rsync hosts
    $ mkdir /etc/autorsyncbackup

yaml config example

    --
    hostname: host.domain.tld
    username: rsyncuser
    password: rsyncpassword
    share: rsyncshare
    backupdir: /var/data/backups_rsync
    speedlimitkb: 1600
    fileset:
      0: /etc/
      1: /home/

create a directory which contain the backups

    $ mkdir /var/data/backups_rsync

create a directory for output XML files, these contain information about the executed jobs

    $ mkdir /var/spool/rsyncbackup

Finally execute the backup (You can cron this command)

    $ cd /usr/share/autorsyncbackup
    $ ./autorsyncbackup -j /etc/autorsyncbackup -l /var/spool/rsyncbackup/
