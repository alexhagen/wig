import numpy as np

class mcnp_companion:
    def __init__(self, comment):
        self.comment = comment
        print "Initialized file with comment \"%s\"." % (comment)
