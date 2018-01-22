import copy
import numpy as np
from pym import func as pym
from pyg.threed import pyg3d
from pyg.colors import pu as puc
import os
import pandas as pd

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
    def __init__(self, y, u_y, name=None, spectrum=None, nps=None, ts=None,
                 Es=None, vals=None, u_vals=None):
        self.y = y
        self.u_y = u_y
        self.nps = nps
        self.ts = ts
        self.Es = Es
        self.vals = vals
        self.u_vals = u_vals
        self.signals = {}
        if name is not None:
            self.name = name
        if spectrum is not None:
            self.spectrum = spectrum
        print self.y
        if ts is not None:
            i = 0
            for E in Es:
                key = r'$E_{n} < %.2f\unit{MeV}$' % E
                vals = self.vals[i*len(self.ts):(i+1)*len(self.ts)]
                print "len ts: %d, len vals: %d" % (len(self.ts), len(vals))
                self.signals[key] = pym.curve(self.ts, vals, key)
                i += 1
            vals = self.vals[i*len(self.ts):(i+1)*len(self.ts)]
            print "len ts: %d, len vals: %d" % (len(self.ts), len(vals))
            self.signals['total'] = pym.curve(self.ts, vals, 'total')

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

class pos_ref_array(object):
    def __init__(self, xs, ys, zs, vals, us=None):
        self.xs = np.unique(xs)
        self.ys = np.unique(ys)
        self.zs = np.unique(zs)


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
    def __init__(self, filename, nps=None, tmesh=False):
        orig_filename = filename
        if '_tallies.out' not in filename and 'meshtal' not in filename:
            filename = filename + '_tallies.out'
        with open(filename, 'r') as f:
            file_string = f.read()

        tallies = list()
        strings = file_string.split('tally')
        # print strings[0].split()
        if '_tallies.out' in filename:
            if nps is None:
                try:
                    self.nps = float(strings[0].split()[5])
                except ValueError:
                    self.nps = 1.0
                    print "could not get nps, defaulting to 1.0"
            else:
                self.nps = nps
        elif 'meshtal' in filename:
            #self.nps = float(strings[0].split()[19])
            self.nps = 1.0e9
        #print "%e" % self.nps
        if '_tallies.out' in filename:
            if tmesh:
                for string in strings[1:]:
                    try:
                        E_bins, xs, ys, zs, phis, u_phis = \
                            self.import_tmesh_section(string)
                        tallies.extend([meshtal(xs, ys, zs, E_bins, phis, u_phis)])
                    except IndexError:
                        total, u_total, name, e_bins, vals, u_vals, t_bins = \
                            self.import_tally_section(string)
                        if len(t_bins) > 1:
                            spect = pym.curve([], [], u_y=[], name=name,
                                              data='binned')
                        else:
                            spect = pym.curve(e_bins, vals, u_y=u_vals,
                                              name=name, data='binned')
                        tallies.extend([tally(total, u_total, name, spect,
                                              nps=self.nps, ts=t_bins,
                                              Es=e_bins, vals=vals,
                                              u_vals=u_vals)])
            else:
                for string in strings[1:]:
                    total, u_total, name, e_bins, vals, u_vals, t_bins = \
                        self.import_tally_section(string)
                    if len(t_bins) > 1:
                        spect = pym.curve([], [], u_y=[], name=name,
                                          data='binned')
                    else:
                        spect = pym.curve(e_bins, vals, u_y=u_vals,
                                          name=name, data='binned')
                    tallies.extend([tally(total, u_total, name, spect,
                                          nps=self.nps, ts=t_bins, Es=e_bins,
                                          vals=vals, u_vals=u_vals)])
        elif 'meshtal' in filename:
            meshtals = list()
            strings = file_string.split('Mesh Tally Number')
            if len(strings) < 2:
                strings = file_string.split('tally')
            print "Length of strings %d" % len(strings)
            for string in strings[1:]:
                E_bins, xs, ys, zs, phis, u_phis = \
                    self.import_meshtal_section(string)
                tallies.extend([meshtal(xs, ys, zs, E_bins, phis, u_phis)])
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
        self.xm = []
        self.ym = []
        self.zm = []
        self.phim = np.array([])
        self.u_phim = np.array([])
        self.locs = []
        self.phis = []
        for line in val_string.split('\n')[1:-1]:
            if len(line) > 0:
                line_vals = ','.join(line.split())
                line_vals = [float(lv) for lv in line_vals.split(',')]
                val = line_vals[-2]
                u_val = line_vals[-1]
                vals.extend([val])
                u_vals.extend([u_val])
        vals = np.array(vals)
        u_vals = np.array(u_vals)
        vals.reshape((len(E_bins)-1, len(x_bins)-1, len(y_bins)-1, len(z_bins)-1))
        u_vals.reshape((len(E_bins)-1, len(x_bins)-1, len(y_bins)-1, len(z_bins)-1))
        return np.array(E_bins), np.array(x_bins), np.array(y_bins), \
            np.array(z_bins), np.array(vals), np.array(u_vals)

    def import_tmesh_section(self, section):
        string = section
        name = string.split('\n')[1].strip()
        bins_string = find_between(string, '\nf', '\nd')
        nums_string = find_between(string, '\nf', '\n')
        nums = nums_string.split()
        total_bins = int(nums[0])
        num_ebins = int(nums[1])
        if num_ebins == 0:
            E_bins = []
        num_xbins = int(nums[2])
        num_ybins = int(nums[3])
        num_zbins = int(nums[4])
        bin_edges_string = find_between(string, nums_string, '\nd')
        bin_edges = bin_edges_string.split()
        bin_edges = [float(be) for be in bin_edges]
        x_bins = bin_edges[0:num_xbins+1]
        y_bins = bin_edges[num_xbins+1:num_xbins+num_ybins+2]
        z_bins = bin_edges[num_xbins+num_ybins+2:]
        val_string = find_between(string, "vals")
        val_string = ' '.join(val_string.split('\n')[1:-1])
        vals = val_string.split()
        u_vals = [float(val) for val in vals[1::2]]
        vals = [float(val) for val in vals[0::2]]
        return np.array(E_bins), np.array(x_bins), np.array(y_bins), \
            np.array(z_bins), np.array(vals), np.array(u_vals)

    def import_tally_section(self, section):
        string = section
        name = string.split('\n')[2].strip()
        # find the string between et and t
        if '\ntt' in string:
            e_bins_string = find_between(string, '\net', '\ntt')
            t_bins_string = find_between(string, '\ntt', '\nvals')
            t_bins_string = ' '.join(t_bins_string.split('\n')[1:])
            t_bins = t_bins_string.split()
            t_bins = [float(_bin) for _bin in t_bins]
        else:
            e_bins_string = find_between(string, '\net', '\nvals')
            t_bins = []
        # remove first line and last line
        e_bins_string = ' '.join(e_bins_string.split('\n')[1:])
        print e_bins_string
        e_bins = e_bins_string.split()
        e_bins = [float(bin) for bin in e_bins]
        # find the string between vals and tfc
        val_string = find_between(string, '\nvals', '\ntfc')
        val_string = ' '.join(val_string.split('\n')[1:-1])
        vals = val_string.split()
        u_vals = [float(val) for val in vals[1::2]]
        vals = [float(val) for val in vals[0::2]]
        #print name
        #print vals
        total = vals[-1]
        u_total = u_vals[-1]
        if '\ntt' not in string:
            u_vals = u_vals[:-1]
            vals = vals[:-1]
        u_vals = np.multiply(vals, u_vals)
        u_total = total * u_total
        return total, u_total, name, e_bins, vals, u_vals, t_bins
