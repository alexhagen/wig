import os

def setup_key(remote, port):
    os.system('ssh %s@%s -p %d mkdir -p .ssh' % (user, remote, port))
    cmd = "cat /home/ahagen/.ssh/id_rsa.pub | ssh %s@%s -p %d 'cat >> .ssh/authorized_keys'" % (user, remote, port)
    print cmd
    os.system(cmd)

# check if ~/.ssh/id_rsa.pub is there

# if not, run ssh-keygen

users = ['inokuser', 'inokuser', 'inokuser']
remotes = ['128.46.92.228', '128.46.92.228', '128.46.92.228']
ports = [2120, 2220, 2420]
# then, for remotes in list
for user, remote, port in zip(users, remotes, ports):
    # run the authorized keys
    setup_key(remote, port)
