import io
import os

import paramiko

from lib.command import command
from models.job import job


def test_checkRemoteHostViaSshProtocol(monkeypatch):
    def mock_connect(self, hostname, username=None, key_filename=None):
        return True

    monkeypatch.setattr(paramiko.SSHClient, 'connect', mock_connect)

    path = os.path.join(
                         os.path.dirname(__file__),
                         'etc/localhost.job',
                       )

    j = job(path)

    cmd = command()

    ret = cmd.checkRemoteHostViaSshProtocol(j)

    assert ret is True


def test_checkRemoteHostViaSshProtocol_exception(monkeypatch, caplog):
    def mock_connect(self, hostname, username=None, key_filename=None):
        raise IOError('Mock connection failed')

    monkeypatch.setattr(paramiko.SSHClient, 'connect', mock_connect)

    path = os.path.join(
                         os.path.dirname(__file__),
                         'etc/localhost.job',
                       )

    j = job(path)

    cmd = command()

    ret = cmd.checkRemoteHostViaSshProtocol(j)

    assert 'Error while connecting to host' in caplog.text

    assert ret is False


def test_executeRemoteCommand(monkeypatch):
    def mock_connect(self, hostname, username=None, key_filename=None):
        return True

    def mock_exec_command(self, command):
        stdin = io.StringIO('')
        stdout = io.StringIO('Mock STDOUT\n0')
        stderr = io.StringIO('')

        return stdin, stdout, stderr

    monkeypatch.setattr(paramiko.SSHClient, 'connect', mock_connect)
    monkeypatch.setattr(paramiko.SSHClient, 'exec_command', mock_exec_command)

    path = os.path.join(
                         os.path.dirname(__file__),
                         'etc/localhost.job',
                       )

    j = job(path)

    cmd = command()

    (status, stdout, stderr) = cmd.executeRemoteCommand(j, 'uptime')

    assert status == 0
    assert 'Mock STDOUT' in stdout


def test_executeRemoteCommand_exception(monkeypatch, caplog):
    def mock_connect(self, hostname, username=None, key_filename=None):
        raise IOError('Mock connection failed')

    monkeypatch.setattr(paramiko.SSHClient, 'connect', mock_connect)

    path = os.path.join(
                         os.path.dirname(__file__),
                         'etc/localhost.job',
                       )

    j = job(path)

    cmd = command()

    (status, stdout, stderr) = cmd.executeRemoteCommand(j, 'uptime')

    assert 'Error while connecting to host' in caplog.text

    assert status == 1
    assert stdout == ''
    assert 'Mock connection failed' in stderr


def test_executeLocalCommand():
    path = os.path.join(
                         os.path.dirname(__file__),
                         'etc/localhost.job',
                       )

    j = job(path)

    cmd = command()

    (status, stdout, stderr) = cmd.executeLocalCommand(j, 'uptime')

    assert status == 0
    assert 'load average' in stdout
    assert stderr == ''
