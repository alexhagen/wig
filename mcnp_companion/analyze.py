import copy
import numpy as np
#from pyg import twod as pyg
from pym import func as pym
from pyg.threed import pyg3d
import numpy as np
from pyg.colors import pu as puc

class tally(object):
    """ A ``tally`` object holds data from a tally.

    The tally object holds the total nps, the error in total nps, the name,
    and the spectrum data from an f4 tally, imported using the ``analyze``
    class.  The location and shape can also be set with external functions.

    :param float y: The total number of neutrons going through the volume.
    :param float u_y: The uncertainty in the total number of neutrons going
        through the volume.
    :param str name: A descriptive name for the tally.
    :param ``pym.func`` spectrum: A ``curve`` object holding the spectrum of the
        particles going through the volume.  ``spectrum.y`` and ``spectrum.x``
        hold the bin height and bin left edges, respectively.
    """
    def __init__(self, y, u_y, name=None, spectrum=None):
        self.y = y
        self.u_y = y
        if name is not None:
            self.name = name
        if spectrum is not None:
            self.fx = fx

        def set_loc(self, loc):
            """ Set the location of the current tally.

            ``set_loc`` sets an internal tuple for the location of the tally,
            usually specified by the center of the cell volume.

            :param tuple loc: The location in an ``(x, y, z)`` format.
            :returns: the modified ``tally`` object.
            """
            self.loc = loc
            return self

        def set_shape(self, shape='rpp'):
            """ Set the shape of the current tally.

            ``set_shape`` holds a string describing the shape of the tally
            volume.  In the future, this will also hold the sizes and directions
            needed to replicate the shape for plotting.

            .. todo:: Add in size and directions to ``tally.set_shape``

            :param str shape: The shape designation of the tally, default 'rpp'
            :returns: the modified ``tally`` object.
            """
            self.shape = shape
            return self

def find_between( s, first, last ):
    try:
        start = s.index( first ) + len( first )
        end = s.index( last, start )
        return s[start:end]
    except ValueError:
        return ""

class analyze(object):
    """ ``analyze`` goes through an output file and checks for tallies.

    An ``analyze`` object will hold ``tally`` objects in a list, one for each of
    the printed tallies on the file ``filename``, if these were generated as a
    tally file through mcnp.  Tallies printed on the ``.out`` file currently do
    not have support.

    .. todo:: Add support for tallies printed in a ``.out`` file.

    :param str filename: filename of the ``tallies.out`` file
    """
    def __init__(self, filename):
        with open(filename, 'r') as f:
            file_string = f.read()

        tallies = list()
        strings = file_string.split('tally')
        for string in strings[1:]:
            total, u_total, name, e_bins, vals, u_vals = \
                self.import_tally_section(string)
            tallies.extend([tally(total, u_total, name,
                                  pym.curve(e_bins, vals, u_y=u_vals,
                                            name=name, data='binned'))])
        self.tallies = tallies

    def import_tally_section(self, section):
        string = section
        name = string.split('\n')[2].strip()
        # find the string between et and t
        e_bins_string = find_between(string, "et", "vals")
        # remove first line and last line
        e_bins_string = ' '.join(e_bins_string.split('\n')[1:-2])
        e_bins = e_bins_string.split()
        e_bins = [float(bin) for bin in e_bins]
        # find the string between vals and tfc
        val_string = find_between(string, "vals", "tfc")
        val_string = ' '.join(val_string.split('\n')[1:-1])
        vals = val_string.split()
        u_vals = [float(val) for val in vals[1::2]]
        vals = [float(val) for val in vals[0::2]]
        total = vals[-1]
        u_total = u_vals[-1]
        u_vals = u_vals[:-1]
        vals = vals[:-1]
        u_vals = np.multiply(vals, u_vals)
        u_total = total * u_total
        return total, u_total, name, e_bins, vals, u_vals
