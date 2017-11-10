import textwrap
from pyg import threed
import numpy as np
from colour import Color
from transforms3d import euler, axangles
from pyb import pyb
import cell as mcnpce
import psgv.psgv as psgv


class geo:
    """ a ``wig.geo`` instance is a single geometric primative for creation of
        the geometry block for MCNP.  Where possible, I've used macrobodies
        instead of surfaces; this decision may be problematic for purists,
        but surfaces are so convoluted to use.
    """
    def __init__(self):
        self.bstring = ''
        self.b_cmds = []
        self.b_kwargs = []
        self.deleted = {}

    def boolean(self, right, operation):
        """ ``wig.geo`` implements some of the boolean geometry used by MCNP.
            The operators usable are:

            - ``+`` - implements a geometric boolean union operator between the two objects
            - ``-`` - implements a geometric boolean difference operator between the two objects
            - ``|`` - implements a geometric boolean union operator between the two objects
            - ``%`` - implements a geometric boolean intersection operator between the two objects

            For example, the following creates a cube on a stick

            .. code-block:: python
                :linenos:

                cube = wig.geo().rpp(x=[0., 5.], y=[0., 5.], z=[0., 5.], id='1')
                stick = wig.geo().rcc(c=(2.5, 2.5, -5.), r=1., lz=5., id='2')
                cube_on_a_stick = cube + stick
                cube_on_a_stick_cell = cube_on_a_stick.cell(some_material)

            .. todo:: Implement more boolean operators
        """
        pass

    def __sub__(self, right):
        if right is None:
            return pseudogeo(self)
        if self.__class__.__name__ is 'geo':
            # convert the right argument to a pseudogeo
            left = pseudogeo(self)
        if right.__class__.__name__ is 'geo':
            # convert the right argument to a pseudogeo
            right = pseudogeo(right)
        self.b_cmds.extend(right.b_cmds)
        self.b_kwargs.extend(right.b_kwargs)
        self.b_cmds.extend([pyb.pyb.subtract])
        self.b_kwargs.extend([{"left": left.id, "right": right.id}])
        self.deleted[right.id] = [right.b_cmds, right.b_kwargs]
        return left - right

    def __add__(self, right):
        if right is None:
            return pseudogeo(self)
        if self.__class__.__name__ is 'geo':
            # convert the right argument to a pseudogeo
            left = pseudogeo(self)
        if right.__class__.__name__ is 'geo':
            # convert the right argument to a pseudogeo
            right = pseudogeo(right)
        self.b_cmds.extend(right.b_cmds)
        self.b_kwargs.extend(right.b_kwargs)
        self.b_cmds.extend([pyb.pyb.union])
        self.b_kwargs.extend([{"left": left.id, "right": right.id}])
        return left + right

    def __mod__(self, right):
        if right is None:
            return pseudogeo(self)
        if self.__class__.__name__ is 'geo':
            # convert the right argument to a pseudogeo
            left = pseudogeo(self)
        if right.__class__.__name__ is 'geo':
            # convert the right argument to a pseudogeo
            right = pseudogeo(right)
        self.b_cmds.extend(right.b_cmds)
        self.b_kwargs.extend(right.b_kwargs)
        self.b_cmds.extend([pyb.pyb.intersect])
        self.b_kwargs.extend([{"left": left.id, "right": right.id}])
        return left % right

    def __or__(self, right):
        if right is None:
            return pseudogeo(self)
        if self.__class__.__name__ is 'geo':
            # convert the right argument to a pseudogeo
            left = pseudogeo(self)
        if right.__class__.__name__ is 'geo':
            # convert the right argument to a pseudogeo
            right = pseudogeo(right)
        self.b_cmds.extend([right.b_cmds])
        self.b_kwargs.extend(right.b_kwargs)
        self.b_cmds.extend([pyb.pyb.union])
        self.b_kwargs.extend([{"left": left.id, "right": right.id}])
        return left | right

    def rpp(self, c=None, l=None, x=None, y=None, z=None, id=None):
        """ ``rpp`` is the same as the MCNP macrobody, a right parallelpiped.

            ``rpp`` has two ways to define it:

            - center (``c``) and length (``l``)
            - :math:`x` extents (``x``), :math:`y` extents (``y``) and :math:`z` extents (``z``)

            :param tuple c: the center of the right parallelpiped
            :param tuple l: the length of each side, centered at ``c``
            :param list x: the :math:`x` extents of the right parallelpiped,
                always with the lowest number first.
            :param list y: the :math:`y` extents of the right parallelpiped,
                always with the lowest number first.
            :param list z: the :math:`z` extents of the right parallelpiped,
                always with the lowest number first.
            :param str id: an identifying string with no spaces
        """
        self.sense = -1
        self.id = id
        self.geo_num = 0
        self.comment = "c --- %s" % (self.id)
        if x is None:
            x1 = c[0] - abs(l[0] / 2.0)
            x2 = c[0] + abs(l[0] / 2.0)
        else:
            c = [0., 0., 0.]
            l = [0., 0., 0.]
            x1 = x[0]
            x2 = x[1]
            c[0] = (x[1] - x[0]) / 2.0 + x[0]
            l[0] = x[1] - x[0]
        if y is None:
            y1 = c[1] - abs(l[1] / 2.0)
            y2 = c[1] + abs(l[1] / 2.0)
        else:
            y1 = y[0]
            y2 = y[1]
            c[1] = (y[1] - y[0]) / 2.0 + y[0]
            l[1] = y[1] - y[0]
        if z is None:
            z1 = c[2] - abs(l[2] / 2.0)
            z2 = c[2] + abs(l[2] / 2.0)
        else:
            z1 = z[0]
            z2 = z[1]
            c[2] = (z[1] - z[0]) / 2.0 + z[0]
            l[2] = z[1] - z[0]
        self.string = "rpp %6.4f %6.4f %6.4f %6.4f %6.4f %6.4f" % \
            (x1, x2, y1, y2, z1, z2)

        # add an r parameter to we can use this for sizing our camera
        self.r = max([x2 - x1, y2 - y1, z2 - z1])
        self.blender_cmd = pyb.pyb.rpp
        self.blender_cmd_args = {"c": c, "l": l, "name": id}
        self.faces = [1, 2, 3, 4, 5, 6]
        return self

    def box(self, v=None, a1=None, a2=None, a3=None, id=None):
        """ ``box`` is similar to ``rpp``, but is not oriented to the cartesian
            axes.  Instead, you must define three axes, which are orthagonal to
            each other, as well as the corner (``v``).

            :param tuple v: The corner of the ``box``
            :param tuple a1: the vector defining one edge emanating from ``v``
            :param tuple a2: the vector defining one edge emanating from ``v``
            :param tuple a3: the vector defining one edge emanating from ``v``
            :param str id: an identifying string with no spaces

            .. todo:: calculate the ``a3`` from ``a1`` and ``a2``, if given

            .. todo:: calculate the box from three points
        """
        self.sense = -1
        self.id = id
        self.geo_num = 0
        self.comment = "c --- %s" % (self.id)
        if a3 is None:
            a3 = np.cross(a1, a2)
        self.string = ("box %6.4f %6.4f %6.4f  %6.4f %6.4f %6.4f  " +
                       "%6.4f %6.4f %6.4f  %6.4f %6.4f %6.4f") % \
                       (v[0], v[1], v[2], a1[0], a1[1], a1[2],
                        a2[0], a2[1], a2[2], a3[0], a3[1], a3[2])
        self.faces = [1, 2, 3, 4, 5, 6]
        c = np.array(v) + np.array(a1) / 2. + np.array(a2) / 2. + np.array(a3) / 2.
        l = np.array(a1) + np.array(a2) + np.array(a3)
        v = np.array(v)
        a1 = np.array(a1)
        a2 = np.array(a2)
        a3 = np.array(a3)
        if np.abs(np.dot(a1, a2)) > 1.0E-5:
            raise ValueError("Vector a1 and a2 are not orthogonal,  their dot product is %f" % np.dot(a1, a2))
        if np.abs(np.dot(a2, a3)) > 1.0E-5:
            raise ValueError("Vector a2 and a3 are not orthogonal,  their dot product is %f" % np.dot(a2, a3))
        if np.abs(np.dot(a1, a3)) > 1.0E-5:
            raise ValueError("Vector a1 and a3 are not orthogonal,  their dot product is %f" % np.dot(a1, a3))
        verts = [tuple(v), tuple(v + a2), tuple(v + a3), tuple(v + a2 + a3),
                 tuple(v + a1), tuple(v + a1 + a2), tuple(v + a1 + a3),
                 tuple(v + a1 + a2 + a3)]
        self.blender_cmd = pyb.pyb.rpp
        self.blender_cmd_args = {"name": id, "verts": verts}
        return self

    def sph(self, c=None, r=None, id=None):
        """ ``sph`` defines a sphere with radius ``r`` at ``c``

            :param tuple c: the center of the sphere
            :param float r: the radius of the sphere
            :param str id: an identifying string with no spaces
        """
        self.sense = -1
        self.id = id
        self.geo_num = 0
        self.comment = "c --- %s" % (self.id)
        self.string = "sph %6.4f %6.4f %6.4f %6.4f" % \
            (c[0], c[1], c[2], r)
        self.faces = [1]
        self.r = r
        self.blender_cmd = pyb.pyb.sph
        self.blender_cmd_args = {"c": c, "r": r, "name": id}
        return self

    def rcc(self, c=None, r=None, id=None, lx=None, ly=None, lz=None):
        """ ``rcc`` defines a right circular cylinder.  The geometry can be
            specified by defining the **center of the base** ``c``, radius
            ``r``, and one of ``lx``, ``ly``, or ``lz`` which is the height in
            one of those ordinal directions.

            :param tuple c: center of the base of the cylinder
            :param float r: radius of the circular base
            :param float lx, ly, lz: height in one of the ordinal directions
            :param str id: an identifying string with no spaces

            .. todo:: allow a vector ``l`` to define slanted cylinders
        """
        self.sense = -1
        h = [0, 0, 0]
        if lx is not None:
            h[0] = lx
        if ly is not None:
            h[1] = ly
        if lz is not None:
            h[2] = lz
        self.id = id
        self.geo_num = 0
        self.comment = "c --- %s" % (self.id)
        self.string = "rcc %6.4f %6.4f %6.4f %6.4f %6.4f %6.4f %6.4f" % \
            (c[0], c[1], c[2], h[0], h[1], h[2], r)
        self.surfaces = [1, 2, 3]
        direction = h.index(max(h))
        self.blender_cmd = pyb.pyb.rcc
        self.blender_cmd_args = {"c": c, "r": r, "h": max(h), "name": id,
                                 "direction": direction}
        return self

    def gq(self, A=None, B=None, C=None, D=None, E=None, F=None, G=None,
           H=None, J=None, K=None, coeffs=None, id='gq'):
        r""" `gq`` creates a generalized quadratic surface defined by the
            equation

            .. warning :: This is not implemented as of yet. Just a placeholder.

        .. math::

            Ax^{2}+By^{2}+Cz^{2}+Dxy+Eyz\\+Fzx+Gx+Hy+Jz+K=0

        and takes inputs of either :math:`A`, :math:`B`, :math:`C`, :math:`D`,
        :math:`E`, :math:`F`, :math:`G`, :math:`H`, :math:`J`, :math:`K`, or an
        array ``coeffs`` which has the coefficients (all 10 of them) defined
        in alphabetical order.

        :param float A: the coefficient :math:`A`
        :param float B: the coefficient :math:`B`
        :param float C: the coefficient :math:`C`
        :param float D: the coefficient :math:`D`
        :param float E: the coefficient :math:`E`
        :param float F: the coefficient :math:`F`
        :param float G: the coefficient :math:`G`
        :param float H: the coefficient :math:`H`
        :param float J: the coefficient :math:`J`
        :param float K: the coefficient :math:`K`
        :param list coeffs: a ``(10,)`` or ``(1,10)`` size array containing the
            coefficients :math:`A` through :math:`K`, respectively
        :returns: the generalized quadratic surface object

        .. todo:: Implement the gq surface
        """
        self.sense = -1
        self.id = id
        self.geo_num = 0
        self.comment = "c --- %s" % (self.id)
        self.string = "gq %10.5e %10.5e %10.5e %10.5e %10.5e %10.5e %10.5e %10.5e %10.5e %10.5e" % \
            (A, B, C, D, E, F, G, H, J, K)
        self.surfaces = None
        direction = None
        self.blender_cmd = pyb.pyb.gq
        self.blender_cmd_args = {"A": A, "B": B, "C": C, "D": D, "E": E,
                                 "F": F, "G": G, "H": H, "J": J, "K": K}
        return self

    def cone(self, c=None, dir='+z', h=None, r=None, r1=0.0, r2=0.0,
             lx=0.0, ly=0.0, lz=0.0, id=0.0):
        """ ``cone`` makes a truncated cone. It allows for specifications of the
            cone in two ways:

            - base center ``c``, radii ``r1`` and ``r2``, height ``h`` in direction ``dir``
            - base center ``c``, radii ``r1`` and ``r2``, height ``lx``, ``ly``, or ``lz`` in the implied direction

            :param tuple c: the base center of the cone
            :param str dir: one of ``+x``, ``-x``, ``+y``, ``-y``, ``+z``, ``-z``
            :param float h: height of the cone
            :param float r1: base radius
            :param float r2: top radius
            :param list r: size two list of base and top radius, respectively
            :param float lx, ly, lz: height in respective direction
            :param str id: an identifying string with no spaces
        """
        self.sense = -1
        self.id = id
        self.geo_num = 0
        _h = [0, 0, 0]
        if 'z' in dir:
            i = 2
        elif 'x' in dir:
            i = 0
        elif 'y' in dir:
            i = 1
        if '+' in dir:
            _h[i] = h
        elif '-' in dir:
            _h[2] = -h
        if h is None:
            _h = [lx, ly, lz]
        if r is None:
            r = [r1, r2]
        self.comment = 'c --- %s' % (self.id)
        self.string = "trc %6.4f %6.4f %6.4f %6.4f %6.4f %6.4f %6.4f %6.4f" % \
            (c[0], c[1], c[2], _h[0], _h[1], _h[2], r[0], r[1])
        self.surfaces = [1, 2, 3]
        blender_dir = dir.replace('+', '').replace('-', '')
        self.blender_cmd = pyb.pyb.cone
        self.blender_cmd_args = {"c": c, "r1": r[0], "r2": r[1],
                                 "h": np.max(h), "direction": blender_dir,
                                 "name": id}
        return self

    def cell(self, matl):
        """ ``geo.cell(matl)`` returns a cell of this geometry with
            material ``matl``

            :param wig.matl.matl matl: The material to make this cell
            :returns: ``mcnpce.cell`` object
        """
        return mcnpce.cell(self, matl)

class pseudogeo:
    def __init__(self, geo):
        if geo.__class__.__name__ == 'cell':
            geo = geo.geo
        if geo.__class__.__name__ == 'pseudogeo':
            geo = geo.geo
        self.id = geo.id
        self.geo = geo
        self.nums = [(geo.geo_num, geo.sense)]
        self.b_cmds = []
        self.b_kwargs = []
        self.deleted = {}
        if len(geo.b_cmds) == 0:
            self.b_cmds = [geo.blender_cmd]
            self.b_kwargs = [geo.blender_cmd_args]
        else:
            self.b_cmds = geo.b_cmds
            self.b_kwargs = geo.b_kwargs

    def __or__(self, right):
        if right is None:
            return pseudogeo(self)
        if self.__class__.__name__ is 'geo':
            # convert the right argument to a pseudogeo
            left = pseudogeo(self)
        else:
            left = self
        if right.__class__.__name__ is 'geo':
            # convert the right argument to a pseudogeo
            right = pseudogeo(right)
        self.b_cmds.extend([right.b_cmds])
        self.b_kwargs.extend(right.b_kwargs)
        self.b_cmds.extend([pyb.pyb.union])
        self.b_kwargs.extend([{"left": left.id, "right": right.id}])
        return self

    def __mod__(self, right):
        if right is None:
            return self
        if right.__class__.__name__ is 'geo':
            right = pseudogeo(right)
        if type(right) is type(list()):
            for _right in right:
                __right = pseudogeo(_right)
                self.nums.extend([(__right.geo.geo_num, -__right.geo.sense)])
                self.id += "_inter_%s" % __right.geo.id
                self.b_cmds.extend(_right.b_cmds)
                self.b_kwargs.extend([_right.b_kwargs])
                self.b_cmds.extend([pyb.pyb.intersect])
                self.b_kwargs.extend([{"left": self.id, "right": _right.id}])
        else:
            self.nums.extend([(right.geo.geo_num, -right.geo.sense)])
            self.b_cmds.extend(right.b_cmds)
            self.b_kwargs.extend(right.b_kwargs)
            self.b_cmds.extend([pyb.pyb.intersect])
            self.b_kwargs.extend([{"left": self.id, "right": right.id}])
            self.id += "_inter_%s" % right.geo.id
        return self

    def __sub__(self, right):
        if right is None:
            return self
        if right.__class__.__name__ is 'geo':
            right = pseudogeo(right)
        if type(right) is type(list()):
            for _right in right:
                __right = pseudogeo(_right)
                self.nums.extend([(__right.geo.geo_num, -__right.geo.sense)])
                self.id += "_less_%s" % __right.geo.id
                self.b_cmds.extend(_right.b_cmds)
                self.b_kwargs.extend([_right.b_kwargs])
                self.b_cmds.extend([pyb.pyb.subtract])
                self.b_kwargs.extend([{"left": self.id, "right": _right.id}])
                self.deleted[_right.id] = [_right.b_cmds, _right.b_kwargs]
        else:
            self.nums.extend([(right.geo.geo_num, -right.geo.sense)])
            self.b_cmds.extend(right.b_cmds)
            self.b_kwargs.extend(right.b_kwargs)
            self.b_cmds.extend([pyb.pyb.subtract])
            self.b_kwargs.extend([{"left": self.id, "right": right.id}])
            self.deleted[right.id] = [right.b_cmds, right.b_kwargs]
            self.id += "_less_%s" % right.geo.id
        return self

    def __add__(self, right):
        if right is None:
            return self
        if right.__class__.__name__ is 'geo':
            right = pseudogeo(right)
        self.nums.extend([(right.geo.geo_num, right.geo.sense)])
        self.b_cmds.extend(right.b_cmds)
        self.b_kwargs.extend(right.b_kwargs)
        self.b_cmds.extend([pyb.pyb.union])
        self.b_kwargs.extend([{"left": self.id, "right": right.id}])
        self.id += "_plus_%s" % right.geo.id
        return self


class group:
    def __init__(self, content, id=None):
        self.suffix = ""
        self.string = ""
        if content.__class__.__name__ is 'geo':
            content = pseudogeo(content)
        if type(content) is type(list()):
            _content = content[0]
            for geo in content[1:]:
                _content = _content + geo
            content = _content
        self.content = content
        self.b_cmds = content.b_cmds
        self.b_kwargs = content.b_kwargs
        if id is None:
            self.id = "%s" % self.content.id
            self.manual_id = False
        else:
            self.id = id
            self.manual_id = True
        self.string = ""
        for num in self.content.nums:
            self.string += "%d " % (num[0] * num[1])
        self.already_unioned = False

    def __or__(self, right):
        if right.__class__.__name__ is not 'group':
            right = group(right)
        if not self.already_unioned:
            self.string = "("
            for num in self.content.nums:
                self.string += "%d " % (num[0] * num[1])
            self.string += "):("
        else:
            self.string += ":("
        for num in right.content.nums:
            self.string += "%d " % (num[0] * num[1])
        self.string += ")"
        if not self.manual_id:
            self.id += "_u_%s" % (right.id)
        left = self
        self.b_cmds.extend([right.b_cmds])
        self.b_kwargs.extend(right.b_kwargs)
        self.b_cmds.extend([pyb.pyb.union])
        self.b_kwargs.extend([{"left": left.id, "right": right.id}])
        self.id += "_u_%s" % right.content.geo.id
        return self
