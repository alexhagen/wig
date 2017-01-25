import textwrap
from pyg import threed
import numpy as np
from colour import Color
from transforms3d import euler, axangles
from pyb import pyb
import cell as mcnpce

class geo:
    """ some docstring
    """
    def __init__(self):
        self.bstring = ''
        self.b_cmds = []
        self.b_kwargs = []

    def cell(self, matl):
        """ use ``geo.cell(matl)`` to return a cell of this geometry with
            material ``matl``

            :param matl mcnpm.matl: The material to make this cell
            :returns: ``mcnpce.cell`` object
        """
        return mcnpce.cell(self, matl)

    def __sub__(self, right):
        if right is None:
            return pseudogeo(self)
        if self.__class__.__name__ is 'geo':
            # convert the right argument to a pseudogeo
            left = pseudogeo(self)
        if right.__class__.__name__ is 'geo':
            # convert the right argument to a pseudogeo
            right = pseudogeo(right)
        self.b_cmds.extend([right.b_cmds])
        self.b_kwargs.extend(right.b_kwargs)
        self.b_cmds.extend([pyb.pyb.subtract])
        self.b_kwargs.extend([{"left": left.id, "right": right.id}])
        return left - right

    def __add__(self, right):
        if right is None:
            return pseudogeo(self)
        if self.__class__.__name__ is 'geo':
            # convert the right argument to a pseudogeo
            left = pseudogeo(self)
        if right.__class__.__name__ is 'geo':
            # convert the right argument to a pseudogeo
            right = pseudogeo(right)
        self.b_cmds.extend([right.b_cmds])
        self.b_kwargs.extend(right.b_kwargs)
        self.b_cmds.extend([pyb.pyb.union])
        self.b_kwargs.extend([{"left": left.id, "right": right.id}])
        return left + right

    def __or__(self, right):
        if right is None:
            return pseudogeo(self)
        if self.__class__.__name__ is 'geo':
            # convert the right argument to a pseudogeo
            left = pseudogeo(self)
        if right.__class__.__name__ is 'geo':
            # convert the right argument to a pseudogeo
            right = pseudogeo(right)
        self.b_cmds.extend([right.blender_cmd])
        self.b_kwargs.extend(right.blender_cmd_args)
        self.b_cmds.extend([pyb.pyb.union])
        self.b_kwargs.extend([{"left": left.id, "right": right.id}])
        return left | right

    def rpp(self, c=None, l=None, x=None, y=None, z=None, id=None, name=None):
        self.sense = -1
        self.id = id
        self.geo_num = 0
        self.comment = "c --- %s" % (self.id)
        if x is None:
            x1 = c[0] - abs(l[0] / 2.0)
            x2 = c[0] + abs(l[0] / 2.0)
        else:
            c = [0., 0., 0.]
            l = [0., 0., 0.]
            x1 = x[0]
            x2 = x[1]
            c[0] = (x[1] - x[0]) / 2.0 + x[0]
            l[0] = x[1] - x[0]
        if y is None:
            y1 = c[1] - abs(l[1] / 2.0)
            y2 = c[1] + abs(l[1] / 2.0)
        else:
            y1 = y[0]
            y2 = y[1]
            c[1] = (y[1] - y[0]) / 2.0 + y[0]
            l[1] = y[1] - y[0]
        if z is None:
            z1 = c[2] - abs(l[2] / 2.0)
            z2 = c[2] + abs(l[2] / 2.0)
        else:
            z1 = z[0]
            z2 = z[1]
            c[2] = (z[1] - z[0]) / 2.0 + z[0]
            l[2] = z[1] - z[0]
        self.string = "rpp %6.4f %6.4f %6.4f %6.4f %6.4f %6.4f" % \
            (x1, x2, y1, y2, z1, z2)
        self.blender_cmd = pyb.pyb.rpp
        self.blender_cmd_args = {"c": c, "l": l, "name": id}
        self.faces = [1, 2, 3, 4, 5, 6]
        return self

    def box(self, v=None, a1=None, a2=None, a3=None, id=None):
        self.sense = -1
        self.id = id
        self.geo_num = 0
        self.comment = "c --- %s" % (self.id)
        self.string = ("box %6.4f %6.4f %6.4f  %6.4f %6.4f %6.4f  " +
                       "%6.4f %6.4f %6.4f  %6.4f %6.4f %6.4f") % \
                       (v[0], v[1], v[2], a1[0], a1[1], a1[2],
                        a2[0], a2[1], a2[2], a3[0], a3[1], a3[2])
        self.faces = [1, 2, 3, 4, 5, 6]
        c = np.array(v) + np.array(a1) / 2. + np.array(a2) / 2. + np.array(a3) / 2.
        l = np.array(a1) + np.array(a2) + np.array(a3)
        v = np.array(v)
        a1 = np.array(a1)
        a2 = np.array(a2)
        a3 = np.array(a3)
        verts = [tuple(v), tuple(v + a2), tuple(v + a3), tuple(v + a2 + a3),
                 tuple(v + a1), tuple(v + a1 + a2), tuple(v + a1 + a3),
                 tuple(v + a1 + a2 + a3)]
        self.blender_cmd = pyb.pyb.rpp
        self.blender_cmd_args = {"name": id, "verts": verts}
        return self

    def sph(self, c=None, r=None, id=None):
        self.sense = -1
        self.id = id
        self.geo_num = 0
        self.comment = "c --- %s" % (self.id)
        self.string = "sph %6.4f %6.4f %6.4f %6.4f" % \
            (c[0], c[1], c[2], r)
        self.faces = [1]
        self.r = r
        self.blender_cmd = pyb.pyb.sph
        self.blender_cmd_args = {"c": c, "r": r, "name": id}
        return self

    def rcc(self, c=None, l=None, r=None, id=None, lx=None, ly=None, lz=None):
        self.sense = -1
        h = [0, 0, 0]
        if lx is not None:
            h[0] = lx
        if ly is not None:
            h[1] = ly
        if lz is not None:
            h[2] = lz
        self.id = id
        self.geo_num = 0
        self.comment = "c --- %s" % (self.id)
        self.string = "rcc %6.4f %6.4f %6.4f %6.4f %6.4f %6.4f %6.4f" % \
            (c[0], c[1], c[2], h[0], h[1], h[2], r)
        self.surfaces = [1, 2, 3]
        direction = h.index(max(h))
        self.blender_cmd = pyb.pyb.rcc
        self.blender_cmd_args = {"c": c, "r": r, "h": max(h), "name": id,
                                 "direction": direction}
        return self

    def cone(self, c=None, dir='+z', h=None, r=None, id=None):
        self.sense = -1
        self.id = id
        self.geo_num = 0
        _h = [0, 0, 0]
        if 'z' in dir:
            i = 2
        elif 'x' in dir:
            i = 0
        elif 'y' in dir:
            i = 1
        if '+' in dir:
            _h[i] = h
        elif '-' in dir:
            _h[2] = -h
        self.comment = 'c --- %s' % (self.id)
        self.string = "trc %6.4f %6.4f %6.4f %6.4f %6.4f %6.4f %6.4f %6.4f" % \
            (c[0], c[1], c[2], h[0], h[1], h[2], r[0], r[1])
        self.surfaces = [1, 2, 3]
        return self

class pseudogeo:
    def __init__(self, geo):
        if geo.__class__.__name__ == 'cell':
            geo = geo.geo
        if geo.__class__.__name__ == 'pseudogeo':
            geo = geo.geo
        self.id = geo.id
        self.geo = geo
        self.nums = [(geo.geo_num, geo.sense)]
        self.b_cmds = []
        self.b_kwargs = []
        if len(geo.b_cmds) == 0:
            self.b_cmds = [geo.blender_cmd]
            self.b_kwargs = [geo.blender_cmd_args]
        else:
            self.b_cmds = geo.b_cmds
            self.b_kwargs = geo.b_kwargs

    def __sub__(self, right):
        if right is None:
            return self
        if right.__class__.__name__ is 'geo':
            right = pseudogeo(right)
        if type(right) is type(list()):
            for _right in right:
                __right = pseudogeo(_right)
                self.nums.extend([(__right.geo.geo_num, -__right.geo.sense)])
                self.id += "_less_%s" % __right.geo.id
                self.b_cmds.extend([_right.b_cmds])
                self.b_kwargs.extend(_right.b_kwargs)
                self.b_cmds.extend([pyb.pyb.subtract])
                self.b_kwargs.extend([{"left": self.id, "right": _right.id}])
        else:
            self.nums.extend([(right.geo.geo_num, -right.geo.sense)])
            self.b_cmds.extend([right.b_cmds])
            self.b_kwargs.extend(right.b_kwargs)
            self.b_cmds.extend([pyb.pyb.subtract])
            self.b_kwargs.extend([{"left": self.id, "right": right.id}])
            self.id += "_less_%s" % right.geo.id
        return self

    def __add__(self, right):
        if right is None:
            return self
        if right.__class__.__name__ is 'geo':
            right = pseudogeo(right)
        self.nums.extend([(right.geo.geo_num, right.geo.sense)])
        self.b_cmds.extend([right.b_cmds])
        self.b_kwargs.extend(right.b_kwargs)
        self.b_cmds.extend([pyb.pyb.union])
        self.b_kwargs.extend([{"left": self.id, "right": right.id}])
        self.id += "_plus_%s" % right.geo.id
        return self


class group:
    def __init__(self, content, id=None):
        self.suffix = ""
        self.string = ""
        if content.__class__.__name__ is 'geo':
            content = pseudogeo(content)
        if type(content) is type(list()):
            _content = content[0]
            for geo in content[1:]:
                _content = _content + geo
            content = _content
        self.content = content
        if id is None:
            self.id = "%s" % self.content.id
            self.manual_id = False
        else:
            self.id = id
            self.manual_id = True
        self.string = ""
        for num in self.content.nums:
            self.string += "%d " % (num[0] * num[1])
        self.already_unioned = False

    def __or__(self, right):
        if right.__class__.__name__ is not 'group':
            right = group(right)
        if not self.already_unioned:
            self.string = "("
            for num in self.content.nums:
                self.string += "%d " % (num[0] * num[1])
            self.string += "):("
        else:
            self.string += ":("
        for num in right.content.nums:
            self.string += "%d " % (num[0] * num[1])
        self.string += ")"
        if not self.manual_id:
            self.id += "_u_%s" % (right.id)
        self.already_unioned = True
        return self
