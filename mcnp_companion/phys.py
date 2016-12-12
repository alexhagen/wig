class phys():
    def __init__(self, particles=None, sources=None, maxE=None, minE=None,
                 nps=None, ctme=None):
        # if we've defined nothing, then we're going to just go ahead and make
        # some default physics
        self.comment = "c --- default physics for "
        self.string = "mode "
        if maxE is None:
            maxE = 20.0
        if minE is None:
            minE = 1.0E-8
        self.maxE = maxE
        self.minE = minE
        for particle in particles:
            self.comment += "%s " % (particle)
            self.string += "%s " % (particle)
        self.comment = "%s" % (self.comment[:-1])
        self.string = "%s\n" % (self.string[:-1])
        if 'p' in particles:
            self.string += "phys:p %e 0 1 -1 2J 1\n" % (maxE)
            self.string += "cut:p %e J 0 0\n" % (maxE)
        if 'n' in particles:
            self.string += "phys:n %e\n" % (maxE)
            self.string += "cut:n j %e\n" % (minE)
        if nps is not None:
            self.nps(nps)
        if ctme is not None:
            self.ctme(ctme)

    def nps(self, num):
        self.string += "nps %e\n" % (num)
        return self

    def ctme(self, num):
        self.string += "ctme %e\n" % (num)
        return self

    def no_fission(self, cells=None):
        if cells is None:
            self.string += "nonu\n"
        return self
