from . import wig

class wsc(wig):
    """A subclass to easily generate additive and encapsulated wig objects.

    Takes the same initialization as a ``wig`` scene, but also generates the
    lists ``geos``, ``matls``, ``cells``, ``tallies``, and a ``phys`` and
    ``source`` object so that you can easily add and modularize your code.
    """
    def __init__(self, filename, comment, **kwargs):
        self.geos = []
        self.matls = []
        self.cells = []
        self.tallies = []
        self.phys = None
        self.source = None
        super(wsc, self).__init__(filename, comment, **kwargs)
