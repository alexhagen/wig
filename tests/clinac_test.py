import sys
sys.path.append('/Users/ahagen/code/mcnp_companion')
from mcnp_companion import mcnp_companion as mcnpc
from mcnp_companion import geo as mcnpg
from mcnp_companion import matl as mcnpm
from mcnp_companion import phys as mcnpp
from mcnp_companion import tally as mcnpt
from mcnp_companion import source as mcnps

# First, we initialize our scene and tell it that we'll use MCNPX
scene = mcnpc.mcnp_companion(filename='clinac_no_target_h2',
                             flavor='x',
                             comment='''A photon source from bremsstrahlung
                                        onto material surrounding the clinac to
                                        determine the photoneutron output''')

# Geometry
# Add the cement floor
floor = mcnpg.geo().rpp(c=(0, 0, -115), l=(200, 200, 30), id='concrete-floor')
subfloor = mcnpg.geo().rpp(c=(0, 0, -180), l=(200, 200, 100), id='dirt-subfloor')
# Add some tally volumes
bulb0 = mcnpg.geo().rcc(c=(0, 0, 0), r=1.4, lz=2.8, id='bulb-0')
bulb52 = mcnpg.geo().rcc(c=(52, 0, 0), r=1.4, lz=2.8, id='bulb-52')
bulb132 = mcnpg.geo().rcc(c=(132, 0, 0), r=1.4, lz=2.8, id='bulb-132')
# Add the universe sphere
uni = mcnpg.geo().sph(c=(0, 0, 0), r=2E3, id='universe')
# Register this to the scene
scene.geo([floor, subfloor, bulb0, bulb52, bulb132, uni])


# Materials - inflate the number of H2
concrete = mcnpm.matl(rho=2.30, atom_perc=[('H-2', 0.304245),
                                           ('C-12', 0.002870),
                                           ('O-16', 0.498628),
                                           ('Na-23', 0.009179),
                                           ('Mg', 0.000717),
                                           ('Al-27', 0.010261),
                                           ('Si', 0.150505),
                                           ('K', 0.007114),
                                           ('Ca', 0.014882),
                                           ('Fe', 0.001599)], id='concrete')
# Soil from Miller and Turk 1951 - found in Wielopolski 2005
dirt = mcnpm.matl(rho=1.0, mass_perc=[('H-2', 2.81), ('C-12', 14.43),
                                      ('N-17', 0.001), ('O-16', 49.64),
                                      ('Na-23', 0.82), ('Al-27', 8.93),
                                      ('Si', 21.32), ('K', 0.56), ('Ca', 0.54),
                                      ('Fe', 0.96)], id='dirt')
air = mcnpm.matl(rho=0.001205, atom_perc=[('H-2', 0.000151),
                                          ('N-17', 0.784437),
                                          ('O-16', 0.210750),
                                          ('Ar', 0.004671)], id='air')
# Register these to the scene
scene.matl((concrete, dirt, air))

# Add some typical neutron physics - this will automatically fill
physics = mcnpp.phys(particles=["n", "p"], ctme=30)
scene.phys(physics)

# Now to add a few tally volumes
det1 = mcnpt.tally(card=4, comment='bulb at center', cell=bulb0, particle='n')
det2 = mcnpt.tally(card=4, comment='bulb at 52cm from axis', cell=bulb52,
                   particle='n')
det3 = mcnpt.tally(card=4, comment='bulb at 132cm from axis', cell=bulb132,
                   particle='n')
# floor_source = new tally(surface=(floor, 'z+'))
scene.tally((det1, det2, det3))

# A photon bremsstrahlung source
clinac = mcnps.source(type='p', spectrum=[(0, 0.0100, 0.0220, 0.0364, 0.0537,
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
'''
# Cells
concrete_cell = new cell(floor, conrete)
dirt_cell = new cell(subfloor, dirt)
air_cell = new cell((bulb0, bulb52, bulb132, uni), air)
# register the cells to the scene
scene.cells((concrete_cell, dirt_cell, air_cell))



# Render the scene so you can see that you're doing it correctly
scene.render('clinac_no_target_h2')
'''

# And, finally, run!
scene.run(remote='ssh://ahagen@mars-ubuntu.dynu.com', sys='linux')
