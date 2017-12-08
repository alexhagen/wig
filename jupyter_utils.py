import threading
from IPython.display import display
import ipywidgets as widgets
import time

def get_ioloop():
    import IPython, zmq
    ipython = IPython.get_ipython()
    if ipython and hasattr(ipython, 'kernel'):
        return zmq.eventloop.ioloop.IOLoop.instance()
ioloop = get_ioloop()
thread_safe = True
def work(filename):
    # before file has been created phase: look for file, poll until exists

    # file exists phase and process is running, poll file while it runs
    for i in range(10):
        def update_progress(i=i):
            #print "calling from thread", threading.currentThread()
            progress.value = (i+1)/10.
        #print i
        time.sleep(0.5)
        if thread_safe:
            get_ioloop().add_callback(update_progress)
        else:
            update_progress()
    # file exists now, but process is done, go ahead and chain on an analysis
#print "we are in thread", threading.currentThread()
def tail_out_file(self, filename):
    thread = threading.Thread(target=work, args=(filename,))
    progress = widgets.Textarea(
        value='Hello World',
        placeholder='Type something',
        description='String:',
        disabled=False
    )
    display(progress)
    thread.start()
