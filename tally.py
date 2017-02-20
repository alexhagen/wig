import numpy as np
import geo
import cell


class tally():
    def __init__(self, **kwargs):
        tally.num = None
        self.mesh = False
        self.comment = kwargs["comment"]
        self.multiplier = False
        if "energy" in kwargs:
            self.process_energy(**kwargs)
            self.energies = True
        else:
            self.energies = False
        if "particle" in kwargs:
            self.particle = kwargs["particle"]

    def flux_tally(self, **kwargs):
        self.card = 4
        if not self.energies:
            self.process_energy(**kwargs)
        if isinstance(kwargs["cell"], cell.cell):
            self.cell = kwargs["cell"].cell_num
        else:
            self.cell = kwargs["cell"]
        self.particle = kwargs["particle"]
        self.string = ":%s %d" % (kwargs["particle"], self.cell)
        return self

    def mesh_tally(self, **kwargs):
        self.card = 4
        self.mesh = True
        #if not self.energies:
        #    self.process_energy(**kwargs)
        origin = (0, 0, 0)
        if "xmin" in kwargs:
            origin[0] = kwargs["xmin"]
        if "ymin" in kwargs:
            origin[1] = kwargs["ymin"]
        if "zmin" in kwargs:
            origin[2] = kwargs["zmin"]
        if "origin" in kwargs:
            origin = kwargs["origin"]
        xmin = origin[0]
        ymin = origin[1]
        zmin = origin[2]
        if "xmax" in kwargs:
            xmax = kwargs["xmax"]
        if "ymax" in kwargs:
            ymax = kwargs["ymax"]
        if "zmax" in kwargs:
            zmax = kwargs["zmax"]
        if "corner" in kwargs:
            xmax, ymax, zmax = kwargs["corner"]
        deltax = xmax - xmin
        deltay = ymax - ymin
        deltaz = zmax - zmin
        if "ijk" in kwargs:
            dx = kwargs["ijk"] + 1
            dy = kwargs["ijk"] + 1
            dz = kwargs["ijk"] + 1
        if "i" in kwargs:
            dx = kwargs["i"] + 1
        if "j" in kwargs:
            dy = kwargs["j"] + 1
        if "k" in kwargs:
            dz = kwargs["k"] + 1
        imesh = np.linspace(xmin, xmax, dx)
        jmesh = np.linspace(ymin, ymax, dy)
        kmesh = np.linspace(zmin, zmax, dz)
        self.string = (":%s geom=%s origin=%6.4f %6.4f %6.4f" % \
            (self.particle, 'xyz', origin[0], origin[1], origin[2])) + \
            " imesh=" + " ".join(["%6.4f" % i for i in imesh[1:]]) + \
            " jmesh=" + " ".join(["%6.4f" % j for j in jmesh[1:]]) + \
            " kmesh=" + " ".join(["%6.4f" % k for k in kmesh[1:]])
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
                if isinstance(surface, float):
                    self.surfaces.extend([surface])
                if isinstance(surface, list):
                    self.surfaces.extend(surface)
                elif surface.__class__.__name__ is 'geo':
                    self.surfaces.extend(float(surface.geo_num) +
                                         0.1 * np.array(surface.faces))
        print kwargs["surfaces"]
        print self.surfaces
        self.string = (":%s (" % kwargs["particle"] +
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
