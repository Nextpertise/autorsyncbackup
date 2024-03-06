import os
import pprint
import re

from models.config import config
from models.job import job


def test_job():
    path = os.path.join(
               os.path.dirname(__file__),
               'etc/localhost.job',
           )

    j = job(path)

    assert j.enabled is True
    assert j.hostname == 'localhost'
    assert j.ssh is False
    assert j.ssh_sudo is False
    assert j.sshusername == 'autorsyncbackup'
    assert j.sshprivatekey == '/home/autorsyncbackup/.ssh/id_rsa'
    assert j.sshdisabledalgs == {'pubkeys': ['rsa-sha2-512', 'rsa-sha2-256']}
    assert j.rsyncusername == 'autorsyncbackup'
    assert j.rsyncpassword == 'fee-fi-fo-fum'
    assert j.port == 10873
    assert j.rsyncshare == 'backup'
    assert j.backupdir == '/tmp'
    assert j.speedlimitkb == 10000
    assert j.dailyrotation == 3
    assert j.weeklyrotation == 2
    assert j.monthlyrotation == 1
    assert j.weeklybackup == 3
    assert j.monthlybackup == 2
    assert j.include == ['/etc']
    assert j.exclude == ['*.bak', '.cache/*']

    hooks = [
              {
                'script':          'uptime',
                'local':           True,
                'runtime':         'before',
                'continueonerror': True,
              },
              {
                'script':          'cat /etc/motd',
                'local':           False,
                'runtime':         'after',
                'continueonerror': True,
              },
            ]

    assert pprint.pformat(j.hooks) == pprint.pformat(hooks)


def test_default_config(test_config):
    path = os.path.join(
               os.path.dirname(__file__),
               'etc/default-config.job',
           )

    j = job(path)

    assert j.enabled is True
    assert j.hostname == 'localhost'
    assert j.ssh is False
    assert j.ssh_sudo is False
    assert j.sshusername is None
    assert j.sshprivatekey is None
    assert j.sshdisabledalgs == {}
    assert j.rsyncusername == 'autorsyncbackup'
    assert j.rsyncpassword == 'fee-fi-fo-fum'
    assert j.rsyncshare == 'backup'
    assert j.port == 873
    assert j.backupdir == config().backupdir
    assert j.speedlimitkb == config().speedlimitkb
    assert j.dailyrotation == config().dailyrotation
    assert j.weeklyrotation == config().weeklyrotation
    assert j.monthlyrotation == config().monthlyrotation
    assert j.weeklybackup == config().weeklybackup
    assert j.monthlybackup == config().monthlybackup
    assert j.exclude == config().exclude


def test_missing():
    path = '/non-existent/foo.job'

    j = job(path)

    assert j.enabled is False


def test_empty():
    path = os.path.join(
               os.path.dirname(__file__),
               'etc/empty.job',
           )

    j = job(path)

    assert j.enabled is False


def test_hostname_only():
    path = os.path.join(
               os.path.dirname(__file__),
               'etc/hostname-only.job',
           )

    j = job(path)

    assert j.enabled is False
    assert j.hostname == 'localhost'
    assert j.ssh is False
    assert j.ssh_sudo is False
    assert j.sshusername is None


def test_ssh_no_username():
    path = os.path.join(
               os.path.dirname(__file__),
               'etc/ssh-no-username.job',
           )

    j = job(path)

    assert j.enabled is False
    assert j.hostname == 'localhost'
    assert j.ssh is True
    assert j.ssh_sudo is True
    assert j.sshusername is None


def test_ssh_no_privatekey():
    path = os.path.join(
               os.path.dirname(__file__),
               'etc/ssh-no-privatekey.job',
           )

    j = job(path)

    assert j.enabled is False
    assert j.hostname == 'localhost'
    assert j.ssh is True
    assert j.ssh_sudo is True
    assert j.sshusername == 'autorsyncbackup'
    assert j.sshprivatekey is None


def test_ssh_no_disabledalgs():
    path = os.path.join(
               os.path.dirname(__file__),
               'etc/ssh-no-disabledalgs.job',
           )

    j = job(path)

    assert j.enabled is False
    assert j.hostname == 'localhost'
    assert j.ssh is True
    assert j.ssh_sudo is True
    assert j.sshusername == 'autorsyncbackup'
    assert j.sshprivatekey == '/home/autorsyncbackup/.ssh/id_rsa'
    assert j.sshdisabledalgs == {}


def test_ssh_no_port():
    path = os.path.join(
               os.path.dirname(__file__),
               'etc/ssh-no-port.job',
           )

    j = job(path)

    assert j.enabled is False
    assert j.hostname == 'localhost'
    assert j.ssh is True
    assert j.ssh_sudo is True
    assert j.sshusername == 'autorsyncbackup'
    assert j.sshprivatekey == '/home/autorsyncbackup/.ssh/id_rsa'
    assert j.port == 22


def test_ssh_no_rsyncshare():
    path = os.path.join(
               os.path.dirname(__file__),
               'etc/ssh-no-rsyncshare.job',
           )

    j = job(path)

    assert j.enabled is False
    assert j.hostname == 'localhost'
    assert j.ssh is True
    assert j.ssh_sudo is True
    assert j.sshusername == 'autorsyncbackup'
    assert j.sshprivatekey == '/home/autorsyncbackup/.ssh/id_rsa'
    assert j.port == 22
    assert j.rsyncshare == ''


def test_rsync_no_username():
    path = os.path.join(
               os.path.dirname(__file__),
               'etc/rsync-no-username.job',
           )

    j = job(path)

    assert j.enabled is False
    assert j.hostname == 'localhost'
    assert j.ssh is False
    assert j.rsyncusername is None


def test_rsync_no_password():
    path = os.path.join(
               os.path.dirname(__file__),
               'etc/rsync-no-password.job',
           )

    j = job(path)

    assert j.enabled is False
    assert j.hostname == 'localhost'
    assert j.ssh is False
    assert j.rsyncusername == 'autorsyncbackup'
    assert j.rsyncpassword is None


def test_rsync_no_port():
    path = os.path.join(
               os.path.dirname(__file__),
               'etc/rsync-no-port.job',
           )

    j = job(path)

    assert j.enabled is False
    assert j.hostname == 'localhost'
    assert j.ssh is False
    assert j.rsyncusername == 'autorsyncbackup'
    assert j.rsyncpassword == 'fee-fi-fo-fum'
    assert j.port == 873


def test_rsync_no_rsyncshare():
    path = os.path.join(
               os.path.dirname(__file__),
               'etc/rsync-no-rsyncshare.job',
           )

    j = job(path)

    assert j.enabled is False
    assert j.hostname == 'localhost'
    assert j.ssh is False
    assert j.rsyncusername == 'autorsyncbackup'
    assert j.rsyncpassword == 'fee-fi-fo-fum'
    assert j.port == 873
    assert j.rsyncshare is None


def test_rsync_no_include():
    path = os.path.join(
               os.path.dirname(__file__),
               'etc/rsync-no-include.job',
           )

    j = job(path)

    assert j.enabled is False
    assert j.hostname == 'localhost'
    assert j.ssh is False
    assert j.rsyncusername == 'autorsyncbackup'
    assert j.rsyncpassword == 'fee-fi-fo-fum'
    assert j.port == 873
    assert j.rsyncshare == 'backup'
    assert j.include == []


def test_rsync_fileset():
    path = os.path.join(
               os.path.dirname(__file__),
               'etc/rsync-fileset.job',
           )

    j = job(path)

    assert j.enabled is True
    assert j.hostname == 'localhost'
    assert j.ssh is False
    assert j.rsyncusername == 'autorsyncbackup'
    assert j.rsyncpassword == 'fee-fi-fo-fum'
    assert j.port == 873
    assert j.rsyncshare == 'backup'
    assert j.include == ['/etc']


def test_hooks_no_username():
    path = os.path.join(
               os.path.dirname(__file__),
               'etc/hooks-no-username.job',
           )

    j = job(path)

    assert j.enabled is True
    assert j.hostname == 'localhost'
    assert j.ssh is False
    assert j.rsyncusername == 'autorsyncbackup'
    assert j.rsyncpassword == 'fee-fi-fo-fum'
    assert j.port == 873
    assert j.rsyncshare == 'backup'
    assert j.sshusername is None
    assert j.sshprivatekey == '/home/autorsyncbackup/.ssh/id_rsa'

    hooks = [
              {
                'script':          'uptime',
                'local':           False,
                'runtime':         'after',
                'continueonerror': True,
              },
            ]

    assert pprint.pformat(j.hooks) == pprint.pformat(hooks)

    assert j.beforeLocalHooks == []
    assert j.afterLocalHooks == []
    assert j.beforeRemoteHooks == []
    assert j.afterRemoteHooks == []


def test_hooks_no_privatekey():
    path = os.path.join(
               os.path.dirname(__file__),
               'etc/hooks-no-privatekey.job',
           )

    j = job(path)

    assert j.enabled is True
    assert j.hostname == 'localhost'
    assert j.ssh is False
    assert j.rsyncusername == 'autorsyncbackup'
    assert j.rsyncpassword == 'fee-fi-fo-fum'
    assert j.port == 873
    assert j.rsyncshare == 'backup'
    assert j.sshusername == 'autorsyncbackup'
    assert j.sshprivatekey is None

    hooks = [
              {
                'script':          'uptime',
                'local':           False,
                'runtime':         'after',
                'continueonerror': True,
              },
            ]

    assert pprint.pformat(j.hooks) == pprint.pformat(hooks)

    assert j.beforeLocalHooks == []
    assert j.afterLocalHooks == []
    assert j.beforeRemoteHooks == []
    assert j.afterRemoteHooks == []


def test_hooks_no_properties():
    path = os.path.join(
               os.path.dirname(__file__),
               'etc/hooks-no-properties.job',
           )

    j = job(path)

    assert j.enabled is True
    assert j.hostname == 'localhost'
    assert j.ssh is False
    assert j.rsyncusername == 'autorsyncbackup'
    assert j.rsyncpassword == 'fee-fi-fo-fum'
    assert j.port == 873
    assert j.rsyncshare == 'backup'
    assert j.sshusername == 'autorsyncbackup'
    assert j.sshprivatekey == '/home/autorsyncbackup/.ssh/id_rsa'
    assert j.hooks == [None]
    assert j.beforeLocalHooks == []
    assert j.afterLocalHooks == []
    assert j.beforeRemoteHooks == []
    assert j.afterRemoteHooks == []


def test_hooks_invalid_properties():
    path = os.path.join(
               os.path.dirname(__file__),
               'etc/hooks-invalid-properties.job',
           )

    j = job(path)

    assert j.enabled is True
    assert j.hostname == 'localhost'
    assert j.ssh is False
    assert j.rsyncusername == 'autorsyncbackup'
    assert j.rsyncpassword == 'fee-fi-fo-fum'
    assert j.port == 873
    assert j.rsyncshare == 'backup'
    assert j.sshusername == 'autorsyncbackup'
    assert j.sshprivatekey == '/home/autorsyncbackup/.ssh/id_rsa'

    hooks = [
              {
                'local':           'yes',
                'runtime':         'any',
                'continueonerror': 'perhaps',
              },
            ]

    assert pprint.pformat(j.hooks) == pprint.pformat(hooks)

    assert j.beforeLocalHooks == []
    assert j.afterLocalHooks == []
    assert j.beforeRemoteHooks == []
    assert j.afterRemoteHooks == []


def test_hooks_invalid_local():
    path = os.path.join(
               os.path.dirname(__file__),
               'etc/hooks-invalid-local.job',
           )

    j = job(path)

    assert j.enabled is True
    assert j.hostname == 'localhost'
    assert j.ssh is False
    assert j.rsyncusername == 'autorsyncbackup'
    assert j.rsyncpassword == 'fee-fi-fo-fum'
    assert j.port == 873
    assert j.rsyncshare == 'backup'
    assert j.sshusername == 'autorsyncbackup'
    assert j.sshprivatekey == '/home/autorsyncbackup/.ssh/id_rsa'

    hooks = [
              {
                'script':          'uptime',
                'local':           'yes',
                'runtime':         'after',
                'continueonerror': True,
              },
            ]

    assert pprint.pformat(j.hooks) == pprint.pformat(hooks)

    assert j.beforeLocalHooks == []
    assert j.afterLocalHooks == []
    assert j.beforeRemoteHooks == []
    assert j.afterRemoteHooks == []


def test_hooks_invalid_runtime():
    path = os.path.join(
               os.path.dirname(__file__),
               'etc/hooks-invalid-runtime.job',
           )

    j = job(path)

    assert j.enabled is True
    assert j.hostname == 'localhost'
    assert j.ssh is False
    assert j.rsyncusername == 'autorsyncbackup'
    assert j.rsyncpassword == 'fee-fi-fo-fum'
    assert j.port == 873
    assert j.rsyncshare == 'backup'
    assert j.sshusername == 'autorsyncbackup'
    assert j.sshprivatekey == '/home/autorsyncbackup/.ssh/id_rsa'

    hooks = [
              {
                'script':          'uptime',
                'local':           True,
                'runtime':         'whenever',
                'continueonerror': True,
              },
            ]

    assert pprint.pformat(j.hooks) == pprint.pformat(hooks)

    assert j.beforeLocalHooks == []
    assert j.afterLocalHooks == []
    assert j.beforeRemoteHooks == []
    assert j.afterRemoteHooks == []


def test_hooks_invalid_continueonerror():
    path = os.path.join(
               os.path.dirname(__file__),
               'etc/hooks-invalid-continueonerror.job',
           )

    j = job(path)

    assert j.enabled is True
    assert j.hostname == 'localhost'
    assert j.ssh is False
    assert j.rsyncusername == 'autorsyncbackup'
    assert j.rsyncpassword == 'fee-fi-fo-fum'
    assert j.port == 873
    assert j.rsyncshare == 'backup'
    assert j.sshusername == 'autorsyncbackup'
    assert j.sshprivatekey == '/home/autorsyncbackup/.ssh/id_rsa'

    hooks = [
              {
                'script':          'uptime',
                'local':           True,
                'runtime':         'after',
                'continueonerror': 'perhaps',
              },
            ]

    assert pprint.pformat(j.hooks) == pprint.pformat(hooks)

    assert j.beforeLocalHooks == []
    assert j.afterLocalHooks == []
    assert j.beforeRemoteHooks == []
    assert j.afterRemoteHooks == []


def test_hooks_no_script():
    path = os.path.join(
               os.path.dirname(__file__),
               'etc/hooks-no-script.job',
           )

    j = job(path)

    assert j.enabled is True
    assert j.hostname == 'localhost'
    assert j.ssh is False
    assert j.rsyncusername == 'autorsyncbackup'
    assert j.rsyncpassword == 'fee-fi-fo-fum'
    assert j.port == 873
    assert j.rsyncshare == 'backup'
    assert j.sshusername == 'autorsyncbackup'
    assert j.sshprivatekey == '/home/autorsyncbackup/.ssh/id_rsa'

    hooks = [
              {
                'local':           True,
                'runtime':         'after',
                'continueonerror': True,
              },
            ]

    assert pprint.pformat(j.hooks) == pprint.pformat(hooks)

    assert j.beforeLocalHooks == []
    assert j.afterLocalHooks == []
    assert j.beforeRemoteHooks == []
    assert j.afterRemoteHooks == []


def test_hooks_no_local():
    path = os.path.join(
               os.path.dirname(__file__),
               'etc/hooks-no-local.job',
           )

    j = job(path)

    assert j.enabled is True
    assert j.hostname == 'localhost'
    assert j.ssh is False
    assert j.rsyncusername == 'autorsyncbackup'
    assert j.rsyncpassword == 'fee-fi-fo-fum'
    assert j.port == 873
    assert j.rsyncshare == 'backup'
    assert j.sshusername == 'autorsyncbackup'
    assert j.sshprivatekey == '/home/autorsyncbackup/.ssh/id_rsa'

    hooks = [
              {
                'script':          'uptime',
                'local':           False,
                'runtime':         'after',
                'continueonerror': True,
              },
            ]

    assert pprint.pformat(j.hooks) == pprint.pformat(hooks)

    assert j.beforeLocalHooks == []
    assert j.afterLocalHooks == []
    assert j.beforeRemoteHooks == []

    assert pprint.pformat(j.afterRemoteHooks) == pprint.pformat(hooks)


def test_hooks_no_runtime():
    path = os.path.join(
               os.path.dirname(__file__),
               'etc/hooks-no-runtime.job',
           )

    j = job(path)

    assert j.enabled is True
    assert j.hostname == 'localhost'
    assert j.ssh is False
    assert j.rsyncusername == 'autorsyncbackup'
    assert j.rsyncpassword == 'fee-fi-fo-fum'
    assert j.port == 873
    assert j.rsyncshare == 'backup'
    assert j.sshusername == 'autorsyncbackup'
    assert j.sshprivatekey == '/home/autorsyncbackup/.ssh/id_rsa'

    hooks = [
              {
                'script':          'uptime',
                'local':           True,
                'runtime':         'before',
                'continueonerror': True,
              },
            ]

    assert pprint.pformat(j.hooks) == pprint.pformat(hooks)

    assert pprint.pformat(j.beforeLocalHooks) == pprint.pformat(hooks)

    assert j.afterLocalHooks == []
    assert j.beforeRemoteHooks == []
    assert j.afterRemoteHooks == []


def test_hooks_no_continueonerror():
    path = os.path.join(
               os.path.dirname(__file__),
               'etc/hooks-no-continueonerror.job',
           )

    j = job(path)

    assert j.enabled is True
    assert j.hostname == 'localhost'
    assert j.ssh is False
    assert j.rsyncusername == 'autorsyncbackup'
    assert j.rsyncpassword == 'fee-fi-fo-fum'
    assert j.port == 873
    assert j.rsyncshare == 'backup'
    assert j.sshusername == 'autorsyncbackup'
    assert j.sshprivatekey == '/home/autorsyncbackup/.ssh/id_rsa'

    hooks = [
              {
                'script':          'uptime',
                'local':           True,
                'runtime':         'after',
                'continueonerror': False,
              },
            ]

    assert pprint.pformat(j.hooks) == pprint.pformat(hooks)

    assert j.beforeLocalHooks == []

    assert pprint.pformat(j.afterLocalHooks) == pprint.pformat(hooks)

    assert j.beforeRemoteHooks == []
    assert j.afterRemoteHooks == []


def test_hooks_local_before():
    path = os.path.join(
               os.path.dirname(__file__),
               'etc/hooks-local-before.job',
           )

    j = job(path)

    assert j.enabled is True
    assert j.hostname == 'localhost'
    assert j.ssh is False
    assert j.rsyncusername == 'autorsyncbackup'
    assert j.rsyncpassword == 'fee-fi-fo-fum'
    assert j.port == 873
    assert j.rsyncshare == 'backup'
    assert j.sshusername == 'autorsyncbackup'
    assert j.sshprivatekey == '/home/autorsyncbackup/.ssh/id_rsa'

    hooks = [
              {
                'script':          'uptime',
                'local':           True,
                'runtime':         'before',
                'continueonerror': True,
              },
            ]

    assert pprint.pformat(j.hooks) == pprint.pformat(hooks)

    assert pprint.pformat(j.beforeLocalHooks) == pprint.pformat(hooks)

    assert j.afterLocalHooks == []
    assert j.beforeRemoteHooks == []
    assert j.afterRemoteHooks == []


def test_hooks_local_after():
    path = os.path.join(
               os.path.dirname(__file__),
               'etc/hooks-local-after.job',
           )

    j = job(path)

    assert j.enabled is True
    assert j.hostname == 'localhost'
    assert j.ssh is False
    assert j.rsyncusername == 'autorsyncbackup'
    assert j.rsyncpassword == 'fee-fi-fo-fum'
    assert j.port == 873
    assert j.rsyncshare == 'backup'
    assert j.sshusername == 'autorsyncbackup'
    assert j.sshprivatekey == '/home/autorsyncbackup/.ssh/id_rsa'

    hooks = [
              {
                'script':          'uptime',
                'local':           True,
                'runtime':         'after',
                'continueonerror': True,
              },
            ]

    assert pprint.pformat(j.hooks) == pprint.pformat(hooks)

    assert j.beforeLocalHooks == []

    assert pprint.pformat(j.afterLocalHooks) == pprint.pformat(hooks)

    assert j.beforeRemoteHooks == []
    assert j.afterRemoteHooks == []


def test_hooks_remote_before():
    path = os.path.join(
               os.path.dirname(__file__),
               'etc/hooks-remote-before.job',
           )

    j = job(path)

    assert j.enabled is True
    assert j.hostname == 'localhost'
    assert j.ssh is False
    assert j.rsyncusername == 'autorsyncbackup'
    assert j.rsyncpassword == 'fee-fi-fo-fum'
    assert j.port == 873
    assert j.rsyncshare == 'backup'
    assert j.sshusername == 'autorsyncbackup'
    assert j.sshprivatekey == '/home/autorsyncbackup/.ssh/id_rsa'

    hooks = [
              {
                'script':          'uptime',
                'local':           False,
                'runtime':         'before',
                'continueonerror': True,
              },
            ]

    assert pprint.pformat(j.hooks) == pprint.pformat(hooks)

    assert j.beforeLocalHooks == []
    assert j.afterLocalHooks == []

    assert pprint.pformat(j.beforeRemoteHooks) == pprint.pformat(hooks)

    assert j.afterRemoteHooks == []


def test_hooks_remote_after():
    path = os.path.join(
               os.path.dirname(__file__),
               'etc/hooks-remote-after.job',
           )

    j = job(path)

    assert j.enabled is True
    assert j.hostname == 'localhost'
    assert j.ssh is False
    assert j.rsyncusername == 'autorsyncbackup'
    assert j.rsyncpassword == 'fee-fi-fo-fum'
    assert j.port == 873
    assert j.rsyncshare == 'backup'
    assert j.sshusername == 'autorsyncbackup'
    assert j.sshprivatekey == '/home/autorsyncbackup/.ssh/id_rsa'

    hooks = [
              {
                'script':          'uptime',
                'local':           False,
                'runtime':         'after',
                'continueonerror': True,
              },
            ]

    assert pprint.pformat(j.hooks) == pprint.pformat(hooks)

    assert j.beforeLocalHooks == []
    assert j.afterLocalHooks == []
    assert j.beforeRemoteHooks == []

    assert pprint.pformat(j.afterRemoteHooks) == pprint.pformat(hooks)


def test_showjob(capsys):
    path = os.path.join(
               os.path.dirname(__file__),
               'etc/localhost.job',
           )

    j = job(path)

    j.showjob()

    captured = capsys.readouterr()

    output_regex = (
                     r'Show job:\n'
                     r'enabled: True\n'
                     r'filepath: ' + path + r'\n'
                     r'hostname: localhost\n'
                     r'rsyncusername: autorsyncbackup\n'
                     r'rsyncpassword: fee-fi-fo-fum\n'
                     r'rsyncshare: backup\n'
                     r'sshusername: autorsyncbackup\n'
                     r'sshprivatekey: /home/autorsyncbackup/.ssh/id_rsa\n'
                     r'backupdir: /tmp\n'
                     r'speedlimitkb: 10000\n'
                     r'dailyrotation: 3\n'
                     r'weeklyrotation: 2\n'
                     r'monthlyrotation: 1\n'
                     r'weeklybackup: 3\n'
                     r'monthlybackup: 2\n'
                     r"include: \['/etc'\]\n"
                     r"exclude: \['\*\.bak', '\.cache/\*'\]\n"
                     r'backupstatus: {}\n'
                     r'hooks: \[{.*?}, {.*?}\]\n'
                     r'beforeLocalHooks: \[.*?\]\n'
                     r'afterLocalHooks: \[\]\n'
                     r'beforeRemoteHooks: \[\]\n'
                     r'beforeRemoteHooks: \[\]\n'
                     r'afterRemoteHooks: \[{.*?}\]\n'
                     r'$'
                   )

    assert re.match(output_regex, captured.out)
