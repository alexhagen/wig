import numpy as np
import textwrap

class mcnp_companion:
    def __init__(self, comment, filename, flavor='6'):
        self.comment = ' '.join(comment.split())
        print "Initialized file with comment \"%s\"." % (self.comment)
        self.filename = filename
        print "Will be written to %s.inp." % (filename)
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
            f.write("\n")
            # write the geometry block
            f.write("c " + " Geometry ".center(78, '-') + "\n")
            f.write(self.geo_block)
            f.write("\n")
            # write the data block
            f.write("c " + " Data ".center(78, '-') + "\n")
            f.write(self.data_block)
            f.write("c " + " Physics ".center(78, '-') + "\n")
            f.write(self.phys_block)
            f.write("c " + " Tallies ".center(78, '-') + "\n")
            f.write(self.tally_block)
            f.write("c " + " Materials ".center(78, '-') + "\n")
            f.write(self.matl_block)
            f.write("\n")


    def geo(self, geos=None):
        # initialize a counter
        self.geo_num = 10
        for geo in geos:
            # print the comment
            self.geo_block += "%s\n" % (geo.comment)
            # print the number
            self.geo_block += "%d    " % (self.geo_num)
            # print the geo string
            self.geo_block += "%s\n" % (geo.string)
            # set that geo number to the geometry object
            geo.num = self.geo_num
            # increment geo num
            self.geo_num += 10

    def cell(self, cells=None):
        # work on this algorithm
        pass

    def matl(self, matls=None):
        # initialize a counter
        self.matl_num = 1
        for matl in matls:
            # print the comment
            self.matl_block += "%s\n" % (matl.comment)
            # print the matl number
            self.matl_block += "m%d " % (self.matl_num)
            # print the matl string
            self.matl_block += "%s\n" % (matl.string)
            # set that number to the geometry object
            matl.num = self.matl_num
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
        self.tally_nums = {"1": 1, "4": 1}
        for tally in tallies:
            # print the comment
            self.tally_block += "fc%d%d %s\n" % \
                (self.tally_nums[str(tally.card)], tally.card, tally.comment)
            # print the tally type card
            self.tally_block += "f%d%d%s\n" % \
                (self.tally_nums[str(tally.card)], tally.card, tally.string)
            # print the tally energy card
            self.tally_block += "e%d%d %s\n" % \
                (self.tally_nums[str(tally.card)], tally.card,
                 tally.energy_string)
            # set that number to the geometry object
            tally.num = self.tally_nums[str(tally.card)]
            # increment matl num
            self.tally_nums[str(tally.card)] += 1

    def source(self, sources=None):
        for source in sources:
            # print the source definition
            self.data_block += "sdef    "
            # print the source string
            self.data_block += "%s\n" % (source.string % (self.sdef_num))
            # print the distributions
            # for dist in source.dists:
            #    # print the distribution definition
            #    self.data_block += "     sp%d    " % (self.sdef_num)
            #    self.data_block += "     %s\n" % (dist.string)
            #    self.sdef_num += 1
