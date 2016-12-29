from vapory import *
from colour import Color
from pyb import pyb

class source():

    def __init__(self, particle='n', pos=None, x=None, y=None, z=None,
                 spectrum=None, shape=None, direction=None, id=None,
                 radius=None, cell=None):
        if cell is not None:
            positioned = False
        else:
            positioned = True
        if pos is None:
            self.x = x
            self.y = y
            self.z = z
        else:
            self.x = pos[0]
            self.y = pos[1]
            self.z = pos[2]
        self.dist_num = 1
        self.dists = []
        self.string = ""
        self.comment = "c --- %s" % id
        types = {"n": 1, "p": 2, "e": 3, "fission": 1}
        colors = {"n": '#7299C6', "p": "#E3AE24"}
        self.string += "par=%s " % (types[particle])
        color = colors[particle]
        if direction == '-z' or direction == 'z-':
            self.string += "vec=0 0 -1 dir=1 "
            self.axis = (0, 0, 1)
        if shape == 'disk' and radius is not None:
            self.dists.extend([dist([0, radius], [-21, 0], self.dist_num,
                                    format='d')])
            self.string += "axs=%d %d %d rad=d%d " % (self.axis[0],
                                                      self.axis[1],
                                                      self.axis[2],
                                                      self.dist_num)
            self.dist_num += 1
            self.blender_cmd = pyb.pyb.rcc
            self.blender_cmd_args = {"c": (self.x, self.y, self.z),
                                     "r": radius, "h": 0.1, "name": id,
                                     "color": color, "direction": direction.replace('-', '').replace('+', ''),
                                     "alpha": 1.0, "emis": True}
        color = '#2EAFA4'
        self.vapory_cmd = LightSource
        col = Color(color).rgb
        self.vapory_cmd_args = [(0,0,0), col, 'looks_like { sphere { <0,0,0>,1 finish { ambient 1 } } } translate <%6.4f, %6.4f, %6.4f>' % (pos[0], pos[1], pos[2])]
        self.vapory_cmd_kwargs = {}
        if positioned:
            self.string += "pos=%6.4f %6.4f %6.4f " % (self.x, self.y, self.z)
        elif cell is not None:
            self.string += "cel=%d " % (cell.cell_num)
        if type(spectrum) is type([]):
            self.dists.extend([dist(spectrum[0], spectrum[1], self.dist_num)])
            self.string += 'erg=d%d ' % self.dist_num
            self.dist_num += 1
        elif particle == "fission":
            self.dists.extend([dist(type='Watt', dist_num=self.dist_num)])
            self.string +=  'erg=d%d ' % self.dist_num
            self.dist_num += 1
        self.string = self.string[:-1]
        self.string += '\n'
        for _dist in self.dists:
            self.string += _dist.dist_string
        self.string = self.string[:-1]

class dist():
    def __init__(self, x=None, y=None, dist_num=None, type=None, format=None):
        self.dist_num = dist_num
        self.dist_string = ''
        if type is None:
            self.dist_string += 'si%d a ' % (self.dist_num)
            for _x in x:
                self.dist_string += "%15.10e " % (_x)
            self.dist_string = self.dist_string[:-1]
            self.dist_string += '\n'
            self.dist_string += 'sp%d d ' % (self.dist_num)
            for _y in y:
                if format is None:
                    self.dist_string += '%15.10e ' % (_y)
                elif format == 'd':
                    self.dist_string += '%d ' % (_y)
            self.dist_string = self.dist_string[:-1]
        elif type is "Maxwellian":
            self.dist_string += 'sp%d -2 %f' % (self.dist_num, a)
        elif type is "Watt":
            a = 0.988
            b = 2.249
            self.dist_string += 'sp%d -3 %e %e' % (self.dist_num, a, b)
        self.dist_string += '\n'
