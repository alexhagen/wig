from colour import Color
from pyb import pyb
import numpy as np

class source():
    """ ``source`` is an object that defines an MCNP source. Currently there are
        only a few implemented type of sources:

        - point source: use ``pos`` or ``x``, ``y``, and ``z``
        - disk source: use ``pos``, ``shape = 'disk'``, and ``direction``
        - cell source: use ``cell`` and an enclosing disk
        - energy spectrum: use ``spectrum`` and a ``dist`` object
        - intensity distribution:

        :param str particle: one of 'n', 'p', 'd', 't', 's', 'a', or 'fission'
        :param tup pos: position of the source
        :param float x, y, z: position of the source - alternate method
        :param spectrum: either a distribution or a two-d list to create an
            energy distribution
        :param str shape: right now, can only be ``'disk'``, more coming.
        :param str direction: one of '+x' or '-x', '+y' or '-y', or '+z' or '-z'
        :param str id: an identifying string
        :param float radius: the radius of a disk source
        :param wig.cell cell: the cell for a volumetric source
        :param bool show: whether the source should be rendered or not

        .. todo:: implement the whole MCNP Primer of sources
    """
    def __init__(self, particle='n', pos=None, x=None, y=None, z=None,
                 spectrum=None, shape=None, direction=None, id=None,
                 radius=None, cell=None, show=True, dist_type='C',
                 axis=None, lx=None, ly=None, lz=None, anisotropic=False,
                 half_angle=None):
        self.show = show
        self.blender_cmd = None
        self.blender_cmd_args = {}
        self.coned = False
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
        if lx is None:
            lx = 1.0
        if ly is None:
            ly = 1.0
        if lz is None:
            lz = 1.0
        types = {"n": 'n', "p": 'p', "e": 3, "fission": 1, "d": 31, "t": 32, "he3": 33, "he4": 34}
        colors = {"n": '#7299C6', "p": "#E3AE24", "fission": '#B95915', 'd': "#5C6F7B", 't': "#F8981D"}
        self.string += "par=%s " % (types[particle])
        color = colors[particle]
        if 'cone' in direction:
            # extract cone from the direction
            self.coned = True
            anisotropic = True
            direction = direction.replace('cone:', '').replace('cone', '')
            # extract angle spread from the direction keyword
            half_angle = float(direction.split(':')[1])
            direction = direction.split(':')[0]
        if direction == '-z' or direction == 'z-':
            if anisotropic:
                self.string += "vec=0 0 -1 "
                if not self.coned:
                    self.string += "dir=1 "
                else:
                    self.string += "dir=d%d " % self.dist_num
            self.axis = (0, 0, lz)
        elif direction == '+z' or direction == 'z+':
            if anisotropic:
                self.string += "vec=0 0 1 "
                if not self.coned:
                    self.string += "dir=1 "
                else:
                    self.string += "dir=d%d " % self.dist_num
            self.axis = (0, 0, lz)
        elif direction == '+x' or direction == 'x+':
            self.string += "vec=1 0 0 dir=1 "
            self.axis = (1, 0, lx)
        elif direction == '+y' or direction == 'y+':
            self.string += "vec=0 1 0 dir=1 "
            self.axis = (0, 1, ly)
        elif direction == '-y' or direction == 'y-':
            self.string += "vec=0 -1 0 dir=1 "
            self.axis = (0, 1, ly)
        if self.coned:
            #self.string += "wgt=%e " % (1.0 / 2.0 * np.pi * (1.0 - np.cos(np.radians(half_angle)))/(4.0 * np.pi))
            self.dists.extend([dist([half_angle], [], self.dist_num, dist_type='ipb')])
            self.dist_num += 1
        if shape == 'disk' and radius is not None:
            self.string += "pos=%6.4f %6.4f %6.4f " % (self.x, self.y, self.z)
            self.dists.extend([dist([0, radius], [-21, 1], self.dist_num,
                                    format='d')])
            self.string += "axs=%d %d %d rad=d%d " % (self.axis[0],
                                                      self.axis[1],
                                                      self.axis[2],
                                                      self.dist_num)
            self.dist_num += 1
            self.blender_cmd = [pyb.pyb.rcc]
            self.blender_cmd_args = [{"c": (self.x, self.y, self.z),
                                     "r": radius, "h": 0.1, "name": id,
                                     "color": color, "direction": direction.replace('-', '').replace('+', ''),
                                     "alpha": 1.0, "emis": True}]
        color = '#2EAFA4'
        if positioned and shape != 'disk':
            self.string += "pos=%6.4f %6.4f %6.4f " % (self.x, self.y, self.z)
            self.blender_cmd = [pyb.pyb.sph]
            self.blender_cmd_args = [{"c": (self.x, self.y, self.z), "r": 1.0,
                                     "name": id, "color": color,
                                     "alpha": 1.0, "emis": True}]
        elif cell is not None:
            self.string += "cel=%d " % (cell.cell_num)
            self.string += "pos=%6.4f %6.4f %6.4f " % (self.x, self.y, self.z)
            self.dists.extend([dist([0, radius], [-21, 1], self.dist_num, format='d')])
            self.string += 'rad=d%d ' % (self.dist_num)
            self.dist_num += 1
            if self.show:
                self.blender_cmd = cell.b_cmds
                self.blender_cmd_args = cell.b_kwargs
        if type(spectrum) is type([]):
            self.dists.extend([dist(spectrum[0], spectrum[1], self.dist_num,
                               dist_type=dist_type)])
            self.string += 'erg=d%d ' % self.dist_num
            self.dist_num += 1
        elif particle == "fission":
            self.dists.extend([dist(dist_type='Watt', dist_num=self.dist_num)])
            self.string +=  'erg=d%d ' % self.dist_num
            self.dist_num += 1
        elif isinstance(spectrum, float):
            self.string += 'erg=%15.10e ' % spectrum
        self.string = self.string[:-1]
        self.string += '\n'
        for _dist in self.dists:
            self.string += _dist.dist_string
        self.string = self.string[:-1]


class dist():
    """ ``dist`` creates a distribution that MCNP uses for its source energy,
        or position, or intensity

        :param list x: the independent variable values of the distribution
        :param list y: the dependent variable values of the distribution
        :param int dist_num: the identifying number, usually assigned
            automatically by ``wig.source``
        :param str dist_type: can be ``'C'``, ``'Maxwellian'``, ``'Watt'``
        :param str format: currently can be ``'d'`` to use only integers in the
            distribution

        .. todo:: implement more distribution types
        .. todo:: make semantic names for the distribution types
    """
    def __init__(self, x=None, y=None, dist_num=None, dist_type=None,
                 format=None):
        self.dist_num = dist_num
        self.dist_string = ''
        if dist_type is None or len(dist_type) == 1:
            if dist_type is None:
                self.dist_string += 'si%d ' % (self.dist_num)
            else:
                self.dist_string += 'si%d ' % (self.dist_num)
            for _x in x:
                self.dist_string += "%15.10e " % (_x)
            self.dist_string = self.dist_string[:-1]
            self.dist_string += '\n'
            self.dist_string += 'sp%d ' % (self.dist_num)
            for _y in y:
                if format is None:
                    self.dist_string += '%15.10e ' % (_y)
                elif format == 'd':
                    self.dist_string += '%d ' % (_y)
            self.dist_string = self.dist_string[:-1]
        elif dist_type is "Maxwellian":
            self.dist_string += 'sp%d -2 %f' % (self.dist_num, a)
        elif dist_type is "Watt":
            # A and B for U-235 induced fission
            a = 0.988
            b = 2.249
            self.dist_string += 'sp%d -3 %e %e' % (self.dist_num, a, b)
        elif dist_type is "ipb":
            self.dist_string += 'si%d -1.0 %e 1.0\n' % (self.dist_num, np.cos(np.radians(x[0])))
            self.dist_string += 'sp%d 0.0 %e %e\n' % (self.dist_num, 2.0 * np.pi * (1.0 - np.cos(np.pi - np.radians(x[0])))/(4.0 * np.pi), 2.0 * np.pi * (1.0 - np.cos(np.radians(x[0])))/(4.0 * np.pi))
            self.dist_string += 'sb%d 0.0 0.0 1.0' % (self.dist_num)
        self.dist_string += '\n'
