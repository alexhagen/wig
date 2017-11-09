import os
import subprocess
from subprocess import PIPE
# import notify2 as n
from os.path import expanduser
from time import sleep
import paramiko
import os

class runner:
    """ ``runner`` is an object that ssh's to a remote (or local) system and
        starts a ``wig`` job, assume that it is set up completely and correctly.
        You can define your systems to run this on in '~/.wig/config.py' as the
        dict ``systems`` with structure

        .. code-block:: python

            systems = {"tianhe-2": {"ip": "255.255.255.255", "port": 22,
                                    "username": "nscwadmin", "password": "123",
                                    "procs": 10649600},
                       "titan": {"ip": "255.255.255.255", "port": 22,
                                 "username": "ornladmin", "password": "123",
                                 "procs": 560640},
                       "local": {"ip": "", "port": "",
                                 "username": "", "password": "",
                                 "procs": 4}}

        .. todo:: write article/todo on how to setup this

        :param str filename: base name of the file to run
        :param str command: command which will call the desired flavor of MCNP
        :param str remote: string identifying the remote system
        :param str sys: type of system this will run on, currently only
            supported for ``'linux'``, although ``'OSX'`` would probably be easy
        :param bool blocking: whether to wait for the MCNP run to finish before
            continuing.  Default ``False``.
        :param bool clean: whether to clean the old files with the same base
            filename from ``filename`` from directory ``~/mcnp/active/``.
            Useful if you've screwed something up and want to start fresh
    """
    def __init__(self, filename, command, remote="local", sys='linux',
                 blocking=False, clean=False, just_write=False, **kwargs):
        systems = {}
        execfile(expanduser('~') + '/.wig/config.py', systems)
        systems = systems['systems']
        if remote in systems.keys():
            system = systems[remote]
            ip = system['ip']
            port = system['port']
            procs = system['procs']
            username = system['username']
            password = system['password']
        # check in the completed directory, and if there is an out file with
        # exactly the same infile, then, don't run
        self.needs_to_run = True
        if command == 'polimi' or command == 'mcnpx' or command == 'mcuned' or command == 'mcuned_polimi':
            procs = 1
        # construct the command
        if blocking or command == 'mcuned':
            cmd = []
        else:
            cmd = ["nohup"]
        cmd.extend([command])
        cmd.extend(['inp=' + filename + '.inp'])
        cmd.extend(['out=' + filename + '.out'])
        cmd.extend(['run=' + filename + '_runtpe'])
        cmd.extend(['mctal=' + filename + '_tallies.out'])
        if command != 'mcuned' and command != 'mcuned_polimi' and command != 'polimi':
            cmd.extend(['meshtal=' + filename + '.meshtal'])
        if command == 'polimi' or command == 'mcnpx' or command == 'mcuned' or command == 'mcuned_polimi':
            cmd.extend(['DUMN1=' + filename + '_polimi.out'])
        else:
            cmd.extend(['tasks %d' % procs])
        if remote is not None and remote is not 'local':
            cmd.extend(['> %s' % (filename + '.nohup')])
        if not blocking:
            pass
        print cmd
        if self.needs_to_run and not just_write:
            if remote is not 'local' and remote in systems.keys():
                ssh = paramiko.SSHClient()
                print "started paramiko"
                ssh.set_missing_host_key_policy(paramiko.AutoAddPolicy())
                ssh.connect(hostname=ip, username=username,
                            password=password, port=port)
                print "connected"
                if clean:
                    _, out, err = ssh.exec_command("cd mcnp/active; rm -f *")
                    status = out.channel.recv_exit_status()
                sftp_client = ssh.open_sftp()
                sftp_client.chdir('~/mcnp/active')
                sftp_client.put(expanduser("~") + '/mcnp/active/' + filename + '.inp', filename + '.inp')
                sshcommand = ' '.join(cmd)
                sshcommand = "nohup bash -c 'source .profile; cd mcnp/active/; %s'" % sshcommand
                print sshcommand
                _, out, err = ssh.exec_command(sshcommand, timeout=0.0)
                sleep(10)
                sftp_client.close()
                ssh.close()
            else:
                self.p = subprocess.Popen(cmd, stdin=PIPE)
                if blocking:
                    self.p.communicate()
                    print "waiting for the process to finish"
        else:
            print ' '.join(cmd)
