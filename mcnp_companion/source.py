class source():

    def __init__(self, particle='n', pos=None, x=None, y=None, z=None,
                 spectrum=None, shape=None, dir=None, id=None, cell=None):
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
        self.string = ""
        self.comment = "c --- %s" % id
        types = {"n": 1, "p": 2, "e": 3, "fission": 1}
        self.string += "par=%s " % (types[particle])
        if positioned:
            self.string += "pos=%6.4f %6.4f %6.4f " % (self.x, self.y, self.z)
        elif cell is not None:
            self.string += "cel=%d " % (cell.cell_num)
        if type(spectrum) is type([]):
            self.dists = [dist(spectrum[0], spectrum[1], self.dist_num)]
            self.string += 'erg=d%d ' % self.dist_num
            self.dist_num += 1
        elif particle == "fission":
            self.dists = [dist(type='Watt', dist_num=self.dist_num)]
            self.string +=  'erg=d%d ' % self.dist_num
            self.dist_num += 1
        self.string = self.string[:-1]
        self.string += '\n'
        for _dist in self.dists:
            self.string += _dist.dist_string
        self.string = self.string[:-1]

class dist():
    def __init__(self, x=None, y=None, dist_num=None, type=None):
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
                self.dist_string += '%15.10e ' % (_y)
            self.dist_string = self.dist_string[:-1]
        elif type is "Maxwellian":
            self.dist_string += 'sp%d -2 %f' % (self.dist_num, a)
        elif type is "Watt":
            a = 0.988
            b = 2.249
            self.dist_string += 'sp%d -3 %e %e' % (self.dist_num, a, b)
        self.dist_string += '\n'
