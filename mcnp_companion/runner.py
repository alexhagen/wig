import os
import subprocess
from mcnpdaemon import mcnpdaemon
import notify2 as n

class runner:
    def __init__(self, filename, command, remote, sys, renderer=None):
        self.needs_to_run = False
        # initialize a notification system
        n.init('MCNP')
        # construct the command
        cmd = command + ' inp=' + filename + '.inp ' + \
            'out=' + filename + '.out ' + 'mctal=' + filename + '_tallies.out'
        # construct the notification
        notification = n.Notification(command, 'Will now run %s.' % cmd)
        notification.show()
        # check if there is an output file that has the EXACT same input and
        # has completed
        if renderer is not None:
            pass
            # renderer.run()
        # now run the actual mcnp
        if self.needs_to_run:
            subprocess.Popen(cmd, shell=True)
        # now start a daemon to watch the output file
        checker = mcnpdaemon('/tmp/mcnpchecker.pid').set_notification_daemon(notification).start()
        # notify when it updates
        # notify when it ends
