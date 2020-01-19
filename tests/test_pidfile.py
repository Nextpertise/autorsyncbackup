import errno
import os
import sys

import pytest

from lib.pidfile import (
    Pidfile,
    ProcessRunningException,
    PidfileProcessRunningException,
)


def test_init(tmp_path):
    path = os.path.join(
                         str(tmp_path),
                         'autorsyncbackup.pid',
                       )

    pf = Pidfile(path)

    assert pf.pidfile == path
    assert pf.log == sys.stdout.write
    assert pf.warn == sys.stderr.write


def test_enter(tmp_path):
    path = os.path.join(
                         str(tmp_path),
                         'autorsyncbackup.pid',
                       )

    pf = Pidfile(path)

    pf.__enter__()

    assert pf.pidfd is not None

    assert os.path.exists(path) is True

    with open(path) as f:
        pid = f.read()

        assert pid == str(os.getpid())


def test_enter_exists(tmp_path):
    path = os.path.join(
                         str(tmp_path),
                         'autorsyncbackup.pid',
                       )

    pf1 = Pidfile(path)

    pf1.__enter__()

    assert pf1.pidfd is not None

    assert os.path.exists(path) is True

    pf2 = Pidfile(path)

    with pytest.raises(ProcessRunningException) as e:
        pf2.__enter__()

        assert pf2.pidfd is None
        assert 'process already running' in str(e)


def test_enter_stale(tmp_path, monkeypatch):
    def mock_kill(pid, signal):
        raise IOError('Mock kill failure')

    monkeypatch.setattr(os, 'kill', mock_kill)

    path = os.path.join(
                         str(tmp_path),
                         'autorsyncbackup.pid',
                       )

    pf1 = Pidfile(path)

    pf1.__enter__()

    assert pf1.pidfd is not None

    assert os.path.exists(path) is True

    pf2 = Pidfile(path)

    pf2.__enter__()

    assert pf2.pidfd is not None

    assert os.path.exists(path) is True


def test_enter_exception(tmp_path, monkeypatch):
    def mock_open(pid, signal):
        raise OSError(errno.ENOSPC, 'Mock open failure')

    monkeypatch.setattr(os, 'open', mock_open)

    path = os.path.join(
                         str(tmp_path),
                         'autorsyncbackup.pid',
                       )

    pf = Pidfile(path)

    with pytest.raises(OSError) as e:
        pf.__enter__()

        assert e.errno == errno.ENOSPC
        assert 'Mock open failure' in str(e)


def test_exit(tmp_path):
    path = os.path.join(
                         str(tmp_path),
                         'autorsyncbackup.pid',
                       )

    pf = Pidfile(path)

    pf.__enter__()

    exc_type = None
    exc_value = None
    exc_tb = None

    ret = pf.__exit__(exc_type, exc_value, exc_tb)

    assert ret is True

    assert os.path.exists(path) is False


def test_exit_PidfileProcessRunningException(tmp_path):
    path = os.path.join(
                         str(tmp_path),
                         'autorsyncbackup.pid',
                       )

    pf = Pidfile(path)

    pf.__enter__()

    exc_type = PidfileProcessRunningException
    exc_value = 'Mock value'
    exc_tb = 'Mock traceback'

    ret = pf.__exit__(exc_type, exc_value, exc_tb)

    assert ret is False

    assert os.path.exists(path) is True


def test_exit_OSError(tmp_path):
    path = os.path.join(
                         str(tmp_path),
                         'autorsyncbackup.pid',
                       )

    pf = Pidfile(path)

    pf.__enter__()

    exc_type = OSError
    exc_value = 'Mock value'
    exc_tb = 'Mock traceback'

    ret = pf.__exit__(exc_type, exc_value, exc_tb)

    assert ret is False

    assert os.path.exists(path) is False


def test_exit_OSError_no_pidfd(tmp_path):
    path = os.path.join(
                         str(tmp_path),
                         'autorsyncbackup.pid',
                       )

    pf = Pidfile(path)

    pf.__enter__()

    pf.pidfd = None

    exc_type = OSError
    exc_value = 'Mock value'
    exc_tb = 'Mock traceback'

    ret = pf.__exit__(exc_type, exc_value, exc_tb)

    assert ret is False

    assert os.path.exists(path) is True


def test_remove(tmp_path):
    path = os.path.join(
                         str(tmp_path),
                         'autorsyncbackup.pid',
                       )

    pf = Pidfile(path)

    pf.__enter__()

    assert os.path.exists(path) is True

    pf._remove()

    assert os.path.exists(path) is False


def test_check(tmp_path):
    path = os.path.join(
                         str(tmp_path),
                         'autorsyncbackup.pid',
                       )

    pf = Pidfile(path)

    pf.__enter__()

    pid = pf._check()

    assert pid == int(os.getpid())


def test_check_ValueError(tmp_path):
    path = os.path.join(
                         str(tmp_path),
                         'autorsyncbackup.pid',
                       )

    pf = Pidfile(path)

    with open(pf.pidfile, 'w') as f:
        f.write('Test')

    pid = pf._check()

    assert pid is False


def test_check_OSError(tmp_path, monkeypatch):
    def mock_kill(pid, signal):
        raise IOError('Mock kill failure')

    monkeypatch.setattr(os, 'kill', mock_kill)

    path = os.path.join(
                         str(tmp_path),
                         'autorsyncbackup.pid',
                       )

    pf = Pidfile(path)

    pf.__enter__()

    pid = pf._check()

    assert pid is False
