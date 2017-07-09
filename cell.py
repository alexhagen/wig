import matl as mcnpm

from pyb import pyb

class cell:
    """ a ``cell`` is a combination of geometric primitives (single or
        combined using ``geo`` operators) and the material applied to that
        section of geometry.  The easiest way to get a ``cell`` is to simply
        call ``geo().cell(matl)`` on the geometry object, but for more
        explicit uses, instantiation of this class can be useful.

        :param wig.geo geo: the geometry object, whether singular or combined
        :param wig.matl matl: the material object
        :param str comment: a comment that will be printed beside the cell
        :param bool show: whether or not the object will be shown in the
            rendering
        :param str color: the color for the material in the rendering, in
            hex format ('#RRGGBB')
        :param float alpha: the opacity of the object in the rendering, from
            0.0 to 1.0, Default: ``1.0``
    """
    def __init__(self, geo=None, matl=None, comment=None,
                 color=None, alpha=1.0, show=True):
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
            if matl.color is not None or color is not None:
                self.b_cmds.extend([pyb.pyb.flat, pyb.pyb.set_matl])
                if color is None:
                    self.b_kwargs.extend([{"name": matl.id, "color": matl.color,
                                           "alpha": matl.alpha}, {"matl": matl.id,
                                           "obj": self.id}])
                else:
                    self.b_kwargs.extend([{"name": matl.id, "color": color,
                                           "alpha": alpha}, {"matl": matl.id,
                                           "obj": self.id}])


        self.cell_num = 0

    @staticmethod
    def air():
        """ ``air`` is the common material for the universe.

        ``air`` is a static method that returns the PNNL compendium defined
        air material for use as universe materials, or others.  It should be
        decided whether to use this class or the materials class as a
        repository for materials.

        .. todo:: define an assets system for this.
        """
        return mcnpm.matl(rho=0.001205, atom_perc=[('H-1', 0.000151),
                                                   ('N-14', 0.784437),
                                                   ('O-16', 0.210750),
                                                   ('Ar', 0.004671)], id='air')

    def universe(self, scene, matl=air):
        """ ``universe`` defines a programatically defined universe around all
            your geometry

            .. warning:: this is not currently implemented, just a placeholder.

            .. todo:: implement the universe
        """
        # get all the geometry added to the scene
        # then, iterate through and subtract all the geometry that isnt an
        # inner wall
        for current_geo in geos:
            if not current_geo.inner_wall:
                pg -= current_geo
        self.geo = pg
        self.id = pg.id
        self.matl = matl

    def refresh(self):
        """ ``refresh`` removes all of the blender commands from the cell.
            Useful for if you are changing cells with new geometry or color.
        """
        self.b_cmds = []
        self.b_kwargs = []
