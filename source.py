from colour import Color
from pyb import pyb

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
                 radius=None, cell=None, show=True, spectrum_type='C',
                 axis=None, lx=None, ly=None, lz=None, anisotropic=False):
        self.show = show
        self.blender_cmd = None
        self.blender_cmd_args = None
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
        types = {"n": 1, "p": 2, "e": 3, "fission": 1, "d": 31, "t": 32, "he3": 33, "he4": 34}
        colors = {"n": '#7299C6', "p": "#E3AE24", "fission": '#B95915', 'd': "#5C6F7B", 't': "#F8981D"}
        self.string += "par=%s " % (types[particle])
        color = colors[particle]
        print color
        if direction == '-z' or direction == 'z-':
            self.string += "vec=0 0 -1 "
            if anisotropic:
                self.string += "dir=1 "
            self.axis = (0, 0, 1)
        elif direction == '+x' or direction == 'x+':
            self.string += "vec=1 0 0 dir=1 "
            self.axis = (1, 0, 0)
        elif direction == '+y' or direction == 'y+':
            self.string += "vec=0 1 0 dir=1 "
            self.axis = (0, 1, 0)
        if axis is not None:
            if axis == '+z' and lz is not None:
                direction = 'z'
                self.string += 'vec=0 0 1 '
                self.axis = [0, 0, lz]
        if shape == 'disk' and radius is not None:
            self.dists.extend([dist([0, radius], [-21, 1], self.dist_num,
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
        if positioned and shape != 'disk':
            self.string += "pos=%6.4f %6.4f %6.4f " % (self.x, self.y, self.z)
            self.blender_cmd = pyb.pyb.sph
            self.blender_cmd_args = {"c": (self.x, self.y, self.z), "r": 1.0,
                                     "name": id, "color": color,
                                     "alpha": 1.0, "emis": True}
        elif cell is not None:
            self.string += "cel=%d " % (cell.cell_num)
            self.string += "pos=%6.4f %6.4f %6.4f " % (self.x, self.y, self.z)
            self.dists.extend([dist([0, radius], [-21, 1], self.dist_num, format='d')])
            self.string += 'rad=d%d ' % (self.dist_num)
            self.dist_num += 1
            if self.show:
                self.blender_cmd = cell.blender_cmd
                self.blender_cmd_args = cell.blender_cmd_args
                self.blender_cmd_args["emis"] = True
        if type(spectrum) is type([]):
            self.dists.extend([dist(spectrum[0], spectrum[1], self.dist_num,
                               spectrum_type=spectrum_type)])
            self.string += 'erg=d%d ' % self.dist_num
            self.dist_num += 1
        elif particle == "fission":
            self.dists.extend([dist(spectrum_type='Watt', dist_num=self.dist_num)])
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
        :param str spectrum_type: can be ``'C'``, ``'Maxwellian'``, ``'Watt'``
        :param str format: currently can be ``'d'`` to use only integers in the
            distribution

        .. todo:: implement more distribution types
        .. todo:: make semantic names for the distribution types
    """
    def __init__(self, x=None, y=None, dist_num=None, spectrum_type=None,
                 format=None):
        self.dist_num = dist_num
        self.dist_string = ''
        if spectrum_type is None or len(spectrum_type) == 1:
            if spectrum_type is None:
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
        elif spectrum_type is "Maxwellian":
            self.dist_string += 'sp%d -2 %f' % (self.dist_num, a)
        elif spectrum_type is "Watt":
            # A and B for U-235 induced fission
            a = 0.988
            b = 2.249
            self.dist_string += 'sp%d -3 %e %e' % (self.dist_num, a, b)
        self.dist_string += '\n'
