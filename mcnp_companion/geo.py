class geo:

    def __sub__(self, right):
        print "left is %s - %s and right is %s - %s\n" % (self.id,
                                                          self.__class__.__name__,
                                                          right.id,
                                                          right.__class__.__name__)
        if self.__class__.__name__ is 'geo':
            # convert the right argument to a pseudogeo
            print "%s is geo\n" % (self.id)
            left = pseudogeo(self)
        if right.__class__.__name__ is 'geo':
            # convert the right argument to a pseudogeo
            print "%s is geo\n" % (right.id)
            right = pseudogeo(right)
        return left - right

    def rpp(self, c=None, l=None, id=None):
        self.sense = -1
        self.id = id
        self.geo_num = 0
        self.comment = "c --- %s" % (self.id)
        self.string = "rpp %6.4f %6.4f %6.4f %6.4f %6.4f %6.4f" % \
            (c[0], c[1], c[2], l[0], l[1], l[2])
        return self

    def sph(self, c=None, r=None, id=None):
        self.sense = -1
        self.id = id
        self.geo_num = 0
        self.comment = "c --- %s" % (self.id)
        self.string = "sph %6.4f %6.4f %6.4f %6.4f" % \
            (c[0], c[1], c[2], r)
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
        return self

class pseudogeo:
    def __init__(self, geo):
        self.id = geo.id
        self.geo = geo
        self.nums = [(geo.geo_num, geo.sense)]

    def __sub__(self, right):
        if right.__class__.__name__ is 'geo':
            right = pseudogeo(right)
        self.nums.extend([(right.geo.geo_num, -right.geo.sense)])
        self.id += "_less_%s" % right.geo.id
        return self
