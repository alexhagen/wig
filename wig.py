import numpy as np
import textwrap
from runner import runner
from pyg import threed
from mcnp_string import mstring
from renderer import renderer
from os.path import expanduser
import geo as mcnpg
import matl as mcnpm
import os
from pyb import pyb

class wig:
    """ The ``wig`` object is the base object for an MCNP setup.

    The ``wig`` object is basically the scene in which we create our MCNP
    geometry, cells, materials, physics, tallies, and other data.  I usually
    just call it ``scene`` and use it from there.

    :param str comment: The comment that will be placed BELOW the first comment
        line of the MCNP deck.
    :param str filename: The filename (duh) of the input deck. '.inp' will be
        automatically appended.  The full path to this file will be the first
        line of the input file (i.e., the full path will be the first comment
        line of the deck)
    :param str flavor: '6' for ``mcnp6``, '5' for ``mcnp5``, 'x' for ``mcnpx``,
        or 'polimi' for ``mcnpx-polimi``.  Make sure you alias the binaries to
        those commands or the runner wont work.
    :param bool render: defines whether to render the scene using
        ``blender`` before running it
    :param list particles: a list of ``'n', 'p', ...`` for the particles we
        should care about
    :return: the ``wig`` object.
    """
    def __init__(self, comment, filename, flavor='6', render=True,
                 particles=['n']):
        self.original_directory = os.getcwd()
        self.set_filename(filename)
        self.set_comment(comment)
        self._particles = particles
        if render:
            self.renderer = renderer(filename)
        else:
            self.renderer = None
        self._render = render
        if flavor is '6':
            self.command = 'mcnp6'
        elif flavor is '5':
            self.command = 'mcnp5'
        elif flavor is 'x':
            self.command = 'mcnpx'
        elif flavor is 'polimi':
            self.command = 'polimi'
        elif flavor is 'mcuned':
            self.command = 'mcuned'
        elif flavor is 'mcuned_polimi':
            self.command = 'mcuned_polimi'
        # initialize all of our blocks
        self.intro_block = ''
        self.geo_block = ''
        self.cell_block = ''
        self.matl_block = ''
        self.phys_block = ''
        self.tally_block = ''
        self.data_block = ''
        self.sdef_num = 1
        self.bscene = pyb.pyb()
        self.bscene.sun()
        # now write the intro file
        self.intro_block += self.comment
        self.geo_num = 10
        self.geo_comments = []
        self.matl_num = 1
        self.matl_comments = []
        self.deleted = {}

    # --------------------------- File Methods ---------------------------------

    def set_filename(self, filename):
        """ ``set_filename`` sets the base of the filenames that will be created

            :param str filename: the base of the filename
        """
        path = expanduser("~") + '/mcnp/active/'
        os.chdir(path)
        self.filename = filename

    def set_comment(self, comment):
        """ ``set_comment`` writes the first line of the ``mcnp`` file, which is
            a comment describing the file. Be descriptive but not too long.

            :param str comment: the first line of the ``mcnp`` file - limit is
                80 characters.  ``wig`` manually strips newlines, so feel free
                to make this a triple quoted (``'''``) string with as many
                returns as you like.
        """
        self.comment = ' '.join(comment.split())

# --------------------------------- Block Methods ------------------------------

    def geo(self, geos=None):
        """ ``geo`` adds all defined ``wig.geo`` objects to an input deck

            :param list geos: the ``wig.geo`` objects to be added to the input
                deck. Make sure this includes a universe
        """
        self.add_geo(geos=geos)

    def add_geo(self, geos=None):
        self.geos = geos
        for geo in geos:
            if geo is not None:
                if geo.comment not in self.geo_comments:
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
                    if 'universe' in geo.id:
                        self.universe = geo
                    # increment geo num
                    self.geo_num += 10
                    self.geo_comments.extend([geo.comment])

    def redefine(self, name=None):
        if name in self.deleted:
            for plot_cmd, plot_kwargs in zip(self.deleted[name].b_cmds, self.deleted[name].b_kwargs):
                if isinstance(plot_cmd, list):
                    plot_cmd = plot_cmd[0]
                    if debug_blender:
                        print plot_cmd
                plot_cmd(self.bscene, **plot_kwargs)
                if debug_blender:
                    print plot_cmd
                    print plot_kwargs

    def cell(self, cells=None, auto_universe=True, universe_matl=None,
             debug_blender=False):
        """ ``cell`` adds all the ``wig.cell`` in a list to an input deck.

            :param list cells: the list of ``wig.cell`` to be added to the
                input deck.  If you don't have a cell named ``'universe'``, this
                method will make one for you, but you might night like it.
            :param bool debug_blender: whether or not you want to see the
                commands that will be sent to ``blender``, default ``False``.
        """
        # initialize a counter
        self.cell_num = 10
        self.cells = cells
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
                if cell.show and self._render:
                    if debug_blender:
                        print cell.id
                    for plot_cmd, plot_kwargs in zip(cell.b_cmds, cell.b_kwargs):
                        if isinstance(plot_cmd, list):
                            plot_cmd = plot_cmd[0]
                            if debug_blender:
                                print plot_cmd
                        self.deleted.update(cell.geo.deleted)
                        #print self.deleted
                        plot_cmd(self.bscene, **plot_kwargs)
                        if debug_blender:
                            print plot_cmd
                            print plot_kwargs
                # increment the cell num
                self.cell_block += " imp:"
                for particle in self._particles:
                    self.cell_block += "%s," % particle
                self.cell_block = self.cell_block[:-1]
                self.cell_block += "=1\n"
                self.cell_num += 10
        if auto_universe:
            self.make_universe(matl=universe_matl)
        # add void
        self.cell_block += "%s\n" % ('c --- void')
        self.cell_block += "%d     " % (99)
        # now print the material number
        self.cell_block += "%d " % (0)
        # now print the density
        self.cell_block += "                 "
        self.cell_block += "%d " % (-self.universe.sense * self.universe.geo_num)
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
        # increment the cell num
        self.cell_block += " imp:"
        for particle in self._particles:
            self.cell_block += "%s," % particle
        self.cell_block = self.cell_block[:-1]
        self.cell_block += "=0\n"

    def make_universe(self, geo=None, matl=None):
        if geo is None:
            geo = self.universe
        if matl is None:
            matl = mcnpm.air()
        self.cell_block += "%d     " % (self.cell_num)
        # now print the material number
        self.cell_block += "%d " % (matl.matl_num)
        # now print the density
        self.cell_block += "%15.10E " % (-matl.rho)
        # now print the universe surface
        self.cell_block += "%d" % (geo.sense * geo.geo_num)
        for cell in self.cells:
            self.cell_block += " #%d" % (cell.cell_num)
        # increment the cell num
        self.cell_block += " imp:"
        for particle in self._particles:
            self.cell_block += "%s," % particle
        self.cell_block = self.cell_block[:-1]
        self.cell_block += "=1\n"
        self.cell_num += 10



    def matl(self, matls=None):
        """ ``matl`` adds all the ``wig.matl`` to the input deck

            :param list matls: the materials to add to the input deck
        """
        self.add_matl(matls=matls)

    def add_matl(self, matls=None):
        for matl in matls:
            if matl.comment not in self.matl_comments:
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
                self.matl_comments.extend([matl.comment])

    def phys(self, phys=None):
        """ ``phys`` adds all ``wig.phys`` blocks to the model

            :param wig.phys phys: the ``wig.phys`` block to be added to the
                model.
        """
        # print the comment
        self.phys_block += "%s\n" % (phys.comment)
        # print the physics string
        self.phys_block += "%s\n" % (phys.string.format(out_src_fname=self.filename + "_source.out"))
        # remove the last character (the new line)
        self.phys_block = self.phys_block[:-1]

    def tally(self, tallies=None):
        """ ``tally`` adds all ``wig.tally`` b'ocks to the model

            :param list tallies: the ``wig.tally`` blocks to be added to the
                model.
        """
        # initialize a counter
        self.tally_nums = {"1": 1, "4": 1, "7": 1, "6": 1}
        self.tally_block = "prdmp j -15 1 4\n"
        # resort the tallies
        new_tallies = []
        new_meshtallies = []
        new_tmeshtallies = []
        for tally in tallies:
            if tally.mesh:
                new_meshtallies.extend([tally])
            elif tally.tmesh:
                new_tmeshtallies.extend([tally])
            else:
                new_tallies.extend([tally])
        for tally in new_tallies:
            self.tally_block += "f%d%d%s\n" % \
                (self.tally_nums[str(tally.card)], tally.card,
                 tally.string)
            self.tally_block += "e%d%d %s\n" % \
                (self.tally_nums[str(tally.card)], tally.card,
                 tally.energy_string)
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
        if len(new_tmeshtallies) > 0:
            self.tally_block += "tmesh\n"
        for tally in new_tmeshtallies:
            self.tally_block += "  %s%d%d%s\n" % \
                (tally.tmeshtype, self.tally_nums[str(tally.card)],
                 tally.card, tally.string.format(card=tally.card, number=self.tally_nums[str(tally.card)]))
            # set that number to the geometry object
            tally.num = self.tally_nums[str(tally.card)]
            # increment matl num
            self.tally_nums[str(tally.card)] += 1
        if len(new_tmeshtallies) > 0:
            self.tally_block += "endmd\n"
        for tally in new_meshtallies:
            self.tally_block += "fmesh%d%d%s\n" % \
                (self.tally_nums[str(tally.card)], tally.card,
                 tally.string)
            # set that number to the geometry object
            tally.num = self.tally_nums[str(tally.card)]
            # increment matl num
            self.tally_nums[str(tally.card)] += 1

    def source(self, sources=None):
        """ ``source`` adds the ``wig.source`` object to the model

            :param list sources: the ``wig.source`` blocks (defining sources and
                distributions) to be added to the model.
        """
        for source in sources:
            # print the source definition
            self.data_block += "sdef    "
            # print the source string
            self.data_block += "%s\n" % (source.string)

            if source.blender_cmd is not None and source.show and self._render:
                for command, _kwargs in zip(source.blender_cmd, source.blender_cmd_args):
                    command(self.bscene, **_kwargs)

    # --------------------------- Running methods ------------------------------

    def run(self, remote='local', sys='linux', blocking=False, clean=False,
            **kwargs):
        """ ``run`` (of course) runs the deck.

            ``run`` first writes the input deck, including rendering with
            whatever additional keyword args you pass, and then opens an
            instance of a ``wig.runner`` , and passes commands to it.

            :param str remote: The ip address of the remote system you want to
                run this on, or ``'local'`` if on this system.  The remote
                system must be set for passwordless ssh login and have ``mcnp``
                on path (whatever flavor you're using). Default: ``'local'``
            :param str sys: The type of system that the remote runs on.
                Currently, this is useless, as I've only made it run on linux.
                Default: ``'linux'``
            :param bool blocking: Whether to wait on the deck to finish running
                before continuing or not.  Useful to block if you want to run
                many decks depending on the previous result (optimization), or
                if you only have a certain number of processors. Default:
                ``False``
            :param bool clean: Whether to clean up the running files in the
                ``~/mcnp/active`` directory or not. Keep the files if storage
                isn't a concern and you're unsure if your deck will run
                correctly. Default: ``False``
            :param dict kwargs: ``run`` passes the rest of the commands to
                ``write``
        """
        if clean:
            os.system('rm ' + expanduser("~") + '/mcnp/active/' +
                      self.filename + '*')
        self.write(**kwargs)
        self._runner = runner(self.filename, self.command, remote, sys,
                              blocking=blocking, clean=clean,
                              **kwargs)

    def write(self, **kwargs):
        """ ``write`` writes the input deck and renders the input deck

            :param dict kwargs: keyword arguments to pass to ``render``
        """
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
        self.render(**kwargs)

    def render(self, filename_suffix='', render_target=None, camera_location=None,
               render=True, **kwargs):
        """ ``render`` passes the input deck to ``pyb``, a simplified renderer
            that uses ``blender`` as the backend

            :param str filename_suffix: suffix to put after the filename when we
                save the rendering. Default: ``''``
            :param tuple render_target: a point for the camera to look at when
                rendering. Default: ``(0, 0, 0)``
            :param tuple camera_location: a point from which the camera looks.
                Default: based on the size of the scene, isotropic placement.
            :param bool render: Whether or not to actually run the render. This
                method will always save a blender file, regardless of if we do a
                full render. Default: ``True``
            :param dict kwargs: Other arguments to pass to ``pyb.render``.
                See ``pyb`` for options, such as ``samples`` or ``res``.
        """
        if render_target is not None:
            self.bscene.look_at(target=render_target)
        if camera_location is None:
            camera_location = (1.5 * self.universe.r, 1.5 * self.universe.r,
                               self.universe.r)
        self.bscene.run(camera_location=camera_location,
                        filename=self.filename + filename_suffix + '_setup.png', render=render,
                        **kwargs)
        self.proj_matrix = self.bscene.proj_matrix
        if render:
            self.bscene.show()

    # ---------------------------- Refresh Methods -----------------------------

    def refresh_data(self):
        """ ``refresh_data`` resets the data block to nothing. Useful if you're
            reusing a model and want to reset sources or materials or something.
        """
        self.data_block = ''

    def refresh_geo(self):
        """ ``refresh_geo`` resets the geometry block to nothing. Useful if
            you're changing geometry, although this probably shouldn't be used
            without also refreshing the cells. But I don't know you, live your
            life.
        """
        for geo in self.geos:
            geo.geo_num = 0
        self.geo_comments = []
        self.geo_num = 10
        self.geo_block = ''

    def refresh_cell(self):
        """ ``refresh_cell`` resets the cell block to nothing.  Again, useful
            for changing up cell definitions or materials.
        """
        for cell in self.cells:
            cell.cell_num = 0
        self.cell_block = ''
        self.bscene = pyb.pyb()
        self.bscene.sun()

    def refresh_phys(self):
        """ ``refresh_phys`` resets the physics block to nothing.  This is a
            subset of the ``refresh_data`` method, so use whichever one is more
            useful.
        """
        self.phys_block = ''

    def refresh_tally(self):
        """ ``refresh_tally`` resets the tally block to nothing.  This is
            probably not useful, unless you're changing other things, too. If
            the model is still the name, just add the all the tallies in one
            input file and run it, it's faster that way.
        """
        self.tally_block = ''

    def refresh_matl(self):
        """ ``refresh_matl`` resets the materials block to nothing. Super useful
            if you're messing around with shielding, or reactions.
        """
        self.matl_block = ''

    # ---------------------------- Convenience Methods -------------------------

    def go_home(self):
        """ ``wig`` runs in the directory ``~/mcnp/active``. ``go_home`` goes to
            the directory in which the script started.
        """
        os.chdir(self.original_directory)
