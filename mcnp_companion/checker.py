import time
import re
import os
import subprocess
import multiprocessing
import sys
import string
from PyQt5.QtGui import *
from PyQt5.QtWidgets import *
from PyQt5.QtCore import *
import notify2 as n

fmt = '%A \n %m-%d-%y %I:%M:%S %p'

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

def check():
    start_times = []
    time_slopes = []
    end_times = []
    cpu_uses = []
    npss = []
    procs = []
    filenames = []
    ps_aux_out = subprocess.check_output(['ps aux | grep mcnp'], shell=True)
    for line in ps_aux_out.split('\n'):
        if '/bin/sh' not in line and 'grep mcnp' not in line and '.inp' in line:
            arr = re.findall(r"[-+]?\d*\.\d+|\d+", line)
            cpu_use = float(arr[1])
            pid = int(arr[0])
            file = find_between(line, 'out=', '.out')
            filenames.extend([file])
            if 'tasks' in line:
                procs.extend([float(arr[-1])])
            else:
                procs.extend([1])
            cpu_use = cpu_use / float(arr[-1])

    for filename, i in zip(filenames, range(len(filenames))):
        dump = 1
        ctm_2 = None
        nps_2 = None
        filestring = ''
        for line in reversed(open(filename + '.out', 'r').readlines()):
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

        # now grab the string from ps aux | grep mcnp
        ps_aux_out = subprocess.check_output(['ps aux | grep mcnp'], shell=True)
        for line in ps_aux_out.split('\n'):
            if filename in line and '/bin/sh' not in line:
                arr = re.findall(r"[-+]?\d*\.\d+|\d+", line)
                cpu_use = float(arr[1])
                pid = int(arr[0])

        cpus = float(multiprocessing.cpu_count())
        now = os.path.getmtime(filename + '.out')
        start_time = now - (ctm_1 * 60.)
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
    return filenames, cpus, cpu_uses, npss, start_times, time_slopes, end_times, procs

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

    def button_text_back(self):
        self.button1.setText('Refresh')

    def fileQuit(self):
        self.close()

    def closeEvent(self, ce):
        self.fileQuit()



qApp = QApplication(sys.argv)
qApp.setStyle(QStyleFactory.create("Fusion"));

darkPalette = QPalette();
darkPalette.setColor(QPalette.Window, QColor('#000000'));
darkPalette.setColor(QPalette.WindowText, QColor('#d1d3d4'));
darkPalette.setColor(QPalette.Base, QColor('#746c66'));
darkPalette.setColor(QPalette.AlternateBase, QColor('#000000'));
darkPalette.setColor(QPalette.ToolTipBase, QColor('#d1d3d4'));
darkPalette.setColor(QPalette.ToolTipText, QColor('#d1d3d4'));
darkPalette.setColor(QPalette.Text, QColor('#d1d3d4'));
darkPalette.setColor(QPalette.Button, QColor('#000000'));
darkPalette.setColor(QPalette.ButtonText, QColor('#d1d3d4'));
darkPalette.setColor(QPalette.BrightText, QColor('#b63f97'));
darkPalette.setColor(QPalette.Link, QColor('#2eafa4'));

darkPalette.setColor(QPalette.Highlight, QColor('#e3ae24'));
darkPalette.setColor(QPalette.HighlightedText, QColor('#746c66'));

# qApp.setPalette(darkPalette);

# qApp.setStyleSheet("QToolTip { color: #d1d3d4; background-color: #7ed0e0; border: 1px solid #d1d3d4; }");

aw = ApplicationWindow()
aw.show()
sys.exit(qApp.exec_())

qApp.exec_()
