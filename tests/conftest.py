import os

import pytest

from lib.jinjafilters import jinjafilters
from models.config import config


@pytest.fixture
def filters():
    filters = jinjafilters()

    yield filters


@pytest.fixture
def test_config(tmp_path):
    path = os.path.join(
                         str(tmp_path),
                         'main.yaml',
                       )

    options = {
                'lockfile':           os.path.join(
                                          str(tmp_path),
                                          'autorsyncbackup.pid'
                                      ),
                'jobconfigdirectory': os.path.join(
                                          str(tmp_path),
                                          'etc',
                                      ),
                'jobspooldirectory':  os.path.join(
                                          str(tmp_path),
                                          'spool',
                                      ),
                'backupdir':          os.path.join(
                                          str(tmp_path),
                                          'backups',
                                      ),
                'logfile':            os.path.join(
                                          str(tmp_path),
                                          'log/autorsyncbackup.log'
                                      ),
                'debuglevel':         4,
              }

    with open(path, 'w') as f:
        for key in options:
            f.write("%s: %s\n" % (key, options[key]))

    config(path)

    return True
