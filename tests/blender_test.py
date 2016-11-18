import bpy
import numpy as np
from mcnp_companion.mcnp_companion.blender_matl import bmatl
from mcnp_companion.mcnp_companion.blender_render import brender
from mcnp_companion.mcnp_companion.blender_light import blight
from mcnp_companion.mcnp_companion.blender_scene import bscene
from mcnp_companion.mcnp_companion.blender_geo import bgeo

scene = bscene()

# Then, make and scale a slab of concrete
floor = bgeo().rpp(c=(0., 0., -65.), l=(500., 500., 30.), name='floor')
subfloor = bgeo().rpp(c=(0., 0., -65. - 15. - 50.), l=(500., 500., 100.),
                      name='subfloor')
concrete = bmatl().concrete(scale=50.).cutaway()
floor.set_matl(concrete)
subfloor.set_matl(concrete)
uranium = bmatl().flat(name="uranium", color=(1.0, 1.0, 0.))

dd_loc = (-65., 0., 0.)

water = bmatl().water().cutaway()

water_jacket = bgeo().sph(c=dd_loc, r=6.5156 + 0.8936 + 2.5461, name="water_jacket")
inner_water_jacket = bgeo().sph(c=dd_loc, r=6.5156, name="plasma")

plasma = bmatl().source()
water_jacket = water_jacket - inner_water_jacket
water_jacket.set_matl(water)

dd_plasma = bgeo().sph(c=dd_loc, r=6.5156, name="plasma")
dd_plasma.set_matl(plasma)

# Now make a small sphere
sphere = bgeo().sph(c=(0., 0., 0.), r=10.0, name="sphere")
sphere.set_matl(uranium)

# now make a bulb
bulbs = []
z = np.array([0., 0., 1.])
panel_face_centers = np.array([[50., 0., -50.], [0., -50., -50.], [0., 50., -50.]])
panel_face_directions = np.array([[0., 1., 0.], [1., 0., 0.], [-1., 0., 0.]])
bulb_offsets = np.array([[9.5, 0., 0.], [0., -9.5, 0.], [0., 9.5, 0.]])
column_spacing = [-45., -22.5, 0., 22.5, 45.]
row_spacing = np.array([0., 30., 60.]) + 7.5
for i in range(3):
    pc = panel_face_centers[i]
    direc = panel_face_directions[i]
    offset = bulb_offsets[i]
    for j in range(5):
        cs = column_spacing[j]
        for k in range(3):
            rs = row_spacing[k]
            center = pc + direc * cs + z * rs + offset + 3.5 / 2.
            bulbs.extend([bgeo().rcc(c=center, h=3.5, r=1.3, name='bulb%d%d%d' % (i,j,k))])

for bulb in bulbs:
    bulb.set_matl(water)

blight().sun(location=(1000., 1000., 1000.), strength=5.)

brender('shot', objects=[bulb for bulb in bulbs] + [sphere])
bpy.ops.wm.save_as_mainfile(filepath="shot.blend")
