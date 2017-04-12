import time
import re
import os
import subprocess
import multiprocessing
import sys
import string
import notify2 as n
import paramiko
from bottle import Bottle, run, response, static_file, template

HTML = """\
<!DOCTYPE html>
<html lang="en">
<head>
    <meta charset="utf-8">
    <meta name="viewport" content="width=device-width, initial-scale=1">
  <link rel="stylesheet" href="https://maxcdn.bootstrapcdn.com/bootstrap/3.3.7/css/bootstrap.min.css">

    <!-- jQuery library -->
    <script src="https://ajax.googleapis.com/ajax/libs/jquery/3.2.0/jquery.min.js"></script>

    <!-- Latest compiled JavaScript -->
    <script src="https://maxcdn.bootstrapcdn.com/bootstrap/3.3.7/js/bootstrap.min.js"></script>

    <script type="text/x-mathjax-config">
    MathJax.Hub.Config({
      tex2jax: {inlineMath: [['$','$'], ['\\(','\\)']]}
    });
    </script>

    <script type="text/javascript" async
      src="https://cdnjs.cloudflare.com/ajax/libs/mathjax/2.7.0/MathJax.js?config=TeX-MML-AM_CHTML">
    </script>
    <style>
        .progress {
            text-align:center;
        }
        .progress-value {
            position:absolute;
            right:0;
            left:0;
        }
    </style>

    <script>
    $(document).ready(function() {
        setInterval(function(){
            $.ajax({
                type: 'GET',
                url: '/all_prog',
                data: $(this).serialize(),
                success: function(response) {
                    $('#ajaxP').html(response);
                }
            });
            MathJax.Hub.Typeset();
        }, 10*60*1000);
    });
    </script>
</head>
<body>
    <div class="container">
      <h1>MCNP Processes</h1>
      <div id="ajaxP">{{!content}}</div>
    </div>
</body>
"""

fmt = '%A \n %m/%d/%y %I:%M:%S %p'

class progress:
    def __init__(self, filename, cpu_use, nps, start_time, time_slope,
                 end_time, proc):
        self.filename = filename
        self.cpu_use = cpu_use
        self.start_time = start_time
        self.time_slope = time_slope
        self.end_time = end_time
        self.nps = nps
        self.proc = proc

def find_between( s, first, last ):
    try:
        start = s.index( first ) + len( first )
        end = s.index( last, start )
        return s[start:end]
    except ValueError:
        return ""

filenames = []

def read_ps_aux(outp, procs, filenames, mcnpservers, mcnpserver, cpu_uses):
    for line in outp.split('\n'):
        if '/bin/sh' not in line and 'grep' not in line and '.inp' in line:
            arr = re.findall(r"[-+]?\d*\.\d+|\d+", line)
            cpu_use = float(arr[1])
            pid = int(arr[0])
            file = find_between(line, 'out=', '.out')
            print file
            filenames.extend([file])
            if 'tasks' in line:
                procs.extend([float(arr[-1])])
            else:
                procs.extend([1])
            cpu_use = cpu_use / float(arr[2])
            cpu_uses.extend([cpu_use])
            mcnpservers.extend([mcnpserver])

class server:
    def __init__(self, type='local', name='sputnik', ip=None, port=None,
                 home_folder='/home/ahagen'):
        self.type = type
        self.name = name
        self.ip = ip
        self.port = port
        self.home_folder = home_folder

def check():
    start_times = []
    time_slopes = []
    end_times = []
    cpu_uses = []
    npss = []
    procs = []
    filenames = []
    mcnpservers = []
    '''
    extra_servers = [server(type='remote', name='mercury',
                                        ip='128.46.92.228', port=2120,
                                        home_folder='/home/inokuser'),
                       server(type='remote', name='venus',
                              ip='128.46.92.228', port=2220,
                              home_folder='/home/inokuser')]]'''
    for mcnpserver in [server()]:
        if mcnpserver.type == 'local':
            ps_aux_out = subprocess.check_output(["ps aux | grep 'mcnp\|polimi'"],
                                                 shell=True)
        else:
            ssh = paramiko.SSHClient()
            print "started paramiko"
            ssh.set_missing_host_key_policy(paramiko.AutoAddPolicy())
            print "going to connect to the ip"
            ssh.connect(hostname=mcnpserver.ip, username='inokuser',
                        password='goldrush1', port=mcnpserver.port)
            print "connected"
            sftp_client = ssh.open_sftp()
            stdin, stdout, stderr = ssh.exec_command('ps aux | grep mcnp')
            ps_aux_out = stdout.read()
            ssh.close()

        read_ps_aux(ps_aux_out, procs, filenames, mcnpservers, mcnpserver, cpu_uses)

    print filenames
    print mcnpservers

    for filename, i, mcnpserver in zip(filenames, range(len(filenames)),
                                       mcnpservers):
        dump = 1
        ctm_2 = None
        nps_2 = None
        filestring = ''
        print mcnpserver.name
        if mcnpserver.type == 'local':
            filename = '/home/ahagen/mcnp/active/' + filename
            filelines = reversed(open(filename + '.out', 'r').readlines())
        else:
            serverfilename = mcnpserver.home_folder + '/mcnp/active/' + \
                filename.replace('/home/ahagen/mcnp/active/', '') + '.out'
            print serverfilename
            ssh = paramiko.SSHClient()
            print "started paramiko"
            ssh.set_missing_host_key_policy(paramiko.AutoAddPolicy())
            print "going to connect to the ip"
            ssh.connect(hostname=mcnpserver.ip, username='inokuser',
                        password='goldrush1', port=mcnpserver.port)
            print "connected"
            sftp_client = ssh.open_sftp()
            filelines = reversed(sftp_client.open(serverfilename, 'r')\
                .readlines())
        for line in filelines:
            if 'particle' in line:
                break
            filestring = line.replace('\n', '') + filestring

        lines = filestring.split('dump')
        lines = lines[1:]

        nps_from_file = []
        ctm_from_file = []

        for line in lines:
            nps = float(find_between(line, 'nps =', 'coll'))
            nps_from_file.extend([nps])
            ctm = float(find_between(line, 'ctm =', 'nrn')) / (procs[i])
            ctm_from_file.extend([ctm])

        if len(nps_from_file) >= 1:
            ctm_1 = ctm_from_file[-1]
            nps_1 = nps_from_file[-1]
            if len(nps_from_file) > 1:
                ctm_2 = ctm_from_file[-2]
                nps_2 = nps_from_file[-2]

        cpu_use = cpu_uses[i]

        cpus = float(multiprocessing.cpu_count())
        if mcnpserver.type == 'remote':
            now = sftp_client.stat(serverfilename).st_mtime
        else:
            now = os.path.getmtime(filename + '.out')
        start_time = now - (ctm_1 * 60.)
        if mcnpserver.type == 'remote':
            start_time = now - (ctm_1 * 60.) - (15. * 60.)
        else:
            now = os.path.getctime(filename + '.out')
        if nps_2 is not None:
            time_slope = procs[i] * (nps_1 - nps_2) / (60. * (ctm_1 - ctm_2))
            end_time = now + (1.E9 - nps_1) / time_slope
        else:
            time_slope = 0.0
            end_time = 0.0
        npss.extend([nps_1])
        start_times.extend([start_time])
        time_slopes.extend([time_slope])
        end_times.extend([end_time])
        cpu_uses.extend([cpu_use])
        if mcnpserver.type == 'remote':
            ssh.close()

    return filenames, cpus, cpu_uses, npss, start_times, time_slopes, \
        end_times, procs
'''
class cpu_progress(QProgressBar):
    def __init__(self):
        QProgressBar.__init__(self)
        self.setMaximum(4000 * 100)
        self.setMinimum(0)
        self.setOrientation(2)
        self.setTextVisible(True)
        self.setVisible(True)
        self.setAlignment(Qt.AlignCenter)

    def setProgress(self, prg):
        # self.setFormat("%.2f %%" % prg)
        self.setValue(int(4000 * prg))
        return self

class progress_view_label(QLabel):
    def __init__(self, string):
        QLabel.__init__(self)
        self.setText(string)
        self.setWordWrap(True)
        self.setFixedWidth(125)
        self.setAlignment(Qt.AlignCenter)

class progress_view(QWidget):
    def __init__(self, progress, parent=None):
        QWidget.__init__(self)
        self.filename = progress_view_label(progress.filename.replace("/home/ahagen/mcnp/active/", ""))
        self.v = QVBoxLayout(self)
        self.prog_bar = cpu_progress().setProgress(100. * progress.nps / 1.E9)
        self.prog_text = progress_view_label("%.2f %%" % (100. * progress.nps / 1.E9))
        self.cpu_use = progress_view_label("CPU Use: %.2f%% x %d" % (progress.cpu_use / progress.proc, progress.proc))
        self.start_time = progress_view_label("Start Time: %s" % time.strftime(fmt,
                                         time.localtime(progress.start_time)))
        self.end_time = progress_view_label("Estimated End Time: %s" %
                                       time.strftime(fmt,
                                       time.localtime(progress.end_time)))
        self.time_slope = progress_view_label("Rate:\n %.2e n/hour" %
                                         (progress.time_slope * 3600.))
        self.v.addWidget(self.filename)
        self.v.addWidget(self.prog_bar)
        self.v.addWidget(self.prog_text)
        self.v.addWidget(self.cpu_use)
        self.v.addWidget(self.start_time)
        self.v.addWidget(self.time_slope)
        self.v.addWidget(self.end_time)
        self.v.setAlignment(Qt.AlignCenter)

    def refresh(self, progress):
        self.filename.setText(progress.filename.replace("/home/ahagen/mcnp/active/", ""))
        self.prog_bar.setProgress(100. * progress.nps / 1.E9)
        self.prog_text.setText("%.2f %%" % (100. * progress.nps / 1.E9))
        self.start_time.setText("Start Time: %s" % time.strftime(fmt,
                                         time.localtime(progress.start_time)))
        self.end_time.setText("Estimated End Time: %s" %
                                       time.strftime(fmt,
                                       time.localtime(progress.end_time)))
        self.time_slope.setText("Rate:\n %.2e n/hour" %
                                         (progress.time_slope * 3600.))

class all_progress(QWidget):
    def __init__(self, parent=None):
        QWidget.__init__(self)
        self.h = QHBoxLayout(self)
        self.prog = []

    def add_progress(self, progresses):
        for progress in progresses:
            prog_bar = progress_view(progress)
            self.prog.extend([prog_bar])
            self.h.addWidget(prog_bar)

    def refresh(self, progresses):
        for progress in progresses:
            for prog_view in self.prog:
                if prog_view.filename.text() in progress.filename:
                    prog_view.refresh(progress)


class refresh_button(QPushButton):
    def __init__(self):
        QPushButton.__init__(self)
        self.setText("Refresh")
        self.setFixedWidth(150)

class ApplicationWindow(QMainWindow):
    def __init__(self):
        QMainWindow.__init__(self)
        self.setFixedHeight(960)
        self.setAttribute(Qt.WA_DeleteOnClose)
        self.setWindowTitle("MCNP Checker")

        self.file_menu = QMenu('&File', self)
        self.file_menu.addAction('&Quit', self.fileQuit,
                                 Qt.CTRL + Qt.Key_Q)
        self.menuBar().addMenu(self.file_menu)

        self.help_menu = QMenu('&Help', self)
        self.menuBar().addSeparator()
        self.menuBar().addMenu(self.help_menu)

        self.main_widget = QWidget(self)

        self.l = QVBoxLayout(self.main_widget)
        self.l.setAlignment(Qt.AlignCenter)
        self.prg = all_progress(self.main_widget)
        filenames, cpus, cpu_uses, npss, start_times, time_slopes, \
            end_times, procs = check()
        self.progresses = [progress(filenames[i], cpu_uses[i], npss[i],
                                    start_times[i], time_slopes[i],
                                    end_times[i], procs[i])
                      for i in range(len(filenames))]
        self.prg.add_progress(self.progresses)
        self.l.addWidget(self.prg)
        self.button1 = refresh_button()
        self.l.addWidget(self.button1)
        self.button1.pressed.connect(self.check_progress)

        timeout = 1E3 * 10 * 60

        self.timer = QTimer(self)
        self.timer.timeout.connect(self.check_progress)
        self.timer.start(1E3 * 10 * 60)

        self.main_widget.setFocus()
        self.setCentralWidget(self.main_widget)


    def check_progress(self):
        self.button1.setText('Refreshed!')
        QTimer.singleShot(1E3, self.button_text_back)
        filenames, cpus, cpu_uses, npss, start_times, time_slopes, \
            end_times, procs = check()
        self.progresses = [progress(filenames[i], cpu_uses[i], npss[i],
                                    start_times[i], time_slopes[i],
                                    end_times[i], procs[i])
                      for i in range(len(filenames))]
        self.prg.refresh(self.progresses)
'''
app = Bottle()


@app.route("/mcnp")
def serve_picture():
    return template(HTML, content=all_prog(), data='somedata')

@app.route('/all_prog', method='GET')
def all_prog():
    string = ""
    filenames, cpus, cpu_uses, npss, start_times, time_slopes, \
        end_times, procs = check()
    for filename, nps, st, ts, et, p in zip(filenames, npss, start_times, time_slopes, end_times, procs):
        string += info(filename, st, ts, et, p)
        string += prog_bar(100. * nps / 1.E9)
    return string

@app.route('/prog_bar', method='GET')
def prog_bar(perc):
    string = ''
    string += r'<div class="progress">'
    string += r'  <span class="progress-value">%.2f %%</span>' % perc
    string += r'  <div class="progress-bar" role="progressbar" aria-valuenow="%.2f"' % perc
    string += r'  aria-valuemin="0" aria-valuemax="100" style="width:%.2f%%">' % perc
    string += r'    <span class="sr-only">%.2f%% Complete</span>' % perc
    string += r'  </div>'
    string += r'</div>'
    return string

@app.route('/info', method='GET')
def info(fname, start_time, time_slope, end_time, procs):
    string = ''
    string += "<p><b>Filename:</b> %s\n" % fname
    string += "<b>Start Time:</b> %s\n" % time.strftime(fmt,\
        time.localtime(start_time))
    string += "<b>End Time:</b> %s\n" % time.strftime(fmt,\
        time.localtime(end_time))
    string += ("<b>Time Slope:</b> $%.2e \\mathrm{\\frac{n}{hour}}$</p>" % (time_slope * 3600.)).replace("e+0", r"\times 10^").replace("e-0", r"\times 10^")
    string += "<p><b>Processes:</b> %d</p>\n" % procs
    return string

run(app, host='128.46.92.223', port=8080, reloader=True)
