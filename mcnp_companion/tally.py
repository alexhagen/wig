import numpy as np
import geo
import cell


class tally():
    def __init__(self, **kwargs):
        tally.num = None
        self.comment = kwargs["comment"]
        self.multiplier = False
        if "energy" in kwargs:
            self.process_energy(**kwargs)
            self.energies = True
        else:
            self.energies = False

    def flux_tally(self, **kwargs):
        self.card = 4
        if not self.energies:
            self.process_energy(**kwargs)
        if isinstance(kwargs["cell"], cell.cell):
            self.cell = kwargs["cell"].cell_num
        else:
            self.cell = kwargs["cell"]
        self.string = ":%s %d" % (kwargs["particle"], self.cell)
        return self

    def add_multiplier(self, **kwargs):
        self.multiplier = True
        if "mat" in kwargs:
            self.mat = kwargs["mat"]
        if "mt" in kwargs:
            self.mt = kwargs["mt"]
        self.multiplier_string = "(-1 %d %d) T" % (self.mat, self.mt)
        return self

    def current_tally(self, **kwargs):
        self.card = 1
        if not self.energies:
            self.process_energy(**kwargs)
        self.surfaces = []
        if "surfaces" in kwargs:
            for surface in kwargs["surfaces"]:
                if type(surface) is "float":
                    self.surfaces.extend([surface])
                elif surface.__class__.__name__ is 'geo':
                    self.surfaces.extend(float(surface.geo_num) +
                                         0.1 * np.array(surface.faces))
        self.string = (":%s (" % kwargs["particle"] +
                       "%.1f " * (len(self.surfaces) - 1) +
                       ' '.join("%.1f" % s for s in self.surfaces) +
                       ")")
        return self

    def fission_tally(self, **kwargs):
        self.card = 7
        if not self.energies:
            self.process_energy(**kwargs)
        if isinstance(kwargs["cell"], cell.cell):
            self.cell = kwargs["cell"].cell_num
        else:
            self.cell = kwargs["cell"]
        self.string = ":n %d" % (self.cell)
        return self

    def process_energy(self, **kwargs):
        if "energy" not in kwargs:
            self.energy_string = '1e-8 99log 20'
        else:
            self.energy_string = '%e 99log %e' % (np.min(kwargs["energy"]),
                                                np.max(kwargs["energy"]))
