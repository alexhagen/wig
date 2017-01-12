import execnet

print "connecting to server"
mercury = execnet.makegateway("ssh=128.46.92.228 -p 2120 -l inokuser")
print "connected to server"
channel = mercury.remote_exec("channel.send(channel.receive()+1)")
channel.send(1)
print channel.receive()
