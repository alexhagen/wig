import textwrap
from pyg import threed

class geo:
    def __init__(self):
        self.bstring = ''

    def __sub__(self, right):
        if right is None:
            return pseudogeo(self)
        if self.__class__.__name__ is 'geo':
            # convert the right argument to a pseudogeo
            left = pseudogeo(self)
        if right.__class__.__name__ is 'geo':
            # convert the right argument to a pseudogeo
            right = pseudogeo(right)
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
        return left | right

    def rpp(self, c=None, l=None, x=None, y=None, z=None, id=None,
            color='gray', show=True):
        self.show = show
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
        self.plot_cmd = threed.pyg3d.cube
        self.plot_cmd_args = {"center": c, "dx": l[0], "dy": l[1], "dz": l[2],
                               "color": color, "planes": 0.5, "lines": True}
        self.faces = [1, 2, 3, 4, 5, 6]
        return self

    def box(self, v=None, a1=None, a2=None, a3=None, id=None, color='gray',
            show=True):
        self.show = show
        self.sense = -1
        self.id = id
        self.geo_num = 0
        self.comment = "c --- %s" % (self.id)
        self.string = ("box %6.4f %6.4f %6.4f  %6.4f %6.4f %6.4f  " +
                       "%6.4f %6.4f %6.4f  %6.4f %6.4f %6.4f") % \
                       (v[0], v[1], v[2], a1[0], a1[1], a1[2],
                        a2[0], a2[1], a2[2], a3[0], a3[1], a3[2])
        self.faces = [1, 2, 3, 4, 5, 6]
        self.plot_cmd = threed.pyg3d.box
        self.plot_cmd_args = {"corner": v, "d1": a1, "d2": a2,
                              "d3": a3, "color": color, "lines": True,
                              "planes": 0.5}
        return self

    def sph(self, c=None, r=None, id=None, color='gray', show=True):
        self.show = show
        self.sense = -1
        self.id = id
        self.geo_num = 0
        self.comment = "c --- %s" % (self.id)
        self.string = "sph %6.4f %6.4f %6.4f %6.4f" % \
            (c[0], c[1], c[2], r)
        self.faces = [1]
        self.plot_cmd = threed.pyg3d.sphere
        self.plot_cmd_args = {"center": c, "r": r, "color": color,
                              "lines": True, "planes": 0.5}
        return self

    def rcc(self, c=None, l=None, r=None, id=None, lx=None, ly=None, lz=None,
            color='gray', show=True):
        self.show = show
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
        self.plot_cmd = threed.pyg3d.cylinder
        self.plot_cmd_args = {"center": c, "h": h, "r": r, "color": color,
                              "lines": True, "planes": 0.5}
        self.surfaces = [1, 2, 3]
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
        else:
            self.nums.extend([(right.geo.geo_num, -right.geo.sense)])
            self.id += "_less_%s" % right.geo.id
        return self

    def __add__(self, right):
        if right is None:
            return self
        if right.__class__.__name__ is 'geo':
            right = pseudogeo(right)
        self.nums.extend([(right.geo.geo_num, right.geo.sense)])
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
