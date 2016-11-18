import numpy as np
import geo
import cell


class tally():
    def __init__(self, **kwargs):
        tally.num = None
        self.comment = kwargs["comment"]

    def flux_tally(self, **kwargs):
        self.card = 4
        self.process_energy()
        if isinstance(kwargs["cell"], cell.cell):
            self.cell = kwargs["cell"].cell_num
        else:
            self.cell = kwargs["cell"]
        self.string = ":%s %d" % (kwargs["particle"], self.cell)
        return self

    def current_tally(self, **kwargs):
        self.card = 1
        self.process_energy()
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
        self.process_energy()
        if isinstance(kwargs["cell"], cell.cell):
            self.cell = kwargs["cell"].cell_num
        else:
            self.cell = kwargs["cell"]
        self.string = ":n %d" % (self.cell)
        return self

    def process_energy(self, **kwargs):
        if "energy" not in kwargs:
            self.energy_string = '1e-8 99i 20'
        else:
            self.energy_string = '%e 99i %e' % (np.min(kwargs["energy"]),
                                                np.max(kwargs["energy"]))
