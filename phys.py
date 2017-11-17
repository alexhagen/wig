class phys():
    """ ``phys`` defines all of the options for physics in the MCNP model

        :param list particles: list of particles included, such as ``['p', 'n']``
        :param list sources: Not implemented
        :param float maxE: maximum energy (in :math:`MeV`) to model
        :param float minE: minimum energy (in :math:`MeV`) to model
        :param int nps: number of particles to simulate
        :param int ctme: number of minutes to run the model
        :param bool polimi: whether this is an MCNP-Polimi deck. Do not use
            when not using ``wig.flavor = 'polimi'``.
        :param list polimi_cells: cells in which to transport neutrons/photos
            using MCNP-Polimi
    """
    def __init__(self, particles=None, sources=None, maxE=None, minE=None,
                 nps=None, ctme=None, polimi=False, polimi_cells=[],
                 ipol=[0, 0, 0], rpol=[0, 0, 0]):
        # if we've defined nothing, then we're going to just go ahead and make
        # some default physics
        if ipol is not None:
            self.ipol = ipol
        else:
            self.ipol = None
        if rpol is not None:
            self.rpol = rpol
        else:
            self.rpol = None
        self.comment = "c --- default physics for "
        self.string = "mode "
        if maxE is None:
            maxE = 20.0
        if minE is None:
            minE = 1.0E-8
        self.maxE = maxE
        self.minE = minE
        for particle in particles:
            self.comment += "%s " % (particle)
            self.string += "%s " % (particle)
        self.comment = "%s" % (self.comment[:-1])
        self.string = "%s\n" % (self.string[:-1])
        if 'p' in particles:
            self.string += "phys:p %e 0 0 1 0 0 1\n" % (maxE)
            self.string += "cut:p J %e\n" % (minE)
        if 'n' in particles:
            self.string += "phys:n %e\n" % (maxE)
            self.string += "cut:n j %e\n" % (minE)
        if 'd' in particles:
            self.string += "phys:d %e\n" % (maxE)
            self.string += "cut:d j %e\n" % (minE)
        if 't' in particles:
            self.string += "phys:t %e\n" % (maxE)
            self.string += "cut:t j %e\n" % (minE)
        if 'h' in particles:
            self.string += "phys:h %e\n" % (maxE)
            self.string += "cut:h j %e\n" % (minE)
        if 's' in particles:
            self.string += "phys:s %e\n" % (maxE)
            self.string += "cut:s j %e\n" % (minE)
        if 'a' in particles:
            self.string += "phys:a %e\n" % (maxE)
            self.string += "cut:a j %e\n" % (minE)
        if nps is not None:
            self.nps(nps)
        if ctme is not None:
            self.ctme(ctme)
        if polimi:
            self.polimi(cells=polimi_cells)

    def nps(self, num):
        """ ``nps`` is a convenience method to change the number of particles to
            simulate

            :param int num: number of particles, maximum around ``2E9`` unless
                you've compiled MCNP with 64-bit integers
        """
        self.string += "nps %e\n" % (num)
        return self

    def ctme(self, num):
        """ ``ctme`` is a convenience method to change the number of minutes to
            run the deck.

            :param int num: number of minutes to run.  Beware that if the number
                of particles exceeds the maximum integer, the simulation will
                fail.
        """
        self.string += "ctme %e\n" % (num)
        return self

    def no_fission(self, cells=None):
        """ ``no_fission`` removes creation of neutrons from fission in certain
            cells using MCNP's ``nonu`` directive.

            :param list cells: list of ``cell`` in which to remove fission
        """
        if cells is None:
            self.string += "nonu\n"
        return self

    def polimi(self, cells=[], out_src=False):
        """ ``polimi`` is a convenience method to use MCNP-Polimi to transport
            particles through the cells in ``cells``.

            :param list cells: list of ``cell`` to use MCNP-Polimi for transport
            :param list out_src: if you want to output the source
        """
        if out_src is True:
            out_src_int = 54
        else:
            out_src_int = 0
        if self.ipol is not None:
            self.string += "ipol {ipol[1]} {ipol[2]} {ipol[3]} {ipol[4]} {ipol[5]} {ipol[6]} ".format(ipol=[0] + self.ipol + [len(cells)])
        else:
            self.string += "ipol %d 0 0 0 2J %d " % (out_src_int, len(cells))
        for cell in cells:
            if isinstance(cell, int):
                self.string += "%d " % cell
            elif cell.__class__.__name__ is 'cell':
                self.string += "%d " % cell.cell_num
        self.string = self.string[:-1]
        self.string += "\n"
        if self.rpol is not None:
            self.string += "rpol {rpol[1]} {rpol[2]} {rpol[3]} {rpol[4]} {rpol[5]} {rpol[6]} {rpol[7]} {rpol[8]} {rpol[9]}\n".format(rpol=[0]+self.rpol)
        else:
            self.string += "rpol 1.0e-8 0 0 1 J\n"
        if len(cells)>0 and out_src is False:
            self.string += "files 21 DUMN1\n"
        elif len(cells)==0 and out_src is True:
            self.string += "files 2J 8J 1 {out_src_fname}\n"
        return self
