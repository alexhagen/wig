import numpy as np
import textwrap
from runner import runner
from pyg import threed
from mcnp_string import mstring
from renderer import renderer
from os.path import expanduser
import geo as mcnpg
from vapory import *
import os
from skimage.filter import sobel
from scipy.misc import imsave
from pyb import pyb

class mcnp_companion:
    """ The ``mcnp_companion`` object is the base object for an MCNP setup.

    The ``mcnp_companion`` object is basically the scene in which we create our
    MCNP geometry, cells, materials, physics, tallies, and other data.  I
    usually just call it ``scene`` and use it from there.

    :param str comment: The comment that will be placed BELOW the first comment
        line of the MCNP deck.
    :param str filename: The filename (duh) of the input deck. '.inp' will be
        automatically appended.  The full path to this file will be the first
        line of the input file (i.e., the full path will be the first comment
        line of the deck)
    :param str flavor: '6' for ``mcnp6``, '5' for ``mcnp5``, 'x' for ``mcnpx``,
        or 'polimi' for ``mcnpx-polimi``.  Make sure you alias the binaries to
        those commands or the runner wont work.
    :return: the ``mcnp_companion`` object.
    :rtype: ``mcnp_companion``
    """
    def __init__(self, comment, filename, flavor='6', render=False):
        self.set_filename(filename)
        self.set_comment(comment)
        if render:
            self.renderer = renderer(filename)
        else:
            self.renderer = None
        if flavor is '6':
            self.command = 'mcnp6'
        elif flavor is '5':
            self.command = 'mcnp5'
        elif flavor is 'x':
            self.command = 'mcnpx'
        # initialize all of our blocks
        self.intro_block = ''
        self.geo_block = ''
        self.cell_block = ''
        self.matl_block = ''
        self.phys_block = ''
        self.tally_block = ''
        self.data_block = ''
        self.sdef_num = 1
        self.light = [LightSource([0, 100, 500], [1.0, 1.0, 1.0])]
        self.vapory_geos = []
        self.bscene = pyb.pyb()
        self.bscene.sun()
        # now write the intro file
        self.intro_block += self.comment

    def set_filename(self, filename):
        self.filename = expanduser("~") + '/mcnp/active/' + filename

    def set_comment(self, comment):
        self.comment = ' '.join(comment.split())

    def refresh_data(self):
        self.data_block = ''

    def refresh_geo(self):
        self.geo_block = ''
        self.bscene = pyb.pyb()
        self.bscene.sun()

    def refresh_cell(self):
        self.cell_block = ''

    def refresh_phys(self):
        self.phys_block = ''

    def refresh_tally(self):
        self.tally_block = ''

    def refresh_matl(self):
        self.matl_block = ''

    def run(self, remote=False, sys='linux', **kwargs):
        self.write(**kwargs)

        self._runner = runner(self.filename, self.command, remote, sys,
                              renderer=self.renderer)

    def write(self, render_target=None):
        with open(self.filename + '.inp', 'w') as f:
            # wrap fill and print to the file
            intro = textwrap.TextWrapper(initial_indent='c ',
                                         subsequent_indent='c ', width=80)
            f.write(self.filename + "\n")
            f.write(intro.fill(self.intro_block))
            f.write("\n")
            # write the cells block
            f.write("c " + " Cells ".center(78, '-') + "\n")
            f.write(mstring(self.cell_block).flow())
            f.write("\n")
            # write the geometry block
            f.write("c " + " Geometry ".center(78, '-') + "\n")
            f.write(mstring(self.geo_block).flow())
            f.write("\n")
            # write the data block
            f.write("c " + " Data ".center(78, '-') + "\n")
            f.write(mstring(self.data_block).flow())
            f.write("c " + " Physics ".center(78, '-') + "\n")
            f.write(mstring(self.phys_block).flow())
            f.write("c " + " Tallies ".center(78, '-') + "\n")
            f.write(mstring(self.tally_block).flow())
            f.write("c " + " Materials ".center(78, '-') + "\n")
            f.write(mstring(self.matl_block).flow())
        scene = Scene(Camera("location", [300, 300, 300], "look_at", [0, 100, 0], 'rotate', [90, 0, 90]),
                   self.light + [Background("White")] + self.vapory_geos,
                   included=["colors.inc", "textures.inc", 'glass.inc'])
        # im1 = scene.render(width=1980, height=1080, antialiasing=0.001)
        # im2 = scene.render(width=1980, height=1080, antialiasing=0.001,
        #                 quality=0.5)
        # sobelized = np.array([sobel(1.0 * im2[:,:,i]) for i in [0, 1, 2]])
        # outline = np.dstack(3*[255*(sobelized.max(axis=0)==0)])
        # cel_shade = np.minimum(im1, outline)
        # imsave('purple_sphere.png', cel_shade)
        # os.system('eog purple_sphere.png &')
        if render_target is not None:
            self.bscene.look_at(target=render_target)
        self.bscene.run(filename=self.filename + '_setup.png')
        self.bscene.show()

    def geo(self, geos=None):
        # initialize a counter
        self.geo_num = 10
        # create a renderer
        self.plot = threed.pyg3d()
        for geo in geos:
            if geo is not None:
                # print the comment
                self.geo_block += "%s\n" % (geo.comment)
                # print the number
                self.geo_block += "%d    " % (self.geo_num)
                geo.geo_num = self.geo_num # does this pointer work?
                # print the geo string
                self.geo_block += "%s\n" % (geo.string)
                # set that geo number to the geometry object
                geo.num = self.geo_num
                # add the geo object to the plot
                if geo.show:
                    self.plot = geo.plot_cmd(self.plot, **geo.plot_cmd_args)
                    self.vapory_geos.extend([geo.vapory_cmd(*geo.vapory_cmd_args, **geo.vapory_cmd_kwargs)])
                    geo.blender_cmd(self.bscene, **geo.blender_cmd_args)
                # increment geo num
                self.geo_num += 10
        #self.plot.view(45, 235)
        #self.plot.export('some_plot', formats=['pdf'], sizes=['cs'],
        #                 customsize=(6., 6.))
        #self.plot.show()

    def cell(self, cells=None):
        # initialize a counter
        self.cell_num = 10
        for cell in cells:
            if cell is not None:
                # print the comment
                self.cell_block += "%s\n" % (cell.comment)
                # now print the cell number
                self.cell_block += "%d     " % (self.cell_num)
                cell.cell_num = self.cell_num
                # now print the material number
                self.cell_block += "%d " % (cell.matl.matl_num)
                # now print the density
                self.cell_block += "%15.10E " % (-cell.matl.rho)
                # now print the sense
                if cell.geo.__class__.__name__ is 'geo':
                    self.cell_block += "%d" % (cell.geo.sense * cell.geo.geo_num)
                elif cell.geo.__class__.__name__ is 'pseudogeo':
                    for num in cell.geo.nums:
                        self.cell_block += "%d " % (num[0] * num[1])
                    self.cell_block = self.cell_block[:-1]
                elif cell.geo.__class__.__name__ is 'group':
                    self.cell_block += "%s" % (cell.geo.string)
                # increment the cell num
                self.cell_block += " imp:n=1\n"
                self.cell_num += 10
        # add void
        self.cell_block += "%s\n" % ('c --- void')
        self.cell_block += "%d     " % (99)
        # now print the material number
        self.cell_block += "%d " % (0)
        # now print the density
        self.cell_block += "                 "
        # now search for the universe cell
        for cell in cells:
            if cell is not None:
                if 'universe' in cell.geo.id:
                    if cell.geo.__class__.__name__ is 'geo':
                        self.cell_block += "%d " % (abs(cell.geo.geo_num))
                    elif cell.geo.__class__.__name__ is 'pseudogeo':
                        self.cell_block += "%d " % cell.geo.nums[0][0]
                    elif cell.geo.__class__.__name__ is 'group':
                        self.cell_block += "%d " % cell.geo.content.nums[0][0]
        self.cell_block += "imp:n=0\n"



    def matl(self, matls=None):
        # initialize a counter
        self.matl_num = 1
        for matl in matls:
            # print the comment
            self.matl_block += "%s\n" % (matl.comment)
            # print the matl number
            self.matl_block += "m%d   " % (self.matl_num)
            # print the matl string
            self.matl_block += "%s\n" % (matl.string)
            # set that number to the geometry object
            matl.matl_num = self.matl_num
            # increment matl num
            self.matl_num += 1

    def phys(self, phys=None):
        # print the comment
        self.phys_block += "%s\n" % (phys.comment)
        # print the physics string
        self.phys_block += "%s\n" % (phys.string)
        # remove the last character (the new line)
        self.phys_block = self.phys_block[:-1]

    def tally(self, tallies=None):
        # initialize a counter
        self.tally_nums = {"1": 1, "4": 1, "7": 1}
        self.tally_block = "prdmp j -15 1 4\n"
        for tally in tallies:
            if tally is not None:
                # print the tally type card
                if tally.mesh:
                    self.tally_block += "fmesh%d%d%s\n" % \
                        (self.tally_nums[str(tally.card)], tally.card,
                         tally.string)
                else:
                    self.tally_block += "f%d%d%s\n" % \
                        (self.tally_nums[str(tally.card)], tally.card,
                         tally.string)
                # print the tally energy card
                if tally.mesh:
                    pass
                else:
                    self.tally_block += "e%d%d %s\n" % \
                        (self.tally_nums[str(tally.card)], tally.card,
                         tally.energy_string)
                # check for multipliers
                if tally.multiplier:
                    self.tally_block += "fm%d%d %s\n" % \
                        (self.tally_nums[str(tally.card)], tally.card,
                         tally.multiplier_string)
                # print the comment
                self.tally_block += "fc%d%d %s\n" % \
                    (self.tally_nums[str(tally.card)], tally.card, tally.comment)
                # set that number to the geometry object
                tally.num = self.tally_nums[str(tally.card)]
                # increment matl num
                self.tally_nums[str(tally.card)] += 1

    def source(self, sources=None):
        for source in sources:
            # print the source definition
            self.data_block += "sdef    "
            # print the source string
            self.data_block += "%s\n" % (source.string)
            if source.vapory_cmd is not None:
                self.vapory_geos.extend([source.vapory_cmd(*source.vapory_cmd_args, **source.vapory_cmd_kwargs)])
            # print the distributions
            # for dist in source.dists:
            #    # print the distribution definition
            #    self.data_block += "     sp%d    " % (self.sdef_num)
            #    self.data_block += "     %s\n" % (dist.string)
            #    self.sdef_num += 1
