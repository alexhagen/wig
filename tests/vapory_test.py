from vapory import *
import os

light = LightSource([10, 15, -20], [1.3, 1.3, 1.3])
wall = Plane([0, 0, 1], 20, Texture(Pigment('color', [1, 1, 1])))
ground = Plane( [0, 1, 0], 0,
                Texture( Pigment( 'color', [1, 1, 1]),
                         Finish( 'phong', 0.1,
                                 'reflection',0.4,
                                 'metallic', 0.3)))
sphere1 = Sphere([-4, 2, 2], 2.0, '''texture { pigment { granite turbulence 1.5 color_map {
    [0  .25 color White color Gray95] [.25  .5 color White color White]
    [.5 .75 color White color White] [.75 1.1 color White color Gray85]}}
    finish { ambient 0.2 diffuse 0.3 crand 0.003 reflection 0 } normal {
    dents .5 scale .5 }}''')
sphere2 =Sphere([4, 1, 0], 1.0, Texture('T_Ruby_Glass'),
                Interior('ior',2))


scene = Scene( Camera("location", [0, 5, -10], "look_at", [1, 3, 0]),
               objects = [ ground, wall, sphere1, sphere2, light],
               included=["glass.inc", "colors.inc", "textures.inc"] )

scene.render("purple_sphere.png", width=400, height=300 )
os.system('eog purple_sphere.png')
