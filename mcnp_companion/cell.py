class cell:
    def __init__(self, geo=None, matl=None, comment=None):
        if comment is None:
            self.comment = "c --- %s" % (geo.id)
        else:
            self.comment = "c --- %s" % (comment)
        self.matl = matl
        self.geo = geo
        self.id = geo.id
