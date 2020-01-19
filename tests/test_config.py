import os
import re
import socket

import pytest
import yaml

from models.config import config


def test_readConfig(test_config, tmp_path):
    attributes = {
                   'mainconfigpath':       os.path.join(
                                               str(tmp_path),
                                               'main.yaml'
                                           ),
                   'rsyncpath':            '/usr/bin/rsync',
                   'lockfile':             os.path.join(
                                               str(tmp_path),
                                               'autorsyncbackup.pid'
                                           ),
                   'jobconfigdirectory':   str(tmp_path),
                   'jobspooldirectory':    str(tmp_path),
                   'backupdir':            str(tmp_path),
                   'logfile':              os.path.join(
                                               str(tmp_path),
                                               'autorsyncbackup.log'
                                           ),
                   'speedlimitkb':         0,
                   'dailyrotation':        8,
                   'weeklyrotation':       5,
                   'monthlyrotation':      13,
                   'weeklybackup':         6,
                   'monthlybackup':        1,
                   'include':              [],
                   'exclude':              [],
                   'backupmailfrom':       'backup@%s' % socket.getfqdn(),
                   'backupmailrecipients': [],
                   'jobworkers':           3,
                   'debuglevel':           0,
                   'databaseretention':    540,
                 }

    with open(attributes['mainconfigpath'], 'w') as f:
        for key in [
                     'rsyncpath',
                     'lockfile',
                     'jobconfigdirectory',
                     'jobspooldirectory',
                     'backupdir',
                     'logfile',
                     'debuglevel',
                   ]:
            f.write('%s: %s\n' % (key, attributes[key]))

    config().mainconfigpath = attributes['mainconfigpath']
    config().backupmailrecipients = []

    config().readConfig()

    assert config().mainconfigpath == attributes['mainconfigpath']
    assert config().rsyncpath == attributes['rsyncpath']
    assert config().lockfile == attributes['lockfile']
    assert config().jobconfigdirectory == attributes['jobconfigdirectory']
    assert config().jobspooldirectory == attributes['jobspooldirectory']
    assert config().backupdir == attributes['backupdir']
    assert config().logfile == attributes['logfile']
    assert config().speedlimitkb == attributes['speedlimitkb']
    assert config().dailyrotation == attributes['dailyrotation']
    assert config().weeklyrotation == attributes['weeklyrotation']
    assert config().monthlyrotation == attributes['monthlyrotation']
    assert config().weeklybackup == attributes['weeklybackup']
    assert config().monthlybackup == attributes['monthlybackup']
    assert config().include == attributes['include']
    assert config().exclude == attributes['exclude']
    assert config().backupmailfrom == attributes['backupmailfrom']
    assert config().backupmailrecipients == attributes['backupmailrecipients']
    assert config().jobworkers == attributes['jobworkers']
    assert config().debuglevel == attributes['debuglevel']
    assert config().databaseretention == attributes['databaseretention']


def test_readConfig_load_exception(monkeypatch, capsys):
    def mock_load(stream):
        raise IOError('Mock load failure')

    monkeypatch.setattr(yaml, 'load', mock_load)

    with pytest.raises(SystemExit) as e:
        config().readConfig()

    assert e.type == SystemExit
    assert e.value.code == 1

    captured = capsys.readouterr()

    assert 'Error while reading main config' in captured.out


def test_readConfig_exceptions(monkeypatch):
    def mock_load(stream):
        return {}

    monkeypatch.setattr(yaml, 'load', mock_load)

    config().debugmessages = []

    assert len(config().debugmessages) == 0

    config().readConfig()

    assert len(config().debugmessages) > 1


def test_spam():
    assert re.match(r'^\d+$', str(config().spam()))
