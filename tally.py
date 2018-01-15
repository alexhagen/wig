import numpy as np
import geo
import cell


class tally():
    """ a ``tally`` object defines one of several types of MCNP tallies:

        - flux tally (``f4``)
        - current tally (``f1``)
        - fission tally (``f7``)
        - mesh tally (``fmesh4``)

        The best pratice is to pass energies and comments to the initializer and
        to use the convenience methods to continue from there

        .. code-block:: python

            Es = [1.0E-4, 1.0, 100.0]
            meshtal1 = wig.tally(comment='a mesh tally for demo purposes', energy=Es)\
                .mesh_tally(xmin=0.0, xmax=10.0, ymin=0.0, ymax=10.0, zmin=0.0, zmax=10.0, ijk=(10, 10, 10))
    """
    def __init__(self, **kwargs):
        tally.num = None
        self.mesh = False
        self.tmesh = False
        self.comment = kwargs["comment"]
        self.multiplier = False
        self.time = False
        if "energy" in kwargs:
            self.process_energy(**kwargs)
            self.energies = True
        else:
            self.energies = False
        if "particle" in kwargs:
            self.particle = kwargs["particle"]

    def flux_tally(self, **kwargs):
        """ ``flux_tally`` is a tally calculating the flux through a cell. Pass
            keywords ``energy``, ``cell``, and ``particle``
        """
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

    def energy_tally(self, **kwargs):
        """ ``energy_tally`` is a tally calculating the energy deposited in a
            cell per unit mass.

            :param list energy: A list whos energies span the range of the
                highest to lowest interesting energies
            :param object tally_cell: the cell of interest
            :param str particle: 'n' for neutrons, 'p' for photons, or 'n, p'
                for both
        """
        self.card = 6
        if not self.energies:
            self.process_energy(**kwargs)
        if isinstance(kwargs["cell"], cell.cell):
            self.cell = kwargs["cell"].cell_num
        else:
            self.cell = kwargs["cell"]
        self.particle = kwargs["particle"]
        self.string = ":%s %d" % (kwargs["particle"], self.cell)
        return self

    def rmesh(self, **kwargs):
        self.card = 1
        self.tmesh = True
        origin = [0, 0, 0]
        if 'geom' not in kwargs:
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
                imesh = np.linspace(xmin, xmax, dx)
            if "j" in kwargs:
                dy = kwargs["j"] + 1
                jmesh = np.linspace(ymin, ymax, dy)
            if "k" in kwargs:
                dz = kwargs["k"] + 1
                kmesh = np.linspace(zmin, zmax, dz)
            self.tmeshtype = 'rmesh'
            self.string = ":%s\n" % self.particle
            if "i" not in kwargs:
                self.string += "  cora{number}{card} %6.4f %6.4f\n" % (xmin, xmax)
            else:
                self.string += "  cora{number}{card} %6.4f %di %6.4f\n" % (xmin, dx - 1, xmax)
            if "j" not in kwargs:
                self.string += "  corb{number}{card} %6.4f %6.4f\n" % (ymin, ymax)
            else:
                self.string += "  corb{number}{card} %6.4f %di %6.4f\n" % (ymin, dy - 1, ymax)
            if "k" not in kwargs:
                self.string += "  corc{number}{card} %6.4f %6.4f" % (zmin, zmax)
            else:
                self.string += "  corc{number}{card} %6.4f %di %6.4f" % (zmin, dz - 1, zmax)
            return self

    def mesh_tally(self, **kwargs):
        """ ``mesh_tally`` is a tally finding the mesh in many voxels.  Pass
            keywords ``xmin``, ``xmax``, ``ymin``, ``ymax``, ``zmin``, ``zmax``,
            and list ``ijk`` or ``i``, ``j``, and ``k``, which are the number of
            voxels in the ``x``, ``y``, and ``z`` directions, respectively
        """
        self.card = 4
        self.mesh = True
        #if not self.energies:
        #    self.process_energy(**kwargs)
        origin = [0, 0, 0]
        if 'geom' not in kwargs:
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
        elif kwargs['geom'] == 'cyl':
            return self

    def add_multiplier(self, **kwargs):
        """ ``add_multiplier`` adds the multiplier defined by ``mt`` in keywords
            on material from keyword ``mat``.  You can also add a constant ``C``
            or leave that to default ``1``.
        """
        self.multiplier = True
        if "mat" in kwargs:
            self.mat = kwargs["mat"]
        if "mt" in kwargs:
            self.mt = kwargs["mt"]
        if "C" in kwargs:
            self.C = kwargs["C"]
        else:
            self.C = 1
        self.multiplier_string = "(%d %d %d) T" % (self.C, self.mat, self.mt)
        return self

    def time_tally(self, ts=None, t_end=None, n_t=None):
        self.time = True
        self.time_string = ""
        if ts is not None:
            for t in ts:
                self.time_string += " %e" % t
        else:
            t = 0.
            while t <= t_end:
                self.time_string += " %e" % t
                t+= t_end / float(n_t)
        return self

    def current_tally(self, **kwargs):
        """ ``current_tally`` is a tally calculating the current through a
            surface. Pass keywords ``energy``, ``surfaces``, and ``particle``
        """
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
        """ ``fission_tally`` is a tally calculating the fissions in a cell.
            Pass keyword ``cell``.
        """
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
        """ ``process_energy`` prints the energies in keyword ``energy`` into
            MCNP notation
        """
        if "energy" not in kwargs:
            if "all_energies" in kwargs:
                self.energy_string = ''
            else:
                self.energy_string = '1e-8 99i 20'
        else:
            self.energy_string = '%e 99i %e' % (np.min(kwargs["energy"]),
                                                np.max(kwargs["energy"]))
