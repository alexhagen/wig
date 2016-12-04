import textwrap

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

    def rpp(self, c=None, l=None, id=None):
        self.sense = -1
        self.id = id
        self.geo_num = 0
        self.comment = "c --- %s" % (self.id)
        x1 = c[0] - abs(l[0] / 2.0)
        x2 = c[0] + abs(l[0] / 2.0)
        y1 = c[1] - abs(l[1] / 2.0)
        y2 = c[1] + abs(l[1] / 2.0)
        z1 = c[2] - abs(l[2] / 2.0)
        z2 = c[2] + abs(l[2] / 2.0)
        self.string = "rpp %6.4f %6.4f %6.4f %6.4f %6.4f %6.4f" % \
            (x1, x2, y1, y2, z1, z2)
        self.faces = [1, 2, 3, 4, 5, 6]
        return self

    def sph(self, c=None, r=None, id=None):
        self.sense = -1
        self.id = id
        self.geo_num = 0
        self.comment = "c --- %s" % (self.id)
        self.string = "sph %6.4f %6.4f %6.4f %6.4f" % \
            (c[0], c[1], c[2], r)
        self.faces = [1]
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
        return self

class pseudogeo:
    def __init__(self, geo):
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
