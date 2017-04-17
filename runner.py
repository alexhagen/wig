import os
import subprocess
from subprocess import PIPE
# import notify2 as n
from os.path import expanduser
import paramiko
from time import sleep

class runner:
    def __init__(self, filename, command, remote="local", sys='linux',
                 renderer=None, blocking=False, clean=False):
        solar_system = {'mercury': 2120, 'venus': 2220, 'mars': 2420}
        if remote in solar_system.keys():
            ip = "128.46.92.228"
            port = solar_system[remote]
        # check in the completed directory, and if there is an out file with
        # exactly the same infile, then, don't run
        self.needs_to_run = True
        if command == 'polimi' or command == 'mcnpx':
            processors = {"local": 1, "mercury": 1, "venus": 1, "mars": 1}
        else:
            processors = {"local": 3, "mercury": 2, "venus": 2, "mars": 2}
        # Then, check the current processes to see if there are any instances
        # running on this machine

        # If there are, then we will run it on the solarsystem

        # initialize a notification system
        # n.init('MCNP')
        # construct the command
        if blocking:
            cmd = []
        else:
            cmd = ["nohup"]
            # cmd = []
        if remote:
            if command == 'mcnp6':
                command = 'mcnp6'

        cmd.extend([command])
        cmd.extend(['inp=' + filename + '.inp'])
        cmd.extend(['out=' + filename + '.out'])
        cmd.extend(['run=' + filename + '_runtpe'])
        cmd.extend(['mctal=' + filename + '_tallies.out'])
        cmd.extend(['meshtal=' + filename + '.meshtal'])
        if command == 'polimi' or command == 'mcnpx':
            cmd.extend(['DUMN1=' + filename + '_polimi.out'])
        else:
            cmd.extend(['tasks %d' % processors[remote]])
        if remote:
            cmd.extend(['> %s' % (filename + '.nohup')])
            #cmd.extend(['&'])
            #cmd.extend(['> /dev/null 2>&1 &'])
        if not blocking:
            pass
            # cmd.extend(['&'])
        print cmd
        # construct the notification
        # notification = n.Notification(command, 'Will now run %s.' % cmd)
        # notification.show()
        # check if there is an output file that has the EXACT same input and
        # has completed
        if renderer is not None:
            pass
            # renderer.run()cd
        # now run the actual mcnp
        if self.needs_to_run:
            if remote in solar_system:
                ssh = paramiko.SSHClient()
                print "started paramiko"
                ssh.set_missing_host_key_policy(paramiko.AutoAddPolicy())
                print "going to connect to the ip"
                ssh.connect(hostname=ip, username='inokuser',
                            password='goldrush1', port=port)
                print "connected"
                if clean:
                    _, out, err = ssh.exec_command("cd mcnp/active; rm *")
                    status = out.channel.recv_exit_status()
                sftp_client = ssh.open_sftp()
                sftp_client.chdir('/home/inokuser/mcnp/active')
                sftp_client.put(expanduser("~") + '/mcnp/active/' + filename + '.inp', filename + '.inp')
                #sftp_client.close()
                #chan = ssh.get_transport().open_session()
                #print "the ssh is %d connected." % ssh.get_transport().is_active()
                sshcommand = ' '.join(cmd)
                #print sshcommand
                #_, out, err = ssh.exec_command('cd mcnp/active')
                # block until remote command completes
                #status = out.channel.recv_exit_status()
                #print status
                #_, out, err = ssh.exec_command('ls -al')
                # block until remote command completes
                #status = out.channel.recv_exit_status()
                #print status
                #print out.readlines()
                sshcommand = "nohup bash -c 'source .profile; cd mcnp/active/; %s'" % sshcommand
                print sshcommand
                _, out, err = ssh.exec_command(sshcommand, timeout=0.0)
                sleep(10)
                #status = out.channel.recv_exit_status()
                #print status
                #print out.readlines()
                #print err.readlines()
                #print "exit status: %s" % chan.recv_exit_status()
                sftp_client.close()
                ssh.close()
            else:
                self.p = subprocess.Popen(cmd, stdin=PIPE)#, shell=True)
                if blocking:
                    self.p.communicate()
                    print "waiting for the process to finish"
        # now start a daemon to watch the output file
        # checker = mcnpdaemon('/tmp/mcnpchecker.pid').set_notification_daemon(notification).start()
        # notify when it updates
        # notify when it ends
