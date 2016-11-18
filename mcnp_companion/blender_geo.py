import bpy

class bgeo:
    def __init__(self):
        pass

    def rpp(self, x1=None, x2=None, y1=None, y2=None, z1=None, z2=None, c=None,
            l=None, name="rpp"):
        self.name = name
        bpy.ops.mesh.primitive_cube_add()
        bpy.context.object.name = name
        bpy.context.object.location = c
        bpy.context.object.scale = (l[0]/2., l[1]/2., l[2]/2.)
        bpy.ops.object.transform_apply(location=True, scale=True)
        self.object = bpy.context.object
        return self

    def sph(self, c=None, r=None, name="sph"):
        self.name = name
        bpy.ops.mesh.primitive_ico_sphere_add(subdivisions=4)
        bpy.context.object.name = name
        bpy.context.object.location = c
        bpy.context.object.scale = (r / 2., r / 2., r / 2.)
        bpy.ops.object.transform_apply(location=True, scale=True)
        self.object = bpy.context.object
        return self

    def rcc(self, c=None, r=None, h=None, name="rcc"):
        self.name = name
        bpy.ops.mesh.primitive_cylinder_add()
        bpy.context.object.name = name
        bpy.context.object.location = c
        bpy.context.object.scale = (r / 2., r / 2., h / 2.)
        bpy.ops.object.transform_apply(location=True, scale=True)
        self.object = bpy.context.object
        return self

    def __add__(self, right):
        self.name = self.name + "p" + right.name
        union = self.object.modifiers.new(self.name,"BOOLEAN")
        union.operation = "UNION"
        union.object = right.object
        bpy.ops.object.modifier_apply(apply_as='DATA', modifier=self.name)
        bpy.context.scene.objects.unlink(right.object)
        # self.object = bpy.context.scene.objects.get(self.name)
        bpy.context.scene.objects.active = self.object
        return self

    def __sub__(self, right):
        self.name = self.name + "m" + right.name
        union = self.object.modifiers.new(self.name,"BOOLEAN")
        union.operation = "DIFFERENCE"
        union.object = right.object
        bpy.ops.object.modifier_apply(apply_as='DATA', modifier=self.name)
        bpy.context.scene.objects.unlink(right.object)
        # self.object = bpy.context.scene.objects.get(self.name)
        bpy.context.scene.objects.active = self.object
        return self

    def pz(self, x1=None, x2=None, y1=None, y2=None, z=None,
           name='p'):
        self.name = name
        verts = [(x1, y1, z), (x1, y2, z), (x2, y2, z), (x2, y1, z)]
        faces = [(0, 1, 2, 3)]
        ground_plane = bpy.data.meshes.new("ground_plane")
        ground_plane_object = bpy.data.objects.new("ground_plane", ground_plane)
        ground_plane_object.location = (0., 0., 0.)
        bpy.context.scene.objects.link(ground_plane_object)
        ground_plane.from_pydata(verts, [], faces)
        ground_plane.update(calc_edges=True)
        self.object = bpy.context.object
        return self

    def set_matl(self, matl=None):
        obj = bpy.context.scene.objects.get(self.name)
        bpy.context.scene.objects.active = obj
        # bpy.ops.object.material_slot_add()
        self.object.active_material = matl.matl
