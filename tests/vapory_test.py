from vapory import *
import os

light = LightSource([10, 15, -20], [1.3, 1.3, 1.3])
wall = Plane([0, 0, 1], 20, Texture(Pigment('color', [1, 1, 1])))
ground = Plane( [0, 1, 0], 0,
                Texture( Pigment( 'color', [1, 1, 1]),
                         Finish( 'phong', 0.1,
                                 'reflection',0.4,
                                 'metallic', 0.3)))
sphere1 = Sphere([-4, 2, 2], 2.0, Pigment('color', [0, 0, 1]),
                                           Finish('phong', 0.8,
                                                  'reflection', 0.5))
sphere2 =Sphere([4, 1, 0], 1.0, Texture('Dark_Wood'))

scene = Scene( Camera("location", [0, 5, -10], "look_at", [1, 3, 0]),
               objects = [ ground, wall, sphere1, sphere2, light],
               included=["glass.inc", "Textures.inc"] )

scene.render("purple_sphere.png", width=800, height=480, antialiasing=0.001)
os.system("open -a Preview purple_sphere.png")
