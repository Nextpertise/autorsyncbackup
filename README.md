autorsyncbackup
---------------

`@author: Teun Ouwehand (teun@nextpertise.nl)`

`@company: Nextpertise B.V.`

autorsyncbackup is a backup solutuon completely written in bash as wrapper around rsync. Currently it's only tested for Debian Wheezy. Please create a issue if you find any problem.

How to use:
-----------

Export by example to: /usr/local/share/autorsyncbackup

    $ cd /usr/local/share/
    $ git clone git@github.com:Nextpertise/autorsyncbackup.git
    
create symlink:

    $ ln -s /usr/local/share/autorsyncbackup/autorsyncbackup-main/autorsyncbackup /usr/local/bin/autorsyncbackup

create a job directory, this directory will contain .yml files with rsync hosts

    $ mkdir /etc/autorsyncbackup

yaml config example: `/etc/autorsyncbackup/host.domain.tld.yml`

    --
    hostname: host.domain.tld
    username: rsyncuser
    password: rsyncpassword
    share: rsyncshare
    backupdir: /var/data/backups_rsync
    speedlimitkb: 1600
    maxcycles: 32
    fileset:
      0: /etc/
      1: /home/

Note: The backupdir will be postfixed with the hostname, by example: `/var/data/backups_rsync/host.domain.tld`

create a directory which contain the backups

    $ mkdir /var/data/backups_rsync

create a directory for output XML files, these contain information about the executed jobs

    $ mkdir /var/spool/autorsyncbackup

Finally execute the backup (You can cron this command)

    $ cd /usr/share/autorsyncbackup
    $ ./autorsyncbackup -j /etc/autorsyncbackup -l /var/spool/autorsyncbackup/
