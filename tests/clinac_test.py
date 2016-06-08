import sys
import mcnp_companion

# First, we initialize our scene and tell it that we'll use MCNPX
scene = mcnp_companion(filename='clinac_no_target_h2', flavor='x',
                       comment='''A photon source from bremsstrahlung onto
                                  material surrounding the clinac to determine
                                  the photoneutron output''')

# Geometry
geo = new geo()
# Add the cement floor
floor = geo.rpp(c=(0, 0, -115), l=(200, 200, 30), id='concrete-floor')
subfloor = geo.rpp(c=(0, 0, -180), l=(200, 200, 100),id='dirt-subfloor')
# Add some tally volumes
bulb0 = geo.rcc(c=(0, 0, 0), r=1.4, lz=2.8, id='bulb-0')
bulb52 = geo.rcc(c=(52, 0, 0), r=1.4, lz=2.8, id='bulb-52')
bulb132 = geo.rcc(c=(132, 0, 0), r=1.4, lz=2.8, id='bulb-132')
# Add the universe sphere
uni = geo.sph(c=(0, 0, 0), r=2E3, id='universe')
# Register this to the scene
scene.geo(geo)

# Materials - inflate the number of H2
concrete = new matl(rho=2.30, atom_perc=[('H-2', 0.304245), ('C-12', 0.002870),
                                         ('O-16', 0.498628),
                                         ('Na-23', 0.009179), ('Mg', 0.000717),
                                         ('Al-27', 0.010261), ('Si', 0.150505),
                                         ('K', 0.007114), ('Ca', 0.014882),
                                         ('Fe', 0.001599)], id='concrete')
# Soil from Miller and Turk 1951 - found in Wielopolski 2005
dirt = new matl(rho=1.0, mass_perc=[('H-2', 2.81), ('C-12', 14.43),
                                    ('N-17', 0.001), ('O-16', 49.64),
                                    ('Na-23', 0.82), ('Al-27', 8.93),
                                    ('Si', 21.32), ('K', 0.56), ('Ca', 0.54),
                                    ('Fe', 0.96)], id='dirt')
air = new matl(rho=0.001205, atom_perc=[('H-2', 0.000151), ('N-17', 0.784437),
                                        ('O-16', 0.210750), ('Ar', 0.004671)],
               id='air')
# Register these to the scene
scene.matl((conrete, dirt, air))

# Cells
concrete_cell = new cell(floor, conrete)
dirt_cell = new cell(subfloor, dirt)
air_cell = new cell((bulb0, bulb52, bulb132, uni), air)
# register the cells to the scene
scene.cells((concrete_cell, dirt_cell, air_cell))

# A photon bremsstrahlung source
clinac = new source(type='p', spectrum=[(0, 0.0100, 0.0220, 0.0364, 0.0537,
                                         0.0744, 0.0993, 0.1292, 0.1650,
                                         0.2080, 0.2596, 0.3215, 0.3958,
                                         0.4850, 0.5920, 0.7204, 0.8744,
                                         1.0593, 1.2812, 1.5474, 1.8669,
                                         2.2503, 2.7103, 3.2624, 3.9248,
                                         4.7198, 5.6738, 6.0000),
                                        (0, 0.1818, 0.2675, 0.3567, 0.4601,
                                         0.5852, 0.7305, 0.8737, 0.9878,
                                         1.1246, 1.4328, 1.4745, 1.3132,
                                         1.0466, 0.8419, 0.6704, 0.5284,
                                         0.4190, 0.3395, 0.2614, 0.1890,
                                         0.1411, 0.1104, 0.0662, 0.0311,
                                         0.0233, 0.0012, 0.0000)],
                    shape=('circle', 5), dir='z-')
scene.source((clinac))

# Now to add a few tally volumes
det1 = new tally(cell=bulb1)
det2 = new tally(cell=bulb2)
det3 = new tally(cell=bulb3)
floor_source = new tally(surface=(floor, 'z+'))
scene.tally((det1, det2, det3, floor_source))

# Add some typical neutron physics - this will automatically fill
scene.physics(ctme=30)

# Render the scene so you can see that you're doing it correctly
scene.render('clinac_no_target_h2')

# And, finally, run!
scene.run(remote='ssh://ahagen@mars-ubuntu.dynu.com', sys='linux')
