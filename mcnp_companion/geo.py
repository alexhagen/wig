class geo:

    def rpp(self, c=None, l=None, id=None):
        self.id = id
        self.comment = "c --- %s" % (self.id)
        self.string = "rpp %6.4f %6.4f %6.4f %6.4f %6.4f %6.4f" % \
            (c[0], c[1], c[2], l[0], l[1], l[2])
        return self

    def sph(self, c=None, r=None, id=None):
        self.id = id
        self.comment = "c --- %s" % (self.id)
        self.string = "sph %6.4f %6.4f %6.4f %6.4f" % \
            (c[0], c[1], c[2], r)
        return self

    def rcc(self, c=None, l=None, r=None, id=None, lx=None, ly=None, lz=None):
        h = [0, 0, 0]
        if lx is not None:
            h[0] = lx
        if ly is not None:
            h[1] = ly
        if lz is not None:
            h[2] = lz
        self.id = id
        self.comment = "c --- %s" % (self.id)
        self.string = "rcc %6.4f %6.4f %6.4f %6.4f %6.4f %6.4f %6.4f" % \
            (c[0], c[1], c[2], h[0], h[1], h[2], r)
        return self
