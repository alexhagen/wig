class phys():
    def __init__(self, particles=None, sources=None, maxE=None, minE=None,
                 nps=None, ctme=None):
        # if we've defined nothing, then we're going to just go ahead and make
        # some default physics
        self.comment = "c --- default physics for "
        self.string = "mode "
        for particle in particles:
            self.comment += "%s " % (particle)
            self.string += "%s " % (particle)
        self.comment = "%s" % (self.comment[:-1])
        self.string = "%s\n" % (self.string[:-1])
        if 'p' in particles:
            self.string += "phys:p 20 0 1 -1 2J 1\n"
            self.string += "cut:p 20 J 0 0\n"
        if 'n' in particles:
            self.string += "phys:n 20.\n"
            self.string += "cut:n j 1.E-9\n"
        if nps is not None:
            self.nps(nps)
        if ctme is not None:
            self.ctme(ctme)

    def nps(self, num):
        self.string += "nps %e\n" % (num)

    def ctme(self, num):
        self.string += "ctme %e\n" % (num)
