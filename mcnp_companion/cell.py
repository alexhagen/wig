import matl as mcnpm

from pyb import pyb

class cell:
    def refresh(self):
        self.b_cmds = []
        self.b_kwargs = []

    def __init__(self, geo=None, matl=None, comment=None, show=True):
        self.show = show
        if comment is None:
            self.comment = "c --- %s" % (geo.id)
        else:
            self.comment = "c --- %s" % (comment)
        self.matl = matl
        self.geo = geo
        self.id = geo.id
        if show:
            if len(geo.b_cmds) == 0:
                self.b_cmds = [geo.blender_cmd]
                self.b_kwargs = [geo.blender_cmd_args]
            else:
                self.b_cmds = geo.b_cmds
                self.b_kwargs = geo.b_kwargs
            if matl.color is not None:
                self.b_cmds.extend([pyb.pyb.flat, pyb.pyb.set_matl])
                self.b_kwargs.extend([{"name": matl.id, "color": matl.color,
                                       "alpha": matl.alpha}, {"matl": matl.id,
                                       "obj": self.id}])

        self.cell_num = 0

    @staticmethod
    def air():
        """ ``air`` is the common material for the universe.

        ``air`` is a static method that returns the PNNL compendium defined
        air material for use as universe materials, or others.  It should be
        decided whether to use this class or the materials class as a
        repository for materials.

        .. todo:: use this or materials class for repo for pnnl defined
            materials?

        :returns: ``mcnp_companion.materials.air``
        """
        return mcnpm.matl(rho=0.001205, atom_perc=[('H-1', 0.000151),
                                                   ('N-14', 0.784437),
                                                   ('O-16', 0.210750),
                                                   ('Ar', 0.004671)], id='air')

    def universe(self, scene, matl=air):
        # get all the geometry added to the scene
        # then, iterate through and subtract all the geometry that isnt an
        # inner wall
        for current_geo in geos:
            if not current_geo.inner_wall:
                pg -= current_geo
        self.geo = pg
        self.id = pg.id
        self.matl = matl
