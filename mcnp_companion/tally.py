import numpy as np
import geo


class tally():
    def __init__(self, **kwargs):
        tally.num = None
        self.comment = kwargs["comment"]
        self.card = kwargs["card"]
        if self.card == 4:
            self.flux_tally(kwargs)
        if self.card == 1:
            self.current_tally(kwargs)

    def flux_tally(self, kwargs):
        self.process_energy(kwargs)
        if isinstance(kwargs["cell"], geo.geo):
            self.cell = kwargs["cell"].num
        else:
            self.cell = kwargs["cell"]
        self.string = ":%s %d" % (kwargs["particle"], self.cell)

    def current_tally(self, **kwargs):
        if energy is None:
            self.energy_string = '1e-8 99i 20'
        else:
            self.energy_string = '%e 99i %e' % (np.min(kwargs["energy"]),
                                                np.max(kwargs["energy"]))
        if type(kwargs["surfaces"]) is "float":
            self.surfaces = [kwargs["surfaces"]]
        self.string = (":%s (" + "%.1f " * (len(self.surfaces) - 1) +
                       "%.1f" + ")") % (kwargs["particle"],
                                        self.surfaces)

    def process_energy(self, kwargs):
        if "energy" not in kwargs:
            self.energy_string = '1e-8 99i 20'
        else:
            self.energy_string = '%e 99i %e' % (np.min(kwargs["energy"]),
                                                np.max(kwargs["energy"]))
