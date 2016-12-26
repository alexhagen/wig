import copy
import numpy as np
#from pyg import twod as pyg
from pym import func as pym
from pyg.threed import pyg3d
import numpy as np
from pyg.colors import pu as puc
import os

class tally(object):
    """ A ``tally`` object holds data from a tally.

    The ``tally`` object holds the total nps, the error in total nps, the name,
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
            self.spectrum = spectrum

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

class meshtal(object):
    def __init__(self, xs, ys, zs, Es, phis, u_phis, name=None, field=None):
        self.xs = xs
        self.ys = ys
        self.zs = zs
        self.Es = Es
        self.phis = phis
        self.u_phis = u_phis
        self.name = name

def find_between( s, first, last=None):
    try:
        start = s.index( first ) + len( first )
        if last is not None:
            end = s.index( last, start )
        else:
            end = len(s)
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
        orig_filename = filename
        if '_tallies.out' not in filename:
            filename = filename + '_tallies.out'
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
        if '_tallies.out' not in orig_filename:
            meshtal_filename = orig_filename + '_meshtal.out'
        if os.path.exists(meshtal_filename):
            with open(meshtal_filename, 'r') as f:
                file_string = f.read()

            meshtals = list()
            strings = file_string.split('Mesh Tally Number')
            for string in strings[1:]:
                E_bins, xs, ys, zs, phis, u_phis = \
                    self.import_meshtal_section(string)
                tallies.extend(meshtal(xs, ys, zs, phis, u_phis))
        self.tallies = tallies

    def import_meshtal_section(self, section):
        string = section
        name = string.split('\n')[1].strip()
        x_bins_string = find_between(string, "X direction:", "Y direction")
        y_bins_string = find_between(string, "Y direction:", "Z direction")
        z_bins_string = find_between(string, "Z direction:", "Energy bin")
        E_bins_string = find_between(string, "Energy bin boundaries:", "Energy")
        x_bins_string = ' '.join(x_bins_string.split('\n'))
        x_bins = x_bins_string.split()
        x_bins = [float(bin) for bin in x_bins]
        y_bins_string = ' '.join(y_bins_string.split('\n'))
        y_bins = y_bins_string.split()
        y_bins = [float(bin) for bin in y_bins]
        z_bins_string = ' '.join(z_bins_string.split('\n'))
        z_bins = z_bins_string.split()
        z_bins = [float(bin) for bin in z_bins]
        E_bins_string = ' '.join(E_bins_string.split('\n'))
        E_bins = E_bins_string.split()
        E_bins = [float(bin) for bin in E_bins]
        val_string = find_between(string, 'Rel Error')
        vals = []
        u_vals = []
        for line in val_string.split('\n')[1:-1]:
            line_vals = ','.join(line.split())
            line_vals = [float(lv) for lv in line_vals.split(',')]
            val = line_vals[-2]
            u_val = line_vals[-1]
            vals.extend([val])
            u_vals.extend([u_val])
        vals = np.array(vals)
        u_vals = np.array(u_vals)
        vals.reshape((len(E_bins)-1, len(x_bins)-1, len(y_bins)-1, len(z_bins)-1))
        return E_bins, x_bins, y_bins, z_bins, vals, u_vals

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
