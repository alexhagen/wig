import bpy

scene = bpy.context.scene

# First, delete the default cube
bpy.ops.object.delete()

# Then, make and scale a slab of concrete
bpy.ops.mesh.primitive_cube_add()
bpy.context.object.name = "cement"
bpy.context.object.location = (0., 0., -0.15)
bpy.context.object.scale = (1.0/2, 1.0/2, 0.3/2)
bpy.ops.object.transform_apply(location=True, scale=True)
bpy.ops.object.mode_set(mode="EDIT")
bpy.ops.uv.unwrap()
bpy.ops.object.mode_set(mode="OBJECT")
soil = bpy.data.materials.new("soil")
soil.use_nodes = True
nodes = soil.node_tree.nodes
# add image texture with specularity file, non-color data
img_tex1 = nodes.new('ShaderNodeTexImage')
# add colorramp and set white downwards
col_ramp = nodes.new('ShaderNodeValToRGB')
# connect image texture -> color to colorramp fac
# add mix shader
mix = nodes.new('ShaderNodeMixShader')
# connect colorramp -> color to mixshader -> fac
# add image texture with color file, color data
img_tex2 = nodes.new('ShaderNodeTexImage')
# add diffuse bsdf, roughness 0
diffuse_node = nodes.new('ShaderNodeBsdfDiffuse')
# connect image texture -> color to diffuse bsdf -> color
# connect diffuse bsdf -> bsdf to mixshader -> shader
# create image texture with normal file, non color data
img_tex3 = nodes.new('ShaderNodeTexImage')
# create normal map, strength 0.2, tangent space
norm_map = nodes.new('ShaderNodeNormalMap')
# connect image texture -> color to normal map -> color
# create glossy bsdf, roughness 0.1
glossy_node = nodes.new('ShaderNodeBsdfGlossy')
# connect normal map -> normal to glossy bsdf -> normal
# connect glossy bsdf -> bsdf to mixshader -> shader
# create material output
output = nodes.new('ShaderNodeOutputMaterial')
# connect mixshader -> shader to material output -> surface
bpy.ops.object.material_slot_add()
bpy.context.object.active_material = soil

# Then, make and scale a slab of dirt
bpy.ops.mesh.primitive_cube_add()
bpy.context.object.name = "dirt"
bpy.context.object.location = (0., 0., -0.60)
bpy.context.object.scale = (1.0/2, 1.0/2, 0.6/2)
bpy.ops.object.transform_apply(location=True, scale=True)

# Now, add a background of pure, diffuse white
verts = [(-100.0, -100.0, -10.9), (-100.0, 100.0, -10.9),
         (100.0, 100.0, -10.9), (100.0, -100.0, -10.9)]
faces = [(0, 1, 2, 3)]
ground_plane = bpy.data.meshes.new("ground_plane")
ground_plane_object = bpy.data.objects.new("ground_plane", ground_plane)
ground_plane_object.location = (0., 0., 0.)
bpy.context.scene.objects.link(ground_plane_object)
ground_plane.from_pydata(verts, [], faces)
ground_plane.update(calc_edges=True)
white = bpy.data.materials.new("white")
white.diffuse_color = (1.0, 1.0, 1.0)
bpy.ops.object.material_slot_add()
bpy.context.object.active_material = white

bpy.data.scenes["Scene"].render.filepath = 'shot.jpg'
bpy.ops.render.render( write_still=True )
