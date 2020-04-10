import socket
import subprocess
import time

from cryptography.utils import CryptographyDeprecationWarning
import paramiko

from .logger import logger


try:
    import warnings

    from cryptography.utils import CryptographyDeprecationWarning

    warnings.filterwarnings(
                             action='ignore',
                             category=CryptographyDeprecationWarning,
                           )
except ImportError:
    pass


class command():

    def checkRemoteHostViaSshProtocol(self, job,
                                      initial_wait=0,
                                      interval=0,
                                      retries=1):
        ssh = paramiko.SSHClient()
        ssh.set_missing_host_key_policy(paramiko.AutoAddPolicy())
        time.sleep(initial_wait)
        for x in range(retries):
            try:
                ssh.connect(job.hostname,
                            username=job.sshusername,
                            key_filename=job.sshprivatekey)
                logger().info(("Successfully connected to host"
                               " via ssh protocol (%s)") % job.hostname)
                return True
            except (paramiko.BadHostKeyException,
                    paramiko.AuthenticationException,
                    paramiko.SSHException,
                    socket.error,
                    IOError) as e:
                logger().error("Error while connecting to host (%s) - %s"
                               % (job.hostname, e))
                time.sleep(interval)
        return False

    def executeRemoteCommand(self, job, command):
        ssh = paramiko.SSHClient()
        ssh.set_missing_host_key_policy(paramiko.AutoAddPolicy())
        try:
            ssh.connect(job.hostname,
                        username=job.sshusername,
                        key_filename=job.sshprivatekey)
            logger().info(("Successfully connected to host"
                           " via ssh protocol (%s)") % job.hostname)

            stdin, stdout, stderr = ssh.exec_command("%s; echo $?" % command)
            lines = stdout.readlines()
            returncode = int(lines[-1].rstrip('\n'))
            stdout_value = lines[0:-1]
            stderr_value = stderr.readlines()
            logger().debug(("Remote execution of %s on %s gives"
                            " (rc=%d, stdout=%s, stderr=%s)")
                           % (command, job.hostname,
                              returncode, stdout_value, stderr_value))
            return (returncode,
                    "".join(stdout_value[:10000]),
                    "".join(stderr_value[:10000]))
        except (paramiko.BadHostKeyException,
                paramiko.AuthenticationException,
                paramiko.SSHException,
                socket.error,
                IOError) as e:
            logger().error("Error while connecting to host (%s) - %s"
                           % (job.hostname, e))
            return 1, '', str(e)

    def executeLocalCommand(self, job, command):
        p = subprocess.Popen(command,
                             shell=True,
                             stdout=subprocess.PIPE,
                             stderr=subprocess.PIPE)
        stdout_value, stderr_value = p.communicate()
        logger().debug(("Local execution of %s gives"
                        " (rc=%d, stdout=%s, stderr=%s)")
                       % (command, p.returncode, stdout_value, stderr_value))
        return p.returncode, stdout_value.decode(), stderr_value.decode()


class CommandException(Exception):
    pass
