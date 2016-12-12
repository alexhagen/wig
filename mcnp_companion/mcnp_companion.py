import numpy as np
import textwrap
from runner import runner
from mcnp_string import mstring
from renderer import renderer
from os.path import expanduser

class mcnp_companion:
    def __init__(self, comment, filename, flavor='6', render=False):
        self.comment = ' '.join(comment.split())
        print "Initialized file with comment \"%s\"." % (self.comment)
        self.filename = expanduser("~") + '/mcnp/active/' + filename
        print "Will be written to %s.inp." % (filename)
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
        # now write the intro file
        self.intro_block += self.comment

    def run(self, remote, sys):
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

        self._runner = runner(self.filename, self.command, remote, sys,
                              renderer=self.renderer)


    def geo(self, geos=None):
        # initialize a counter
        self.geo_num = 10
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
                # increment geo num
                self.geo_num += 10

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
                    print cell.geo.nums
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
                self.tally_block += "f%d%d%s\n" % \
                    (self.tally_nums[str(tally.card)], tally.card, tally.string)
                # print the tally energy card
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
            # print the distributions
            # for dist in source.dists:
            #    # print the distribution definition
            #    self.data_block += "     sp%d    " % (self.sdef_num)
            #    self.data_block += "     %s\n" % (dist.string)
            #    self.sdef_num += 1
